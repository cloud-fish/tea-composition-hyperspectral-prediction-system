import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# 设置随机种子，保证结果可复现
torch.manual_seed(42)
np.random.seed(42)

# 检查是否有可用的GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")


# ===================== 1. 数据加载与预处理（适配4种成分） =====================
def load_data(file_path):
    """
    加载并预处理数据（适配4种成分预测）
    参数:
        file_path: Excel文件地址
    返回:
        标准化后的张量数据 + 标准化器
    """
    # 读取Excel中的光谱数据和目标成分数据
    # 光谱数据sheet：每行1个样本，204列对应204个波长点
    x_train_df = pd.read_excel(file_path, engine='openpyxl', sheet_name='train_spectrum', header=0)  # (288, 204)
    x_test_df = pd.read_excel(file_path, engine='openpyxl', sheet_name='test_spectrum', header=0)  # (72, 204)

    # 目标成分sheet：每行1个样本，4列对应4种成分（儿茶素/咖啡因/茶碱/茶氨酸）
    y_train_df = pd.read_excel(file_path, engine='openpyxl', sheet_name='train_target', header=0)  # (288, 4)
    y_test_df = pd.read_excel(file_path, engine='openpyxl', sheet_name='test_target', header=0)  # (72, 4)

    # 转换为ndarray格式
    x_train = x_train_df.values  # (288, 204)
    x_test = x_test_df.values  # (72, 204)
    y_train = y_train_df.iloc[:, 0:4].values  # 提取全部4种成分 (288, 4)
    y_test = y_test_df.iloc[:, 0:4].values  # (72, 4)

    # 特征标准化（光谱数据）
    scaler_x = StandardScaler()
    x_train_scaled = scaler_x.fit_transform(x_train)  # (288, 204)
    x_test_scaled = scaler_x.transform(x_test)  # (72, 204)

    # 目标值标准化（4种成分）
    scaler_y = StandardScaler()
    y_train_scaled = scaler_y.fit_transform(y_train)  # (288, 4)
    y_test_scaled = scaler_y.transform(y_test)  # (72, 4)

    return x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled, scaler_x, scaler_y

def to_tensor(x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled):
    """
    加载并预处理数据（适配4种成分预测）
    参数:
        file_path: Excel文件地址
    返回:
        标准化后的张量数据 + 标准化器
    """
    # 转换为PyTorch张量并适配模型输入格式
    # 模型输入格式：(样本数, 序列长度(波长数), 特征维度) → 序列长度=204，特征维度=1
    x_train_tensor = torch.FloatTensor(x_train_scaled).unsqueeze(2).to(device)  # (288, 204, 1)
    x_test_tensor = torch.FloatTensor(x_test_scaled).unsqueeze(2).to(device)  # (72, 204, 1)
    y_train_tensor = torch.FloatTensor(y_train_scaled).to(device)  # (288, 4)
    y_test_tensor = torch.FloatTensor(y_test_scaled).to(device)  # (72, 4)

    return x_train_tensor, y_train_tensor, x_test_tensor, y_test_tensor


# ===================== 2. Transformer核心模块实现（手动编写） =====================
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.transformer import TransformerRegressor


# ===================== 3. 训练/评估/可视化函数 =====================
def train_model(model, train_loader, criterion, optimizer, num_epochs):
    """
    训练多输出回归模型
    参数：
        model: 待训练模型
        train_loader: 训练数据加载器
        criterion: 损失函数（MSE）
        optimizer: 优化器
        num_epochs: 训练轮数
    返回：
        train_losses: 每轮训练的平均损失
    """
    model.train()  # 训练模式
    train_losses = []

    for epoch in range(num_epochs):
        total_loss = 0.0

        for batch_x, batch_y in train_loader:
            # 前向传播（获取预测值，注意力权重暂时不用）
            outputs, _ = model(batch_x)
            loss = criterion(outputs, batch_y)  # 计算MSE损失

            # 反向传播+优化
            optimizer.zero_grad()  # 梯度清零
            loss.backward()  # 反向传播
            optimizer.step()  # 更新参数

            total_loss += loss.item()

        # 计算本轮平均损失
        avg_loss = total_loss / len(train_loader)
        train_losses.append(avg_loss)

        # 每10轮打印损失
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], 平均损失: {avg_loss:.6f}')

    return train_losses


