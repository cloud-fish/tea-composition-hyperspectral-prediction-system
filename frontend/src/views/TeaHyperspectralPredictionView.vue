<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { BarChart3, Zap, FlaskConical, Sparkles, PanelLeftClose, PanelLeftOpen, Usb } from 'lucide-vue-next';
import DataView from '../components/DataView.vue';
import { usePrediction } from '../composables/usePrediction';
import { useHyperspectralViewer } from '../composables/useHyperspectralViewer';
import { mockDevices } from '../data/devices';
import DeviceListSidebar from '../components/DeviceListSidebar.vue';
import PlatformFooter from '../components/PlatformFooter.vue';
import PlatformLayout from '../components/PlatformLayout.vue';
import FileUploader from '../components/FileUploader.vue';
import StatusBar from '../components/StatusBar.vue';
import ResultCard from '../components/ResultCard.vue';

const {
  isPredicting,
  uploadProgress,
  hasResults,
  uploadedFile,
  uploadedSampleId,
  isUploadedSpectrumLoading,
  uploadedSpectrumError,
  results,
  startPrediction,
  handleUploadChange,
  handleFolderChange,
  resetPrediction
} = usePrediction();

const cards = [
  { key: 'catechin', name: '儿茶素', action: '抗氧化', color: 'emerald', low: 5, high: 20, icon: BarChart3 },
  { key: 'caffeine', name: '咖啡因', action: '提神', color: 'teal', low: 1, high: 6, icon: Zap },
  { key: 'theanine', name: '茶氨酸', action: '放松', color: 'lime', low: 0.5, high: 3, icon: Sparkles },
  { key: 'theophylline', name: '茶碱', action: '刺激', color: 'cyan', low: 0, high: 2, icon: FlaskConical },
] as const;

const selectedDeviceId = ref<string | null>(mockDevices[0]?.id ?? null);
const isDesktopSidebarCollapsed = ref(false);
const selectedDeviceName = computed(
  () => mockDevices.find((device) => device.id === selectedDeviceId.value)?.name ?? '未选择',
);
const {
  sampleId,
  sampleMeta,
  spectrum,
  spectrumPoints,
  selectedPoint,
  previewUrl,
  isMetaLoading,
  isSpectrumLoading,
  errorMessage,
  reload,
  handlePreviewSelect,
} = useHyperspectralViewer();

watch(uploadedSampleId, async (newSampleId) => {
  sampleId.value = newSampleId;
  await reload();
}, { immediate: true });

const activeVisualizationTitle = computed(() =>
  '高光谱数据可视化',
);
const activeVisualizationDeviceName = computed(() =>
  sampleMeta.value?.device_name || null,
);
const activeVisualizationSampleName = computed(() =>
  spectrum.value?.sample_name || sampleMeta.value?.sample_name || null,
);
const activeVisualizationCapturedAt = computed(() =>
  spectrum.value?.acquisition_date || sampleMeta.value?.acquisition_date || null,
);
const activeVisualizationUnit = computed(() => spectrum.value?.unit || '反射率');
const activeVisualizationPoints = computed(() => spectrumPoints.value);
const activeVisualizationPreviewUrl = computed(() => previewUrl.value);
const activeVisualizationSelectedX = computed(() => selectedPoint.value?.x ?? null);
const activeVisualizationSelectedY = computed(() => selectedPoint.value?.y ?? null);
const activeVisualizationLoading = computed(() =>
  isUploadedSpectrumLoading.value || (Boolean(uploadedSampleId.value) && (isMetaLoading.value || isSpectrumLoading.value)),
);
const activeVisualizationError = computed(() =>
  uploadedSpectrumError.value || (uploadedSampleId.value ? errorMessage.value : null),
);
</script>

