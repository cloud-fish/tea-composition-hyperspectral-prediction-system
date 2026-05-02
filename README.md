# 茶叶成分高光谱预测系统 (Tea Composition Hyperspectral Prediction System)

这是一个基于深度学习高光谱分析技术的茶叶化学成分预测系统。系统利用 Transformer 架构的模型（SpecTeaFormer），通过分析茶叶的高光谱数据（.dat 格式），能够快速且准确地预测茶叶中的四种核心化学成分含量。

## 🌟 核心特性

- **高精度预测**：采用基于 Transformer 的多输出回归模型，精准捕捉光谱特征与化学成分之间的非线性关系。
- **四组分同步分析**：一次上传即可同时获取以下四种成分的含量（%）：
  - **儿茶素 (Catechins)**：抗氧化能力的关键指标。
  - **咖啡因 (Caffeine)**：茶叶提神效果的主要来源。
  - **茶氨酸 (Theanine)**：赋予茶叶鲜爽味及放松功效。
  - **茶碱 (Theophylline)**：重要的生物碱成分。
- **现代化交互界面**：基于 Vue 3 和 Element Plus 构建的响应式 Web 界面，支持文件拖拽上传和结果可视化。
- **智能语义评价**：根据预测数值自动给出“高/中/低”的语义化等级评价。

## 🛠️ 技术栈

### 后端 (Backend)
- **框架**: [FastAPI](https://fastapi.tiangolo.com/) - 高性能的 Python Web API 框架。
- **深度学习**: [PyTorch](https://pytorch.org/) - 用于构建和运行 Transformer 预测模型。
- **数据处理**: Scikit-learn (数据标准化), Joblib (模型序列化), NumPy, Pandas。
- **模型架构**: 自定义 Transformer Encoder 结构，专为一维光谱序列优化。

### 前端 (Frontend)
- **框架**: [Vue 3](https://vuejs.org/) (Composition API)
- **构建工具**: [Vite](https://vitejs.dev/)
- **UI 组件库**: [Element Plus](https://element-plus.org/)
- **样式**: [Tailwind CSS](https://tailwindcss.com/)
- **图标**: [Lucide Vue Next](https://lucide.dev/)
- **动画**: [Motion for Vue](https://motion.dev/)

## 📂 项目结构

```text
tea-composition-hyperspectral-prediction-system/
├── backend/                # 后端代码
│   ├── models/             # 预训练模型权重 (.pth) 及标准化器 (.pkl)
│   ├── utils/              # 光谱读取、模型定义及预测逻辑
│   ├── api.py              # FastAPI 主入口
│   └── requirements.txt    # 后端依赖
├── frontend/               # 前端代码
│   ├── src/                # Vue 源代码
│   ├── package.json        # 前端依赖及脚本
│   └── vite.config.ts      # Vite 配置
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备
确保您的系统中已安装 Python 3.9+ 和 Node.js 16+。

### 2. 后端部署
```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 启动服务 (默认运行在 http://127.0.0.1:8000)
python api.py
```

### 3. 前端部署
```bash
cd frontend
# 安装依赖
pnpm install  # 或 npm install
# 启动开发服务器 (默认运行在 http://localhost:3000)
pnpm dev      # 或 npm run dev
```

## 📝 使用指南

1. 启动后端和前端服务。
2. 在浏览器中访问 `http://localhost:3000`。
3. 将采集到的茶叶高光谱 `.dat` 文件拖拽至上传区域。
4. 点击“开始智能预测”按钮。
5. 系统将自动调用后端 Transformer 模型进行推理，并在界面上实时展示四种成分的预测值及其分布情况。

## 🔬 模型说明

本系统使用的 **SpecTeaFormer** 模型采用 2 层 Transformer Encoder 结构，包含 4 个注意力头。模型输入为经过预处理的一维光谱序列，通过位置编码（Positional Encoding）保留波长顺序信息，最终通过回归头输出四维连续变量。

---
*本项目仅供科研及辅助决策使用。*
