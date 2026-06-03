import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import type { UploadFile } from 'element-plus';
import axios from 'axios';

export interface DetectionItem {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
}

export interface PestDetectionResult {
  task_id: string;
  filename: string;
  detection_count: number;
  detections: DetectionItem[];
  result_image_url: string;
}

export function usePestDetection() {
  const uploadedFile = ref<File | null>(null);
  const isDetecting = ref(false);
  const uploadProgress = ref(0);
  const previewImageUrl = ref<string | null>(null);
  const detectionResult = ref<PestDetectionResult | null>(null);
  const resultImageUrl = ref<string | null>(null);

  const supportedImageExtensions = ['.png', '.jpg', '.jpeg', '.webp'];

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
    detectionResult.value = null;
    resultImageUrl.value = null;
    updatePreviewImage(file.raw);
    ElMessage.success(`已载入虫害图像：${file.raw.name}`);
  };

  const startDetection = async () => {
    if (!uploadedFile.value) {
      ElMessage.warning('请先上传虫害图像');
      return;
    }

    isDetecting.value = true;
    uploadProgress.value = 15;
    detectionResult.value = null;
    resultImageUrl.value = null;

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile.value);

      const response = await axios.post('/api/pest-detection/detect', formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          }
        },
      });

      uploadProgress.value = 100;
      detectionResult.value = response.data;
      resultImageUrl.value = response.data.result_image_url;
      ElMessage.success(`检测完成，共发现 ${response.data.detection_count} 个目标`);
    } catch (error: any) {
      console.error('Pest detection error:', error);
      ElMessage.error(`检测失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      isDetecting.value = false;
    }
  };

  const resetDetection = () => {
    uploadedFile.value = null;
    detectionResult.value = null;
    resultImageUrl.value = null;
    uploadProgress.value = 0;
    if (previewImageUrl.value) {
      URL.revokeObjectURL(previewImageUrl.value);
      previewImageUrl.value = null;
    }
  };

  return {
    uploadedFile,
    isDetecting,
    uploadProgress,
    previewImageUrl,
    detectionResult,
    resultImageUrl,
    handleUploadChange,
    startDetection,
    resetDetection,
  };
}
