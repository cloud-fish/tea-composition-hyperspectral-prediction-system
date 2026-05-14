<script setup lang="ts">
import { RouterView } from 'vue-router'
import LargeModelQa from './components/LargeModelQa.vue'
</script>

<template>
  <RouterView v-slot="{ Component }">
    <KeepAlive>
      <component :is="Component" />
    </KeepAlive>
  </RouterView>
  <LargeModelQa />
</template>

<style>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.professional-upload {
  display: flex !important;
  flex-direction: column !important;
}

.professional-upload .el-upload {
  width: 100% !important;
  height: auto !important;
}

.professional-upload .el-upload-dragger {
  width: 100% !important;
  height: auto !important;
  min-height: 0 !important;
  padding: 0 !important;
  border-radius: 1rem !important;
  border: 2px dashed #d1fae5 !important;
  background-color: rgba(236, 253, 245, 0.2) !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.professional-upload .el-upload-dragger:hover {
  background-color: rgba(236, 253, 245, 0.4) !important;
  border-color: #10b981 !important;
}

.professional-upload .el-upload--text {
  height: auto !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* V-loading customization */
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.7) !important;
  border-radius: 1rem !important;
}

.el-loading-spinner .path {
  stroke: #059669 !important;
}

.el-loading-spinner .el-loading-text {
  color: #059669 !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: -0.025em !important;
}
</style>
