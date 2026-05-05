"""
使用训练好的Transformer模型预测茶叶四种成分
文件: predict_tea_components.py
"""

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import ReadHyperspectrum
import joblib

# 设置随机种子，保证结果可复现
torch.manual_seed(42)
np.random.seed(42)

# 检查是否有可用的GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")


# ===================== 1. 定义与训练时完全相同的模型结构 =====================
# 注意：必须与训练代码中的模型定义完全一致，否则无法加载参数
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.transformer import TransformerRegressor


# ===================== 2. 模型加载函数 =====================
def load_trained_model(model_path, model_config, device='cpu'):
    """
    加载训练好的Transformer模型

    参数:
        model_path: 模型文件路径 (.pth)
        model_config: 模型配置字典，包含以下键：
            - input_dim: 输入特征维度（光谱数据为1）
            - d_model: 模型维度
            - num_layers: 编码器层数
            - num_heads: 注意力头数
            - d_ff: 前馈网络维度
            - max_seq_len: 最大序列长度（波长数）
            - dropout: dropout概率
        device: 设备 ('cpu' 或 'cuda')

    返回:
        model: 加载好权重的模型
    """
    # 实例化模型
    model = TransformerRegressor(
        input_dim=model_config['input_dim'],
        d_model=model_config['d_model'],
        num_layers=model_config['num_layers'],
        num_heads=model_config['num_heads'],
        d_ff=model_config['d_ff'],
        max_seq_len=model_config['max_seq_len'],
        dropout=model_config['dropout']
    ).to(device)

    # 加载模型权重
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()  # 切换到评估模式
    print(f"模型已从 {model_path} 加载成功")

    return model

# ===================== 3. 预测函数 =====================
def predict_components(model, x_tensor, scaler_y=None):
    """
    使用加载的模型进行成分含量预测

    参数:
        model: 加载好的Transformer模型
        x_tensor: 预处理后的光谱张量 (n_samples, 204, 1)
        scaler_y: 目标值标准化器（如果提供，会将预测结果反标准化）

    返回:
        predictions: 预测的成分含量 (n_samples, 4)
            列顺序: [儿茶素, 咖啡因, 茶碱, 茶氨酸]
        attn_weights: 所有层的注意力权重（可用于可视化）
    """
    model.eval()
    with torch.no_grad():
        y_pred_scaled, attn_weights = model(x_tensor)
        y_pred = y_pred_scaled.cpu().numpy()

        # 如果提供了标准化器，进行反标准化
        if scaler_y is not None:
            y_pred = scaler_y.inverse_transform(y_pred)

    return y_pred, attn_weights


def predict_single_sample(model, spectrum_single, scaler_x, scaler_y=None):
    """
    预测单个样本的成分含量

    参数:
        model: 加载好的模型
        spectrum_single: 单个样本的光谱数据 (204,) 或 (1, 204)
        scaler_x: 特征标准化器
        scaler_y: 目标值标准化器（可选）

    返回:
        predictions: 预测结果字典，包含四种成分的值
    """
    # 确保输入是二维数组
    if len(spectrum_single.shape) == 1:
        spectrum_single = spectrum_single.reshape(1, -1)

    # 标准化
    x_scaled = scaler_x.transform(spectrum_single)
    x_tensor = torch.FloatTensor(x_scaled).unsqueeze(2).to(device)

    # 预测
    y_pred, _ = predict_components(model, x_tensor, scaler_y)

    # 组织成字典返回
    result = {
        '儿茶素 (%)': y_pred[0, 0],
        '咖啡因 (%)': y_pred[0, 1],
        '茶碱 (%)': y_pred[0, 2],
        '茶氨酸 (%)': y_pred[0, 3]
    }

    return result

# ===================== 6. 主函数 =====================
def main():
    """
    使用示例：加载模型并对新数据进行预测
    """

    # ========== 1.配置参数（与训练时一致） ==========
    model_config = {
        'input_dim': 1,  # 每个波长点的特征维度
        'd_model': 72,  # 模型维度
        'num_layers': 2,  # 编码器层数
        'num_heads': 4,  # 注意力头数
        'd_ff': 128,  # 前馈网络维度
        'max_seq_len': 204,  # 序列长度（波长数）
        'dropout': 0.1  # dropout概率
    }

    # ========== 2.加载模型 ==========
    # 动态获取当前目录下的相对路径 (指向 backend 目录)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 训练好的模型文件路径
    model_path = os.path.join(base_dir, 'models', 'transformer_4components.pth')
    model = load_trained_model(model_path, model_config, device)  # 加载模型

    # 加载训练时保存的标准化器
    scaler_x = joblib.load(os.path.join(base_dir, 'models', 'scaler_x.pkl'))
    scaler_y = joblib.load(os.path.join(base_dir, 'models', 'scaler_y.pkl'))

    # ========== 3.读取预测新数据 ==========
    # file是文件编号，每张光谱图像有一个编号
    file = 9247
    file_name = str(file)  # 文件名
    
    file_path = os.path.join(base_dir, 'data', file_name, "results", f"REFLECTANCE_{file_name}.dat")
    
    print(f"\n开始读取{file_name}数据...")
    mean_spectrum = ReadHyperspectrum.read_data(file_path, file_name)

    # ========== 4.预测 ==========
    result = predict_single_sample(model, mean_spectrum, scaler_x, scaler_y)
    print("\n单个样本预测结果：")
    for component, value in result.items():
        print(f"  {component}: {value:.4f}")


if __name__ == "__main__":
    main()