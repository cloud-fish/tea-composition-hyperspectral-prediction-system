import os
import shutil
import joblib
import torch
import uvicorn
import torch.nn as nn
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入你现有的模块
from utils import ReadHyperspectrum

# ===================== 1. 定义模型结构 =====================

class PositionalEncoding(nn.Module):
    """位置编码器：为光谱序列（波长点）添加位置信息"""

    def __init__(self, d_model, max_len=5000, dropout=0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class MultiHeadAttention(nn.Module):
    """多头自注意力模块"""

    def __init__(self, d_model, num_heads, dropout=0.1):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0, "d_model必须能被num_heads整除"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        k = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        v = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        scores = torch.matmul(q, k.transpose(-2, -1)) / np.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attn_weights = self.softmax(scores)
        attn_weights = self.dropout(attn_weights)

        output = torch.matmul(attn_weights, v)
        output = output.transpose(1, 2).contiguous()
        output = output.view(batch_size, -1, self.d_model)
        output = self.w_o(output)

        return output, attn_weights


class PositionWiseFeedForward(nn.Module):
    """位置前馈网络"""

    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionWiseFeedForward, self).__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class ResidualConnection(nn.Module):
    """残差连接 + 层归一化"""

    def __init__(self, size, dropout=0.1):
        super(ResidualConnection, self).__init__()
        self.norm = nn.LayerNorm(size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        return x + self.dropout(sublayer(self.norm(x)))


class EncoderLayer(nn.Module):
    """Transformer编码器层"""

    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff, dropout)
        self.residual1 = ResidualConnection(d_model, dropout)
        self.residual2 = ResidualConnection(d_model, dropout)

    def forward(self, x, mask=None):
        attn_output, attn_weights = self.self_attn(x, x, x, mask)
        x = self.residual1(x, lambda x: attn_output)
        x = self.residual2(x, self.feed_forward)
        return x, attn_weights


class TransformerEncoder(nn.Module):
    """完整Transformer编码器"""

    def __init__(self, input_dim, d_model, num_layers, num_heads, d_ff, max_seq_len, dropout=0.1):
        super(TransformerEncoder, self).__init__()
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_seq_len, dropout)

        self.layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        all_attn_weights = []
        x = self.input_projection(x)
        x = self.pos_encoder(x)

        for layer in self.layers:
            x, attn_weights = layer(x, mask)
            all_attn_weights.append(attn_weights)

        x = self.norm(x)
        return x, all_attn_weights


class TransformerRegressor(nn.Module):
    """基于Transformer的多输出回归模型"""

    def __init__(self, input_dim, d_model, num_layers, num_heads, d_ff, max_seq_len, dropout=0.1):
        super(TransformerRegressor, self).__init__()
        self.encoder = TransformerEncoder(
            input_dim=input_dim,
            d_model=d_model,
            num_layers=num_layers,
            num_heads=num_heads,
            d_ff=d_ff,
            max_seq_len=max_seq_len,
            dropout=dropout
        )

        self.regression_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 4)  # 输出4种成分
        )

    def forward(self, x):
        enc_output, all_attn_weights = self.encoder(x)
        final_hidden = enc_output[:, -1, :]  # 取最后一个波长点的输出
        outputs = self.regression_head(final_hidden)
        return outputs, all_attn_weights


# ===================== 2. 模型加载与预测逻辑 =====================

def load_trained_model(model_path, model_config, device='cpu'):
    """加载训练好的Transformer模型"""
    model = TransformerRegressor(
        input_dim=model_config['input_dim'],
        d_model=model_config['d_model'],
        num_layers=model_config['num_layers'],
        num_heads=model_config['num_heads'],
        d_ff=model_config['d_ff'],
        max_seq_len=model_config['max_seq_len'],
        dropout=model_config['dropout']
    ).to(device)

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def predict_components(model, x_tensor, scaler_y=None):
    """使用加载的模型进行成分含量预测"""
    model.eval()
    with torch.no_grad():
        y_pred_scaled, attn_weights = model(x_tensor)
        y_pred = y_pred_scaled.cpu().numpy()

        if scaler_y is not None:
            y_pred = scaler_y.inverse_transform(y_pred)

    return y_pred, attn_weights

def predict_single_sample(model, spectrum_single, scaler_x, scaler_y=None, device='cpu'):
    """预测单个样本的成分含量"""
    if len(spectrum_single.shape) == 1:
        spectrum_single = spectrum_single.reshape(1, -1)

    x_scaled = scaler_x.transform(spectrum_single)
    x_tensor = torch.FloatTensor(x_scaled).unsqueeze(2).to(device)

    y_pred, _ = predict_components(model, x_tensor, scaler_y)

    result = {
        '儿茶素 (%)': y_pred[0, 0],
        '咖啡因 (%)': y_pred[0, 1],
        '茶碱 (%)': y_pred[0, 2],
        '茶氨酸 (%)': y_pred[0, 3]
    }

    return result

app = FastAPI(title="茶叶成分高光谱预测 API", version="1.0.0")


# 配置 CORS，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中建议替换为实际前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量缓存模型和标准化器
model = None
scaler_x = None
scaler_y = None
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@app.on_event("startup")
async def startup_event():
    """服务启动时加载模型，避免每次请求都重新加载"""
    global model, scaler_x, scaler_y
    print("正在加载模型和预处理文件...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    model_config = {
        'input_dim': 1, 'd_model': 72, 'num_layers': 2, 'num_heads': 4,
        'd_ff': 128, 'max_seq_len': 204, 'dropout': 0.1
    }
    
    model_path = os.path.join(base_dir, 'models', 'transformer_4components.pth')
    model = load_trained_model(model_path, model_config, device)
    
    scaler_x = joblib.load(os.path.join(base_dir, 'models', 'scaler_x.pkl'))
    scaler_y = joblib.load(os.path.join(base_dir, 'models', 'scaler_y.pkl'))
    print("模型加载完成，服务已就绪！")


@app.get("/api/health")
async def health_check():
    """验证服务是否正常运行"""
    return {"status": "ok", "message": "服务运行正常", "device": str(device)}

@app.post("/api/predict")
async def predict_spectrum(file: UploadFile = File(...)):
    """接收高光谱dat文件并返回预测结果"""
    print(f"--- 收到上传请求 ---")
    print(f"文件名: {file.filename}")
    
    if not file.filename.endswith('.dat'):
        raise HTTPException(status_code=400, detail="仅支持 .dat 格式的高光谱文件")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # 1. 保存上传的文件到临时目录
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. 读取并处理高光谱数据
        # 这里复用 ReadHyperspectrum 中的逻辑
        mean_spectrum = ReadHyperspectrum.read_data(temp_path, file.filename)
        
        # 3. 进行预测
        result = predict_single_sample(model, mean_spectrum, scaler_x, scaler_y, device=device)
        
        # 4. 返回格式化结果
        return {
            "code": 200,
            "message": "预测成功",
            "filename": file.filename,
            "data": {
                "catechins": {"name": "儿茶素", "value": float(result['儿茶素 (%)'])},
                "caffeine": {"name": "咖啡因", "value": float(result['咖啡因 (%)'])},
                "theophylline": {"name": "茶碱", "value": float(result['茶碱 (%)'])},
                "theanine": {"name": "茶氨酸", "value": float(result['茶氨酸 (%)'])}
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理过程中发生错误: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)