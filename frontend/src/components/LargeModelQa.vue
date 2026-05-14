<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import { Bot, LoaderCircle, MessageCircle, Send, Sparkles, UserRound, X } from 'lucide-vue-next';
import { ElMessage } from 'element-plus';

type ChatRole = 'system' | 'user' | 'assistant';

interface ChatMessage {
  role: ChatRole;
  content: string;
}

interface OpenAIChatChoice {
  message?: {
    role?: ChatRole;
    content?: string;
  };
}

interface OpenAIChatResponse {
  choices?: OpenAIChatChoice[];
}

interface OpenAIModelsResponse {
  data?: Array<{
    id?: string;
  }>;
}

const props = withDefaults(defineProps<{
  apiBase?: string;
  model?: string;
}>(), {
  apiBase: import.meta.env.VITE_LLM_API_BASE || '/llm-api',
  model: import.meta.env.VITE_LLM_MODEL || '',
});

const systemPrompt = '你是茶园智能感知与诊断平台的大模型助手，回答应围绕茶叶高光谱成分分析、虫害识别、茶园管理和系统使用问题。回答要准确、简洁，并在不确定时说明需要结合现场数据进一步确认。';

const inputValue = ref('');
const isLoading = ref(false);
const isOpen = ref(false);
const isDragging = ref(false);
const dragPosition = ref<{ x: number; y: number } | null>(null);
const selectedModel = ref(props.model);
const messages = ref<ChatMessage[]>([
  {
    role: 'assistant',
    content: '你好，我可以协助解读茶叶成分预测结果、说明高光谱数据含义，或给出茶园虫害诊断建议。',
  },
]);
const messagesContainer = ref<HTMLElement | null>(null);

const apiKey = import.meta.env.VITE_LLM_API_KEY || '';

const endpointBase = computed(() => props.apiBase.replace(/\/$/, ''));
const canSend = computed(() => inputValue.value.trim().length > 0 && !isLoading.value);
const panelStyle = computed(() => (
  dragPosition.value
    ? {
        left: `${dragPosition.value.x}px`,
        top: `${dragPosition.value.y}px`,
        right: 'auto',
        bottom: 'auto',
      }
    : {}
));

const requestHeaders = () => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    headers.Authorization = `Bearer ${apiKey}`;
  }

  return headers;
};

const scrollToBottom = async () => {
  await nextTick();
  messagesContainer.value?.scrollTo({
    top: messagesContainer.value.scrollHeight,
    behavior: 'smooth',
  });
};

const loadDefaultModel = async () => {
  if (selectedModel.value) {
    return;
  }

  try {
    const response = await fetch(`${endpointBase.value}/models`, {
      headers: requestHeaders(),
    });

    if (!response.ok) {
      return;
    }

    const data = await response.json() as OpenAIModelsResponse;
    selectedModel.value = data.data?.find((item) => item.id)?.id || '';
  } catch {
    selectedModel.value = '';
  }
};

