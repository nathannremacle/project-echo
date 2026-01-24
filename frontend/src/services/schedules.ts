import apiClient from './api';

export interface PublicationSchedule {
  id: string;
  channelId: string;
  videoId?: string;
  scheduleType: 'simultaneous' | 'staggered' | 'independent';
  scheduledAt: string;
  delaySeconds?: number;
  status: 'pending' | 'scheduled' | 'executing' | 'completed' | 'failed' | 'cancelled';
  coordinationGroupId?: string;
  waveId?: string;
  isPaused: boolean;
  executedAt?: string;
  errorMessage?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ScheduleFilters {
  channelId?: string;
  videoId?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
  scheduleType?: string;
  includeHistory?: boolean;
}

export interface ScheduleUpdate {
  scheduledAt?: string;
  delaySeconds?: number;
  status?: string;
  isPaused?: boolean;
}

export interface BulkScheduleRequest {
  videoIds: string[];
  channelIds: string[];
  scheduledAt: string;
  scheduleType: 'simultaneous' | 'staggered' | 'independent';
  delaySeconds?: number;
}

export const scheduleService = {
  // Get schedules
  getSchedules: async (filters?: ScheduleFilters): Promise<PublicationSchedule[]> => {
    const params = new URLSearchParams();
    if (filters?.channelId) params.append('channelId', filters.channelId);
    if (filters?.videoId) params.append('videoId', filters.videoId);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.startDate) params.append('startDate', filters.startDate);
    if (filters?.endDate) params.append('endDate', filters.endDate);
    if (filters?.scheduleType) params.append('scheduleType', filters.scheduleType);
    if (filters?.includeHistory) params.append('includeHistory', 'true');

    const response = await apiClient.get(`/api/orchestration/schedules?${params.toString()}`);
    return response.data;
  },

  // Get schedule by ID
  getSchedule: async (scheduleId: string): Promise<PublicationSchedule> => {
    const response = await apiClient.get(`/api/orchestration/schedules/${scheduleId}`);
    return response.data;
  },

  // Update schedule
  updateSchedule: async (scheduleId: string, updates: ScheduleUpdate): Promise<PublicationSchedule> => {
    const response = await apiClient.put(`/api/orchestration/schedules/${scheduleId}`, updates);
    return response.data;
  },

  // Cancel schedule
  cancelSchedule: async (scheduleId: string): Promise<void> => {
    await apiClient.post(`/api/orchestration/schedules/${scheduleId}/cancel`);
  },

  // Bulk schedule
  bulkSchedule: async (request: BulkScheduleRequest): Promise<PublicationSchedule[]> => {
    const response = await apiClient.post('/api/orchestration/schedules/bulk', request);
    return response.data;
  },
};