<template>
  <PlatformLayout
    :uploadedFile="uploadedFile"
    pageClass="min-h-screen bg-slate-50 font-sans text-slate-800 flex flex-col lg:h-screen lg:overflow-hidden"
    mainClass="flex-1 flex flex-col gap-6 p-4 md:p-6 lg:min-h-0 lg:flex-row lg:items-stretch lg:overflow-hidden"
  >
      <div class="flex w-full flex-col gap-6 lg:hidden">
        <DeviceListSidebar
          v-model:selectedDeviceId="selectedDeviceId"
          :devices="mockDevices"
        />

        <FileUploader 
          :uploadedFile="uploadedFile"
          :isPredicting="isPredicting"
          :uploadProgress="uploadProgress"
          @upload-change="handleUploadChange"
          @folder-change="handleFolderChange"
          @start-prediction="startPrediction"
        />
      </div>

      <aside
        :class="[
          isDesktopSidebarCollapsed ? 'lg:w-[92px]' : 'lg:w-[320px]',
          'relative hidden lg:flex lg:h-full lg:min-h-0 lg:flex-shrink-0 lg:flex-col lg:overflow-visible',
        ]"
      >
        <button
          type="button"
          :class="[
            isDesktopSidebarCollapsed ? 'bg-white text-slate-500' : 'bg-emerald-50 text-emerald-600',
            'absolute right-3 top-4 z-10 hidden h-10 w-10 items-center justify-center rounded-full border border-emerald-100 shadow-sm transition hover:border-emerald-200 hover:text-emerald-600 lg:flex',
          ]"
          @click="isDesktopSidebarCollapsed = !isDesktopSidebarCollapsed"
        >
          <PanelLeftOpen v-if="isDesktopSidebarCollapsed" class="h-4 w-4" />
          <PanelLeftClose v-else class="h-4 w-4" />
        </button>

        <div
          v-if="isDesktopSidebarCollapsed"
          class="flex h-full flex-col items-center gap-4 rounded-2xl border border-emerald-100 bg-white px-3 py-4 shadow-sm"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
            <Usb class="h-5 w-5" />
          </div>

          <div class="w-full rounded-2xl bg-slate-50 px-2 py-3 text-center">
            <div class="text-[10px] font-bold uppercase tracking-widest text-slate-400">设备</div>
            <div class="mt-2 text-lg font-bold text-slate-800">{{ mockDevices.length }}</div>
          </div>

          <div class="w-full rounded-2xl bg-emerald-50 px-2 py-3 text-center">
            <div class="text-[10px] font-bold uppercase tracking-widest text-emerald-500">当前</div>
            <div class="mt-2 break-all text-[11px] font-semibold text-emerald-700">
              {{ selectedDeviceName }}
            </div>
          </div>
        </div>

        <div v-else class="flex h-full min-h-0 flex-col gap-3 overflow-y-auto pr-1">
          <div class="flex min-h-0 flex-1 flex-col gap-6 pt-1">
            <DeviceListSidebar
              v-model:selectedDeviceId="selectedDeviceId"
              :devices="mockDevices"
              class="min-h-0 flex-[1.3]"
            />

            <FileUploader 
              class="min-h-0 flex-[0.7]"
              :uploadedFile="uploadedFile"
              :isPredicting="isPredicting"
              :uploadProgress="uploadProgress"
              @upload-change="handleUploadChange"
              @folder-change="handleFolderChange"
              @start-prediction="startPrediction"
            />
          </div>
        </div>
      </aside>

      <section class="flex-1 flex flex-col gap-6 lg:min-h-0 lg:overflow-y-auto lg:pr-1">
          <StatusBar 
            :isPredicting="isPredicting" 
            :hasResults="hasResults" 
          />

          <DataView
            :title="activeVisualizationTitle"
            :deviceName="activeVisualizationDeviceName"
            :sampleName="activeVisualizationSampleName"
            :capturedAt="activeVisualizationCapturedAt"
            :unit="activeVisualizationUnit"
            :points="activeVisualizationPoints"
            :previewImageUrl="activeVisualizationPreviewUrl"
            :imageWidth="sampleMeta?.samples || null"
            :imageHeight="sampleMeta?.lines || null"
            :selectedX="activeVisualizationSelectedX"
            :selectedY="activeVisualizationSelectedY"
            :loading="activeVisualizationLoading"
            :error="activeVisualizationError"
            :useDemoData="false"
            @select-point="handlePreviewSelect"
          />

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

          <PlatformFooter showReset @reset="resetPrediction" />
      </section>
  </PlatformLayout>
</template>
