import apiClient from './api';

export interface ChannelStatistics {
  id: string;
  channelId: string;
  subscriberCount: number;
  viewCount: number;
  videoCount: number;
  totalViews: number;
  totalVideos: number;
  timestamp: string;
}

export interface VideoStatistics {
  id: string;
  videoId: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  watchTime?: number;
  averageViewDuration?: number;
  recordedAt: string;
}

export interface StatisticsOverview {
  totalChannels: number;
  activeChannels: number;
  totalVideos: number;
  totalViews: number;
  totalSubscribers: number;
  recentActivity: {
    videosPublished: number;
    viewsGained: number;
    subscribersGained: number;
    period: string;
  };
}

export interface ChannelStatisticsWithTrends {
  current: {
    subscriberCount: number;
    viewCount: number;
    videoCount: number;
    totalViews: number;
    totalVideos: number;
  };
  history: ChannelStatistics[];
  trends: {
    subscriberGrowth: number;
    viewGrowth: number;
  };
}

export interface StatisticsFilters {
  channelId?: string;
  startDate?: string;
  endDate?: string;
  metric?: string;
}

export const statisticsService = {
  // Get overview statistics
  getOverview: async (): Promise<StatisticsOverview> => {
    const response = await apiClient.get('/api/statistics/overview');
    return response.data;
  },

  // Get channel statistics
  getChannelStatistics: async (
    channelId: string,
    startDate?: string,
    endDate?: string
  ): Promise<ChannelStatisticsWithTrends> => {
    const params = new URLSearchParams();
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);

    const response = await apiClient.get(
      `/api/channels/${channelId}/statistics?${params.toString()}`
    );
    return response.data;
  },

  // Get video statistics
  getVideoStatistics: async (videoId: string): Promise<{
    current: VideoStatistics;
    history: VideoStatistics[];
  }> => {
    const response = await apiClient.get(`/api/videos/${videoId}/statistics`);
    return response.data;
  },
};
