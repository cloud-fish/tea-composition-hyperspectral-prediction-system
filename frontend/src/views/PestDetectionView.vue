<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue';
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
                <h2 class="text-lg font-bold text-slate-800">识别结果预留区</h2>
                <p class="mt-1 text-sm text-slate-500">后续用于展示虫害识别结果、风险等级和诊断建议</p>
              </div>
            </div>

            <div class="mt-4 flex flex-1 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white px-6 text-center">
              <div class="max-w-sm text-slate-400">
                <Bug class="mx-auto h-12 w-12 opacity-20" />
                <p class="mt-4 text-base font-semibold text-slate-500">结果区域待接入</p>
                <p class="mt-2 text-sm leading-6">
                  这里可继续接入识别类别、置信度、虫情统计和诊断建议等业务内容。
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </section>
  </PlatformLayout>
</template>
