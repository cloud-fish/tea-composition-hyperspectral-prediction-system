import { ref, computed, onMounted } from 'vue';

export interface PestTrendItem {
  date: string;
  pest1: number;
  pest2: number;
}

export function usePestTrend() {
  const trendData = ref<PestTrendItem[]>([]);
  const isLoading = ref(false);

  const chartWidth = 760;
  const chartHeight = 300;
  const padding = { top: 22, right: 28, bottom: 42, left: 44 };
  const usableWidth = chartWidth - padding.left - padding.right;
  const usableHeight = chartHeight - padding.top - padding.bottom;

  const maxValue = computed(() =>
    Math.max(...trendData.value.flatMap((item) => [item.pest1, item.pest2]))
  );

  const yAxisMax = computed(() => {
    const max = maxValue.value || 0;
    return Math.ceil(max / 5) * 5;
  });

  const yAxisTicks = computed(() =>
    Array.from({ length: 6 }, (_, i) => Math.round((yAxisMax.value / 5) * i)).reverse()
  );

  const getPoint = (value: number, index: number) => {
    const x = padding.left + (index / Math.max(trendData.value.length - 1, 1)) * usableWidth;
    const y = padding.top + (1 - value / Math.max(yAxisMax.value, 1)) * usableHeight;
    return { x, y };
  };

  const createPath = (key: 'pest1' | 'pest2') =>
    trendData.value
      .map((item, index) => {
        const point = getPoint(item[key], index);
        return `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
      })
      .join(' ');

  const pest1LinePath = computed(() => createPath('pest1'));
  const pest2LinePath = computed(() => createPath('pest2'));

  const markers = computed(() =>
    trendData.value.map((item, index) => ({
      ...item,
      pest1Point: getPoint(item.pest1, index),
      pest2Point: getPoint(item.pest2, index),
    }))
  );

  const xAxisLabels = computed(() =>
    trendData.value.filter((_, index) => index % 5 === 0 || index === trendData.value.length - 1)
  );

  const peak = computed(() =>
    trendData.value.reduce(
      (p, item) => (item.pest1 > p.pest1 ? item : p),
      trendData.value[0] || { date: '-', pest1: 0, pest2: 0 }
    )
  );

  const loadTrendData = async () => {
    isLoading.value = true;
    try {
      const response = await fetch('/data/pest_trend.csv');
      const csvText = await response.text();
      const lines = csvText.trim().split('\n').slice(1); // skip header
      trendData.value = lines.map((line) => {
        const [date, pest1, pest2] = line.split(',');
        return { date, pest1: Number(pest1), pest2: Number(pest2) };
      });
    } catch (error) {
      console.error('Failed to load pest trend data:', error);
    } finally {
      isLoading.value = false;
    }
  };

  onMounted(() => {
    loadTrendData();
  });

  return {
    trendData,
    isLoading,
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
  };
}
