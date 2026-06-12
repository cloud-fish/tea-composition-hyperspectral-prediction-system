# 茶园智能感知与诊断平台 (Tea Garden Intelligent Perception and Diagnosis Platform)

基于深度学习与高光谱分析技术的茶园智能感知与诊断平台，集成茶叶化学成分预测和虫害识别两大核心模块。

## 核心特性

### 茶叶高光谱成分分析
- **高精度预测**：基于 Transformer 架构（SpecTeaFormer），精准捕捉光谱特征与化学成分之间的非线性关系
- **四组分同步分析**：一次上传即可同时获取以下四种成分的含量（%）：
  - **儿茶素 (Catechins)**：抗氧化能力的关键指标
  - **咖啡因 (Caffeine)**：茶叶提神效果的主要来源
  - **茶氨酸 (Theanine)**：赋予茶叶鲜爽味及放松功效
  - **茶碱 (Theophylline)**：重要的生物碱成分
- **高光谱可视化**：支持样本预览图与像素点光谱曲线联动查看

### 虫害识别
- **图像上传与识别**：支持茶园巡检照片、虫害样本图和现场图像统一接入
- **检测结果展示**：标注图像展示、虫害种类统计与占比分析
- **虫害趋势分析**：多虫害类型（茶小绿叶蝉、蚜虫、茶尺蠖、介壳虫、茶毛虫）发生趋势可视化
- **可扩展架构**：便于后续扩展虫害识别、风险研判和诊断建议等业务能力

## 技术栈

### 后端
- **框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **深度学习**: [PyTorch](https://pytorch.org/)
- **数据处理**: Scikit-learn, NumPy, Pandas
- **目标检测**: YOLO (虫害识别)

### 前端
- **框架**: [Vue 3](https://vuejs.org/) (Composition API + TypeScript)
- **构建工具**: [Vite](https://vitejs.dev/)
- **UI 组件库**: [Element Plus](https://element-plus.org/)
- **样式**: [Tailwind CSS](https://tailwindcss.com/)
- **图标**: [Lucide Vue Next](https://lucide.dev/)
- **PWA**: [Vite PWA](https://vite-pwa-org.netlify.app/)

## 快速开始

### 环境准备
- Python 3.9+
- Node.js 18+
- pnpm 8+

### 启动后端
```bash
cd backend
pip install -r requirements.txt
python api.py
```
服务默认运行在 `http://127.0.0.1:8000`

### 启动前端
```bash
cd frontend
pnpm install
pnpm dev
```
前端默认运行在 `http://localhost:3000`

## 项目结构

```text
tea-composition-hyperspectral-prediction-system/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── core/           # 核心配置
│   │   ├── routers/        # API 路由
│   │   ├── schemas/        # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # FastAPI 应用
│   ├── models/             # 预训练模型
│   ├── utils/              # 工具类
│   └── requirements.txt
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # 通用组件
│   │   ├── composables/    # 组合式函数
│   │   ├── router/         # 路由配置
│   │   └── views/          # 页面视图
│   └── package.json
└── README.md
```

## 页面路由

| 路径 | 说明 |
|------|------|
| `/` | 平台首页 |
| `/tea-hyperspectral-prediction` | 茶叶高光谱成分分析 |
| `/pest-detection` | 虫害识别 |
