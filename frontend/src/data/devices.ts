export type DeviceState = 'online' | 'offline' | 'watching' | 'error';

export interface DeviceListItem {
  id: string;
  name: string;
  status: DeviceState;
  mountPath?: string | null;
  lastSeenAt?: string | null;
  unreadCount?: number;
}

export const mockDevices: DeviceListItem[] = [
  {
    id: 'hs-001',
    name: 'Specim IQ ',
    status: 'watching',
    mountPath: '/Volumes/SpecimIQ-A',
    lastSeenAt: new Date().toISOString(),
    unreadCount: 2,
  },
];
