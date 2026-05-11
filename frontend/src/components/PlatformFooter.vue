<script setup lang="ts">
withDefaults(defineProps<{
  showReset?: boolean;
}>(), {
  showReset: false,
});

defineEmits<{
  (e: 'reset'): void;
}>();
</script>

<template>
  <div class="mt-4 flex flex-col items-center justify-between gap-4 pb-4 text-[9px] font-bold uppercase text-slate-400 sm:flex-row">
    <p>© 2026 茶园智能感知与诊断平台 · v0.1.0</p>
    <div class="flex gap-4">
      <button
        v-if="showReset"
        class="transition-colors hover:text-emerald-600"
        @click="$emit('reset')"
      >
        重置系统
      </button>
      <span v-if="showReset" class="hidden sm:inline">|</span>
      <span class="text-slate-300">GPU ACCELERATED</span>
    </div>
  </div>
</template>
