<script setup lang="ts">
import { ArrowRight, Bug, Leaf, LineChart, Radar, ShieldCheck } from 'lucide-vue-next';
import PlatformLayout from '../components/PlatformLayout.vue';

const moduleCards = [
  {
    title: '成分分析',
    subtitle: '茶叶高光谱预测页面',
    description: '接入高光谱样本上传、采集预览、像素点光谱查看与茶叶关键成分智能预测能力。',
    to: '/tea-hyperspectral-prediction',
    icon: LineChart,
    status: '已接入',
  },
  {
    title: '虫害识别',
    subtitle: '茶园病虫害诊断页面',
    description: '预留虫害图像采集、识别分析、风险评估和诊断建议等后续业务能力入口。',
    to: '/pest-detection',
    icon: Bug,
    status: '准备中',
  },
];

const sharedCapabilities = [
  '统一顶部导航与模块入口',
  '平台级业务扩展与模块接入',
  '茶园数据感知与诊断能力整合',
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
              这里承载平台公共入口和能力概览，后续新增模块时可以继续在首页聚合展示，再分别进入对应业务页面。
            </p>
          </div>

          <div class="grid gap-3 rounded-2xl border border-white/20 bg-white/10 p-4 backdrop-blur sm:grid-cols-3 lg:min-w-[460px]">
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">Modules</div>
              <div class="mt-2 text-lg font-semibold">2 个入口</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">Current Focus</div>
              <div class="mt-2 text-lg font-semibold">成分分析</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-emerald-100">Platform</div>
              <div class="mt-2 text-lg font-semibold">持续扩展</div>
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

      <section class="grid gap-5 lg:grid-cols-[1.3fr_1fr]">
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-sky-50 text-sky-600">
              <Radar class="h-5 w-5" />
            </div>
            <div>
              <h2 class="text-xl font-bold text-slate-800">平台公共能力</h2>
              <p class="mt-1 text-sm text-slate-500">首页保留平台层面的统一说明与入口分发</p>
            </div>
          </div>

          <div class="mt-5 grid gap-3">
            <div
              v-for="capability in sharedCapabilities"
              :key="capability"
              class="rounded-2xl bg-slate-50 px-4 py-4 text-sm font-medium text-slate-600"
            >
              {{ capability }}
            </div>
          </div>
        </article>

        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
              <ShieldCheck class="h-5 w-5" />
            </div>
            <div>
              <h2 class="text-xl font-bold text-slate-800">当前拆分结果</h2>
              <p class="mt-1 text-sm text-slate-500">页面职责已经按平台层和业务层分开</p>
            </div>
          </div>

          <div class="mt-5 space-y-3 text-sm leading-7 text-slate-500">
            <p>`HomeView` 现在只负责平台公共内容。</p>
            <p>原来的业务页面已经迁移为“茶叶高光谱预测页面”。</p>
            <p>后续新增业务模块时，可以继续复用这个首页结构扩展。</p>
          </div>
        </article>
      </section>
  </PlatformLayout>
</template>
