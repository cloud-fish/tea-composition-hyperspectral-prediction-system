<script setup lang="ts">
import { onBeforeUnmount } from 'vue';
import { Bug, Camera, ImageIcon } from 'lucide-vue-next';
import FileUploader from '../components/FileUploader.vue';
import PlatformLayout from '../components/PlatformLayout.vue';
import { usePestDetection } from '../composables/usePestDetection';
import { usePestTrend } from '../composables/usePestTrend';

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
  yAxisMax,
  chartWidth,
  chartHeight,
  padding,
  yAxisTicks,
  pest1LinePath,
  pest2LinePath,
  markers,
  xAxisLabels,
  peak,
  getPoint,
} = usePestTrend();

onBeforeUnmount(() => {
  resetDetection();
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
                <h2 class="text-lg font-bold text-slate-800">检测结果</h2>
                <p class="mt-1 text-sm text-slate-500">
                  {{ detectionResult ? `共发现 ${detectionResult.detection_count} 个目标` : '等待检测分析' }}
                </p>
              </div>
            </div>

            <div class="mt-4 flex flex-1 flex-col rounded-2xl border border-slate-200 bg-white p-4">
              <div v-if="detectionResult" class="grid gap-3 sm:grid-cols-3">
                <div class="rounded-2xl bg-slate-50 px-4 py-3">
                  <div class="text-xs font-semibold text-slate-400">检测任务 ID</div>
                  <div class="mt-1 truncate text-sm font-bold text-slate-800">{{ detectionResult.task_id }}</div>
                </div>
                <div class="rounded-2xl bg-emerald-50 px-4 py-3">
                  <div class="text-xs font-semibold text-emerald-500">目标数量</div>
                  <div class="mt-1 text-lg font-bold text-emerald-700">{{ detectionResult.detection_count }} 个</div>
                </div>
                <div class="rounded-2xl bg-cyan-50 px-4 py-3">
                  <div class="text-xs font-semibold text-cyan-500">原始文件</div>
                  <div class="mt-1 truncate text-sm font-bold text-cyan-700">{{ detectionResult.filename }}</div>
                </div>
              </div>

              <div v-if="detectionResult && detectionResult.detections.length > 0" class="mt-4 max-h-[240px] overflow-y-auto rounded-2xl border border-slate-100 bg-slate-50/70 p-3">
                <div v-for="(det, index) in detectionResult.detections" :key="index" class="mb-2 flex items-center justify-between rounded-xl bg-white px-3 py-2 text-sm last:mb-0">
                  <div class="flex items-center gap-2">
                    <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
                    <span class="font-semibold text-slate-700">{{ det.class_name || `类别 ${det.class_id}` }}</span>
                  </div>
                  <span class="font-mono text-xs text-slate-500">{{ (det.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>

              <div v-else-if="!detectionResult" class="mt-4 flex flex-1 items-center justify-center text-center text-slate-400">
                <div>
                  <Bug class="mx-auto h-12 w-12 opacity-20" />
                  <p class="mt-3 text-base font-semibold text-slate-500">暂无检测结果</p>
                  <p class="mt-2 text-sm leading-6">请上传虫害图像并点击"开始识别分析"</p>
                </div>
              </div>

              <div v-if="resultImageUrl" class="mt-4 min-h-[200px] overflow-hidden rounded-2xl border border-slate-100 bg-slate-50/70">
                <img :src="resultImageUrl" alt="检测结果标注图" class="h-full w-full object-contain" />
              </div>

              <div class="mt-4 flex-1">
                <div class="flex items-center gap-5 text-sm font-semibold text-slate-600">
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
                    :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
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
                        v-for="tick in yAxisTicks"
                        :key="`y-${tick}`"
                        :x1="padding.left"
                        :x2="chartWidth - padding.right"
                        :y1="padding.top + (1 - tick / (yAxisMax || 1)) * (chartHeight - padding.top - padding.bottom)"
                        :y2="padding.top + (1 - tick / (yAxisMax || 1)) * (chartHeight - padding.top - padding.bottom)"
                      />
                    </g>

                    <g fill="#64748b" font-size="12" font-weight="700">
                      <text
                        v-for="tick in yAxisTicks"
                        :key="`label-y-${tick}`"
                        :x="padding.left - 10"
                        :y="padding.top + (1 - tick / (yAxisMax || 1)) * (chartHeight - padding.top - padding.bottom) + 4"
                        text-anchor="end"
                      >
                        {{ tick }}
                      </text>
                    </g>

                    <g fill="#64748b" font-size="12" font-weight="700">
                      <text
                        v-for="label in xAxisLabels"
                        :key="label.date"
                        :x="getPoint(label.pest1, trendData.findIndex((item) => item.date === label.date)).x"
                        :y="chartHeight - 12"
                        text-anchor="middle"
                      >
                        {{ label.date }}
                      </text>
                    </g>

                    <path
                      :d="`${pest1LinePath} L ${chartWidth - padding.right} ${chartHeight - padding.bottom} L ${padding.left} ${chartHeight - padding.bottom} Z`"
                      fill="url(#pestTrendArea)"
                    />
                    <path :d="pest2LinePath" stroke="#0ea5e9" stroke-linecap="round" stroke-linejoin="round" stroke-width="3" stroke-dasharray="8 8" />
                    <path :d="pest1LinePath" stroke="#10b981" stroke-linecap="round" stroke-linejoin="round" stroke-width="4" />

                    <circle
                      v-for="marker in markers"
                      :key="`pest1-${marker.date}`"
                      :cx="marker.pest1Point.x"
                      :cy="marker.pest1Point.y"
                      r="3.6"
                      fill="#ffffff"
                      stroke="#10b981"
                      stroke-width="2.5"
                    />

                    <text x="14" y="18" fill="#64748b" font-size="13" font-weight="700">数量（只/板）</text>
                    <text :x="chartWidth - 12" :y="chartHeight - 12" text-anchor="end" fill="#64748b" font-size="13" font-weight="700">日期</text>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </section>
  </PlatformLayout>
</template>
