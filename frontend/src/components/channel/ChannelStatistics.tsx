import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  People,
  Visibility,
  VideoLibrary,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { ChannelStatistics as ChannelStats } from '../../services/channels';

interface ChannelStatisticsProps {
  statistics: ChannelStats;
}

export default function ChannelStatistics({ statistics }: ChannelStatisticsProps) {
  const { current, trends } = statistics;

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Statistics
        </Typography>

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <People color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Subscribers
                </Typography>
              </Box>
              <Typography variant="h5">{formatNumber(current.subscriberCount)}</Typography>
              {trends.subscriberGrowth !== undefined && (
                <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                  {trends.subscriberGrowth >= 0 ? (
                    <TrendingUp fontSize="small" color="success" />
                  ) : (
                    <TrendingDown fontSize="small" color="error" />
                  )}
                  <Typography variant="caption" color={trends.subscriberGrowth >= 0 ? 'success.main' : 'error.main'}>
                    {trends.subscriberGrowth >= 0 ? '+' : ''}{trends.subscriberGrowth.toFixed(1)}%
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Visibility color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Total Views
                </Typography>
              </Box>
              <Typography variant="h5">{formatNumber(current.totalViews)}</Typography>
              {trends.viewGrowth !== undefined && (
                <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                  {trends.viewGrowth >= 0 ? (
                    <TrendingUp fontSize="small" color="success" />
                  ) : (
                    <TrendingDown fontSize="small" color="error" />
                  )}
                  <Typography variant="caption" color={trends.viewGrowth >= 0 ? 'success.main' : 'error.main'}>
                    {trends.viewGrowth >= 0 ? '+' : ''}{trends.viewGrowth.toFixed(1)}%
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <VideoLibrary color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Videos
                </Typography>
              </Box>
              <Typography variant="h5">{current.totalVideos}</Typography>
              <Typography variant="caption" color="text.secondary">
                Avg: {current.totalVideos > 0 ? formatNumber(current.totalViews / current.totalVideos) : 0} views
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary" mb={1}>
                Recent Activity
              </Typography>
              <Typography variant="h5">{current.videoCount}</Typography>
              <Typography variant="caption" color="text.secondary">
                Videos (last period)
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
