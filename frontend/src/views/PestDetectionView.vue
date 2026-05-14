<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue';
import { ElMessage } from 'element-plus';
import type { UploadFile } from 'element-plus';
import { Bug, Camera, ImageIcon } from 'lucide-vue-next';
import FileUploader from '../components/FileUploader.vue';
import PlatformLayout from '../components/PlatformLayout.vue';

const uploadedFile = ref<File | null>(null);
const isRecognizing = ref(false);
const uploadProgress = ref(0);
const previewImageUrl = ref<string | null>(null);

const supportedImageExtensions = ['.png', '.jpg', '.jpeg', '.webp'];

const pestTrendData = [
  { date: '4.1', pest1: 0, pest2: 0 },
  { date: '4.2', pest1: 1, pest2: 1 },
  { date: '4.3', pest1: 1, pest2: 1 },
  { date: '4.4', pest1: 2, pest2: 2 },
  { date: '4.5', pest1: 2, pest2: 2 },
  { date: '4.6', pest1: 3, pest2: 3 },
  { date: '4.7', pest1: 4, pest2: 4 },
  { date: '4.8', pest1: 4, pest2: 4 },
  { date: '4.9', pest1: 5, pest2: 5 },
  { date: '4.10', pest1: 7, pest2: 7 },
  { date: '4.11', pest1: 8, pest2: 8 },
  { date: '4.12', pest1: 9, pest2: 9 },
  { date: '4.13', pest1: 11, pest2: 11 },
  { date: '4.14', pest1: 12, pest2: 12 },
  { date: '4.15', pest1: 14, pest2: 14 },
  { date: '4.16', pest1: 15, pest2: 15 },
  { date: '4.17', pest1: 17, pest2: 17 },
  { date: '4.18', pest1: 18, pest2: 18 },
  { date: '4.19', pest1: 19, pest2: 19 },
  { date: '4.20', pest1: 20, pest2: 20 },
  { date: '4.21', pest1: 18, pest2: 18 },
  { date: '4.22', pest1: 15, pest2: 15 },
  { date: '4.23', pest1: 12, pest2: 12 },
  { date: '4.24', pest1: 10, pest2: 10 },
  { date: '4.25', pest1: 8, pest2: 8 },
  { date: '4.26', pest1: 5, pest2: 5 },
];

const trendChartWidth = 760;
const trendChartHeight = 300;
const trendPadding = {
  top: 22,
  right: 28,
  bottom: 42,
  left: 44,
};
const trendUsableWidth = trendChartWidth - trendPadding.left - trendPadding.right;
const trendUsableHeight = trendChartHeight - trendPadding.top - trendPadding.bottom;
const trendMaxValue = Math.max(...pestTrendData.flatMap((item) => [item.pest1, item.pest2]));
const trendYAxisMax = Math.ceil(trendMaxValue / 5) * 5;
const trendYAxisTicks = Array.from({ length: 6 }, (_, index) => Math.round((trendYAxisMax / 5) * index)).reverse();

const getTrendPoint = (value: number, index: number) => {
  const x = trendPadding.left + (index / Math.max(pestTrendData.length - 1, 1)) * trendUsableWidth;
  const y = trendPadding.top + (1 - value / Math.max(trendYAxisMax, 1)) * trendUsableHeight;

  return { x, y };
};

