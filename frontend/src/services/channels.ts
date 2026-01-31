import apiClient from './api';

export interface PostingSchedule {
  frequency: 'daily' | 'weekly' | 'custom';
  preferredTimes: string[];
  timezone: string;
  daysOfWeek?: number[];
}

export interface ContentFilters {
  minResolution: '720p' | '1080p' | '1440p' | '2160p';
  minViews?: number;
  excludeWatermarked: boolean;
  preferredSources?: string[];
}

export interface MetadataTemplate {
  titleTemplate: string;
  descriptionTemplate: string;
  defaultTags: string[];
}

export interface Channel {
  id: string;
  name: string;
  youtubeChannelId: string;
  youtubeChannelUrl: string;
  isActive: boolean;
  postingSchedule: PostingSchedule;
  effectPresetId?: string;
  contentFilters: ContentFilters;
  metadataTemplate: MetadataTemplate;
  githubRepoUrl?: string;
  createdAt: string;
  updatedAt: string;
  lastPublicationAt?: string;
  phase2Enabled: boolean;
}

export interface ChannelStatistics {
  current: {
    subscriberCount: number;
    viewCount: number;
    videoCount: number;
    totalViews: number;
    totalVideos: number;
  };
  history: Array<{
    id: string;
    channelId: string;
    subscriberCount: number;
    viewCount: number;
    videoCount: number;
    totalViews: number;
    totalVideos: number;
    timestamp: string;
  }>;
  trends: {
    subscriberGrowth: number;
    viewGrowth: number;
  };
}

export interface ChannelUpdate {
  name?: string;
  postingSchedule?: PostingSchedule;
  effectPresetId?: string;
  contentFilters?: ContentFilters;
  metadataTemplate?: MetadataTemplate;
}

export interface ChannelCreate {
  name: string;
  youtubeChannelId: string;
  youtubeChannelUrl?: string;
  isActive?: boolean;
}

export const channelService = {
  // List all channels
  getChannels: async (activeOnly?: boolean): Promise<{ channels: Channel[] }> => {
    const params = activeOnly ? '?active_only=true' : '';
    const response = await apiClient.get(`/api/channels${params}`);
    return response.data;
  },

  // Get channel by ID
  getChannel: async (channelId: string): Promise<Channel> => {
    const response = await apiClient.get(`/api/channels/${channelId}`);
    return response.data;
  },

  // Update channel
  updateChannel: async (channelId: string, updates: ChannelUpdate): Promise<Channel> => {
    const response = await apiClient.put(`/api/channels/${channelId}`, updates);
    return response.data;
  },

  // Get channel statistics
  getChannelStatistics: async (channelId: string, startDate?: string, endDate?: string): Promise<ChannelStatistics> => {
    const params = new URLSearchParams();
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);
    
    const response = await apiClient.get(`/api/channels/${channelId}/statistics?${params.toString()}`);
    return response.data;
  },

  // Activate channel
  activateChannel: async (channelId: string): Promise<Channel> => {
    const response = await apiClient.post(`/api/channels/${channelId}/activate`);
    return response.data;
  },

  // Deactivate channel
  deactivateChannel: async (channelId: string): Promise<Channel> => {
    const response = await apiClient.post(`/api/channels/${channelId}/deactivate`);
    return response.data;
  },

  // Enable Phase 2
  enablePhase2: async (channelId: string): Promise<Channel> => {
    const response = await apiClient.post(`/api/channels/${channelId}/enable-phase2`);
    return response.data;
  },

  // Create channel (test/demo mode with placeholder credentials)
  createChannel: async (data: ChannelCreate): Promise<Channel> => {
    const response = await apiClient.post('/api/channels', data);
    return response.data;
  },
};
