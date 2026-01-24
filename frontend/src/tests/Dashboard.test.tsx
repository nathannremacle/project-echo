import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from '../pages/Dashboard';
import { theme } from '../theme';
import { orchestrationService } from '../services/orchestration';

// Mock orchestration service
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

describe('Dashboard', () => {
  it('renders loading state', () => {
    vi.mocked(orchestrationService.getDashboard).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders dashboard with data', async () => {
    const mockData = {
      system: {
        status: {
          running: true,
          paused: false,
        },
        queue_paused: false,
      },
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
              published_7d: 8,
              success_rate: 80,
            },
          },
        ],
      },
      statistics: {
        overall: {
          total: 100,
          by_status: {},
          by_method: {},
          success_rate: 85,
          published_count: 85,
        },
        period: '30_days',
      },
      schedules: {
        pending: 5,
        upcoming_7d: 5,
      },
    };

    vi.mocked(orchestrationService.getDashboard).mockResolvedValue(mockData);

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Test Channel 1')).toBeInTheDocument();
    });
  });

  it('renders error state', async () => {
    vi.mocked(orchestrationService.getDashboard).mockRejectedValue(
      new Error('Failed to fetch')
    );

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/failed to load dashboard/i)).toBeInTheDocument();
    });
  });
});
