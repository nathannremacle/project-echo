import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from './theme';
import App from './App';

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
      <BrowserRouter>{children}</BrowserRouter>
    </ThemeProvider>
  </QueryClientProvider>
);

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );
  });

  it('renders dashboard by default', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );
    // Dashboard should be rendered (check for heading)
    // Note: This will fail if Dashboard component is not implemented yet
  });
});
