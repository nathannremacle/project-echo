import apiClient from './api';

export interface Phase2Status {
  phase2_enabled: boolean;
  phase2_channels_count: number;
  total_channels: number;
  active_channels: number;
  channels: Array<{
    id: string;
    name: string;
    phase2_enabled: boolean;
    is_active: boolean;
  }>;
  available_music_tracks: number;
}

export interface ActivatePhase2Request {
  channel_ids?: string[];
  music_id: string;
  video_filter?: {
    transformation_status?: string;
    created_after?: string;
    created_before?: string;
  };
  apply_retroactive?: boolean;
  normalize?: boolean;
  loop_audio?: boolean;
}

export interface ChannelReadiness {
  channel_id: string;
  ready: boolean;
  checks: {
    subscribers?: {
      required: number;
      current: number | null;
      met: boolean;
    };
    views?: {
      required: number;
      current: number | null;
      met: boolean;
    };
  };
}

export const phase2Service = {
  // Get Phase 2 status
  getStatus: async (): Promise<Phase2Status> => {
    const response = await apiClient.get('/api/phase2/status');
    return response.data;
  },

  // Activate Phase 2
  activate: async (request: ActivatePhase2Request): Promise<{
    activated: Array<{
      channel_id: string;
      channel_name: string;
      videos_processed: number;
      videos_failed: number;
    }>;
    failed: Array<{
      channel_id: string;
      channel_name: string;
      error: string;
    }>;
    total: number;
  }> => {
    const response = await apiClient.post('/api/phase2/activate', request);
    return response.data;
  },

  // Deactivate Phase 2
  deactivate: async (channel_ids?: string[]): Promise<{
    deactivated: Array<{
      channel_id: string;
      channel_name: string;
    }>;
    failed: Array<{
      channel_id: string;
      channel_name: string;
      error: string;
    }>;
    total: number;
  }> => {
    const response = await apiClient.post('/api/phase2/deactivate', {
      channel_ids: channel_ids || null,
    });
    return response.data;
  },

  // Apply retroactive
  applyRetroactive: async (request: {
    channel_ids: string[];
    music_id: string;
    video_filter?: any;
    normalize?: boolean;
    loop_audio?: boolean;
  }): Promise<{
    processed: Array<{
      channel_id: string;
      channel_name: string;
      videos_processed: number;
      videos_failed: number;
    }>;
    failed: Array<{
      channel_id: string;
      error: string;
    }>;
    total: number;
  }> => {
    const response = await apiClient.post('/api/phase2/apply-retroactive', request);
    return response.data;
  },

  // Check channel readiness
  checkReadiness: async (
    channel_id: string,
    min_subscribers?: number,
    min_views?: number
  ): Promise<ChannelReadiness> => {
    const response = await apiClient.post('/api/phase2/check-readiness', {
      channel_id,
      min_subscribers,
      min_views,
    });
    return response.data;
  },
};