const sendMessage = async () => {
  const question = inputValue.value.trim();

  if (!question || isLoading.value) {
    return;
  }

  if (!selectedModel.value) {
    await loadDefaultModel();
  }

  if (!selectedModel.value) {
    ElMessage.error('未获取到可用模型，请检查 vLLM 的 /v1/models 接口或配置 VITE_LLM_MODEL');
    return;
  }

  messages.value.push({ role: 'user', content: question });
  inputValue.value = '';
  isLoading.value = true;
  await scrollToBottom();

  try {
    const response = await fetch(`${endpointBase.value}/chat/completions`, {
      method: 'POST',
      headers: requestHeaders(),
      body: JSON.stringify({
        model: selectedModel.value,
        messages: [
          { role: 'system', content: systemPrompt },
          ...messages.value.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        ],
        temperature: 0.7,
        max_tokens: 10240,
        stream: false,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `请求失败：${response.status}`);
    }

    const data = await response.json() as OpenAIChatResponse;
    const answer = data.choices?.[0]?.message?.content?.trim();

    messages.value.push({
      role: 'assistant',
      content: answer || '模型未返回有效内容，请稍后重试。',
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : '请求大模型服务失败';
    ElMessage.error(message);
    messages.value.push({
      role: 'assistant',
      content: '当前无法连接大模型服务，请确认 100.113.187.68:8001 服务可访问，并且模型名称配置正确。',
    });
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  event.stopPropagation();

  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    void sendMessage();
  }
};

const openAssistant = () => {
  isOpen.value = true;
  void loadDefaultModel();
  void scrollToBottom();
};

const toggleAssistant = () => {
  if (isOpen.value) {
    isOpen.value = false;
    return;
  }

  openAssistant();
};

let dragOffsetX = 0;
let dragOffsetY = 0;

const clampWindowPosition = (x: number, y: number) => {
  const panelWidth = Math.min(420, window.innerWidth - 40);
  const panelHeight = Math.min(620, window.innerHeight - 120);
  const margin = 16;

  return {
    x: Math.min(Math.max(x, margin), Math.max(margin, window.innerWidth - panelWidth - margin)),
    y: Math.min(Math.max(y, margin), Math.max(margin, window.innerHeight - panelHeight - margin)),
  };
};

const stopDragging = () => {
  isDragging.value = false;
  window.removeEventListener('pointermove', handleDragMove);
  window.removeEventListener('pointerup', stopDragging);
};

function handleDragMove(event: PointerEvent) {
  if (!isDragging.value) {
    return;
  }

  dragPosition.value = clampWindowPosition(
    event.clientX - dragOffsetX,
    event.clientY - dragOffsetY,
  );
}

const startDragging = (event: PointerEvent) => {
  if (event.button !== 0) {
    return;
  }

  const panel = (event.currentTarget as HTMLElement).closest('[data-qa-panel]');

  if (!panel) {
    return;
  }

  const rect = panel.getBoundingClientRect();
  dragOffsetX = event.clientX - rect.left;
  dragOffsetY = event.clientY - rect.top;
  dragPosition.value = clampWindowPosition(rect.left, rect.top);
  isDragging.value = true;

  window.addEventListener('pointermove', handleDragMove);
  window.addEventListener('pointerup', stopDragging);
};

onBeforeUnmount(() => {
  stopDragging();
});
</script>

<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="translate-y-3 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-3 opacity-0"
    >
      <section
        v-if="isOpen"
        data-qa-panel
        :style="panelStyle"
        :class="[
          isDragging ? 'select-none shadow-2xl shadow-emerald-900/20' : 'shadow-2xl shadow-slate-900/20',
          'fixed bottom-24 right-5 z-50 flex h-[min(620px,calc(100vh-120px))] w-[calc(100vw-40px)] max-w-[420px] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white md:right-6',
        ]"
        @click.stop
        @keydown.stop
        @keyup.stop
        @pointerdown.stop
        @submit.prevent.stop
      >
        <div
          class="flex cursor-move touch-none items-start justify-between gap-3 border-b border-slate-100 px-4 py-4"
          @pointerdown="startDragging"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
              <Sparkles class="h-5 w-5" />
            </div>
            <div class="min-w-0">
              <h2 class="text-base font-bold text-slate-800">大模型问答助手</h2>
              <p class="mt-1 truncate text-xs text-slate-500">{{ selectedModel || '模型连接中' }}</p>
            </div>
          </div>

          <button
            type="button"
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            aria-label="关闭大模型问答助手"
            @pointerdown.stop
            @click.stop.prevent="isOpen = false"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <div
          ref="messagesContainer"
          class="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto bg-slate-50 px-4 py-4"
        >
          <div
            v-for="(message, index) in messages"
            :key="`${message.role}-${index}`"
            :class="[
              message.role === 'user' ? 'self-end bg-emerald-600 text-white' : 'self-start border border-slate-200 bg-white text-slate-700',
              'max-w-[88%] rounded-2xl px-4 py-3 shadow-sm',
            ]"
          >
            <div class="mb-2 flex items-center gap-2 text-xs font-bold">
              <UserRound v-if="message.role === 'user'" class="h-4 w-4" />
              <Bot v-else class="h-4 w-4 text-emerald-600" />
              <span>{{ message.role === 'user' ? '我' : '智能助手' }}</span>
            </div>
            <p class="whitespace-pre-wrap text-sm leading-7">{{ message.content }}</p>
          </div>

          <div v-if="isLoading" class="flex items-center gap-2 self-start rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-500 shadow-sm">
            <LoaderCircle class="h-4 w-4 animate-spin text-emerald-600" />
            正在生成回答...
          </div>
        </div>

        <div class="border-t border-slate-100 bg-white p-3">
          <textarea
            v-model="inputValue"
            class="max-h-28 min-h-20 w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100"
            placeholder="请输入问题，例如：儿茶素含量偏高代表什么？"
            @keydown="handleKeydown"
          />
          <div class="mt-3 flex items-center justify-between gap-3">
            <p class="text-xs text-slate-400">Enter 发送，Shift + Enter 换行</p>
            <button
              type="button"
              :disabled="!canSend"
              class="flex h-10 items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-4 text-sm font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              @click.stop.prevent="sendMessage"
            >
              <LoaderCircle v-if="isLoading" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              发送
            </button>
          </div>
        </div>
      </section>
    </transition>

    <button
      type="button"
      class="group fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-600 text-white shadow-xl shadow-emerald-900/25 transition hover:-translate-y-0.5 hover:bg-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-200 md:bottom-6 md:right-6"
      :aria-label="isOpen ? '收起大模型问答助手' : '打开大模型问答助手'"
      @click.stop.prevent="toggleAssistant"
      @keydown.stop
      @pointerdown.stop
    >
      <LoaderCircle v-if="isLoading && !isOpen" class="h-6 w-6 animate-spin" />
      <X v-else-if="isOpen" class="h-6 w-6 transition group-hover:scale-105" />
      <MessageCircle v-else class="h-6 w-6 transition group-hover:scale-105" />
    </button>
  </Teleport>
</template>
