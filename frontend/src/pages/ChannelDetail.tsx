import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  Button,
  Switch,
  FormControlLabel,
  IconButton,
  Tooltip,
} from '@mui/material';
import { ArrowBack, Refresh } from '@mui/icons-material';
import { channelService, Channel, ChannelUpdate } from '../services/channels';
import ChannelInfo from '../components/channel/ChannelInfo';
import ChannelStatistics from '../components/channel/ChannelStatistics';
import ChannelConfiguration from '../components/channel/ChannelConfiguration';
import ChannelCredentials from '../components/channel/ChannelCredentials';

export default function ChannelDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch channel data
  const {
    data: channel,
    isLoading: isLoadingChannel,
    error: channelError,
  } = useQuery({
    queryKey: ['channel', id],
    queryFn: () => channelService.getChannel(id!),
    enabled: !!id,
  });

  // Fetch channel statistics
  const {
    data: statistics,
    isLoading: isLoadingStats,
    error: statsError,
  } = useQuery({
    queryKey: ['channel-statistics', id],
    queryFn: () => channelService.getChannelStatistics(id!),
    enabled: !!id,
  });

  // Update channel mutation
  const updateMutation = useMutation({
    mutationFn: (updates: ChannelUpdate) => channelService.updateChannel(id!, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['channel', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  // Activate/deactivate mutation
  const toggleActiveMutation = useMutation({
    mutationFn: (isActive: boolean) =>
      isActive ? channelService.activateChannel(id!) : channelService.deactivateChannel(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['channel', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const handleSave = async (updates: ChannelUpdate) => {
    await updateMutation.mutateAsync(updates);
  };

  const handleToggleActive = () => {
    if (channel) {
      toggleActiveMutation.mutate(!channel.isActive);
    }
  };

  if (isLoadingChannel) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (channelError) {
    return (
      <Alert severity="error">
        Failed to load channel: {channelError instanceof Error ? channelError.message : 'Unknown error'}
      </Alert>
    );
  }

  if (!channel) {
    return (
      <Alert severity="info">Channel not found</Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate('/channels')}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h4">{channel.name}</Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControlLabel
            control={
              <Switch
                checked={channel.isActive}
                onChange={handleToggleActive}
                disabled={toggleActiveMutation.isPending}
              />
            }
            label={channel.isActive ? 'Active' : 'Inactive'}
          />
          <Tooltip title="Refresh">
            <IconButton
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['channel', id] });
                queryClient.invalidateQueries({ queryKey: ['channel-statistics', id] });
              }}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3} direction="column">
            <Grid item>
              <ChannelInfo channel={channel} />
            </Grid>
            {statistics && (
              <Grid item>
                <ChannelStatistics statistics={statistics} />
              </Grid>
            )}
            {isLoadingStats && (
              <Grid item>
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress size={24} />
                </Box>
              </Grid>
            )}
            {statsError && (
              <Grid item>
                <Alert severity="warning">
                  Failed to load statistics: {statsError instanceof Error ? statsError.message : 'Unknown error'}
                </Alert>
              </Grid>
            )}
          </Grid>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={4}>
          <Box display="flex" flexDirection="column" gap={3}>
            <ChannelCredentials
              channelId={channel.id}
              onSuccess={() => queryClient.invalidateQueries({ queryKey: ['channel', id] })}
            />
            <ChannelConfiguration channel={channel} onSave={handleSave} />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
