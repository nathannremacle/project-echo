import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Grid,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { statisticsService, StatisticsFilters } from '../services/statistics';
import { orchestrationService } from '../services/orchestration';
import StatisticsOverview from '../components/statistics/StatisticsOverview';
import ChannelBreakdown from '../components/statistics/ChannelBreakdown';
import GrowthTrendsChart from '../components/statistics/GrowthTrendsChart';
import StatisticsFiltersComponent from '../components/statistics/StatisticsFilters';
import AnomalyIndicator from '../components/statistics/AnomalyIndicator';

export default function Statistics() {
  const [filters, setFilters] = useState<StatisticsFilters>({});

  // Fetch overview statistics
  const {
    data: overview,
    isLoading: isLoadingOverview,
    error: overviewError,
  } = useQuery({
    queryKey: ['statistics-overview'],
    queryFn: () => statisticsService.getOverview(),
    refetchInterval: 60000, // Refetch every minute
  });

  // Fetch channels for filter and breakdown
  const { data: channelsData } = useQuery({
    queryKey: ['channels-list'],
    queryFn: async () => {
      const dashboard = await orchestrationService.getDashboard();
      return {
        channels: dashboard.channels.statuses.map((s) => ({
          id: s.channel_id,
          name: s.name,
        })),
      };
    },
  });

  // Fetch channel statistics for breakdown (simplified - fetch all or filtered)
  const channelsToFetch = filters.channelId
    ? channelsData?.channels.filter((c) => c.id === filters.channelId) || []
    : channelsData?.channels || [];

  // For MVP, we'll fetch statistics for all channels or the selected one
  // In production, this could be optimized with parallel queries
  const { data: allChannelStats } = useQuery({
    queryKey: ['all-channel-statistics', filters],
    queryFn: async () => {
      const stats = await Promise.all(
        channelsToFetch.map((channel) =>
          statisticsService
            .getChannelStatistics(channel.id, filters.startDate, filters.endDate)
            .then((data) => ({ channelId: channel.id, data }))
            .catch(() => ({ channelId: channel.id, data: null }))
        )
      );
      return stats;
    },
    enabled: channelsToFetch.length > 0,
  });

  const handleExport = (format: 'csv' | 'json') => {
    // TODO: Implement export functionality
    console.log(`Exporting statistics as ${format}`);
    // In full implementation, would generate CSV/JSON and download
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  if (isLoadingOverview) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (overviewError) {
    return (
      <Alert severity="error">
        Failed to load statistics: {overviewError instanceof Error ? overviewError.message : 'Unknown error'}
      </Alert>
    );
  }

  // Prepare channel breakdown data
  const channelBreakdownData =
    channelsData?.channels
      .map((channel) => {
        const statsResult = allChannelStats?.find((s) => s.channelId === channel.id);
        if (!statsResult?.data) return null;
        return {
          id: channel.id,
          name: channel.name,
          statistics: statsResult.data,
        };
      })
      .filter(Boolean) || [];

  // Get first channel's history for trends (or filtered channel)
  const selectedChannelId = filters.channelId || channelsData?.channels[0]?.id;
  const selectedChannelStats = channelBreakdownData.find(
    (c) => c.id === selectedChannelId
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Statistics & Analytics</Typography>
        <Tooltip title="Refresh">
          <IconButton
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ['statistics-overview'] });
              queryClient.invalidateQueries({ queryKey: ['all-channel-statistics'] });
            }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Overview Statistics */}
      {overview && (
        <Box mb={3}>
          <StatisticsOverview overview={overview} />
        </Box>
      )}

      {/* Filters */}
      <StatisticsFiltersComponent
        filters={filters}
        channels={channelsData?.channels || []}
        onChange={setFilters}
        onClear={handleClearFilters}
        onExport={handleExport}
      />

      {/* Anomaly Indicators */}
      {selectedChannelStats && selectedChannelStats.statistics.history.length > 0 && (
        <Box mb={2}>
          <AnomalyIndicator
            history={selectedChannelStats.statistics.history}
            metric="subscribers"
          />
        </Box>
      )}

      {/* Growth Trends */}
      {selectedChannelStats && selectedChannelStats.statistics.history.length > 0 && (
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={6}>
            <GrowthTrendsChart
              history={selectedChannelStats.statistics.history}
              metric="subscribers"
              title="Subscriber Growth"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <GrowthTrendsChart
              history={selectedChannelStats.statistics.history}
              metric="views"
              title="View Growth"
            />
          </Grid>
        </Grid>
      )}

      {/* Channel Breakdown */}
      <Box mb={3}>
        <ChannelBreakdown channels={channelBreakdownData} />
      </Box>
    </Box>
  );
}
