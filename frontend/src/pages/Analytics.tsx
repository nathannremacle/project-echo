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
  Button,
  TextField,
  Card,
  CardContent,
} from '@mui/material';
import { Refresh, Download } from '@mui/icons-material';
import { enhancedAnalyticsService } from '../services/enhancedAnalytics';
import MusicPromotionMetricsComponent from '../components/analytics/MusicPromotionMetrics';
import WaveEffectMetricsComponent from '../components/analytics/WaveEffectMetrics';
import Phase2ComparisonComponent from '../components/analytics/Phase2Comparison';
import InsightsPanel from '../components/analytics/InsightsPanel';
import RecommendationsPanel from '../components/analytics/RecommendationsPanel';

export default function Analytics() {
  const queryClient = useQueryClient();
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Fetch music promotion metrics
  const { data: musicMetrics, isLoading: isLoadingMusic } = useQuery({
    queryKey: ['analytics-music-promotion', startDate, endDate],
    queryFn: () => enhancedAnalyticsService.getMusicPromotionMetrics(startDate, endDate),
    refetchInterval: 60000,
  });

  // Fetch wave effect metrics
  const { data: waveMetrics, isLoading: isLoadingWave } = useQuery({
    queryKey: ['analytics-wave-effect', startDate, endDate],
    queryFn: () => enhancedAnalyticsService.getWaveEffectMetrics(startDate, endDate),
    refetchInterval: 60000,
  });

  // Fetch Phase 2 comparison
  const { data: phase2Comparison, isLoading: isLoadingPhase2 } = useQuery({
    queryKey: ['analytics-phase2-comparison'],
    queryFn: () => enhancedAnalyticsService.getPhase2Comparison(),
    refetchInterval: 60000,
  });

  // Fetch ROI metrics
  const { data: roiMetrics, isLoading: isLoadingROI } = useQuery({
    queryKey: ['analytics-roi', startDate, endDate],
    queryFn: () => enhancedAnalyticsService.getROIMetrics(startDate, endDate),
    refetchInterval: 60000,
  });

  // Fetch insights
  const { data: insightsData, isLoading: isLoadingInsights } = useQuery({
    queryKey: ['analytics-insights', startDate, endDate],
    queryFn: () => enhancedAnalyticsService.getInsights(startDate, endDate),
    refetchInterval: 60000,
  });

  // Fetch recommendations
  const { data: recommendationsData, isLoading: isLoadingRecommendations } = useQuery({
    queryKey: ['analytics-recommendations'],
    queryFn: () => enhancedAnalyticsService.getRecommendations(),
    refetchInterval: 60000,
  });

  const isLoading =
    isLoadingMusic ||
    isLoadingWave ||
    isLoadingPhase2 ||
    isLoadingROI ||
    isLoadingInsights ||
    isLoadingRecommendations;

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['analytics-music-promotion'] });
    queryClient.invalidateQueries({ queryKey: ['analytics-wave-effect'] });
    queryClient.invalidateQueries({ queryKey: ['analytics-phase2-comparison'] });
    queryClient.invalidateQueries({ queryKey: ['analytics-roi'] });
    queryClient.invalidateQueries({ queryKey: ['analytics-insights'] });
    queryClient.invalidateQueries({ queryKey: ['analytics-recommendations'] });
  };

  const handleExport = async () => {
    try {
      const data = await enhancedAnalyticsService.exportAnalytics(startDate, endDate);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export analytics:', error);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Enhanced Analytics</Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button variant="outlined" startIcon={<Download />} onClick={handleExport}>
            Export
          </Button>
        </Box>
      </Box>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          label="Start Date"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="End Date"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Box>

      <Grid container spacing={3}>
        {musicMetrics && (
          <Grid item xs={12}>
            <MusicPromotionMetricsComponent metrics={musicMetrics} />
          </Grid>
        )}

        {waveMetrics && (
          <Grid item xs={12} md={6}>
            <WaveEffectMetricsComponent metrics={waveMetrics} />
          </Grid>
        )}

        {roiMetrics && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ROI Metrics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Effort: {roiMetrics.effort} videos
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Results: {roiMetrics.results.toLocaleString()} views
                </Typography>
                <Typography variant="h5" color="primary">
                  ROI: {roiMetrics.roi.toLocaleString(undefined, { maximumFractionDigits: 0 })} views/video
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {phase2Comparison && (
          <Grid item xs={12}>
            <Phase2ComparisonComponent comparison={phase2Comparison} />
          </Grid>
        )}

        {insightsData && (
          <Grid item xs={12} md={6}>
            <InsightsPanel insights={insightsData.insights} />
          </Grid>
        )}

        {recommendationsData && (
          <Grid item xs={12} md={6}>
            <RecommendationsPanel recommendations={recommendationsData.recommendations} />
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
