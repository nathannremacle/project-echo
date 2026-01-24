import apiClient from './api';

export interface Creator {
  name: string;
  video_count: number;
}

export interface VideoAttribution {
  id: string;
  source_title: string;
  source_url: string;
  channel_id: string;
  publication_status: string;
  created_at: string | null;
}

export interface CreatorVideos {
  creator: string;
  videos: VideoAttribution[];
  total: number;
  limit: number | null;
  offset: number;
}

export const creatorAttributionService = {
  // List all creators
  listCreators: async (): Promise<{ creators: Creator[]; total: number }> => {
    const response = await apiClient.get('/api/creators');
    return response.data;
  },

  // Search creators
  searchCreators: async (
    query: string,
    limit?: number
  ): Promise<{ creators: Creator[]; total: number; query: string }> => {
    const response = await apiClient.get('/api/creators/search', {
      params: { q: query, limit },
    });
    return response.data;
  },

  // Get videos by creator
  getVideosByCreator: async (
    creatorName: string,
    limit?: number,
    offset?: number
  ): Promise<CreatorVideos> => {
    const response = await apiClient.get(`/api/creators/${encodeURIComponent(creatorName)}/videos`, {
      params: { limit, offset },
    });
    return response.data;
  },

  // Attribute a video
  attributeVideo: async (
    videoId: string,
    creatorName: string,
    creatorChannel?: string
  ): Promise<{
    video_id: string;
    creator_name: string;
    message: string;
  }> => {
    const response = await apiClient.post(`/api/creators/videos/${videoId}/attribute`, {
      creator_name: creatorName,
      creator_channel: creatorChannel,
    });
    return response.data;
  },

  // Bulk attribute videos
  bulkAttributeVideos: async (
    videoIds: string[],
    creatorName: string,
    creatorChannel?: string
  ): Promise<{
    updated: Array<{ video_id: string; video_title: string }>;
    failed: Array<{ video_id: string; error: string }>;
    total: number;
  }> => {
    const response = await apiClient.post('/api/creators/videos/bulk-attribute', {
      video_ids: videoIds,
      creator_name: creatorName,
      creator_channel: creatorChannel,
    });
    return response.data;
  },

  // Export creators
  exportCreators: async (format: 'json' | 'csv' = 'json'): Promise<any> => {
    const response = await apiClient.get('/api/creators/export', {
      params: { format },
    });
    return response.data;
  },

  // Get attribution template
  getAttributionTemplate: async (
    videoId: string
  ): Promise<{ video_id: string; attribution: string }> => {
    const response = await apiClient.get(`/api/creators/videos/${videoId}/attribution-template`);
    return response.data;
  },
};
