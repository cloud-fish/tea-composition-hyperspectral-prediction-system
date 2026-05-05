import joblib
import torch
from app.core.transformer import TransformerRegressor
from app.config import settings

class ModelService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.scaler_x = None
            cls._instance.scaler_y = None
            cls._instance.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return cls._instance
        
    def load_model(self):
        """加载模型和标准化器"""
        if self.model is not None:
            return
            
        print("正在加载模型和预处理文件...")
        
        self.model = TransformerRegressor(
            input_dim=settings.MODEL_INPUT_DIM,
            d_model=settings.MODEL_D_MODEL,
            num_layers=settings.MODEL_NUM_LAYERS,
            num_heads=settings.MODEL_NUM_HEADS,
            d_ff=settings.MODEL_D_FF,
            max_seq_len=settings.MODEL_MAX_SEQ_LEN,
            dropout=settings.MODEL_DROPOUT
        ).to(self.device)
        
        self.model.load_state_dict(torch.load(settings.MODEL_PATH, map_location=self.device))
        self.model.eval()
        
        self.scaler_x = joblib.load(settings.SCALER_X_PATH)
        self.scaler_y = joblib.load(settings.SCALER_Y_PATH)
        print("模型加载完成，服务已就绪！")
        
    def predict_single_sample(self, spectrum_single):
        """预测单个样本"""
        if self.model is None:
            self.load_model()
            
        if len(spectrum_single.shape) == 1:
            spectrum_single = spectrum_single.reshape(1, -1)
            
        x_scaled = self.scaler_x.transform(spectrum_single)
        x_tensor = torch.FloatTensor(x_scaled).unsqueeze(2).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            y_pred_scaled, _ = self.model(x_tensor)
            y_pred = y_pred_scaled.cpu().numpy()
            
            if self.scaler_y is not None:
                y_pred = self.scaler_y.inverse_transform(y_pred)
                
        result = {
            '儿茶素 (%)': y_pred[0, 0],
            '咖啡因 (%)': y_pred[0, 1],
            '茶碱 (%)': y_pred[0, 2],
            '茶氨酸 (%)': y_pred[0, 3]
        }
        
        return result

model_service = ModelService()
