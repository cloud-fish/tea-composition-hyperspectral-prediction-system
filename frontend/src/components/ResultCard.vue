<script setup lang="ts">
const props = defineProps<{
  card: { key: string, name: string, action: string, color: string, low: number, high: number, icon: any },
  hasResults: boolean,
  value: number
}>();

const getLevelLabel = (key: string, value: number) => {
  if (!props.hasResults) return '-';
  if (key === 'catechin') return value > 5 ? '高' : '正常';
  if (key === 'caffeine') return value > 3 ? '高' : (value > 1 ? '中' : '低');
  if (key === 'theanine') return value > 2 ? '高' : (value > 0.5 ? '中' : '低');
  if (key === 'theophylline') return value > 0.1 ? '高' : '低';
  return '中';
};

const getColorClasses = (color: string) => {
  const map: Record<string, any> = {
    emerald: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-50', bar: 'bg-emerald-500', shadow: 'shadow-emerald-200' },
    teal: { bg: 'bg-teal-50', text: 'text-teal-600', border: 'border-teal-50', bar: 'bg-teal-500', shadow: 'shadow-teal-200' },
    cyan: { bg: 'bg-cyan-50', text: 'text-cyan-600', border: 'border-cyan-50', bar: 'bg-cyan-500', shadow: 'shadow-cyan-200' },
    lime: { bg: 'bg-lime-50', text: 'text-lime-600', border: 'border-lime-50', bar: 'bg-lime-500', shadow: 'shadow-lime-200' },
  };
  return map[color] || map.emerald;
};

const getProgress = (key: string, value: number) => {
  const norm: Record<string, number> = {
    catechin: (value / 25) * 100,
    caffeine: (value / 8) * 100,
    theophylline: (value / 2) * 100,
    theanine: (value / 4) * 100,
  };
  return Math.min(norm[key] || value, 100);
};
</script>

<template>
  <div 
    class="bg-white rounded-2xl border transition-all duration-500 p-5 md:p-6 flex flex-col justify-between group shadow-sm"
    :class="[getColorClasses(card.color).border, hasResults ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4']"
  >
    <div class="flex justify-between items-start mb-4">
      <div>
        <h3 class="text-slate-400 text-base font-bold uppercase tracking-wider mb-1">{{ card.name }}</h3>
        <div class="flex items-center gap-2">
          <p class="text-slate-800 text-2xl font-black">{{ card.action }}</p>
          <span v-if="hasResults" class="text-sm px-2 py-1 rounded-md font-bold uppercase" :class="getColorClasses(card.color).bg + ' ' + getColorClasses(card.color).text">
            {{ getLevelLabel(card.key, value) }}
          </span>
        </div>
      </div>
      <div class="p-4 rounded-2xl shadow-inner" :class="getColorClasses(card.color).bg">
        <component :is="card.icon" class="w-10 h-10 md:w-12 md:h-12" :class="getColorClasses(card.color).text" />
      </div>
    </div>
    <div>
      <div class="text-3xl md:text-4xl font-black text-slate-800 mb-4 flex items-baseline">
        {{ value }}
        <span class="text-lg ml-1 text-slate-300 font-bold">mg/g</span>
      </div>
      <div class="space-y-2">
        <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
          <div 
            class="h-full rounded-full transition-all duration-1000 ease-out" 
            :class="[getColorClasses(card.color).bar]"
            :style="{ width: getProgress(card.key, value) + '%' }"
          ></div>
        </div>
        <div class="flex justify-between text-[9px] text-slate-400 font-bold">
          <span>MIN: {{ card.low }}</span>
          <span>MAX: {{ card.high }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
