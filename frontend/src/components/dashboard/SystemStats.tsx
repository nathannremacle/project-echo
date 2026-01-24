import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  VideoLibrary,
  Queue,
  TrendingUp,
} from '@mui/icons-material';
import { DashboardData } from '../../services/orchestration';

interface SystemStatsProps {
  data: DashboardData;
}

export default function SystemStats({ data }: SystemStatsProps) {
  const getSystemStatusColor = () => {
    if (!data.system.status.running) return 'error';
    if (data.system.status.paused) return 'warning';
    return 'success';
  };

  const getSystemStatusLabel = () => {
    if (!data.system.status.running) return 'Stopped';
    if (data.system.status.paused) return 'Paused';
    return 'Running';
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <CheckCircle color={getSystemStatusColor() as any} />
              <Typography variant="h6">System Status</Typography>
            </Box>
            <Chip
              label={getSystemStatusLabel()}
              color={getSystemStatusColor() as any}
              size="small"
            />
            {data.system.queue_paused && (
              <Chip label="Queue Paused" color="warning" size="small" sx={{ ml: 1 }} />
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <VideoLibrary color="primary" />
              <Typography variant="h6">Published</Typography>
            </Box>
            <Typography variant="h4">
              {data.statistics.overall.published_count || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total: {data.statistics.overall.total || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <TrendingUp color="success" />
              <Typography variant="h6">Success Rate</Typography>
            </Box>
            <Typography variant="h4">
              {data.statistics.overall.success_rate?.toFixed(1) || 0}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Last 30 days
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Queue color="info" />
              <Typography variant="h6">Schedules</Typography>
            </Box>
            <Typography variant="h4">
              {data.schedules.pending || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Upcoming: {data.schedules.upcoming_7d || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
