<script setup lang="ts">
import { computed } from 'vue';
import {
  Cpu,
  HardDrive,
  Radio,
  Usb,
} from 'lucide-vue-next';
import { type DeviceListItem, type DeviceState, mockDevices } from '../data/devices';

const props = withDefaults(defineProps<{
  devices?: DeviceListItem[];
  selectedDeviceId?: string | null;
  title?: string;
}>(), {
  devices: () => [],
  selectedDeviceId: null,
  title: '设备列表',
});

const emit = defineEmits<{
  (e: 'update:selectedDeviceId', value: string): void;
  (e: 'select-device', device: DeviceListItem): void;
}>();

const resolvedDevices = computed(() =>
  props.devices.length > 0 ? props.devices : mockDevices,
);

const activeDeviceId = computed(() => {
  if (props.selectedDeviceId) {
    return props.selectedDeviceId;
  }

  return resolvedDevices.value[0]?.id ?? null;
});

const onlineCount = computed(() =>
  resolvedDevices.value.filter((device) => device.status !== 'offline').length,
);

function handleSelect(device: DeviceListItem) {
  emit('update:selectedDeviceId', device.id);
  emit('select-device', device);
}

function getStatusLabel(status: DeviceState) {
  switch (status) {
    case 'online':
      return '在线';
    case 'watching':
      return '监听中';
    case 'error':
      return '异常';
    default:
      return '离线';
  }
}

function getStatusClass(status: DeviceState) {
  switch (status) {
    case 'online':
      return 'bg-cyan-500';
    case 'watching':
      return 'bg-emerald-500 animate-pulse';
    case 'error':
      return 'bg-rose-500';
    default:
      return 'bg-slate-300';
  }
}

function formatLastSeen(value?: string | null) {
  if (!value) {
    return '暂无记录';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString('zh-CN', {
    hour12: false,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}
</script>

<template>
  <aside
    class="flex h-full min-h-[280px] w-full flex-shrink-0 flex-col overflow-hidden rounded-2xl border border-emerald-100 bg-white shadow-sm transition-all duration-300 lg:min-h-0"
  >
    <div class="flex items-center border-b border-slate-100 px-4 py-4">
      <div class="flex min-w-0 items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
          <Usb class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <div class="truncate text-sm font-bold text-slate-800">{{ title }}</div>
          <div class="text-xs text-slate-400">已连接 {{ onlineCount }} / {{ resolvedDevices.length }}</div>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-3 py-3">
      <div class="flex flex-col gap-2">
        <button
          v-for="device in resolvedDevices"
          :key="device.id"
          type="button"
          :class="[
            activeDeviceId === device.id
              ? 'border-emerald-200 bg-emerald-50 shadow-sm'
              : 'border-transparent bg-slate-50 hover:border-slate-200 hover:bg-white',
            'relative group flex w-full rounded-xl border px-3 py-3.5 text-left transition-all',
          ]"
          @click="handleSelect(device)"
        >
          <div
            :class="[
              activeDeviceId === device.id
                ? 'bg-white text-emerald-600'
                : 'bg-white text-slate-500',
              'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg border border-slate-100',
            ]"
          >
            <Cpu class="h-4 w-4" />
          </div>

          <div class="ml-3 min-w-0 flex-1">
            <div class="flex items-start justify-between gap-2">
              <div class="truncate text-sm font-semibold text-slate-800">{{ device.name }}</div>
              <span
                v-if="device.unreadCount"
                class="rounded-full bg-emerald-600 px-2 py-0.5 text-[10px] font-bold text-white"
              >
                {{ device.unreadCount }}
              </span>
            </div>

            <div class="mt-2 flex items-center gap-2 text-xs font-medium text-slate-500">
              <span class="h-2 w-2 rounded-full" :class="getStatusClass(device.status)"></span>
              <span>{{ getStatusLabel(device.status) }}</span>
            </div>

            <div class="mt-2 flex items-start gap-2 text-[11px] leading-5 text-slate-400">
              <HardDrive class="mt-0.5 h-3.5 w-3.5 flex-shrink-0" />
              <span class="line-clamp-2 break-all">{{ device.mountPath || '未挂载目录' }}</span>
            </div>

            <div class="mt-2 flex items-center gap-2 text-[11px] text-slate-400">
              <Radio class="h-3.5 w-3.5 flex-shrink-0" />
              <span>最近检测 {{ formatLastSeen(device.lastSeenAt) }}</span>
            </div>
          </div>
        </button>
      </div>
    </div>

    <div class="border-t border-slate-100 px-4 py-3">
      <div class="rounded-xl bg-slate-50 px-3 py-3">
        <div class="text-[10px] font-bold uppercase tracking-widest text-slate-400">设备状态概览</div>
        <div class="mt-2 flex items-center justify-between text-sm font-medium text-slate-700">
          <span>在线设备</span>
          <span>{{ onlineCount }}</span>
        </div>
        <div class="mt-1 flex items-center justify-between text-sm font-medium text-slate-700">
          <span>离线设备</span>
          <span>{{ resolvedDevices.length - onlineCount }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>
