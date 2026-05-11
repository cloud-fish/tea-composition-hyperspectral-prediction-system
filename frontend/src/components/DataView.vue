<script setup lang="ts">
import { computed } from 'vue';
import { Activity, Camera, MapPinned, ScanLine, Waves } from 'lucide-vue-next';

interface SpectrumPoint {
  wavelength: number;
  intensity: number;
}

const props = withDefaults(defineProps<{
  title?: string;
  deviceName?: string | null;
  sampleName?: string | null;
  capturedAt?: string | null;
  unit?: string;
  points?: SpectrumPoint[];
  previewImageUrl?: string | null;
  imageWidth?: number | null;
  imageHeight?: number | null;
  selectedX?: number | null;
  selectedY?: number | null;
  loading?: boolean;
  error?: string | null;
  useDemoData?: boolean;
}>(), {
  title: '高光谱数据可视化',
  deviceName: null,
  sampleName: null,
  capturedAt: null,
  unit: '反射率',
  points: () => [],
  previewImageUrl: null,
  imageWidth: null,
  imageHeight: null,
  selectedX: null,
  selectedY: null,
  loading: false,
  error: null,
  useDemoData: true,
});

const emit = defineEmits<{
  (e: 'select-point', payload: { x: number; y: number }): void;
}>();

function gaussian(x: number, center: number, width: number, amplitude: number) {
  return amplitude * Math.exp(-((x - center) ** 2) / (2 * width ** 2));
}

function generateDemoPoints() {
  return Array.from({ length: 180 }, (_, index) => {
    const wavelength = 400 + index * 10;
    const baseline = 0.22 + (index / 180) * 0.18;
    const peakA = gaussian(wavelength, 550, 70, 0.22);
    const peakB = gaussian(wavelength, 880, 95, 0.31);
    const peakC = gaussian(wavelength, 1350, 130, 0.18);
    const trough = gaussian(wavelength, 1100, 85, 0.09);
    const ripple = Math.sin(index / 8) * 0.015 + Math.cos(index / 13) * 0.01;
    const intensity = Math.max(0.06, baseline + peakA + peakB + peakC - trough + ripple);

    return {
      wavelength,
      intensity: Number(intensity.toFixed(4)),
    };
  });
}

const resolvedPoints = computed(() => {
  if (props.points.length > 0) {
    return props.points;
  }
  return props.useDemoData ? generateDemoPoints() : [];
});

const hasSpectrumData = computed(() => resolvedPoints.value.length > 0);

const minIntensity = computed(() => {
  if (!hasSpectrumData.value) {
    return 0;
  }
  return Math.min(...resolvedPoints.value.map((point) => point.intensity));
});

const maxIntensity = computed(() => {
  if (!hasSpectrumData.value) {
    return 0;
  }
  return Math.max(...resolvedPoints.value.map((point) => point.intensity));
});

const avgIntensity = computed(() => {
  if (!hasSpectrumData.value) {
    return 0;
  }
  const total = resolvedPoints.value.reduce((sum, point) => sum + point.intensity, 0);
  return total / resolvedPoints.value.length;
});

const peakPoint = computed(() => {
  if (!hasSpectrumData.value) {
    return null;
  }
  return resolvedPoints.value.reduce((max, point) => (
    point.intensity > max.intensity ? point : max
  ), resolvedPoints.value[0]);
});

const wavelengthRange = computed(() => {
  if (!hasSpectrumData.value) {
    return '--';
  }
  const first = resolvedPoints.value[0];
  const last = resolvedPoints.value[resolvedPoints.value.length - 1];
  return `${Math.round(first.wavelength)}-${Math.round(last.wavelength)} nm`;
});

const chartWidth = 760;
const chartHeight = 280;
const chartPaddingX = 22;
const chartPaddingY = 18;
const usableWidth = chartWidth - chartPaddingX * 2;
const usableHeight = chartHeight - chartPaddingY * 2;

