<script setup lang="ts">
import { Bug, Camera, ShieldCheck, Workflow } from 'lucide-vue-next';
import PlatformLayout from '../components/PlatformLayout.vue';

const capabilityCards = [
  {
    title: '虫害图像采集',
    description: '接入茶园现场照片、监控画面或移动端巡检图像，形成统一的虫害识别输入源。',
    icon: Camera,
  },
  {
    title: '智能识别分析',
    description: '支持后续接入目标检测、分类识别和虫情统计模型，输出识别结果与风险等级。',
    icon: Bug,
  },
  {
    title: '诊断结果联动',
    description: '识别结果可进一步关联地块、时间、设备和环境信息，形成完整诊断记录。',
    icon: Workflow,
  },
];
</script>

<template>
  <PlatformLayout>
      <section class="overflow-hidden rounded-3xl border border-emerald-100 bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-500 px-6 py-8 text-white shadow-sm md:px-8 md:py-10">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-3xl">
            <div class="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-sm font-semibold backdrop-blur">
              <ShieldCheck class="h-4 w-4" />
              虫害识别模块
            </div>
            <h1 class="mt-4 text-3xl font-bold tracking-tight md:text-4xl">茶园虫害检测识别能力正在接入</h1>
            <p class="mt-4 max-w-2xl text-sm leading-7 text-emerald-50 md:text-base">
              当前先完成平台级导航入口预留，后续可以在这里接入虫害图像上传、识别模型推理、虫情统计看板和诊断建议等完整能力。
            </p>
          </div>
          <div class="grid gap-3 rounded-2xl border border-white/20 bg-white/10 p-4 backdrop-blur sm:grid-cols-3 lg:min-w-[420px]">
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">Status</div>
              <div class="mt-2 text-lg font-semibold">准备中</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">Next Step</div>
              <div class="mt-2 text-lg font-semibold">模型接入</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">Scope</div>
              <div class="mt-2 text-lg font-semibold">图像识别</div>
            </div>
          </div>
        </div>
      </section>

      <section class="grid gap-5 lg:grid-cols-3">
        <article
          v-for="card in capabilityCards"
          :key="card.title"
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
            <component :is="card.icon" class="h-6 w-6" />
          </div>
          <h2 class="mt-4 text-xl font-semibold text-slate-800">{{ card.title }}</h2>
          <p class="mt-3 text-sm leading-7 text-slate-500">{{ card.description }}</p>
        </article>
      </section>

      <section class="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-10 text-center shadow-sm">
        <div class="mx-auto max-w-2xl">
          <div class="text-sm font-semibold tracking-[0.25em] text-slate-400">COMING SOON</div>
          <h2 class="mt-3 text-2xl font-bold text-slate-800 md:text-3xl">页面入口已预留，后续可直接扩展虫害识别业务流</h2>
          <p class="mt-4 text-sm leading-7 text-slate-500 md:text-base">
            如果你下一步要继续推进，我可以直接基于这个页面接入图片上传、识别结果展示、样本管理和诊断建议区块。
          </p>
        </div>
      </section>
  </PlatformLayout>
</template>
