<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { Leaf } from 'lucide-vue-next';

const props = defineProps<{
  uploadedFile: any
}>();

const route = useRoute();
const navItems = [
  { label: '首页', to: '/' },
  { label: '成分分析', to: '/tea-hyperspectral-prediction' },
  { label: '虫害识别', to: '/pest-detection' },
];

const isHomeRoute = computed(() => route.path === '/');
const isCompositionRoute = computed(() => route.path.startsWith('/tea-hyperspectral-prediction'));
const isPestDetectionRoute = computed(() => route.path.startsWith('/pest-detection'));
const isNavItemActive = (path: string) => {
  if (path === '/') {
    return route.path === '/';
  }
  return route.path.startsWith(path);
};

const systemStatusLabel = computed(() => {
  if (isHomeRoute.value) {
    return '平台运行中';
  }
  if (isPestDetectionRoute.value) {
    return '模块建设中';
  }
  if (isCompositionRoute.value) {
    return props.uploadedFile ? '分析就绪' : '等待数据';
  }
  return '平台在线';
});

const systemStatusClass = computed(() => {
  if (isHomeRoute.value) {
    return 'bg-sky-400';
  }
  if (isPestDetectionRoute.value) {
    return 'bg-amber-400';
  }
  if (isCompositionRoute.value) {
    return props.uploadedFile ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300';
  }
  return 'bg-emerald-500';
});
</script>

<template>
  <nav class="sticky top-0 z-10 flex flex-col gap-3 border-b border-emerald-100 bg-white px-4 py-3 shadow-sm md:px-8 lg:h-20 lg:flex-row lg:items-center lg:justify-between lg:gap-4 lg:py-0">
    <div class="flex items-center justify-between gap-3 lg:justify-start">
      <RouterLink to="/" class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-lg shadow-emerald-200 md:h-10 md:w-10">
          <Leaf class="w-5 h-5 md:w-6 md:h-6" />
        </div>
        <div class="flex flex-col">
          <h1 class="text-base md:text-xl font-bold text-slate-800 leading-none">茶园智能感知与诊断平台</h1>
          <p class="hidden sm:block text-[10px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">Tea Garden Intelligent Sensing And Diagnosis Platform</p>
        </div>
      </RouterLink>
    </div>
    <div class="flex flex-1 items-center justify-between gap-3 lg:justify-end">
      <div class="flex items-center gap-2 overflow-x-auto rounded-2xl bg-slate-50 px-2 py-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :class="[
            isNavItemActive(item.to)
              ? 'bg-white text-emerald-600 shadow-sm'
              : 'text-slate-500 hover:text-emerald-600',
            'rounded-xl px-3 py-2 text-sm font-semibold transition-colors whitespace-nowrap',
          ]"
        >
          {{ item.label }}
        </RouterLink>
      </div>
      <div class="flex items-center gap-2 md:gap-4 text-xs md:text-sm text-slate-500">
      <span class="flex items-center gap-1.5 font-medium">
        <span class="w-2 h-2 rounded-full" :class="systemStatusClass"></span> 
        <span class="hidden sm:inline">{{ systemStatusLabel }}</span>
      </span>
      <div class="hidden sm:block h-3 w-[1px] bg-slate-200 mx-1"></div>
      <span class="font-mono text-[10px] text-slate-400">v0.1.0</span>
      </div>
    </div>
  </nav>
</template>
