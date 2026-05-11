<script setup lang="ts">
import { ArrowRight, Bug, Leaf, LineChart } from 'lucide-vue-next';
import PlatformLayout from '../components/PlatformLayout.vue';

const moduleCards = [
  {
    title: '成分分析',
    subtitle: '茶叶高光谱成分分析',
    description: '围绕茶叶样本提供高光谱数据导入、预览交互、像素点光谱分析与关键成分智能预测能力。',
    to: '/tea-hyperspectral-prediction',
    icon: LineChart,
    status: '已上线',
  },
  {
    title: '虫害识别',
    subtitle: '茶园虫害识别诊断',
    description: '面向茶园巡检场景提供虫害图像识别、风险研判与诊断建议入口，支撑茶园健康监测。',
    to: '/pest-detection',
    icon: Bug,
    status: '建设中',
  },
];
</script>

<template>
  <PlatformLayout>
      <section class="overflow-hidden rounded-3xl border border-emerald-100 bg-gradient-to-r from-emerald-700 via-emerald-600 to-teal-500 px-6 py-8 text-white shadow-sm md:px-8 md:py-10">
        <div class="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-3xl">
            <div class="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-sm font-semibold backdrop-blur">
              <Leaf class="h-4 w-4" />
              平台首页
            </div>
            <h1 class="mt-4 text-3xl font-bold tracking-tight md:text-4xl">茶园智能感知与诊断平台</h1>
            <p class="mt-4 max-w-2xl text-sm leading-7 text-emerald-50 md:text-base">
              平台面向茶园场景提供成分分析、虫害识别等核心业务入口，统一承载数据感知、智能分析与诊断决策能力，支撑茶叶品质评估和茶园健康管理。
            </p>
          </div>

          <div class="grid gap-3 rounded-2xl border border-white/20 bg-white/10 p-4 backdrop-blur sm:grid-cols-3 lg:min-w-[460px]">
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">业务模块</div>
              <div class="mt-2 text-lg font-semibold">2 个核心模块</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">当前能力</div>
              <div class="mt-2 text-lg font-semibold">成分分析已上线</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">平台定位</div>
              <div class="mt-2 text-lg font-semibold">智能感知与诊断</div>
            </div>
          </div>
        </div>
      </section>

      <section class="grid gap-5 lg:grid-cols-2">
        <RouterLink
          v-for="module in moduleCards"
          :key="module.title"
          :to="module.to"
          class="group rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
              <component :is="module.icon" class="h-7 w-7" />
            </div>
            <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
              {{ module.status }}
            </span>
          </div>

          <div class="mt-5">
            <h2 class="text-2xl font-bold text-slate-800">{{ module.title }}</h2>
            <p class="mt-2 text-sm font-semibold text-emerald-600">{{ module.subtitle }}</p>
            <p class="mt-3 text-sm leading-7 text-slate-500">{{ module.description }}</p>
          </div>

          <div class="mt-6 flex items-center gap-2 text-sm font-semibold text-emerald-600">
            进入模块
            <ArrowRight class="h-4 w-4 transition group-hover:translate-x-0.5" />
          </div>
        </RouterLink>
      </section>

  </PlatformLayout>
</template>