const chartPoints = computed(() => {
  if (!hasSpectrumData.value) {
    return [];
  }

  const minWave = resolvedPoints.value[0]?.wavelength ?? 0;
  const maxWave = resolvedPoints.value[resolvedPoints.value.length - 1]?.wavelength ?? 1;
  const intensitySpan = Math.max(maxIntensity.value - minIntensity.value, 0.001);

  return resolvedPoints.value.map((point) => {
    const x = chartPaddingX + ((point.wavelength - minWave) / (maxWave - minWave || 1)) * usableWidth;
    const y = chartPaddingY + (1 - ((point.intensity - minIntensity.value) / intensitySpan)) * usableHeight;

    return {
      ...point,
      x,
      y,
    };
  });
});

const linePath = computed(() =>
  chartPoints.value
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
    .join(' '),
);

const areaPath = computed(() => {
  if (chartPoints.value.length === 0) {
    return '';
  }

  const first = chartPoints.value[0];
  const last = chartPoints.value[chartPoints.value.length - 1];

  return `${linePath.value} L ${last.x.toFixed(2)} ${(chartHeight - chartPaddingY).toFixed(2)} L ${first.x.toFixed(2)} ${(chartHeight - chartPaddingY).toFixed(2)} Z`;
});

const previewMarkers = computed(() => {
  if (chartPoints.value.length === 0) {
    return [];
  }
  const step = Math.max(1, Math.floor(chartPoints.value.length / 6));
  return chartPoints.value.filter((_, index) => index % step === 0).slice(0, 6);
});

