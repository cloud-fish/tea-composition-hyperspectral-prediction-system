<script setup lang="ts">
import type { UploadFile } from 'element-plus';
import { Upload, Play, CheckCircle, Loader2, Zap, BarChart3 } from 'lucide-vue-next';

defineProps<{
  uploadedFile: any,
  isPredicting: boolean,
  uploadProgress: number
}>();

defineEmits<{
  (e: 'upload-change', file: any): void,
  (e: 'start-prediction'): void
}>();
</script>

<template>
  <aside class="w-full flex flex-col gap-3">
    <div class="bg-white rounded-2xl border border-emerald-100 shadow-sm p-3.5 md:p-4 flex flex-col gap-3 transition-all hover:shadow-md lg:flex-1">
      <div class="flex items-center gap-2 border-b border-slate-50 pb-2.5">
        <span class="bg-emerald-50 p-1.5 rounded-md">
          <Upload class="w-4.5 h-4.5 text-emerald-600" />
        </span>
        <h2 class="font-semibold text-slate-700">数据输入区</h2>
      </div>

      <!-- Drag & Drop Zone -->
      <div class="flex flex-col upload-container min-h-[52px]">
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          :on-change="(file: UploadFile) => $emit('upload-change', file)"
          accept=".dat"
          class="professional-upload"
        >
          <div class="flex flex-col items-center justify-center p-2.5 md:p-3 text-center">
            <div class="w-9 h-9 md:w-12 md:h-12 bg-white rounded-full flex items-center justify-center shadow-md mb-2.5 border border-emerald-50 group-hover:scale-105 transition-transform">
              <Upload class="w-4.5 h-4.5 md:w-7 md:h-7 text-emerald-500" />
            </div>
            <p class="text-emerald-700 font-bold mb-1 text-sm">点击或拖拽上传</p>
            <p class="text-slate-400 text-[11px] font-medium">支持格式：.dat 高光谱影像数据</p>
            <div v-if="uploadedFile" class="mt-2.5 flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-xl text-[10px] text-emerald-600 font-bold uppercase overflow-hidden max-w-[190px]">
              <CheckCircle class="w-3 h-3 flex-shrink-0" />
              <span class="truncate">{{ uploadedFile.name }}</span>
            </div>
          </div>
        </el-upload>
      </div>

      <!-- Action Button -->
      <button 
        @click="$emit('start-prediction')"
        :disabled="isPredicting"
        class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white py-2.5 rounded-xl font-bold shadow-lg shadow-emerald-100 flex items-center justify-center gap-2 transition-all active:scale-95 group overflow-hidden relative"
      >
        <div v-if="isPredicting" class="flex items-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin" />
          <span>智能推理中...</span>
        </div>
        <template v-else>
          <Play class="w-4 h-4" />
          <span>开始智能预测</span>
        </template>
      </button>

      <!-- 进度条显示 -->
      <div v-if="isPredicting" class="mt-1.5">
        <div class="flex justify-between text-xs text-slate-500 mb-1 font-medium">
          <span>{{ uploadProgress < 100 ? '数据上传中...' : '服务器分析中...' }}</span>
          <span>{{ uploadProgress }}%</span>
        </div>
        <el-progress 
          :percentage="uploadProgress" 
          :status="uploadProgress === 100 ? 'success' : ''"
          :stroke-width="8"
          :show-text="false"
          color="#059669"
        />
        <p v-if="uploadProgress === 100" class="text-[10px] text-slate-400 mt-2 text-center animate-pulse">
          大数据量处理中，请稍后...
        </p>
      </div>
    </div>

    <!-- Info Card -->
    <div class="bg-slate-900 rounded-2xl p-3.5 md:p-4 text-white relative overflow-hidden flex-shrink-0">
      <div class="relative z-10">
        <h3 class="text-emerald-400 font-bold text-[11px] uppercase tracking-widest mb-2">模型推理说明</h3>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center">
              <Zap class="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <p class="text-[10px] text-slate-400 leading-tight">采用 TensorRT 加速引擎，典型推理延迟 &lt; 300ms</p>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center">
              <BarChart3 class="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <p class="text-[10px] text-slate-400 leading-tight">基于 50,000+ 样本真实标定，支持全光谱校正</p>
          </div>
        </div>
      </div>
      <div class="absolute -bottom-6 -right-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl"></div>
    </div>
  </aside>
</template>
