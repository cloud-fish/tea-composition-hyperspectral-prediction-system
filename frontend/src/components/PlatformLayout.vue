<script setup lang="ts">
import LargeModelQa from './LargeModelQa.vue';
import NavBar from './NavBar.vue';

withDefaults(defineProps<{
  uploadedFile?: any;
  pageClass?: string;
  mainClass?: string;
}>(), {
  uploadedFile: null,
  pageClass: 'min-h-screen bg-slate-50 text-slate-800',
  mainClass: 'mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 md:px-6 lg:px-8',
});
</script>

<template>
  <div :class="pageClass">
    <NavBar :uploadedFile="uploadedFile" />
    <main :class="mainClass">
      <slot />
    </main>
    <LargeModelQa />
  </div>
</template>
