import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Queue from '../pages/Queue';
import { theme } from '../theme';
import { queueService } from '../services/queue';
import { orchestrationService } from '../services/orchestration';

// Mock services
vi.mock('../services/queue', () => ({
  queueService: {
    getJobs: vi.fn(),
    getVideos: vi.fn(),
    getQueueStatistics: vi.fn(),
    retryVideo: vi.fn(),
    cancelJob: vi.fn(),
    deleteVideo: vi.fn(),
  },
}));

vi.mock('../services/orchestration', () => ({
  orchestrationService: {
    getDashboard: vi.fn(),
  },
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>{children}</BrowserRouter>
    </ThemeProvider>
  </QueryClientProvider>
);

describe('Queue', () => {
  it('renders loading state', () => {
    vi.mocked(queueService.getJobs).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );
    vi.mocked(queueService.getVideos).mockImplementation(
      () => new Promise(() => {})
    );

    render(
      <TestWrapper>
        <Queue />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders queue with data', async () => {
    const mockJobs = {
      jobs: [
        {
          id: 'job-1',
          videoId: 'video-1',
          channelId: 'channel-1',
          jobType: 'transform' as const,
          status: 'processing' as const,
          priority: 0,
          attempts: 1,
          maxAttempts: 3,
          queuedAt: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
      total: 1,
    };

    const mockVideos = {
      videos: [
        {
          id: 'video-1',
          channelId: 'channel-1',
          sourceUrl: 'https://example.com/video',
          sourceTitle: 'Test Video',
          sourcePlatform: 'youtube',
          scrapedAt: new Date().toISOString(),
          downloadStatus: 'downloaded' as const,
          transformationStatus: 'processing' as const,
          publicationStatus: 'pending' as const,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
      total: 1,
    };

    const mockStats = {
      total: 1,
      byStatus: { processing: 1 },
      byJobType: { transform: 1 },
      averageProcessingTime: 60,
      successRate: 100,
      failedCount: 0,
    };

    const mockDashboard = {
      system: { status: { running: true, paused: false }, queue_paused: false },
      channels: { total: 1, active: 1, statuses: [] },
      statistics: { overall: { total: 0, success_rate: 0, published_count: 0 } },
      schedules: { pending: 0, upcoming_7d: 0 },
    };

    vi.mocked(queueService.getJobs).mockResolvedValue(mockJobs);
    vi.mocked(queueService.getVideos).mockResolvedValue(mockVideos);
    vi.mocked(queueService.getQueueStatistics).mockResolvedValue(mockStats);
    vi.mocked(orchestrationService.getDashboard).mockResolvedValue(mockDashboard);

    render(
      <TestWrapper>
        <Queue />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Video Processing Queue')).toBeInTheDocument();
      expect(screen.getByText('Test Video')).toBeInTheDocument();
    });
  });

  it('renders error state', async () => {
    vi.mocked(queueService.getJobs).mockRejectedValue(
      new Error('Failed to fetch')
    );

    render(
      <TestWrapper>
        <Queue />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/failed to load queue/i)).toBeInTheDocument();
    });
  });
});
