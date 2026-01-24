import apiClient from './api';

export interface SystemConfiguration {
  id: string;
  key: string;
  value: any;
  description?: string;
  category: 'scraping' | 'transformation' | 'publication' | 'system';
  isEncrypted: boolean;
  updatedAt: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    database?: {
      status: string;
      responseTime?: number;
    };
    storage?: {
      status: string;
    };
    youtubeApi?: {
      status: string;
      quotaRemaining?: number;
    };
  };
}

export interface SystemInfo {
  version: string;
  status: SystemHealth;
  resourceUsage?: {
    cpu?: number;
    memory?: number;
    disk?: number;
  };
}

export interface TransformationPreset {
  id: string;
  name: string;
  description?: string;
  effects: {
    brightness?: number;
    contrast?: number;
    saturation?: number;
    hue?: number;
    blur?: number;
    sharpen?: number;
    noise?: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface MusicTrack {
  id: string;
  name: string;
  artist: string;
  spotifyUrl?: string;
  fileUrl?: string;
  uploadedAt: string;
}

export interface SettingsUpdate {
  key: string;
  value: any;
  category?: string;
}

export const settingsService = {
  // Get system configuration
  getConfiguration: async (category?: string): Promise<SystemConfiguration[]> => {
    const params = category ? `?category=${category}` : '';
    const response = await apiClient.get(`/api/config${params}`);
    return response.data.config || [];
  },

  // Update system configuration
  updateConfiguration: async (update: SettingsUpdate): Promise<SystemConfiguration> => {
    const response = await apiClient.put('/api/config', update);
    return response.data;
  },

  // Get system health
  getSystemHealth: async (): Promise<SystemHealth> => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },

  // Get transformation presets
  getPresets: async (): Promise<TransformationPreset[]> => {
    const response = await apiClient.get('/api/transformation-presets');
    return response.data.presets || [];
  },

  // Create transformation preset
  createPreset: async (preset: Omit<TransformationPreset, 'id' | 'createdAt' | 'updatedAt'>): Promise<TransformationPreset> => {
    const response = await apiClient.post('/api/transformation-presets', preset);
    return response.data;
  },

  // Update transformation preset
  updatePreset: async (id: string, preset: Partial<TransformationPreset>): Promise<TransformationPreset> => {
    const response = await apiClient.put(`/api/transformation-presets/${id}`, preset);
    return response.data;
  },

  // Delete transformation preset
  deletePreset: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/transformation-presets/${id}`);
  },

  // Get music tracks
  getMusicTracks: async (): Promise<MusicTrack[]> => {
    const response = await apiClient.get('/api/music');
    return response.data.tracks || [];
  },

  // Upload music track
  uploadMusic: async (file: File, metadata: { name: string; artist: string; spotifyUrl?: string }): Promise<MusicTrack> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', metadata.name);
    formData.append('artist', metadata.artist);
    if (metadata.spotifyUrl) {
      formData.append('spotifyUrl', metadata.spotifyUrl);
    }

    const response = await apiClient.post('/api/music', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete music track
  deleteMusic: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/music/${id}`);
  },
};
