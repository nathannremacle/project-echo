import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from '../App';
import { theme } from '../theme';

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
    
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });
});
