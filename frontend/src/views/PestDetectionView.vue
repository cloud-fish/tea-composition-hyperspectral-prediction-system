<script setup lang="ts">
import { onBeforeUnmount, computed } from 'vue';
import { Bug, Camera, ImageIcon, BarChart3, TrendingUp, Info } from 'lucide-vue-next';
import FileUploader from '../components/FileUploader.vue';
import PlatformLayout from '../components/PlatformLayout.vue';
import { usePestDetection } from '../composables/usePestDetection';
import { usePestTrendChart, PEST_TYPES } from '../composables/usePestTrendChart';

const {
  uploadedFile,
  isDetecting,
  uploadProgress,
  previewImageUrl,
  detectionResult,
  resultImageUrl,
  handleUploadChange,
  startDetection,
  resetDetection,
} = usePestDetection();

const {
  trendData,
  selectedRange,
  yAxisMax,
  chartWidth,
  chartHeight,
  padding,
  yAxisTicks,
  linePaths,
  markers,
  xAxisLabels,
  getPoint,
} = usePestTrendChart();

onBeforeUnmount(() => {
  resetDetection();
});

// Compute per-pest counts from detection results
const pestCounts = computed(() => {
  if (!detectionResult.value) return [];
  const map = new Map<string, number>();
  for (const det of detectionResult.value.detections) {
    const name = det.class_name || `类别 ${det.class_id}`;
    map.set(name, (map.get(name) || 0) + 1);
  }
  return Array.from(map.entries()).map(([name, count]) => ({ name, count }));
});

const totalCount = computed(() =>
  pestCounts.value.reduce((sum, item) => sum + item.count, 0)
);

const pestPercentages = computed(() =>
  pestCounts.value.map((item) => ({
    ...item,
    percentage: totalCount.value > 0 ? ((item.count / totalCount.value) * 100).toFixed(2) : '0.00',
  }))
);

// Donut chart computation
const donutColors = ['#22c55e', '#3b82f6', '#f59e0b', '#a855f7', '#ef4444'];
const donutMidR = 66;
const donutStrokeWidth = 28;
const donutCircumference = 2 * Math.PI * donutMidR;

const donutSegments = computed(() => {
  const total = totalCount.value || 1;
  let cumulativeOffset = 0;
  return pestCounts.value.map((item, index) => {
    const ratio = item.count / total;
    const dashLength = ratio * donutCircumference;
    const gapLength = donutCircumference - dashLength;
    const offset = -cumulativeOffset;
    cumulativeOffset += dashLength;
    return {
      dashArray: `${dashLength.toFixed(2)} ${gapLength.toFixed(2)}`,
      offset: offset.toFixed(2),
      color: donutColors[index % donutColors.length],
    };
  });
});

// Legend items for detection result
const legendItems = computed(() => {
  const items: Array<{ name: string; count: number; color: string }> = [];
  for (let i = 0; i < pestCounts.value.length; i++) {
    items.push({
      name: pestCounts.value[i].name,
      count: pestCounts.value[i].count,
      color: donutColors[i % donutColors.length],
    });
  }
  return items;
});
</script>

