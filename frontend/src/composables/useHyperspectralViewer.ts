import { computed, ref } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

export interface HyperspectralSampleMeta {
  sample_id: string;
  sample_name: string;
  device_name: string;
  acquisition_date: string | null;
  samples: number;
  lines: number;
  bands: number;
  interleave: string;
  data_type: number;
  wavelength_start: number;
  wavelength_end: number;
  wavelength_count: number;
  center_x: number;
  center_y: number;
  preview_url: string | null;
  reflectance_preview_url: string | null;
}

export interface SpectrumPoint {
  wavelength: number;
  intensity: number;
}

export interface HyperspectralSpectrumResponse {
  sample_id: string;
  sample_name: string;
  device_name: string;
  acquisition_date: string | null;
  unit: string;
  x: number;
  y: number;
  preview_url: string | null;
  points: SpectrumPoint[];
}

export function useHyperspectralViewer(initialSampleId: string | null = null) {
  const sampleId = ref<string | null>(initialSampleId);
  const sampleMeta = ref<HyperspectralSampleMeta | null>(null);
  const spectrum = ref<HyperspectralSpectrumResponse | null>(null);
  const selectedPoint = ref<{ x: number; y: number } | null>(null);
  const isMetaLoading = ref(false);
  const isSpectrumLoading = ref(false);
  const errorMessage = ref<string | null>(null);

  const spectrumPoints = computed(() => spectrum.value?.points ?? []);
  const previewUrl = computed(() => sampleMeta.value?.preview_url ?? spectrum.value?.preview_url ?? null);

  async function loadSampleMeta() {
    if (!sampleId.value) {
      sampleMeta.value = null;
      selectedPoint.value = null;
      return;
    }

    isMetaLoading.value = true;
    errorMessage.value = null;

    try {
      const response = await axios.get<HyperspectralSampleMeta>(`/api/hyperspectral/samples/${sampleId.value}`);
      sampleMeta.value = response.data;
      selectedPoint.value = {
        x: response.data.center_x,
        y: response.data.center_y,
      };
    } catch (error: any) {
      console.error('Load sample meta error:', error);
      errorMessage.value = error.response?.data?.detail ?? '加载高光谱样本信息失败';
      ElMessage.error(errorMessage.value);
    } finally {
      isMetaLoading.value = false;
    }
  }

  async function loadSpectrum(x?: number, y?: number) {
    if (!sampleId.value) {
      spectrum.value = null;
      selectedPoint.value = null;
      return;
    }

    isSpectrumLoading.value = true;
    errorMessage.value = null;

    try {
      const params: Record<string, number> = {};
      if (typeof x === 'number') params.x = x;
      if (typeof y === 'number') params.y = y;

      const response = await axios.get<HyperspectralSpectrumResponse>(
        `/api/hyperspectral/samples/${sampleId.value}/spectrum`,
        { params },
      );
      spectrum.value = response.data;
      selectedPoint.value = {
        x: response.data.x,
        y: response.data.y,
      };
    } catch (error: any) {
      console.error('Load spectrum error:', error);
      errorMessage.value = error.response?.data?.detail ?? '加载高光谱曲线失败';
      ElMessage.error(errorMessage.value);
    } finally {
      isSpectrumLoading.value = false;
    }
  }

  async function reload() {
    if (!sampleId.value) {
      sampleMeta.value = null;
      spectrum.value = null;
      selectedPoint.value = null;
      errorMessage.value = null;
      return;
    }

    await loadSampleMeta();
    await loadSpectrum(sampleMeta.value?.center_x, sampleMeta.value?.center_y);
  }

  async function handlePreviewSelect(payload: { x: number; y: number }) {
    await loadSpectrum(payload.x, payload.y);
  }

  return {
    sampleId,
    sampleMeta,
    spectrum,
    spectrumPoints,
    selectedPoint,
    previewUrl,
    isMetaLoading,
    isSpectrumLoading,
    errorMessage,
    loadSpectrum,
    reload,
    handlePreviewSelect,
  };
}
