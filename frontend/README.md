# 茶园智能感知与诊断平台前端

这是茶园智能感知与诊断平台的前端项目，基于 Vue 3、TypeScript 和 Vite 构建。当前前端已接入平台首页、茶叶高光谱成分分析模块，以及建设中的虫害识别模块，并支持高光谱数据上传、样本可视化和预测结果展示。

## 项目概览

当前前端包含以下业务入口：

- 平台首页：展示平台定位、核心模块和导航入口。
- 茶叶高光谱成分分析：支持上传 `.dat` 文件或高光谱文件夹，联动后端完成样本导入、光谱查看和成分预测。
- 虫害识别：已接入图像上传与预览界面，结果区仍为预留状态，便于后续扩展识别模型与诊断能力。

## 核心特性

- 响应式平台布局：基于 `PlatformLayout`、导航栏、页脚和模块卡片形成统一风格。
- 高光谱上传流程：支持单文件上传和文件夹导入，自动识别主 `.dat` 文件。
- 可视化联动：加载样本元信息、预览图和像素点光谱曲线，支持交互式选点查看。
- 成分预测展示：对儿茶素、咖啡因、茶氨酸和茶碱等指标进行结果卡片化展示。
- 模块复用设计：通过 `FileUploader`、`StatusBar`、`ResultCard` 等组件在不同业务场景中复用交互能力。
- PWA 支持：已集成 `vite-plugin-pwa`，可用于安装和离线缓存基础资源。

## 目录结构

```text
frontend/
├── public/                     # PWA 图标与静态资源
├── src/
│   ├── components/             # 通用组件与业务组件
│   ├── composables/            # 组合式逻辑，如预测与高光谱查看
│   ├── data/                   # 本地模拟数据
│   ├── router/                 # 路由配置
│   ├── views/                  # 页面视图
│   ├── App.vue                 # 根组件
│   ├── index.css               # 全局样式
│   ├── env.d.ts                # 环境类型声明
│   └── main.ts                 # 应用入口
├── .env.example                # 示例环境变量
├── index.html                  # HTML 模板
├── package.json                # 依赖与脚本
├── pnpm-lock.yaml              # pnpm 锁定文件
├── tsconfig.json               # TypeScript 配置
└── vite.config.ts              # Vite、代理与 PWA 配置
```

## 页面与路由

当前路由如下：

- `/`：平台首页
- `/tea-hyperspectral-prediction`：茶叶高光谱成分分析
- `/pest-detection`：虫害识别

## 技术栈

- Vue 3
- TypeScript
- Vite
- Vue Router
- Element Plus
- Tailwind CSS v4
- Axios
- Lucide Vue Next
- Vite PWA Plugin

## 开发环境

建议使用以下环境：

- Node.js 18+
- pnpm 8+

安装依赖：

```bash
cd frontend
pnpm install
```

启动开发服务器：

```bash
pnpm dev
```

默认监听地址为：

```text
http://localhost:3000
```

## 可用脚本

```bash
pnpm dev      # 启动开发环境
pnpm build    # 构建生产版本
pnpm preview  # 本地预览构建产物
pnpm lint     # 使用 TypeScript 进行类型检查
pnpm clean    # 删除 dist 目录
```

## 环境变量

项目根目录提供了 `.env.example`，当前示例变量如下：

```bash
APP_URL="MY_APP_URL"
```

可按需复制为本地环境文件：

```bash
cp .env.example .env
```

## 后端接口与代理

开发环境下，Vite 已将 `/api` 请求代理到本地后端：

```text
http://127.0.0.1:8000
```

当前前端已使用到的主要接口包括：

- `POST /api/hyperspectral/upload/import`：导入上传的高光谱文件或文件夹
- `GET /api/hyperspectral/samples/:sampleId`：获取样本元信息
- `GET /api/hyperspectral/samples/:sampleId/spectrum`：获取指定像素点光谱数据
- `POST /api/predict`：执行茶叶成分预测

## 高光谱分析流程

茶叶高光谱模块的典型使用流程如下：

1. 上传单个 `.dat` 文件，或直接选择包含高光谱数据的文件夹。
2. 前端调用导入接口，获取后端返回的 `sample_id`。
3. 根据样本信息加载预览图、中心像素点及对应光谱曲线。
4. 用户在预览图中切换像素点，前端重新请求该点的光谱数据。
5. 点击预测后，前端调用模型接口并展示成分结果卡片。

## PWA 说明

项目已启用 PWA 配置，应用名称为“茶园智能感知与诊断平台”。生产构建后可部署 `dist/` 目录，并在支持的浏览器中获得安装入口。

构建命令：

```bash
pnpm build
```

请确保 `public/` 目录中保留以下图标资源：

- `apple-touch-icon.png`
- `pwa-192x192.png`
- `pwa-512x512.png`

## 说明

- 虫害识别模块当前以界面与上传流程为主，识别结果区尚未接入正式模型输出。
- 部分设备数据当前来自本地模拟数据，后续可替换为真实设备接入能力。
