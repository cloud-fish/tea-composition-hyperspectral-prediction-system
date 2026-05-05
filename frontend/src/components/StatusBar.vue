<script setup lang="ts">
defineProps<{
  isPredicting: boolean,
  hasResults: boolean
}>();
</script>

<template>
  <div class="bg-white rounded-xl px-4 md:px-6 py-4 border border-emerald-100 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3 w-full sm:w-auto">
      <div class="text-[10px] text-slate-400 uppercase tracking-widest font-bold">引擎状态</div>
      <div class="flex items-center gap-2 text-xs text-emerald-700 font-bold bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">
        <span class="w-2 h-2 rounded-full" :class="[isPredicting ? 'animate-spin' : 'animate-pulse', hasResults ? 'bg-emerald-500' : (isPredicting ? 'bg-cyan-500' : 'bg-slate-300')]"></span>
        {{ hasResults ? '分析完成' : (isPredicting ? '运算中' : '待机中') }}
      </div>
    </div>
    <div v-if="hasResults" class="text-sm text-slate-500 font-mono font-bold self-end sm:self-auto bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
      CONFIDENCE: 99.1%
    </div>
  </div>
</template>