const createTrendPath = (key: 'pest1' | 'pest2') =>
  pestTrendData
    .map((item, index) => {
      const point = getTrendPoint(item[key], index);
      return `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
    })
    .join(' ');

const pest1LinePath = computed(() => createTrendPath('pest1'));
const pest2LinePath = computed(() => createTrendPath('pest2'));
const pestTrendMarkers = computed(() =>
  pestTrendData.map((item, index) => ({
    ...item,
    pest1Point: getTrendPoint(item.pest1, index),
    pest2Point: getTrendPoint(item.pest2, index),
  })),
);
const pestTrendXAxisLabels = computed(() =>
  pestTrendData.filter((_, index) => index % 5 === 0 || index === pestTrendData.length - 1),
);
const pestTrendPeak = computed(() =>
  pestTrendData.reduce((peak, item) => (item.pest1 > peak.pest1 ? item : peak), pestTrendData[0]),
);

const isSupportedImageFile = (file: File) => {
  const fileName = file.name.toLowerCase();
  return supportedImageExtensions.some((extension) => fileName.endsWith(extension));
};

const updatePreviewImage = (file: File) => {
  if (previewImageUrl.value) {
    URL.revokeObjectURL(previewImageUrl.value);
  }
  previewImageUrl.value = URL.createObjectURL(file);
};

const handleUploadChange = (file: UploadFile) => {
  if (file.status !== 'ready' && file.status !== 'success') {
    return;
  }

  if (!file.raw || !isSupportedImageFile(file.raw)) {
    ElMessage.warning('请上传 png、jpg、jpeg 或 webp 格式的虫害图像');
    return;
  }

  uploadedFile.value = file.raw;
  updatePreviewImage(file.raw);
  ElMessage.success(`已载入虫害图像：${file.raw.name}`);
};

const startRecognition = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先上传虫害图像或选择图像文件夹');
    return;
  }

  isRecognizing.value = true;
  uploadProgress.value = 15;

  window.setTimeout(() => {
    uploadProgress.value = 55;
  }, 300);

  window.setTimeout(() => {
    uploadProgress.value = 100;
  }, 700);

  window.setTimeout(() => {
    isRecognizing.value = false;
    ElMessage.info('虫害识别模块正在建设中，当前已完成左侧图像输入区复用接入');
  }, 1100);
};

onBeforeUnmount(() => {
  if (previewImageUrl.value) {
    URL.revokeObjectURL(previewImageUrl.value);
  }
});
</script>

<template>
  <PlatformLayout mainClass="flex w-full flex-col gap-6 px-4 py-6 md:px-6 lg:px-8">
    <section class="grid gap-6 lg:min-h-[calc(100vh-160px)] lg:grid-cols-[340px_1fr] lg:items-stretch">
      <FileUploader
        class="h-full"
        :uploadedFile="uploadedFile"
        :isPredicting="isRecognizing"
        :uploadProgress="uploadProgress"
        fillUploadArea
        sectionTitle="虫害图像输入"
        accept=".png,.jpg,.jpeg,.webp"
        uploadTitle="点击或拖拽上传图像"
        uploadDescription="支持巡检照片、虫害样本图和现场识别图像"
        :showFolderPicker="false"
        actionText="开始识别分析"
        actionLoadingText="识别分析中..."
        progressUploadingText="图像上传中..."
        progressProcessingText="模型识别中..."
        processingHint="图像识别处理中，请稍后..."
        infoTitle="识别能力说明"
        :infoItems="[
          { icon: Camera, text: '支持茶园巡检照片、虫害样本图和现场图像统一接入' },
          { icon: Bug, text: '可扩展虫害识别、风险研判和诊断建议等业务能力' },
        ]"
        @upload-change="handleUploadChange"
        @start-prediction="startRecognition"
      />

      <section class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="grid gap-5 lg:grid-cols-2">
          <div class="flex min-h-[520px] flex-col rounded-2xl border border-emerald-100 bg-slate-50 p-4">
            <div class="flex items-center gap-3 border-b border-slate-200 pb-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
                <ImageIcon class="h-5 w-5" />
              </div>
              <div>
                <h2 class="text-lg font-bold text-slate-800">上传图像预览</h2>
                <p class="mt-1 text-sm text-slate-500">展示当前载入的巡检图像或虫害样本图</p>
              </div>
            </div>

            <div class="mt-4 flex min-h-0 flex-1 overflow-hidden rounded-2xl border border-dashed border-slate-200 bg-white">
              <img
                v-if="previewImageUrl"
                :src="previewImageUrl"
                :alt="uploadedFile?.name || '虫害识别上传图像'"
                class="h-full w-full object-contain"
              />
              <div
                v-else
                class="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center text-slate-400"
              >
                <ImageIcon class="h-12 w-12 opacity-20" />
                <div>
                  <p class="text-base font-semibold text-slate-500">暂无图像预览</p>
                  <p class="mt-2 text-sm leading-6">请在左侧上传虫害图像或选择图片文件夹</p>
                </div>
              </div>
            </div>
          </div>

          <div class="flex min-h-[520px] flex-col rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="flex items-center gap-3 border-b border-slate-200 pb-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
                <Bug class="h-5 w-5" />
              </div>
              <div>
                <h2 class="text-lg font-bold text-slate-800">模拟预测结果</h2>
                <p class="mt-1 text-sm text-slate-500">按日期展示害虫数量变化趋势</p>
              </div>
            </div>

            <div class="mt-4 flex flex-1 flex-col rounded-2xl border border-slate-200 bg-white p-4">
              <div class="grid gap-3 sm:grid-cols-3">
                <div class="rounded-2xl bg-slate-50 px-4 py-3">
                  <div class="text-xs font-semibold text-slate-400">统计周期</div>
                  <div class="mt-1 text-lg font-bold text-slate-800">4.1-4.26</div>
                </div>
                <div class="rounded-2xl bg-emerald-50 px-4 py-3">
                  <div class="text-xs font-semibold text-emerald-500">峰值数量</div>
                  <div class="mt-1 text-lg font-bold text-emerald-700">{{ pestTrendPeak.pest1 }} 只/板</div>
                </div>
                <div class="rounded-2xl bg-cyan-50 px-4 py-3">
                  <div class="text-xs font-semibold text-cyan-500">峰值日期</div>
                  <div class="mt-1 text-lg font-bold text-cyan-700">{{ pestTrendPeak.date }}</div>
                </div>
              </div>

              <div class="mt-4 flex items-center gap-5 text-sm font-semibold text-slate-600">
                <div class="flex items-center gap-2">
                  <span class="h-3 w-3 rounded-full bg-emerald-500"></span>
                  <span>害虫1（只/板）</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="h-3 w-3 rounded-full bg-sky-500"></span>
                  <span>害虫2（只/板）</span>
                </div>
              </div>

              <div class="mt-3 min-h-[320px] flex-1 overflow-hidden rounded-2xl border border-slate-100 bg-slate-50/70 px-3 py-4">
                <svg
                  class="h-full min-h-[300px] w-full"
                  :viewBox="`0 0 ${trendChartWidth} ${trendChartHeight}`"
                  preserveAspectRatio="none"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <defs>
                    <linearGradient id="pestTrendArea" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="#10b981" stop-opacity="0.22" />
                      <stop offset="100%" stop-color="#10b981" stop-opacity="0.02" />
                    </linearGradient>
                  </defs>

                  <g stroke="#e2e8f0" stroke-dasharray="4 6">
                    <line
                      v-for="tick in trendYAxisTicks"
                      :key="`y-${tick}`"
                      :x1="trendPadding.left"
                      :x2="trendChartWidth - trendPadding.right"
                      :y1="trendPadding.top + (1 - tick / trendYAxisMax) * trendUsableHeight"
                      :y2="trendPadding.top + (1 - tick / trendYAxisMax) * trendUsableHeight"
                    />
                  </g>

                  <g fill="#64748b" font-size="12" font-weight="700">
                    <text
                      v-for="tick in trendYAxisTicks"
                      :key="`label-y-${tick}`"
                      :x="trendPadding.left - 10"
                      :y="trendPadding.top + (1 - tick / trendYAxisMax) * trendUsableHeight + 4"
                      text-anchor="end"
                    >
                      {{ tick }}
                    </text>
                  </g>

                  <g fill="#64748b" font-size="12" font-weight="700">
                    <text
                      v-for="label in pestTrendXAxisLabels"
                      :key="label.date"
                      :x="getTrendPoint(label.pest1, pestTrendData.findIndex((item) => item.date === label.date)).x"
                      :y="trendChartHeight - 12"
                      text-anchor="middle"
                    >
                      {{ label.date }}
                    </text>
                  </g>

                  <path
                    :d="`${pest1LinePath} L ${trendChartWidth - trendPadding.right} ${trendChartHeight - trendPadding.bottom} L ${trendPadding.left} ${trendChartHeight - trendPadding.bottom} Z`"
                    fill="url(#pestTrendArea)"
                  />
                  <path :d="pest2LinePath" stroke="#0ea5e9" stroke-linecap="round" stroke-linejoin="round" stroke-width="3" stroke-dasharray="8 8" />
                  <path :d="pest1LinePath" stroke="#10b981" stroke-linecap="round" stroke-linejoin="round" stroke-width="4" />

                  <circle
                    v-for="marker in pestTrendMarkers"
                    :key="`pest1-${marker.date}`"
                    :cx="marker.pest1Point.x"
                    :cy="marker.pest1Point.y"
                    r="3.6"
                    fill="#ffffff"
                    stroke="#10b981"
                    stroke-width="2.5"
                  />

                  <text x="14" y="18" fill="#64748b" font-size="13" font-weight="700">数量（只/板）</text>
                  <text :x="trendChartWidth - 12" :y="trendChartHeight - 12" text-anchor="end" fill="#64748b" font-size="13" font-weight="700">日期</text>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>
    </section>
  </PlatformLayout>
</template>
