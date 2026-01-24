import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Statistics from '../pages/Statistics';
import { theme } from '../theme';
import { statisticsService } from '../services/statistics';
import { orchestrationService } from '../services/orchestration';

// Mock services
vi.mock('../services/statistics', () => ({
  statisticsService: {
    getOverview: vi.fn(),
    getChannelStatistics: vi.fn(),
    getVideoStatistics: vi.fn(),
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

describe('Statistics', () => {
  it('renders loading state', () => {
    vi.mocked(statisticsService.getOverview).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <TestWrapper>
        <Statistics />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders statistics with data', async () => {
    const mockOverview = {
      totalChannels: 2,
      activeChannels: 2,
      totalVideos: 100,
      totalViews: 50000,
      totalSubscribers: 1000,
      recentActivity: {
        videosPublished: 10,
        viewsGained: 5000,
        subscribersGained: 50,
        period: 'Last 7 days',
      },
    };

    const mockDashboard = {
      system: { status: { running: true, paused: false }, queue_paused: false },
      channels: {
        total: 2,
        active: 2,
        statuses: [
          {
            channel_id: 'channel-1',
            name: 'Test Channel 1',
            is_active: true,
            health: 'healthy',
            status: 'active',
            errors: [],
            statistics: {
              distributions_7d: 10,
              published_7d: 5,
              success_rate: 80,
            },
          },
        ],
      },
      statistics: { overall: { total: 0, success_rate: 0, published_count: 0 } },
      schedules: { pending: 0, upcoming_7d: 0 },
    };

    const mockChannelStats = {
      current: {
        subscriberCount: 500,
        viewCount: 25000,
        videoCount: 50,
        totalViews: 25000,
        totalVideos: 50,
      },
      history: [],
      trends: {
        subscriberGrowth: 5.0,
        viewGrowth: 10.0,
      },
    };

    vi.mocked(statisticsService.getOverview).mockResolvedValue(mockOverview);
    vi.mocked(orchestrationService.getDashboard).mockResolvedValue(mockDashboard);
    vi.mocked(statisticsService.getChannelStatistics).mockResolvedValue(mockChannelStats);

    render(
      <TestWrapper>
        <Statistics />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Statistics & Analytics')).toBeInTheDocument();
      expect(screen.getByText('Total Subscribers')).toBeInTheDocument();
    });
  });

  it('renders error state', async () => {
    vi.mocked(statisticsService.getOverview).mockRejectedValue(
      new Error('Failed to fetch')
    );

    render(
      <TestWrapper>
        <Statistics />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/failed to load statistics/i)).toBeInTheDocument();
    });
  });
});
