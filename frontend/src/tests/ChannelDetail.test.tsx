import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ChannelDetail from '../pages/ChannelDetail';
import { theme } from '../theme';
import { channelService } from '../services/channels';

// Mock channel service
vi.mock('../services/channels', () => ({
  channelService: {
    getChannel: vi.fn(),
    getChannelStatistics: vi.fn(),
    updateChannel: vi.fn(),
    activateChannel: vi.fn(),
    deactivateChannel: vi.fn(),
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

describe('ChannelDetail', () => {
  it('renders loading state', () => {
    vi.mocked(channelService.getChannel).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <TestWrapper>
        <ChannelDetail />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders channel details', async () => {
    const mockChannel = {
      id: 'channel-1',
      name: 'Test Channel',
      youtubeChannelId: 'UC1234567890',
      youtubeChannelUrl: 'https://youtube.com/channel/UC1234567890',
      isActive: true,
      postingSchedule: {
        frequency: 'daily' as const,
        preferredTimes: ['10:00', '18:00'],
        timezone: 'UTC',
      },
      contentFilters: {
        minResolution: '1080p' as const,
        excludeWatermarked: true,
      },
      metadataTemplate: {
        titleTemplate: '{{video_title}} | Edit',
        descriptionTemplate: 'Check out this edit!',
        defaultTags: ['edit', 'shorts'],
      },
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
      phase2Enabled: false,
    };

    const mockStatistics = {
      current: {
        subscriberCount: 1000,
        viewCount: 5000,
        videoCount: 10,
        totalViews: 50000,
        totalVideos: 50,
      },
      history: [],
      trends: {
        subscriberGrowth: 5.0,
        viewGrowth: 10.0,
      },
    };

    vi.mocked(channelService.getChannel).mockResolvedValue(mockChannel);
    vi.mocked(channelService.getChannelStatistics).mockResolvedValue(mockStatistics);

    render(
      <TestWrapper>
        <ChannelDetail />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Channel')).toBeInTheDocument();
      expect(screen.getByText('UC1234567890')).toBeInTheDocument();
    });
  });

  it('renders error state', async () => {
    vi.mocked(channelService.getChannel).mockRejectedValue(
      new Error('Failed to fetch')
    );

    render(
      <TestWrapper>
        <ChannelDetail />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/failed to load channel/i)).toBeInTheDocument();
    });
  });
});
