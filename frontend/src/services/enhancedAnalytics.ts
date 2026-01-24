import apiClient from './api';

export interface MusicPromotionMetrics {
  total_music_videos: number;
  total_views: number;
  unique_music_tracks: number;
  average_views_per_video: number;
  videos: Array<{
    id: string;
    title: string;
    channel_id: string;
    published_at: string | null;
    music_track_id: string | null;
  }>;
}

export interface WaveEffectMetrics {
  total_waves: number;
  largest_wave: {
    videos_count: number;
    channels_count: number;
    start_time: string;
  } | null;
  average_wave_size: number;
  total_reach: number;
  average_reach_per_wave: number;
}

export interface Phase2Comparison {
  pre_phase2: {
    total_videos: number;
    total_views: number;
    average_views_per_video: number;
  };
  post_phase2: {
    total_videos: number;
    total_views: number;
    average_views_per_video: number;
  };
  improvement: {
    views_per_video: number;
  };
}

export interface ROIMetrics {
  effort: number;
  results: number;
  roi: number;
  efficiency: {
    views_per_video: number;
    average_views: number;
  };
}

export interface Insight {
  type: 'success' | 'info' | 'warning';
  title: string;
  message: string;
  metric: string;
  value: number;
}

export interface Recommendation {
  type: 'action' | 'suggestion';
  title: string;
  message: string;
  action: string;
  channels?: string[];
}

export const enhancedAnalyticsService = {
  // Get music promotion metrics
  getMusicPromotionMetrics: async (
    startDate?: string,
    endDate?: string,
    channelIds?: string[]
  ): Promise<MusicPromotionMetrics> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (channelIds && channelIds.length > 0) params.channel_ids = channelIds;
    const response = await apiClient.get('/api/analytics/music-promotion', { params });
    return response.data;
  },

  // Get wave effect metrics
  getWaveEffectMetrics: async (
    startDate?: string,
    endDate?: string,
    timeWindowHours?: number
  ): Promise<WaveEffectMetrics> => {
    const response = await apiClient.get('/api/analytics/wave-effect', {
      params: {
        start_date: startDate,
        end_date: endDate,
        time_window_hours: timeWindowHours,
      },
    });
    return response.data;
  },

  // Get Phase 2 comparison
  getPhase2Comparison: async (
    channelIds?: string[],
    phase2StartDate?: string
  ): Promise<Phase2Comparison> => {
    const response = await apiClient.get('/api/analytics/phase2-comparison', {
      params: {
        channel_ids: channelIds,
        phase2_start_date: phase2StartDate,
      },
    });
    return response.data;
  },

  // Get ROI metrics
  getROIMetrics: async (
    startDate?: string,
    endDate?: string,
    channelIds?: string[]
  ): Promise<ROIMetrics> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (channelIds && channelIds.length > 0) params.channel_ids = channelIds;
    const response = await apiClient.get('/api/analytics/roi', { params });
    return response.data;
  },

  // Get insights
  getInsights: async (
    startDate?: string,
    endDate?: string,
    channelIds?: string[]
  ): Promise<{ insights: Insight[] }> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (channelIds && channelIds.length > 0) params.channel_ids = channelIds;
    const response = await apiClient.get('/api/analytics/insights', { params });
    return response.data;
  },

  // Get recommendations
  getRecommendations: async (channelIds?: string[]): Promise<{ recommendations: Recommendation[] }> => {
    const response = await apiClient.get('/api/analytics/recommendations', {
      params: {
        channel_ids: channelIds,
      },
    });
    return response.data;
  },

  // Export analytics
  exportAnalytics: async (
    startDate?: string,
    endDate?: string,
    channelIds?: string[]
  ): Promise<any> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (channelIds && channelIds.length > 0) params.channel_ids = channelIds;
    const response = await apiClient.get('/api/analytics/export', { params });
    return response.data;
  },
};
