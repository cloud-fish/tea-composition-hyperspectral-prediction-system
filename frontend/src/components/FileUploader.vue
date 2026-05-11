<script setup lang="ts">
import type { Component } from 'vue';
import { ref } from 'vue';
import type { UploadFile } from 'element-plus';
import { Upload, Play, CheckCircle, Loader2, Zap, BarChart3 } from 'lucide-vue-next';

const folderInputRef = ref<HTMLInputElement | null>(null);

interface FileUploaderInfoItem {
  icon: Component;
  text: string;
}

withDefaults(defineProps<{
  uploadedFile: any,
  isPredicting: boolean,
  uploadProgress: number,
  fillUploadArea?: boolean,
  sectionTitle?: string,
  accept?: string,
  uploadTitle?: string,
  uploadDescription?: string,
  folderTitle?: string,
  folderDescription?: string,
  folderButtonText?: string,
  showFolderPicker?: boolean,
  actionText?: string,
  actionLoadingText?: string,
  progressUploadingText?: string,
  progressProcessingText?: string,
  processingHint?: string,
  infoTitle?: string,
  infoItems?: FileUploaderInfoItem[],
}>(), {
  fillUploadArea: false,
  sectionTitle: '数据输入区',
  accept: '.dat',
  uploadTitle: '点击或拖拽上传',
  uploadDescription: '支持 `.dat` 高光谱影像数据',
  folderTitle: '也可以直接选择结果文件夹',
  folderDescription: '自动识别目录中的 `.dat` 文件用于可视化和预测',
  folderButtonText: '选择文件夹',
  showFolderPicker: true,
  actionText: '开始智能预测',
  actionLoadingText: '智能推理中...',
  progressUploadingText: '数据上传中...',
  progressProcessingText: '服务器分析中...',
  processingHint: '大数据量处理中，请稍后...',
  infoTitle: '模型推理说明',
  infoItems: () => ([
    {
      icon: Zap,
      text: '采用TensorRT加速引擎，典型推理延迟 < 300ms',
    },
    {
      icon: BarChart3,
      text: '基于 50,000+ 样本真实标定，支持全光谱校正',
    },
  ]),
});

const emit = defineEmits<{
  (e: 'upload-change', file: any): void,
  (e: 'folder-change', files: File[]): void,
  (e: 'start-prediction'): void
}>();

function openFolderPicker() {
  folderInputRef.value?.click();
}

function handleFolderSelection(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files ?? []);
  if (files.length > 0) {
    emit('folder-change', files);
  }
  input.value = '';
}
</script>

<template>
  <aside class="w-full flex h-full flex-col gap-3">
    <div class="bg-white rounded-2xl border border-emerald-100 shadow-sm p-3.5 md:p-4 flex flex-col gap-3 transition-all hover:shadow-md lg:flex-1">
      <div class="flex items-center gap-2 border-b border-slate-50 pb-2.5">
        <span class="bg-emerald-50 p-1.5 rounded-md">
          <Upload class="w-4.5 h-4.5 text-emerald-600" />
        </span>
        <h2 class="font-semibold text-slate-700">{{ sectionTitle }}</h2>
      </div>

      <!-- Drag & Drop Zone -->
      <div
        :class="[
          fillUploadArea ? 'min-h-[320px] flex-1' : 'min-h-[32px]',
          'flex flex-col upload-container',
        ]"
      >
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          :on-change="(file: UploadFile) => $emit('upload-change', file)"
          :accept="accept"
          :class="[
            fillUploadArea ? 'h-full' : '',
            'professional-upload',
          ]"
        >
          <div
            :class="[
              fillUploadArea
                ? 'h-full min-h-[280px] flex-col content-center px-4 py-4 sm:justify-center sm:text-center'
                : 'flex-wrap px-2 py-1 sm:justify-start sm:text-left',
              'flex items-center justify-center gap-2.5 text-center',
            ]"
          >
            <div class="w-8 h-8 md:w-9 md:h-9 bg-white rounded-full flex items-center justify-center shadow-md border border-emerald-50 group-hover:scale-105 transition-transform">
              <Upload class="w-4 h-4 md:w-5 md:h-5 text-emerald-500" />
            </div>
            <div class="min-w-0">
              <p class="text-emerald-700 font-bold text-sm leading-none">{{ uploadTitle }}</p>
              <p class="mt-1 text-slate-400 text-[10px] font-medium leading-none">{{ uploadDescription }}</p>
            </div>
            <div v-if="uploadedFile" class="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 border border-emerald-100 rounded-xl text-[10px] text-emerald-600 font-bold uppercase overflow-hidden max-w-[180px]">
              <CheckCircle class="w-3 h-3 flex-shrink-0" />
              <span class="truncate">{{ uploadedFile.name }}</span>
            </div>
          </div>
        </el-upload>
      </div>

      <div
        v-if="showFolderPicker"
        class="flex items-center justify-between gap-3 rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5"
      >
        <div class="min-w-0">
          <p class="text-xs font-semibold text-slate-700">{{ folderTitle }}</p>
          <p class="mt-1 text-[10px] leading-none text-slate-400">{{ folderDescription }}</p>
        </div>
        <button
          type="button"
          class="flex-shrink-0 rounded-lg border border-emerald-200 bg-white px-3 py-1.5 text-xs font-semibold text-emerald-600 transition hover:bg-emerald-50"
          @click="openFolderPicker"
        >
          {{ folderButtonText }}
        </button>
        <input
          ref="folderInputRef"
          type="file"
          multiple
          webkitdirectory
          directory
          class="hidden"
          @change="handleFolderSelection"
        />
      </div>

      <!-- Action Button -->
      <button 
        @click="$emit('start-prediction')"
        :disabled="isPredicting"
        class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white py-2.5 rounded-xl font-bold shadow-lg shadow-emerald-100 flex items-center justify-center gap-2 transition-all active:scale-95 group overflow-hidden relative"
      >
        <div v-if="isPredicting" class="flex items-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin" />
          <span>{{ actionLoadingText }}</span>
        </div>
        <template v-else>
          <Play class="w-4 h-4" />
          <span>{{ actionText }}</span>
        </template>
      </button>

      <!-- 进度条显示 -->
      <div v-if="isPredicting" class="mt-1.5">
        <div class="flex justify-between text-xs text-slate-500 mb-1 font-medium">
          <span>{{ uploadProgress < 100 ? progressUploadingText : progressProcessingText }}</span>
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
          {{ processingHint }}
        </p>
      </div>
    </div>

    <!-- Info Card -->
    <div class="bg-slate-900 rounded-2xl p-3.5 md:p-4 text-white relative overflow-hidden flex-shrink-0">
      <div class="relative z-10">
        <h3 class="text-emerald-400 font-bold text-[11px] uppercase tracking-widest mb-2">{{ infoTitle }}</h3>
        <div class="space-y-2">
          <div v-for="item in infoItems" :key="item.text" class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center">
              <component :is="item.icon" class="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <p class="text-[10px] text-slate-400 leading-tight">{{ item.text }}</p>
          </div>
        </div>
      </div>
      <div class="absolute -bottom-6 -right-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl"></div>
    </div>
  </aside>
</template>
