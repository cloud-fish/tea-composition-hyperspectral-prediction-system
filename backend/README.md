# 茶园智能感知与诊断平台 - 后端

基于 FastAPI 和 PyTorch 构建的茶园智能感知与诊断平台后端，提供茶叶高光谱成分预测和虫害检测两大核心服务。

## 功能模块

### 茶叶高光谱成分分析
- 读取 `.dat` 格式高光谱二进制文件（BIL 存储格式，512x512x204）
- 自动识别叶片区域、提取平均光谱曲线
- 转换为吸光度并计算一阶导数增强特征
- 基于 Transformer 回归模型（SpecTeaFormer）预测四种成分含量

### 虫害检测
- 基于 YOLO 目标检测模型识别茶园图像中的虫害
- 支持多种虫害类型：茶小绿叶蝉、蚜虫、茶尺蠖、介壳虫、茶毛虫等
- 返回检测框坐标、类别和置信度，生成标注结果图

## 技术栈

- **框架**: FastAPI
- **深度学习**: PyTorch
- **目标检测**: YOLO (ultralytics)
- **数据处理**: Scikit-learn, NumPy, Pandas, Joblib
- **服务部署**: Uvicorn

## 环境要求

- Python 3.9+
- CUDA（可选，用于加速推理）

## 安装与启动

```bash
cd backend
pip install -r requirements.txt
python api.py
```

服务默认运行在 `http://127.0.0.1:8000`

## API 接口

### 健康检查
- `GET /api/health` — 验证服务状态及模型加载情况

### 高光谱成分分析
- `POST /api/hyperspectral/upload/import` — 导入高光谱文件
- `GET /api/hyperspectral/samples/{sampleId}` — 获取样本信息
- `GET /api/hyperspectral/samples/{sampleId}/spectrum` — 获取光谱数据
- `POST /api/predict` — 执行成分预测

### 虫害检测
- `POST /api/pest-detection/detect` — 上传图像执行虫害检测

## 项目结构

```text
backend/
├── app/
│   ├── core/           # 核心配置
│   ├── routers/        # API 路由
│   ├── schemas/        # 数据模型
│   ├── services/       # 业务逻辑
│   └── main.py         # FastAPI 应用
├── models/             # 预训练模型
│   ├── transformer_4components.pth
│   ├── detection_best.pt
│   ├── scaler_x.pkl
│   └── scaler_y.pkl
├── utils/              # 工具类
│   ├── ReadHyperspectrum.py
│   ├── SpecTeaFormer.py
│   └── predict_components.py
── api.py              # 启动入口
── requirements.txt
```

## 模型说明

### SpecTeaFormer（成分预测）
- 输入维度：1（单波长点特征）
- 序列长度：204（波段数）
- 2 层 Transformer Encoder，4 个 Multi-head Attention 头，72 维 Embedding
- 全连接回归头，输出 4 维连续变量（儿茶素、咖啡因、茶氨酸、茶碱）

### YOLO（虫害检测）
- 基于 YOLO 目标检测架构
- 支持多类别虫害识别
- 输出检测框、类别标签和置信度
