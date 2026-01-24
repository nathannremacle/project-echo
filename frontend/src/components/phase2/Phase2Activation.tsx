import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  TextField,
  Alert,
  Grid,
  Chip,
} from '@mui/material';
import { PlayArrow, Stop, Refresh } from '@mui/icons-material';
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { phase2Service, ActivatePhase2Request } from '../../services/phase2';
import { orchestrationService } from '../../services/orchestration';

export default function Phase2Activation() {
  const queryClient = useQueryClient();
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [selectedMusic, setSelectedMusic] = useState<string>('');
  const [applyRetroactive, setApplyRetroactive] = useState(false);
  const [normalize, setNormalize] = useState(true);
  const [loopAudio, setLoopAudio] = useState(true);

  // Fetch Phase 2 status
  const { data: status, isLoading: isLoadingStatus } = useQuery({
    queryKey: ['phase2-status'],
    queryFn: () => phase2Service.getStatus(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch channels for selection
  const { data: channelsData } = useQuery({
    queryKey: ['channels-list'],
    queryFn: async () => {
      const dashboard = await orchestrationService.getDashboard();
      return {
        channels: dashboard.channels.statuses.map((s) => ({
          id: s.channel_id,
          name: s.name,
          phase2_enabled: false, // Would come from status
        })),
      };
    },
  });

  // Fetch music tracks
  const { data: musicTracks } = useQuery({
    queryKey: ['music-tracks'],
    queryFn: async () => {
      const { settingsService } = await import('../../services/settings');
      return settingsService.getMusicTracks();
    },
  });

  // Activate mutation
  const activateMutation = useMutation({
    mutationFn: (request: ActivatePhase2Request) => phase2Service.activate(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['phase2-status'] });
      queryClient.invalidateQueries({ queryKey: ['channels-list'] });
    },
  });

  // Deactivate mutation
  const deactivateMutation = useMutation({
    mutationFn: (channel_ids?: string[]) => phase2Service.deactivate(channel_ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['phase2-status'] });
      queryClient.invalidateQueries({ queryKey: ['channels-list'] });
    },
  });

  const handleActivate = () => {
    if (!selectedMusic) {
      return;
    }

    activateMutation.mutate({
      channel_ids: selectedChannels.length > 0 ? selectedChannels : undefined,
      music_id: selectedMusic,
      apply_retroactive: applyRetroactive,
      normalize,
      loop_audio: loopAudio,
    });
  };

  const handleDeactivate = () => {
    deactivateMutation.mutate(
      selectedChannels.length > 0 ? selectedChannels : undefined
    );
  };

  if (isLoadingStatus) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Phase 2 Activation</Typography>
          <Chip
            label={status?.phase2_enabled ? 'Active' : 'Inactive'}
            color={status?.phase2_enabled ? 'success' : 'default'}
          />
        </Box>

        {status && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Phase 2 is {status.phase2_enabled ? 'active' : 'inactive'} on{' '}
            {status.phase2_channels_count} of {status.total_channels} channels.
            {status.available_music_tracks > 0 && (
              <> {status.available_music_tracks} music track(s) available.</>
            )}
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Channels</InputLabel>
              <Select
                multiple
                value={selectedChannels}
                onChange={(e) => setSelectedChannels(e.target.value as string[])}
                label="Select Channels"
                renderValue={(selected) => {
                  if (selected.length === 0) return 'All Channels';
                  return `${selected.length} channel(s) selected`;
                }}
              >
                <MenuItem value="">All Channels</MenuItem>
                {channelsData?.channels.map((channel) => (
                  <MenuItem key={channel.id} value={channel.id}>
                    {channel.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Music Track</InputLabel>
              <Select
                value={selectedMusic}
                onChange={(e) => setSelectedMusic(e.target.value)}
                label="Music Track"
              >
                {musicTracks && musicTracks.length > 0 ? (
                  musicTracks.map((track) => (
                    <MenuItem key={track.id} value={track.id}>
                      {track.name} - {track.artist}
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem disabled>No music tracks available</MenuItem>
                )}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={applyRetroactive}
                  onChange={(e) => setApplyRetroactive(e.target.checked)}
                />
              }
              label="Apply to already published videos (retroactive)"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={normalize}
                  onChange={(e) => setNormalize(e.target.checked)}
                />
              }
              label="Normalize audio levels"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={loopAudio}
                  onChange={(e) => setLoopAudio(e.target.checked)}
                />
              }
              label="Loop audio if shorter than video"
            />
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PlayArrow />}
                onClick={handleActivate}
                disabled={!selectedMusic || activateMutation.isPending}
              >
                Activate Phase 2
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<Stop />}
                onClick={handleDeactivate}
                disabled={deactivateMutation.isPending}
              >
                Deactivate Phase 2
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  queryClient.invalidateQueries({ queryKey: ['phase2-status'] });
                }}
              >
                Refresh
              </Button>
            </Box>
          </Grid>

          {activateMutation.isSuccess && (
            <Grid item xs={12}>
              <Alert severity="success">
                Phase 2 activated successfully! {activateMutation.data.activated.length} channel(s)
                processed.
              </Alert>
            </Grid>
          )}

          {activateMutation.isError && (
            <Grid item xs={12}>
              <Alert severity="error">
                Failed to activate Phase 2: {activateMutation.error?.message}
              </Alert>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
}
