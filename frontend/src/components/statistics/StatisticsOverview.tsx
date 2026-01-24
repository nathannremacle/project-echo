import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
} from '@mui/material';
import {
  People,
  Visibility,
  VideoLibrary,
  TrendingUp,
} from '@mui/icons-material';
import { StatisticsOverview as StatsOverview } from '../../services/statistics';

interface StatisticsOverviewProps {
  overview: StatsOverview;
}

export default function StatisticsOverview({ overview }: StatisticsOverviewProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <People color="primary" />
              <Typography variant="h6">Total Subscribers</Typography>
            </Box>
            <Typography variant="h4">{formatNumber(overview.totalSubscribers)}</Typography>
            <Typography variant="caption" color="text.secondary">
              Across {overview.activeChannels} active channels
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Visibility color="primary" />
              <Typography variant="h6">Total Views</Typography>
            </Box>
            <Typography variant="h4">{formatNumber(overview.totalViews)}</Typography>
            <Typography variant="caption" color="text.secondary">
              {overview.totalVideos} videos published
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <VideoLibrary color="primary" />
              <Typography variant="h6">Total Videos</Typography>
            </Box>
            <Typography variant="h4">{overview.totalVideos}</Typography>
            <Typography variant="caption" color="text.secondary">
              Published across all channels
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <TrendingUp color="success" />
              <Typography variant="h6">Recent Activity</Typography>
            </Box>
            <Typography variant="h5">
              +{formatNumber(overview.recentActivity.subscribersGained)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {overview.recentActivity.period}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
