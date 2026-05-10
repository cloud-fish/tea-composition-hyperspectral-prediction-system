<script setup lang="ts">
import { ref } from 'vue';
import { BarChart3, Zap, FlaskConical, Sparkles } from 'lucide-vue-next';
import { usePrediction } from '../composables/usePrediction';
import { mockDevices } from '../data/devices';
import DeviceListSidebar from '../components/DeviceListSidebar.vue';
import NavBar from '../components/NavBar.vue';
import FileUploader from '../components/FileUploader.vue';
import StatusBar from '../components/StatusBar.vue';
import ResultCard from '../components/ResultCard.vue';

const {
  isPredicting,
  uploadProgress,
  hasResults,
  uploadedFile,
  results,
  startPrediction,
  handleUploadChange,
  resetPrediction
} = usePrediction();

const cards = [
  { key: 'catechin', name: '儿茶素', action: '抗氧化', color: 'emerald', low: 5, high: 20, icon: BarChart3 },
  { key: 'caffeine', name: '咖啡因', action: '提神', color: 'teal', low: 1, high: 6, icon: Zap },
  { key: 'theanine', name: '茶氨酸', action: '放松', color: 'lime', low: 0.5, high: 3, icon: Sparkles },
  { key: 'theophylline', name: '茶碱', action: '刺激', color: 'cyan', low: 0, high: 2, icon: FlaskConical },
] as const;

const selectedDeviceId = ref<string | null>(mockDevices[0]?.id ?? null);
</script>

<template>
  <div class="h-screen overflow-hidden bg-slate-50 font-sans text-slate-800 flex flex-col">
    <!-- Header Navigation -->
    <NavBar :uploadedFile="uploadedFile" />

    <!-- Main Content Area -->
    <main class="flex-1 min-h-0 flex flex-col gap-6 overflow-hidden p-4 md:p-6 lg:flex-row lg:items-stretch">
      <div class="flex w-full flex-col gap-6 lg:h-full lg:min-h-0 lg:w-[300px] lg:flex-shrink-0 lg:overflow-y-auto">
        <DeviceListSidebar
          v-model:selectedDeviceId="selectedDeviceId"
          :devices="mockDevices"
          class="lg:min-h-0 lg:flex-[1.05]"
        />

        <FileUploader 
          class="lg:min-h-0 lg:flex-1"
          :uploadedFile="uploadedFile"
          :isPredicting="isPredicting"
          :uploadProgress="uploadProgress"
          @upload-change="handleUploadChange"
          @start-prediction="startPrediction"
        />
      </div>

      <!-- Right Section: Prediction Results -->
      <section class="flex-1 min-h-0 flex flex-col gap-6 overflow-hidden">
          <!-- Status / Info Bar -->
          <StatusBar 
            :isPredicting="isPredicting" 
            :hasResults="hasResults" 
          />

          <!-- Results Grid -->
          <div class="flex-1 min-h-[300px]">
            <div v-if="!hasResults && !isPredicting" class="h-full flex flex-col items-center justify-center text-slate-400 bg-white rounded-2xl border border-dashed border-slate-200 py-10">
              <BarChart3 class="w-12 h-12 mb-4 opacity-10" />
              <p class="font-bold">暂无预测数据</p>
            </div>

            <div v-loading="isPredicting" element-loading-text="计算中..." class="h-full grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
              <ResultCard 
                v-for="card in cards" 
                :key="card.key"
                :card="card"
                :hasResults="hasResults"
                :value="results[card.key as keyof typeof results]"
              />
            </div>
          </div>

          <!-- Footer -->
          <div class="mt-4 flex flex-col sm:flex-row items-center justify-between gap-4 text-[9px] text-slate-400 font-bold uppercase pb-4">
            <p>© 2026 TEA LAB · v0.1.0</p>
            <div class="flex gap-4">
              <button class="hover:text-emerald-600 transition-colors" @click="resetPrediction">重置系统</button>
              <span class="hidden sm:inline">|</span>
              <span class="text-slate-300">GPU ACCELERATED</span>
            </div>
          </div>
      </section>

    </main>
  </div>
</template>
