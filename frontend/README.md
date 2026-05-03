<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/93f2fb9d-589a-4b79-ba7f-da8b867353ef

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Run the app:
   `npm run dev`

## PWA 部署说明

本项目已配置支持 Progressive Web App (PWA)。部署前请执行以下步骤：

1. **安装 PWA 插件**:
   ```bash
   pnpm add -D vite-plugin-pwa
   ```

2. **添加图标资源**:
   请在 `public/` 目录下添加以下图标文件：
   - `pwa-192x192.png`
   - `pwa-512x512.png`
   - `apple-touch-icon.png` (建议 180x180)

3. **构建应用**:
   ```bash
   npm run build
   ```
   构建完成后，浏览器访问时会提示“安装应用”，且在断网状态下也能访问已缓存的资源。
