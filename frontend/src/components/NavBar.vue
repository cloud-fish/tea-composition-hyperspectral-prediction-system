<script setup lang="ts">
import { Leaf } from 'lucide-vue-next';

defineProps<{
  uploadedFile: any
}>();
</script>

<template>
  <nav class="h-16 bg-white border-b border-emerald-100 flex-shrink-0 px-4 md:px-8 flex items-center justify-between shadow-sm z-10 sticky top-0">
    <div class="flex items-center gap-2 md:gap-3">
      <div class="w-8 h-8 md:w-10 md:h-10 bg-emerald-600 rounded-lg flex items-center justify-center text-white shadow-emerald-200 shadow-lg">
        <Leaf class="w-5 h-5 md:w-6 md:h-6" />
      </div>
      <div class="flex flex-col">
        <h1 class="text-base md:text-xl font-bold text-slate-800 leading-none">茶叶四组分高光谱预测系统</h1>
        <p class="hidden sm:block text-[10px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">Hyperspectral Intelligence Prediction System</p>
      </div>
    </div>
    <div class="flex items-center gap-2 md:gap-4 text-xs md:text-sm text-slate-500">
      <span class="flex items-center gap-1.5 font-medium">
        <span class="w-2 h-2 rounded-full" :class="uploadedFile ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'"></span> 
        <span class="hidden sm:inline">{{ uploadedFile ? '系统就绪' : '等待输入' }}</span>
      </span>
      <div class="hidden sm:block h-3 w-[1px] bg-slate-200 mx-1"></div>
      <span class="font-mono text-[10px] text-slate-400">v0.1.0</span>
    </div>
  </nav>
</template>