def evaluate_model(model, x_test, y_test, scaler_y):
    """
    评估模型性能（4种成分分别计算指标）
    参数：
        model: 训练好的模型
        x_test: 测试输入 (90, 204, 1)
        y_test: 测试目标 (90, 4)
        scaler_y: 目标值标准化器
    返回：
        metrics: 各成分的MSE/RMSE/R2字典
        y_pred_original: 反标准化后的预测值 (90, 4)
        y_test_original: 反标准化后的真实值 (90, 4)
        all_attn_weights: 测试集的注意力权重（用于可视化）
    """

    model.eval()  # 评估模式
    with torch.no_grad():  # 禁用梯度计算
        # 预测 + 注意力权重
        y_pred, all_attn_weights = model(x_test)

        # 反标准化（恢复原始成分含量尺度）
        y_pred_np = y_pred.cpu().numpy()
        y_test_np = y_test.cpu().numpy()
        y_pred_original = scaler_y.inverse_transform(y_pred_np)
        y_test_original = scaler_y.inverse_transform(y_test_np)

        # 计算4种成分的评估指标
        component_names = ['儿茶素', '咖啡因', '茶碱', '茶氨酸']
        metrics = {}
        for i, name in enumerate(component_names):
            mse = mean_squared_error(y_test_original[:, i], y_pred_original[:, i])
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test_original[:, i], y_pred_original[:, i])
            metrics[name] = {'MSE': mse, 'RMSE': rmse, 'R2': r2}
            print(f"\n{name} 评估指标:")
            print(f'  MSE: {mse:.6f}')
            print(f'  RMSE: {rmse:.6f}')
            print(f'  R2: {r2:.6f}')

        return metrics, y_pred_original, y_test_original, all_attn_weights


