import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export interface PredictionResults {
  catechin: number;
  caffeine: number;
  theophylline: number;
  theanine: number;
}

export interface UploadedSampleImportResponse {
  sample_id: string;
}

type RelativeFile = File & {
  webkitRelativePath?: string;
};

export function usePrediction() {
  const isPredicting = ref(false);
  const uploadProgress = ref(0);
  const hasResults = ref(false);
  const uploadedFile = ref<any>(null);
  const uploadedSampleId = ref<string | null>(null);
  const isUploadedSpectrumLoading = ref(false);
  const uploadedSpectrumError = ref<string | null>(null);

  const results = reactive<PredictionResults>({
    catechin: 0,
    caffeine: 0,
    theophylline: 0,
    theanine: 0,
  });

  const pickPrimaryDatFile = (files: File[]) => {
    const datFiles = files.filter((file) => file.name.toLowerCase().endsWith('.dat'));
    if (datFiles.length === 0) {
      return null;
    }

    return datFiles.find((file) => file.name.toUpperCase().startsWith('REFLECTANCE_')) ?? datFiles[0];
  };

  const importUploadedFiles = async (files: File[]) => {
    isUploadedSpectrumLoading.value = true;
    uploadedSpectrumError.value = null;
    uploadedSampleId.value = null;

    try {
      const formData = new FormData();
      files.forEach((file) => {
        const relativeFile = file as RelativeFile;
        formData.append('files', file, relativeFile.webkitRelativePath || file.name);
      });

      const response = await axios.post<UploadedSampleImportResponse>('/api/hyperspectral/upload/import', formData);
      uploadedSampleId.value = response.data.sample_id;
      return true;
    } catch (error: any) {
      console.error('Import uploaded files error:', error);
      uploadedSampleId.value = null;
      uploadedSpectrumError.value = error.response?.data?.detail ?? '上传内容的高光谱导入失败';
      ElMessage.warning(uploadedSpectrumError.value);
      return false;
    } finally {
      isUploadedSpectrumLoading.value = false;
    }
  };

  const startPrediction = async () => {
    if (!uploadedFile.value) {
      ElMessage.warning('请先完成数据文件上传');
      return;
    }

    isPredicting.value = true;
    hasResults.value = false;
    uploadProgress.value = 0;
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile.value);

      const response = await axios.post('/api/predict', formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          }
        }
      });

      const result = response.data;
      
      results.catechin = parseFloat(result.data.catechins.value.toFixed(4));
      results.caffeine = parseFloat(result.data.caffeine.value.toFixed(4));
      results.theophylline = parseFloat(result.data.theophylline.value.toFixed(4));
      results.theanine = parseFloat(result.data.theanine.value.toFixed(4));
      
      hasResults.value = true;
      ElMessage.success('智能推演算法执行成功');
    } catch (error: any) {
      console.error('Prediction error:', error);
      ElMessage.error(`模型推理异常: ${error.message || '网络请求失败'}`);
    } finally {
      isPredicting.value = false;
    }
  };

  const handleUploadChange = async (file: any) => {
    if (file.status === 'ready' || file.status === 'success') {
      const isDat = file.name.endsWith('.dat');
      if (!isDat) {
        ElMessage.error('只能上传 .dat 格式的高光谱图像文件！');
        return;
      }
      uploadedFile.value = file.raw;
      const success = await importUploadedFiles([file.raw]);
      if (success) {
        ElMessage({
          message: '数据文件已装载',
          type: 'success',
          plain: true
        });
      }
    }
  };

  const handleFolderChange = async (files: File[]) => {
    const datFile = pickPrimaryDatFile(files);
    if (!datFile) {
      ElMessage.error('所选文件夹中未找到 .dat 高光谱文件');
      return;
    }

    uploadedFile.value = datFile;
    const success = await importUploadedFiles(files);
    if (success) {
      ElMessage({
        message: `文件夹已装载，已识别 ${datFile.name}`,
        type: 'success',
        plain: true
      });
    }
  };

  const resetPrediction = () => {
    uploadedFile.value = null;
    hasResults.value = false;
    uploadProgress.value = 0;
    uploadedSampleId.value = null;
    uploadedSpectrumError.value = null;
  };

  return {
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
  };
}
