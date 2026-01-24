import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { orchestrationService } from '../services/orchestration';
import SystemStats from '../components/dashboard/SystemStats';
import ChannelCard from '../components/dashboard/ChannelCard';
import QuickActions from '../components/dashboard/QuickActions';
import ActivityFeed from '../components/dashboard/ActivityFeed';

export default function Dashboard() {
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => orchestrationService.getDashboard(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load dashboard: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Dashboard</Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={() => refetch()} disabled={isRefetching}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* System Statistics */}
      <Box mb={3}>
        <SystemStats data={data} />
      </Box>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Channels Grid */}
        <Grid item xs={12} md={8}>
          <Box mb={2}>
            <Typography variant="h6" gutterBottom>
              Channels ({data.channels.active} / {data.channels.total} active)
            </Typography>
          </Box>
          <Grid container spacing={2}>
            {data.channels.statuses.map((channel) => (
              <Grid item xs={12} sm={6} md={4} key={channel.channel_id}>
                <ChannelCard channel={channel} />
              </Grid>
            ))}
            {data.channels.statuses.length === 0 && (
              <Grid item xs={12}>
                <Alert severity="info">No channels configured yet. Add a channel to get started.</Alert>
              </Grid>
            )}
          </Grid>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2} direction="column">
            <Grid item>
              <QuickActions />
            </Grid>
            <Grid item>
              <ActivityFeed data={data} />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}
