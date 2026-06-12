# 茶园智能感知与诊断平台 - 前端

基于 Vue 3、TypeScript 和 Vite 构建的茶园智能感知与诊断平台前端，集成茶叶高光谱成分分析和虫害识别两大模块。

## 功能模块

- **平台首页**：展示平台定位、核心模块和导航入口
- **茶叶高光谱成分分析**：支持上传 `.dat` 文件或高光谱文件夹，联动后端完成样本导入、光谱查看和成分预测
- **虫害识别**：支持图像上传、检测结果展示、虫害统计概览和发生趋势分析

## 核心特性

- 响应式平台布局，统一视觉风格
- 高光谱上传流程：支持单文件上传和文件夹导入
- 高光谱可视化：预览图与像素点光谱曲线联动
- 虫害检测结果：标注图像、种类统计环形图和占比表格
- 虫害趋势分析：多类型虫害折线图，支持近7天/14天/30天筛选
- PWA 支持，可安装和离线缓存

## 技术栈

- Vue 3 + TypeScript
- Vite
- Vue Router
- Element Plus
- Tailwind CSS v4
- Axios
- Lucide Vue Next
- Vite PWA Plugin

## 开发环境

- Node.js 18+
- pnpm 8+

```bash
cd frontend
pnpm install
pnpm dev
```

默认地址：`http://localhost:3000`

## 可用脚本

```bash
pnpm dev      # 启动开发环境
pnpm build    # 构建生产版本
pnpm preview  # 本地预览构建产物
pnpm lint     # TypeScript 类型检查
pnpm clean    # 删除 dist 目录
```

## 目录结构

```text
frontend/
├── public/
│   └── data/
│       └── pest_trend.csv        # 虫害趋势数据
├── src/
│   ├── components/               # 通用组件
│   │   ├── FileUploader.vue      # 文件上传组件
│   │   ├── NavBar.vue            # 导航栏
│   │   ├── PlatformLayout.vue    # 平台布局
│   │   └── PlatformFooter.vue    # 页脚
│   ├── composables/              # 组合式函数
│   │   ├── usePrediction.ts      # 成分预测逻辑
│   │   ├── useHyperspectralViewer.ts  # 高光谱查看逻辑
│   │   ├── usePestDetection.ts   # 虫害检测逻辑
│   │   └── usePestTrendChart.ts  # 虫害趋势图表逻辑
│   ├── router/                   # 路由配置
│   ├── views/                    # 页面视图
│   │   ├── HomeView.vue
│   │   ├── TeaHyperspectralPredictionView.vue
│   │   └── PestDetectionView.vue
│   └── main.ts
├── package.json
└── vite.config.ts
```

## 路由

| 路径 | 页面 |
|------|------|
| `/` | 平台首页 |
| `/tea-hyperspectral-prediction` | 茶叶高光谱成分分析 |
| `/pest-detection` | 虫害识别 |

## 后端接口与代理

开发环境下，Vite 已将 `/api` 请求代理到 `http://127.0.0.1:8000`

主要接口：

- `POST /api/hyperspectral/upload/import`：导入高光谱文件
- `GET /api/hyperspectral/samples/:sampleId`：获取样本信息
- `GET /api/hyperspectral/samples/:sampleId/spectrum`：获取光谱数据
- `POST /api/predict`：执行成分预测
- `POST /api/pest-detection/detect`：执行虫害检测
