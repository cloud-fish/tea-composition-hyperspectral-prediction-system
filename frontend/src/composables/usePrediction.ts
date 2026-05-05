import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export interface PredictionResults {
  catechin: number;
  caffeine: number;
  theophylline: number;
  theanine: number;
}

export function usePrediction() {
  const isPredicting = ref(false);
  const uploadProgress = ref(0);
  const hasResults = ref(false);
  const uploadedFile = ref<any>(null);

  const results = reactive<PredictionResults>({
    catechin: 0,
    caffeine: 0,
    theophylline: 0,
    theanine: 0,
  });

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

  const handleUploadChange = (file: any) => {
    if (file.status === 'ready' || file.status === 'success') {
      const isDat = file.name.endsWith('.dat');
      if (!isDat) {
        ElMessage.error('只能上传 .dat 格式的高光谱图像文件！');
        return;
      }
      uploadedFile.value = file.raw;
      ElMessage({
        message: '数据文件已装载',
        type: 'success',
        plain: true
      });
    }
  };

  const resetPrediction = () => {
    uploadedFile.value = null;
    hasResults.value = false;
    uploadProgress.value = 0;
  };

  return {
    isPredicting,
    uploadProgress,
    hasResults,
    uploadedFile,
    results,
    startPrediction,
    handleUploadChange,
    resetPrediction
  };
}
