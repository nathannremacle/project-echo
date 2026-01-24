import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { queueService, QueueFilters } from '../services/queue';
import QueueList from '../components/queue/QueueList';
import QueueFiltersComponent from '../components/queue/QueueFilters';
import QueueStatistics from '../components/queue/QueueStatistics';

export default function Queue() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<QueueFilters>({});
  const [previewVideoId, setPreviewVideoId] = useState<string | null>(null);

  // Fetch jobs
  const {
    data: jobsData,
    isLoading: isLoadingJobs,
    error: jobsError,
  } = useQuery({
    queryKey: ['queue-jobs', filters],
    queryFn: () => queueService.getJobs(filters),
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // Fetch videos
  const {
    data: videosData,
    isLoading: isLoadingVideos,
    error: videosError,
  } = useQuery({
    queryKey: ['queue-videos', filters],
    queryFn: () => queueService.getVideos(filters),
    refetchInterval: 10000,
  });

  // Fetch channels for filter
  const { data: channelsData } = useQuery({
    queryKey: ['channels-list'],
    queryFn: async () => {
      // Use orchestration service to get channels
      const { orchestrationService } = await import('../services/orchestration');
      const dashboard = await orchestrationService.getDashboard();
      return {
        channels: dashboard.channels.statuses.map((s) => ({
          id: s.channel_id,
          name: s.name,
        })),
      };
    },
  });

  // Fetch statistics
  const {
    data: statistics,
    isLoading: isLoadingStats,
  } = useQuery({
    queryKey: ['queue-statistics'],
    queryFn: () => queueService.getQueueStatistics(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Retry mutation
  const retryMutation = useMutation({
    mutationFn: (videoId: string) => queueService.retryVideo(videoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queue-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['queue-videos'] });
    },
  });

  // Cancel mutation
  const cancelMutation = useMutation({
    mutationFn: (jobId: string) => queueService.cancelJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queue-jobs'] });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (videoId: string) => queueService.deleteVideo(videoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queue-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['queue-videos'] });
    },
  });

  const handleRetry = (videoId: string) => {
    retryMutation.mutate(videoId);
  };

  const handleCancel = (jobId: string) => {
    if (window.confirm('Are you sure you want to cancel this job?')) {
      cancelMutation.mutate(jobId);
    }
  };

  const handleDelete = (videoId: string) => {
    if (window.confirm('Are you sure you want to delete this video?')) {
      deleteMutation.mutate(videoId);
    }
  };

  const handlePrioritize = (jobId: string) => {
    // TODO: Implement prioritize endpoint
    console.log('Prioritize job:', jobId);
  };

  const handlePreview = (videoId: string) => {
    setPreviewVideoId(videoId);
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  if (isLoadingJobs || isLoadingVideos) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (jobsError || videosError) {
    return (
      <Alert severity="error">
        Failed to load queue: {jobsError instanceof Error ? jobsError.message : 'Unknown error'}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Video Processing Queue</Typography>
        <Tooltip title="Refresh">
          <IconButton
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ['queue-jobs'] });
              queryClient.invalidateQueries({ queryKey: ['queue-videos'] });
              queryClient.invalidateQueries({ queryKey: ['queue-statistics'] });
            }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Statistics */}
      {statistics && (
        <Box mb={3}>
          <QueueStatistics statistics={statistics} />
        </Box>
      )}

      {/* Filters */}
      <QueueFiltersComponent
        filters={filters}
        channels={channelsData?.channels || []}
        onChange={setFilters}
        onClear={handleClearFilters}
      />

      {/* Queue List */}
      {jobsData && videosData && (
        <QueueList
          jobs={jobsData.jobs}
          videos={videosData.videos}
          onRetry={handleRetry}
          onCancel={handleCancel}
          onDelete={handleDelete}
          onPrioritize={handlePrioritize}
          onPreview={handlePreview}
        />
      )}

      {/* Preview Dialog */}
      <Dialog
        open={!!previewVideoId}
        onClose={() => setPreviewVideoId(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Video Preview</DialogTitle>
        <DialogContent>
          {previewVideoId && videosData && (
            <Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Preview for video: {previewVideoId}
              </Typography>
              <Alert severity="info">
                Video preview functionality will be implemented in a future update.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewVideoId(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