def visualize_attention(all_attn_weights, file_path, seq_len=204, layer_idx=0, head_idx=0):
    """
    注意力权重可视化：展示指定层/头对各波长的注意力分数
    参数：
        all_attn_weights: 所有层的注意力权重列表 [(batch, heads, 204, 204), ...]
        seq_len: 序列长度（波长数=204）
        layer_idx: 选择可视化的编码器层（默认第0层）
        head_idx: 选择可视化的注意力头（默认第0头）
    """
    # 取指定层的注意力权重 (batch, heads, 204, 204)
    layer_attn = all_attn_weights[layer_idx]
    # 取指定头的注意力权重，并对batch求平均 (204, 204)
    head_attn = layer_attn[:, head_idx, :, :].mean(dim=0).cpu().numpy()

    # 方案1：热力图（展示每个波长对其他波长的注意力）
    plt.figure(figsize=(8, 8))
    sns.heatmap(head_attn, cmap='viridis', xticklabels=50, yticklabels=50)
    plt.title(f'Transformer第{layer_idx + 1}层 第{head_idx + 1}注意力头 权重热力图', fontsize=14)
    plt.xlabel('注意力目标波长索引', fontsize=12)
    plt.ylabel('注意力查询波长索引', fontsize=12)
    plt.tight_layout()
    plt.show()

    # 方案2：平均注意力分数曲线（展示每个波长的平均注意力贡献）
    avg_attn_per_wavelength = head_attn.mean(axis=0)  # 每个波长的平均注意力分数 (204,)
    # df_to_write = pd.DataFrame(avg_attn_per_wavelength, columns=['Transformer'])
    # with pd.ExcelWriter(file_path, mode='a', engine='openpyxl') as writer:
    #     df_to_write.to_excel(writer, sheet_name='Sheet4', index=False, header=True)

    wavelength = np.arange(397, 1009, 3)
    plt.figure(figsize=(8, 6))
    plt.plot(wavelength, avg_attn_per_wavelength, color='darkred', linewidth=2)
    plt.fill_between(wavelength, avg_attn_per_wavelength, alpha=0.3, color='darkred')
    plt.title(f'Transformer第{layer_idx + 1}层 第{head_idx + 1}注意力头 波长注意力分数', fontsize=14)
    plt.xlabel('波长索引（204个数据点）', fontsize=12)
    plt.ylabel('平均注意力分数', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 方案3：Top-N重要波长（展示贡献最大的10个波长）
    top_k = 10
    top_indices = np.argsort(avg_attn_per_wavelength)[-top_k:][::-1]
    top_scores = avg_attn_per_wavelength[top_indices]

    plt.figure(figsize=(8, 6))
    plt.bar(range(top_k), top_scores, color='darkblue', alpha=0.7)
    plt.xticks(range(top_k), [f'波长{idx}' for idx in top_indices])
    plt.title(f'贡献最大的{top_k}个波长（第{layer_idx + 1}层 第{head_idx + 1}头）', fontsize=14)
    plt.xlabel('波长索引', fontsize=12)
    plt.ylabel('注意力分数', fontsize=12)
    plt.tight_layout()
    plt.show()


# ===================== 4. 主函数（执行流程） =====================
def main():
    # 1. 加载数据并标准化
    # 动态获取当前目录下的相对路径 (指向 backend 目录)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'spectroscopicdata.xlsx')
    x_train, y_train, x_test, y_test, scaler_x, scaler_y = load_data(file_path)
    print(f"训练输入形状: {x_train.shape}")  # (270, 204, 1)
    print(f"训练目标形状: {y_train.shape}")  # (270, 4)
    print(f"测试输入形状: {x_test.shape}")  # (90, 204, 1)
    print(f"测试目标形状: {y_test.shape}")  # (90, 4)

    # 2. 转为Tensor并创建数据加载器
    x_train_tnsor, y_train_tensor, x_test_tensor, y_test_tensor = to_tensor(x_train, y_train, x_test, y_test)
    batch_size = 32
    train_dataset = torch.utils.data.TensorDataset(x_train_tnsor, y_train_tensor)
    train_loader = torch.utils.data.DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=True  # 训练时打乱数据
    )

    # 3. 模型参数配置
    input_dim = 1  # 每个波长点的特征维度
    d_model = 72  # 模型维度（可调）
    num_layers = 2  # 编码器层数（可调）
    num_heads = 4  # 注意力头数（可调）
    d_ff = 128  # 前馈网络维度（可调）
    max_seq_len = 204  # 序列长度=波长数
    dropout = 0.1  # dropout概率
    learning_rate = 0.001  # 学习率
    num_epochs = 200  # 训练轮数

    # 4. 初始化模型/损失函数/优化器
    model = TransformerRegressor(
        input_dim=input_dim,
        d_model=d_model,
        num_layers=num_layers,
        num_heads=num_heads,
        d_ff=d_ff,
        max_seq_len=max_seq_len,
        dropout=dropout
    ).to(device)

    criterion = nn.MSELoss()  # 多输出回归仍用MSE（自动对4维求和）
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 5. 训练模型
    print("\n开始训练模型...")
    train_losses = train_model(model, train_loader, criterion, optimizer, num_epochs)

    # 6. 评估模型
    print("\n开始评估模型...")
    metrics, y_pred, y_test_ori, all_attn_weights = evaluate_model(model, x_test_tensor, y_test_tensor, scaler_y)

    # 7. 可视化训练损失
    plt.rcParams["font.family"] = ["STZhongsong"]  # 中文显示
    plt.rcParams["axes.unicode_minus"] = False  # 负号显示
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, num_epochs + 1), train_losses, label='训练损失', color='darkgreen')
    plt.xlabel('训练轮数 (Epoch)', fontsize=12)
    plt.ylabel('MSE损失', fontsize=12)
    plt.title('Transformer模型训练损失曲线', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    # 8. 保存模型
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    torch.save(model.state_dict(), os.path.join(models_dir, 'transformer_4components.pth'))
    print(f"\n模型已保存为: {os.path.join(models_dir, 'transformer_4components.pth')}")
    # 保存标准化器
    joblib.dump(scaler_x, os.path.join(models_dir, 'scaler_x.pkl'))
    joblib.dump(scaler_y, os.path.join(models_dir, 'scaler_y.pkl'))
    print(f"标准化器已保存到: {models_dir}")

if __name__ == "__main__":
    main()