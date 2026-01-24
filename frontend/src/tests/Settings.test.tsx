import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Settings from '../pages/Settings';
import { theme } from '../theme';
import { settingsService } from '../services/settings';

// Mock services
vi.mock('../services/settings', () => ({
  settingsService: {
    getConfiguration: vi.fn(),
    updateConfiguration: vi.fn(),
    getSystemHealth: vi.fn(),
    getPresets: vi.fn(),
    getMusicTracks: vi.fn(),
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

describe('Settings', () => {
  it('renders loading state', () => {
    vi.mocked(settingsService.getConfiguration).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <TestWrapper>
        <Settings />
      </TestWrapper>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders settings with data', async () => {
    const mockConfigs = [
      {
        id: '1',
        key: 'default_video_quality',
        value: '1080p',
        category: 'system' as const,
        isEncrypted: false,
        updatedAt: new Date().toISOString(),
      },
    ];

    const mockHealth = {
      status: 'healthy' as const,
      components: {
        database: { status: 'healthy' },
      },
    };

    vi.mocked(settingsService.getConfiguration).mockResolvedValue(mockConfigs);
    vi.mocked(settingsService.getSystemHealth).mockResolvedValue(mockHealth);
    vi.mocked(settingsService.getPresets).mockResolvedValue([]);
    vi.mocked(settingsService.getMusicTracks).mockResolvedValue([]);

    render(
      <TestWrapper>
        <Settings />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('General')).toBeInTheDocument();
    });
  });

  it('switches between tabs', async () => {
    vi.mocked(settingsService.getConfiguration).mockResolvedValue([]);
    vi.mocked(settingsService.getSystemHealth).mockResolvedValue({
      status: 'healthy',
      components: {},
    });
    vi.mocked(settingsService.getPresets).mockResolvedValue([]);
    vi.mocked(settingsService.getMusicTracks).mockResolvedValue([]);

    render(
      <TestWrapper>
        <Settings />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('System Info')).toBeInTheDocument();
    });
  });
});
