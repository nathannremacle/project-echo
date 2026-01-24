import apiClient from './api';

export interface VideoProcessingJob {
  id: string;
  videoId: string;
  channelId: string;
  jobType: 'scrape' | 'download' | 'transform' | 'publish';
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'retrying';
  priority: number;
  attempts: number;
  maxAttempts: number;
  errorMessage?: string;
  errorDetails?: string;
  queuedAt: string;
  startedAt?: string;
  completedAt?: string;
  duration?: number;
  githubWorkflowRunId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Video {
  id: string;
  channelId: string;
  sourceUrl: string;
  sourceTitle: string;
  sourceCreator?: string;
  sourcePlatform: string;
  scrapedAt: string;
  downloadStatus: 'pending' | 'downloading' | 'downloaded' | 'failed';
  downloadUrl?: string;
  downloadSize?: number;
  downloadDuration?: number;
  downloadResolution?: string;
  transformationStatus: 'pending' | 'processing' | 'transformed' | 'failed';
  transformedUrl?: string;
  transformedSize?: number;
  processingDuration?: number;
  publicationStatus: 'pending' | 'scheduled' | 'publishing' | 'published' | 'failed';
  youtubeVideoId?: string;
  youtubeUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface QueueFilters {
  status?: string;
  channelId?: string;
  jobType?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}

export interface QueueStatistics {
  total: number;
  byStatus: Record<string, number>;
  byJobType: Record<string, number>;
  averageProcessingTime: number;
  successRate: number;
  failedCount: number;
}

export const queueService = {
  // Get processing jobs
  getJobs: async (filters?: QueueFilters): Promise<{ jobs: VideoProcessingJob[]; total: number }> => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.channelId) params.append('channelId', filters.channelId);
    if (filters?.jobType) params.append('jobType', filters.jobType);
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());

    const response = await apiClient.get(`/api/jobs?${params.toString()}`);
    return response.data;
  },

  // Get job by ID
  getJob: async (jobId: string): Promise<VideoProcessingJob> => {
    const response = await apiClient.get(`/api/jobs/${jobId}`);
    return response.data;
  },

  // Cancel job
  cancelJob: async (jobId: string): Promise<void> => {
    await apiClient.post(`/api/jobs/${jobId}/cancel`);
  },

  // Get videos
  getVideos: async (filters?: QueueFilters): Promise<{ videos: Video[]; total: number }> => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.channelId) params.append('channelId', filters.channelId);
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());

    const response = await apiClient.get(`/api/videos?${params.toString()}`);
    return response.data;
  },

  // Get video by ID
  getVideo: async (videoId: string): Promise<Video> => {
    const response = await apiClient.get(`/api/videos/${videoId}`);
    return response.data;
  },

  // Retry failed video
  retryVideo: async (videoId: string): Promise<Video> => {
    const response = await apiClient.post(`/api/videos/${videoId}/retry`);
    return response.data;
  },

  // Delete video
  deleteVideo: async (videoId: string): Promise<void> => {
    await apiClient.delete(`/api/videos/${videoId}`);
  },

  // Get queue statistics
  getQueueStatistics: async (): Promise<QueueStatistics> => {
    // This would be a custom endpoint or calculated from jobs
    const { jobs } = await queueService.getJobs({ limit: 1000 });
    
    const stats: QueueStatistics = {
      total: jobs.length,
      byStatus: {},
      byJobType: {},
      averageProcessingTime: 0,
      successRate: 0,
      failedCount: 0,
    };

    let totalDuration = 0;
    let completedCount = 0;
    let failedCount = 0;

    jobs.forEach((job) => {
      // Count by status
      stats.byStatus[job.status] = (stats.byStatus[job.status] || 0) + 1;
      
      // Count by job type
      stats.byJobType[job.jobType] = (stats.byJobType[job.jobType] || 0) + 1;

      // Calculate average processing time
      if (job.duration) {
        totalDuration += job.duration;
        completedCount++;
      }

      // Count failures
      if (job.status === 'failed') {
        failedCount++;
      }
    });

    stats.averageProcessingTime = completedCount > 0 ? totalDuration / completedCount : 0;
    stats.successRate = jobs.length > 0 ? ((jobs.length - failedCount) / jobs.length) * 100 : 0;
    stats.failedCount = failedCount;

    return stats;
  },
};
