import apiClient from './api';

export interface OrchestrationStatus {
  running: boolean;
  paused: boolean;
  started_at?: string;
  stopped_at?: string;
}

export interface ChannelStatus {
  channel_id: string;
  name: string;
  is_active: boolean;
  health: string;
  status: string;
  errors: string[];
  last_publication_at?: string;
  statistics: {
    distributions_7d: number;
    published_7d: number;
    success_rate: number;
  };
}

export interface DashboardData {
  system: {
    status: OrchestrationStatus;
    queue_paused: boolean;
  };
  channels: {
    total: number;
    active: number;
    statuses: ChannelStatus[];
  };
  statistics: {
    overall: {
      total: number;
      by_status: Record<string, number>;
      by_method: Record<string, number>;
      success_rate: number;
      published_count: number;
    };
    period: string;
  };
  schedules: {
    pending: number;
    upcoming_7d: number;
  };
}

export const orchestrationService = {
  // System control
  start: async () => {
    const response = await apiClient.post('/api/orchestration/start');
    return response.data;
  },

  stop: async () => {
    const response = await apiClient.post('/api/orchestration/stop');
    return response.data;
  },

  pause: async () => {
    const response = await apiClient.post('/api/orchestration/pause');
    return response.data;
  },

  resume: async () => {
    const response = await apiClient.post('/api/orchestration/resume');
    return response.data;
  },

  getStatus: async (): Promise<OrchestrationStatus> => {
    const response = await apiClient.get('/api/orchestration/status');
    return response.data;
  },

  // Monitoring
  monitorChannels: async (): Promise<ChannelStatus[]> => {
    const response = await apiClient.get('/api/orchestration/monitor-channels');
    return response.data;
  },

  getDashboard: async (): Promise<DashboardData> => {
    const response = await apiClient.get('/api/orchestration/dashboard');
    return response.data;
  },

  // Coordination
  coordinatePublication: async (data: {
    video_id: string;
    channel_ids: string[];
    timing: string;
    scheduled_at?: string;
  }) => {
    const response = await apiClient.post('/api/orchestration/coordinate-publication', data);
    return response.data;
  },

  triggerPipeline: async (data: {
    channel_id: string;
    video_id?: string;
  }) => {
    const response = await apiClient.post('/api/orchestration/trigger-pipeline', data);
    return response.data;
  },

  distributeVideos: async () => {
    const response = await apiClient.post('/api/orchestration/distribute-videos');
    return response.data;
  },
};
