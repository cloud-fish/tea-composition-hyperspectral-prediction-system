# 茶叶成分高光谱预测系统 - 前端 (Frontend)

这是茶叶成分高光谱预测系统的前端部分，基于 **Vue 3** (Composition API) 和 **Vite** 构建。本应用提供了一个现代化、响应式的用户界面，用于上传高光谱数据文件并实时可视化呈现茶叶成分的预测结果。

## 🚀 核心特性

- **组件化设计**：页面拆分为多个高内聚、低耦合的组件 (如 `ResultCard`, `StatusBar`, `UploadArea` 等)，便于维护和复用。
- **业务逻辑抽离**：使用 Vue Composables (`usePrediction`) 封装状态管理与后端通信逻辑。
- **响应式界面**：结合 **Tailwind CSS** 与 **Element Plus** 实现精美的自适应布局。
- **拖拽上传**：支持直观的文件拖拽上传，并包含状态提示。
- **PWA 支持**：配置了 Vite PWA 插件，支持离线缓存和作为桌面应用安装。

## 📁 目录结构

```text
frontend/
├── public/                 # 静态资源 (PWA 图标等)
├── src/
│   ├── components/         # 页面级和通用组件
│   ├── composables/        # 抽离的组合式业务逻辑
│   ├── router/             # Vue Router 路由配置
│   ├── views/              # 顶层视图组件
│   ├── App.vue             # 根组件
│   ├── index.css           # 全局样式 (包括 Tailwind 注入)
│   └── main.ts             # 应用入口
├── index.html              # HTML 模板
├── package.json            # 依赖管理
├── vite.config.ts          # Vite 及 PWA 配置
└── tsconfig.json           # TypeScript 配置
```

## 🛠️ 技术栈

- **Vue 3** (Composition API + `<script setup>`)
- **Vite** (快速的开发构建工具)
- **TypeScript** (强类型保障)
- **Element Plus** (Vue 3 UI 组件库)
- **Tailwind CSS** (原子化 CSS 框架)
- **Lucide Vue Next** (精美的 SVG 图标)
- **Vue Router** (前端路由)
- **Axios** (HTTP 客户端)

## 📦 安装与启动

1. **进入前端目录**:
   ```bash
   cd frontend
   ```

2. **安装依赖**:
   ```bash
   pnpm install  # 如果使用 npm 则运行 npm install
   ```

3. **启动开发服务器**:
   ```bash
   pnpm dev      # 或 npm run dev
   ```
   应用默认运行在 `http://localhost:3000`。

## 🌐 PWA 部署说明

本项目已配置支持 Progressive Web App (PWA)。

1. 确保在 `public/` 目录下包含 `pwa-192x192.png`, `pwa-512x512.png` 和 `apple-touch-icon.png` 等图标资源。
2. **构建生产版本**:
   ```bash
   pnpm build
   ```
3. 部署生成的 `dist/` 目录。在支持 PWA 的浏览器中访问时，地址栏会出现安装应用的提示，并且应用在离线状态下也能访问已缓存的页面骨架。
