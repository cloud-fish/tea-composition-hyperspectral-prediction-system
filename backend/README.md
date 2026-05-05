# 茶叶成分高光谱预测系统 - 后端 (Backend)

这是茶叶成分高光谱预测系统的后端部分，采用模块化的分层架构，负责处理高光谱图像数据并使用预训练的深度学习模型（SpecTeaFormer）进行成分预测。

## 🚀 功能特性

- **数据解析**：支持读取 `.dat` 格式的高光谱二进制文件（BIL 存储格式，512x512x204）。
- **预处理流程**：
  - 基于波段算法自动识别叶片区域。
  - 提取平均光谱曲线。
  - 转换为吸光度并计算一阶导数以增强特征。
- **深度学习推理**：集成基于 Transformer 的回归模型，同步预测儿茶素、咖啡因、茶碱和茶氨酸。
- **RESTful API**：基于 FastAPI 提供高性能的预测接口。
- **高可维护性架构**：将路由、业务逻辑、数据模式和核心配置分离，便于功能的扩展与测试。

## 📁 目录结构

```text
backend/
├── app/
│   ├── core/               # 核心模块（如配置管理 config.py, 生命周期 main.py 包含的逻辑）
│   ├── routers/            # API 路由定义 (例如 prediction.py)
│   ├── schemas/            # Pydantic 数据验证模型 (请求和响应格式)
│   ├── services/           # 核心业务逻辑 (如 prediction_service.py)
│   ├── __init__.py
│   └── main.py             # FastAPI 实例创建和中间件配置
├── models/                 # 预训练权重与标准化文件
│   ├── transformer_4components.pth  # Transformer 模型权重
│   ├── scaler_x.pkl                 # 输入特征标准化器
│   └── scaler_y.pkl                 # 输出目标标准化器
├── utils/                  # 工具模块
│   ├── ReadHyperspectrum.py # 高光谱文件读取与图像处理逻辑
│   └── SpecTeaFormer.py     # Transformer 模型架构定义
├── tests/                  # 单元测试与集成测试
├── api.py                  # Uvicorn 启动包装器
└── requirements.txt        # Python 依赖包列表
```

## 🛠️ 环境要求

- Python 3.9+
- CUDA (可选，用于加速推理)

## 📦 安装与启动

1. **进入后端目录**:
   ```bash
   cd backend
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **运行服务**:
   ```bash
   python api.py
   ```
   服务默认运行在 `http://127.0.0.1:8000`。

## 🔌 API 接口说明

### 1. 健康检查
- **URL**: `/api/health`
- **Method**: `GET`
- **Description**: 验证 API 服务是否正常运行及模型是否加载成功。

### 2. 成分预测
- **URL**: `/api/predict`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file`: `.dat` 格式的高光谱图像文件。
- **Success Response**: 返回包含四种成分预测值及其语义评价的 JSON 数据，符合 `schemas` 中定义的数据结构。

## 🧠 模型细节 (SpecTeaFormer)

后端集成的模型采用了自定义的 Transformer Encoder 架构：
- **输入维度**: 1 (单波长点特征)
- **序列长度**: 204 (波段数)
- **模型参数**: 2 层 Encoder，4 个 Multi-head Attention 头，72 维 Embedding。
- **回归头**: 全连接网络，输出 4 维连续变量。

---
*Backend module for Tea Composition Hyperspectral Prediction.*
