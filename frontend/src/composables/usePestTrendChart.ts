import { ref, computed, onMounted } from 'vue';

export interface PestTrendItem {
  date: string;
  [key: string]: string | number;
}

export const PEST_TYPES = [
  { key: 'greenLeafhopper', label: '茶小绿叶蝉', color: '#22c55e' },
  { key: 'aphid', label: '蚜虫', color: '#3b82f6' },
  { key: 'teaGeometrid', label: '茶尺蠖', color: '#f59e0b' },
  { key: 'scaleInsect', label: '介壳虫', color: '#a855f7' },
  { key: 'teaHairyWorm', label: '茶毛虫', color: '#ef4444' },
] as const;

export function usePestTrendChart() {
  const trendData = ref<PestTrendItem[]>([]);
  const isLoading = ref(false);
  const selectedRange = ref('近7天');

  const chartWidth = 760;
  const chartHeight = 300;
  const padding = { top: 30, right: 20, bottom: 40, left: 44 };
  const usableWidth = chartWidth - padding.left - padding.right;
  const usableHeight = chartHeight - padding.top - padding.bottom;

  const yAxisMax = computed(() => {
    const max = maxValue.value || 0;
    return Math.ceil(max / 10) * 10;
  });

  const yAxisTicks = computed(() => {
    const step = yAxisMax.value / 5;
    return Array.from({ length: 6 }, (_, i) => Math.round(step * i)).reverse();
  });

  const getPoint = (value: number, index: number) => {
    const x = padding.left + (index / Math.max(filteredData.value.length - 1, 1)) * usableWidth;
    const y = padding.top + (1 - value / Math.max(yAxisMax.value, 1)) * usableHeight;
    return { x, y };
  };

  const createPath = (key: string) =>
    filteredData.value
      .map((item, index) => {
        const val = Number((item as any)[key] || 0);
        const point = getPoint(val, index);
        return `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
      })
      .join(' ');

  const linePaths = computed(() => {
    const paths: Record<string, string> = {};
    for (const pest of PEST_TYPES) {
      paths[pest.key] = createPath(pest.key);
    }
    return paths;
  });

  const markers = computed(() => {
    const result: Record<string, Array<{ x: number; y: number }>> = {};
    for (const pest of PEST_TYPES) {
      result[pest.key] = filteredData.value.map((item, index) => {
        const val = Number((item as any)[pest.key] || 0);
        return getPoint(val, index);
      });
    }
    return result;
  });

  const xAxisLabels = computed(() =>
    filteredData.value.map((item) => item.date)
  );

  const loadTrendData = async () => {
    isLoading.value = true;
    try {
      const response = await fetch('/data/pest_trend.csv');
      const csvText = await response.text();
      const lines = csvText.trim().split('\n').slice(1);
      trendData.value = lines.map((line) => {
        const parts = line.split(',');
        return {
          date: parts[0],
          greenLeafhopper: Number(parts[1] || 0),
          aphid: Number(parts[2] || 0),
          teaGeometrid: Number(parts[3] || 0),
          scaleInsect: Number(parts[4] || 0),
          teaHairyWorm: Number(parts[5] || 0),
        };
      });
    } catch (error) {
      console.error('Failed to load pest trend data:', error);
    } finally {
      isLoading.value = false;
    }
  };

  const filteredData = computed(() => {
    const days = selectedRange.value === '近7天' ? 7 : selectedRange.value === '近14天' ? 14 : 30;
    return trendData.value.slice(-days);
  });

  const maxValue = computed(() => {
    let max = 0;
    for (const item of filteredData.value) {
      for (const pest of PEST_TYPES) {
        const val = Number((item as any)[pest.key] || 0);
        if (val > max) max = val;
      }
    }
    return max;
  });

  onMounted(() => {
    loadTrendData();
  });

  return {
    trendData,
    isLoading,
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
  };
}
