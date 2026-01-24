import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Calendar from '../pages/Calendar';
import { theme } from '../theme';
import { scheduleService } from '../services/schedules';
import { orchestrationService } from '../services/orchestration';

// Mock services
vi.mock('../services/schedules', () => ({
  scheduleService: {
    getSchedules: vi.fn(),
    updateSchedule: vi.fn(),
    cancelSchedule: vi.fn(),
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

describe('Calendar', () => {
  it('renders loading state', () => {
    vi.mocked(scheduleService.getSchedules).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <TestWrapper>
        <Calendar />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders calendar with schedules', async () => {
    const mockSchedules = [
      {
        id: 'schedule-1',
        channelId: 'channel-1',
        videoId: 'video-1',
        scheduleType: 'simultaneous' as const,
        scheduledAt: new Date().toISOString(),
        status: 'pending' as const,
        isPaused: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    const mockDashboard = {
      system: { status: { running: true, paused: false }, queue_paused: false },
      channels: { total: 1, active: 1, statuses: [] },
      statistics: { overall: { total: 0, success_rate: 0, published_count: 0 } },
      schedules: { pending: 1, upcoming_7d: 1 },
    };

    vi.mocked(scheduleService.getSchedules).mockResolvedValue(mockSchedules);
    vi.mocked(orchestrationService.getDashboard).mockResolvedValue(mockDashboard);

    render(
      <TestWrapper>
        <Calendar />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Publication Calendar')).toBeInTheDocument();
    });
  });

  it('renders error state', async () => {
    vi.mocked(scheduleService.getSchedules).mockRejectedValue(
      new Error('Failed to fetch')
    );

    render(
      <TestWrapper>
        <Calendar />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/failed to load calendar/i)).toBeInTheDocument();
    });
  });
});