<template>
  <PlatformLayout mainClass="flex w-full flex-col gap-6 px-4 py-6 md:px-6 lg:px-8">
    <section class="grid gap-6 lg:min-h-[calc(100vh-160px)] lg:grid-cols-[340px_1fr] lg:items-stretch">
      <FileUploader
        class="h-full"
        :uploadedFile="uploadedFile"
        :isPredicting="isDetecting"
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
        @start-prediction="startDetection"
      />

      <!-- Right panel: 2x2 grid -->
      <section class="flex flex-col gap-4">
        <div class="grid flex-1 grid-cols-1 gap-4 md:grid-cols-2">
          <!-- Top-left: Original image -->
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="mb-3 flex items-center gap-2">
              <ImageIcon class="h-4 w-4 text-emerald-600" />
              <h2 class="text-base font-bold text-slate-800">原图展示</h2>
            </div>
            <div class="flex h-[280px] overflow-hidden rounded-xl border border-dashed border-slate-200 bg-slate-50">
              <img
                v-if="previewImageUrl"
                :src="previewImageUrl"
                :alt="uploadedFile?.name || '虫害识别上传图像'"
                class="h-full w-full object-contain"
              />
              <div
                v-else
                class="flex flex-1 flex-col items-center justify-center gap-2 text-slate-400"
              >
                <ImageIcon class="h-10 w-10 opacity-20" />
                <p class="text-sm font-semibold text-slate-500">暂无图像预览</p>
                <p class="text-xs leading-5 text-slate-400">请在左侧上传虫害图像</p>
              </div>
            </div>
          </div>

          <!-- Top-right: Detection result -->
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="mb-3 flex items-center gap-2">
              <Bug class="h-4 w-4 text-emerald-600" />
              <h2 class="text-base font-bold text-slate-800">检测效果</h2>
              <span v-if="pestCounts.length > 0" class="ml-1 text-sm font-normal text-emerald-600">
                （识别结果：<strong>{{ pestCounts.length }}种虫害</strong>）
              </span>
            </div>
            <div class="flex h-[280px] overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
              <img
                v-if="resultImageUrl"
                :src="resultImageUrl"
                alt="检测结果标注图"
                class="h-full w-full object-contain"
              />
              <div
                v-else
                class="flex flex-1 flex-col items-center justify-center gap-2 text-slate-400"
              >
                <Bug class="h-10 w-10 opacity-20" />
                <p class="text-sm font-semibold text-slate-500">暂无检测结果</p>
                <p class="text-xs leading-5 text-slate-400">请上传图像并点击"开始识别分析"</p>
              </div>
            </div>
            <!-- Legend -->
            <div v-if="legendItems.length > 0" class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-600">
              <div v-for="item in legendItems" :key="item.name" class="flex items-center gap-1.5">
                <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: item.color }"></span>
                <span>{{ item.name }}</span>
                <span class="font-bold text-slate-800">{{ item.count }}</span>
              </div>
              <div class="ml-auto font-bold text-slate-800">总数：{{ totalCount }}</div>
            </div>
          </div>
        </div>

        <div class="grid flex-1 grid-cols-1 gap-4 md:grid-cols-2">
          <!-- Bottom-left: Pest statistics overview -->
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="mb-3 flex items-center gap-2">
              <BarChart3 class="h-4 w-4 text-emerald-600" />
              <h2 class="text-base font-bold text-slate-800">虫害统计概览</h2>
            </div>
            <div v-if="pestCounts.length > 0" class="flex items-center gap-4">
              <!-- Donut chart -->
              <div class="relative flex-shrink-0">
                <svg viewBox="0 0 200 200" class="h-[160px] w-[160px]" style="transform: rotate(-90deg)">
                  <circle
                    v-for="(seg, idx) in donutSegments"
                    :key="idx"
                    cx="100"
                    cy="100"
                    :r="donutMidR"
                    fill="none"
                    :stroke="seg.color"
                    :stroke-width="donutStrokeWidth"
                    :stroke-dasharray="seg.dashArray"
                    :stroke-dashoffset="seg.offset"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-xs text-slate-400">总数</span>
                  <span class="text-2xl font-bold text-slate-800">{{ totalCount }}</span>
                </div>
              </div>
              <!-- Table -->
              <div class="min-w-0 flex-1">
                <div class="mb-2 grid grid-cols-3 gap-2 text-xs font-semibold text-slate-400">
                  <span>虫害种类</span>
                  <span class="text-center">数量（个）</span>
                  <span class="text-right">占比</span>
                </div>
                <div
                  v-for="(item, idx) in pestPercentages"
                  :key="item.name"
                  class="grid grid-cols-3 gap-2 border-t border-slate-50 py-1.5 text-xs"
                >
                  <div class="flex items-center gap-1.5 truncate">
                    <span class="h-2.5 w-2.5 flex-shrink-0 rounded-full" :style="{ backgroundColor: donutColors[idx % donutColors.length] }"></span>
                    <span class="truncate font-medium text-slate-700">{{ item.name }}</span>
                  </div>
                  <span class="text-center font-bold text-slate-800">{{ item.count }}</span>
                  <span class="text-right text-slate-500">{{ item.percentage }}%</span>
                </div>
              </div>
            </div>
            <div v-else class="flex h-[160px] items-center justify-center text-slate-400">
              <div class="text-center">
                <BarChart3 class="mx-auto h-10 w-10 opacity-20" />
                <p class="mt-2 text-sm font-semibold text-slate-500">暂无统计数据</p>
                <p class="text-xs leading-5 text-slate-400">完成检测后将自动展示统计概览</p>
              </div>
            </div>
          </div>

          <!-- Bottom-right: Pest occurrence trend -->
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <TrendingUp class="h-4 w-4 text-emerald-600" />
                <h2 class="text-base font-bold text-slate-800">虫害发生趋势</h2>
              </div>
              <select
                v-model="selectedRange"
                class="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-600 outline-none focus:border-emerald-400"
              >
                <option>近7天</option>
                <option>近14天</option>
                <option>近30天</option>
              </select>
            </div>
            <!-- Legend -->
            <div class="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
              <div v-for="pest in PEST_TYPES" :key="pest.key" class="flex items-center gap-1">
                <span class="h-0.5 w-4" :style="{ backgroundColor: pest.color }"></span>
                <span>{{ pest.label }}</span>
              </div>
            </div>
            <!-- Chart -->
            <div class="min-h-[220px] overflow-hidden rounded-xl border border-slate-100 bg-slate-50/70 px-2 py-2">
              <svg
                class="h-full min-h-[200px] w-full"
                :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
                preserveAspectRatio="none"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <!-- Grid lines -->
                <g stroke="#e2e8f0" stroke-dasharray="4 6">
                  <line
                    v-for="tick in yAxisTicks"
                    :key="`y-${tick}`"
                    :x1="padding.left"
                    :x2="chartWidth - padding.right"
                    :y1="padding.top + (1 - tick / (yAxisMax || 1)) * (chartHeight - padding.top - padding.bottom)"
                    :y2="padding.top + (1 - tick / (yAxisMax || 1)) * (chartHeight - padding.top - padding.bottom)"
                  />
                </g>

                <!-- Y axis labels -->
                <g fill="#64748b" font-size="11" font-weight="600">
                  <text
                    v-for="tick in yAxisTicks"
                    :key="`label-y-${tick}`"
                    :x="padding.left - 8"
                    :y="padding.top + (1 - tick / (yAxisMax || 1)) * (chartHeight - padding.top - padding.bottom) + 4"
                    text-anchor="end"
                  >
                    {{ tick }}
                  </text>
                </g>

                <!-- X axis labels -->
                <g fill="#64748b" font-size="11" font-weight="600">
                  <text
                    v-for="(label, idx) in xAxisLabels"
                    :key="label"
                    :x="padding.left + (idx / Math.max(xAxisLabels.length - 1, 1)) * (chartWidth - padding.left - padding.right)"
                    :y="chartHeight - 10"
                    text-anchor="middle"
                  >
                    {{ label }}
                  </text>
                </g>

                <!-- Lines for each pest type -->
                <path
                  v-for="pest in PEST_TYPES"
                  :key="pest.key"
                  :d="linePaths[pest.key] || ''"
                  :stroke="pest.color"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                />

                <!-- Markers -->
                <template v-for="pest in PEST_TYPES" :key="`markers-${pest.key}`">
                  <circle
                    v-for="(pt, idx) in markers[pest.key] || []"
                    :key="`${pest.key}-${idx}`"
                    :cx="pt.x"
                    :cy="pt.y"
                    r="3"
                    fill="white"
                    :stroke="pest.color"
                    stroke-width="2"
                  />
                </template>

                <!-- Axis titles -->
                <text x="14" y="16" fill="#64748b" font-size="12" font-weight="600">数量（个）</text>
              </svg>
            </div>
          </div>
        </div>

        <!-- Footer tip -->
        <div class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-xs text-slate-500 shadow-sm">
          <Info class="h-3.5 w-3.5 flex-shrink-0 text-slate-400" />
          <span>提示：检测结果仅供参考，请结合人工判断进行综合决策</span>
        </div>
      </section>
    </section>
  </PlatformLayout>
</template>