const capturedAtLabel = computed(() => {
  if (!props.capturedAt) {
    return '未加载';
  }

  const date = new Date(props.capturedAt);
  if (Number.isNaN(date.getTime())) {
    return props.capturedAt;
  }

  return date.toLocaleString('zh-CN', {
    hour12: false,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
});

const summaryItems = computed(() => [
  {
    label: '峰值波段',
    value: peakPoint.value ? `${Math.round(peakPoint.value.wavelength)} nm` : '--',
    hint: peakPoint.value ? `峰值 ${peakPoint.value.intensity.toFixed(3)} ${props.unit}` : '等待光谱数据',
    icon: ScanLine,
  },
  {
    label: '平均响应',
    value: hasSpectrumData.value ? avgIntensity.value.toFixed(3) : '--',
    hint: hasSpectrumData.value ? `范围 ${wavelengthRange.value}` : '等待光谱数据',
    icon: Activity,
  },
  {
    label: '采集设备',
    value: props.deviceName || '--',
    hint: capturedAtLabel.value,
    icon: Camera,
  },
]);

const selectedPointLabel = computed(() => {
  if (props.selectedX == null || props.selectedY == null) {
    return '未选择';
  }
  return `(${props.selectedX}, ${props.selectedY})`;
});

function handlePreviewClick(event: MouseEvent) {
  if (!props.previewImageUrl || !props.imageWidth || !props.imageHeight) {
    return;
  }

  const element = event.currentTarget as HTMLElement;
  const rect = element.getBoundingClientRect();
  const relativeX = (event.clientX - rect.left) / rect.width;
  const relativeY = (event.clientY - rect.top) / rect.height;
  const x = Math.min(props.imageWidth - 1, Math.max(0, Math.floor(relativeX * props.imageWidth)));
  const y = Math.min(props.imageHeight - 1, Math.max(0, Math.floor(relativeY * props.imageHeight)));

  emit('select-point', { x, y });
}
</script>

<template>
  <section class="rounded-2xl border border-emerald-100 bg-white p-5 shadow-sm md:p-6">
    <!-- #顶部信息 -->
    <div class="flex flex-col gap-4 border-b border-slate-100 pb-4 lg:flex-row lg:items-start lg:justify-between">
      <div class="min-w-0">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
            <Waves class="h-5 w-5" />
          </div>
          <div>
            <h2 class="text-lg font-bold text-slate-800">{{ title }}</h2>
            <p class="text-sm text-slate-400">
              {{ sampleName || '未加载样本' }} · {{ wavelengthRange }}
            </p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div
          v-for="item in summaryItems"
          :key="item.label"
          class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3"
        >
          <div class="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">
            <component :is="item.icon" class="h-3.5 w-3.5" />
            <span>{{ item.label }}</span>
          </div>
          <div class="mt-2 text-base font-bold text-slate-800">{{ item.value }}</div>
          <div class="mt-1 text-xs text-slate-400">{{ item.hint }}</div>
        </div>
      </div>
    </div>

    <!-- #预览图 -->
    <div class="mt-5 grid gap-5 xl:grid-cols-2">
      <!-- #预览图 -->
      <div class="flex h-full flex-col rounded-2xl border border-slate-100 bg-slate-50 px-4 py-4">
        <div class="mb-3 flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">
          <MapPinned class="h-3.5 w-3.5" />
          <span>采集预览</span>
        </div>

        <div class="mt-3 rounded-xl bg-white px-3 py-3 text-sm">
          <div class="flex items-center justify-between">
            <span class="text-slate-500">当前点位</span>
            <span class="font-semibold text-slate-800">{{ selectedPointLabel }}</span>
          </div>
          <div class="mt-2 text-xs leading-5 text-slate-400">
            点击预览图可切换像素点，并重新请求该点的 204 波段光谱。
          </div>
        </div>

        <button
          v-if="previewImageUrl"
          type="button"
          class="group relative block min-h-[360px] flex-1 overflow-hidden rounded-2xl border border-emerald-100 bg-white"
          @click="handlePreviewClick"
        >
          <img
            :src="previewImageUrl"
            :alt="sampleName || '高光谱预览图'"
            class="h-full w-full object-cover transition duration-300 group-hover:scale-[1.02]"
          />
          <div class="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/35 via-transparent to-transparent"></div>
          <div class="pointer-events-none absolute left-1/2 top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/90 shadow-sm"></div>
          <div class="absolute inset-x-3 bottom-3 rounded-xl bg-slate-950/70 px-3 py-2 text-left text-[11px] text-white backdrop-blur">
            点击图像选择像素点
          </div>
        </button>
        <div
          v-else
          class="flex min-h-[360px] flex-1 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white text-sm text-slate-400"
        >
          暂无预览图
        </div>


      </div>

      <!-- #光谱曲线 -->
      <div class="flex h-full flex-col rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
        <!-- #光谱曲线标题 -->
        <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div class="text-xs font-bold uppercase tracking-widest text-slate-400">光谱曲线</div>
            <div class="mt-1 text-sm text-slate-500">
              展示样本在不同波长下的 {{ unit }} 变化趋势
            </div>
          </div>
          <div class="flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-500 shadow-sm">
            <span class="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            {{ resolvedPoints.length }} 个采样点
          </div>
        </div>
        <!-- #光谱曲线内容 -->
        <div class="relative flex min-h-[360px] flex-1 flex-col overflow-hidden rounded-2xl border border-emerald-100 bg-white px-3 py-4">
          <!-- <div class="pointer-events-none absolute inset-x-4 top-4 h-12 rounded-xl bg-gradient-to-r from-emerald-50 via-cyan-50 to-violet-50 opacity-80"></div> -->

          <div v-if="!hasSpectrumData && !loading" class="flex flex-1 items-center justify-center text-sm font-medium text-slate-400">
            暂无可展示的高光谱曲线
          </div>
          
          <!-- #光谱曲线图表 -->
          <svg
            v-else
            class="min-h-0 flex-1 w-full"
            :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
            preserveAspectRatio="none"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="spectrumLine" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#14b8a6" />
                <stop offset="50%" stop-color="#10b981" />
                <stop offset="100%" stop-color="#6366f1" />
              </linearGradient>
              <linearGradient id="spectrumArea" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#10b981" stop-opacity="0.26" />
                <stop offset="100%" stop-color="#10b981" stop-opacity="0.03" />
              </linearGradient>
            </defs>

            <g stroke="#e2e8f0" stroke-dasharray="4 6">
              <line
                v-for="index in 5"
                :key="`grid-${index}`"
                :x1="chartPaddingX"
                :y1="chartPaddingY + ((usableHeight / 4) * (index - 1))"
                :x2="chartWidth - chartPaddingX"
                :y2="chartPaddingY + ((usableHeight / 4) * (index - 1))"
              />
            </g>

            <path :d="areaPath" fill="url(#spectrumArea)" />
            <path :d="linePath" stroke="url(#spectrumLine)" stroke-linecap="round" stroke-linejoin="round" stroke-width="4" />

            <circle
              v-for="marker in previewMarkers"
              :key="marker.wavelength"
              :cx="marker.x"
              :cy="marker.y"
              r="4.5"
              fill="#ffffff"
              stroke="#10b981"
              stroke-width="3"
            />

            <text
              x="16"
              y="20"
              fill="#94a3b8"
              font-size="12"
              font-weight="700"
            >
              {{ unit }}
            </text>
            <text
              :x="chartWidth - chartPaddingX"
              :y="chartHeight - 4"
              text-anchor="end"
              fill="#94a3b8"
              font-size="12"
              font-weight="700"
            >
              wavelength / nm
            </text>
          </svg>

          <div class="mt-3 flex items-center justify-between text-[11px] font-semibold text-slate-400">
            <span>{{ resolvedPoints[0]?.wavelength ?? '-' }} nm</span>
            <span>{{ peakPoint ? `${peakPoint.wavelength.toFixed(0)} nm 峰值增强` : '等待光谱数据' }}</span>
            <span>{{ resolvedPoints[resolvedPoints.length - 1]?.wavelength ?? '-' }} nm</span>
          </div>

          <div v-if="loading" class="pointer-events-none absolute inset-0 flex items-center justify-center bg-white/70 text-sm font-semibold text-emerald-600">
            正在加载高光谱数据...
          </div>
        </div>
      </div>

    </div>

    <!-- #数据统计 -->
    <div class="mt-5 grid gap-4 lg:grid-cols-3">
      <div class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-4">
        <div class="text-[11px] font-bold uppercase tracking-widest text-slate-400">数据统计</div>
        <div class="mt-4 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500">最小值</span>
            <span class="font-bold text-slate-800">{{ hasSpectrumData ? minIntensity.toFixed(3) : '--' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500">最大值</span>
            <span class="font-bold text-slate-800">{{ hasSpectrumData ? maxIntensity.toFixed(3) : '--' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500">平均值</span>
            <span class="font-bold text-slate-800">{{ hasSpectrumData ? avgIntensity.toFixed(3) : '--' }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-emerald-100 bg-emerald-50/70 px-4 py-4">
        <div class="text-[11px] font-bold uppercase tracking-widest text-emerald-600">采集信息</div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
          <div class="flex items-center justify-between gap-3">
            <span>设备</span>
            <span class="font-semibold text-slate-800">{{ deviceName }}</span>
          </div>
          <div class="flex items-center justify-between gap-3">
            <span>样本</span>
            <span class="truncate font-semibold text-slate-800">{{ sampleName || '--' }}</span>
          </div>
          <div class="flex items-center justify-between gap-3">
            <span>时间</span>
            <span class="font-semibold text-slate-800">{{ capturedAtLabel }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-2xl bg-slate-900 px-4 py-4 text-white">
        <div class="text-[11px] font-bold uppercase tracking-widest text-emerald-400">分析提示</div>
        <p v-if="error" class="mt-3 text-sm leading-6 text-rose-200">
          {{ error }}
        </p>
        <p v-else class="mt-3 text-sm leading-6 text-slate-300">
          当前组件已支持真实高光谱数据接入。点击右侧预览图，可以查看不同像素位置的反射率曲线。
        </p>
      </div>
    </div>
  </section>
</template>
