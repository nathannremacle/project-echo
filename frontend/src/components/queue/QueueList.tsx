import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Box,
  Typography,
} from '@mui/material';
import {
  PlayArrow,
  Refresh,
  Delete,
  ArrowUpward,
  Visibility,
} from '@mui/icons-material';
import { VideoProcessingJob, Video } from '../../services/queue';
// Format time ago helper
const formatTimeAgo = (date: string) => {
  const now = new Date();
  const then = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);
  
  if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

interface QueueListProps {
  jobs: VideoProcessingJob[];
  videos: Video[];
  onRetry?: (videoId: string) => void;
  onCancel?: (jobId: string) => void;
  onDelete?: (videoId: string) => void;
  onPrioritize?: (jobId: string) => void;
  onPreview?: (videoId: string) => void;
}

export default function QueueList({
  jobs,
  videos,
  onRetry,
  onCancel,
  onDelete,
  onPrioritize,
  onPreview,
}: QueueListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'transformed':
      case 'published':
        return 'success';
      case 'processing':
      case 'downloading':
      case 'publishing':
        return 'info';
      case 'failed':
        return 'error';
      case 'queued':
      case 'pending':
      case 'scheduled':
        return 'default';
      case 'retrying':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getJobTypeLabel = (jobType: string) => {
    switch (jobType) {
      case 'scrape':
        return 'Scrape';
      case 'download':
        return 'Download';
      case 'transform':
        return 'Transform';
      case 'publish':
        return 'Publish';
      default:
        return jobType;
    }
  };

  // Combine jobs and videos for display
  const queueItems = jobs.map((job) => {
    const video = videos.find((v) => v.id === job.videoId);
    return {
      job,
      video,
    };
  });

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Video</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Channel</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>Duration</TableCell>
            <TableCell>Queued</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {queueItems.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} align="center">
                <Typography variant="body2" color="text.secondary">
                  No items in queue
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            queueItems.map(({ job, video }) => (
              <TableRow key={job.id}>
                <TableCell>
                  <Box>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {video?.sourceTitle || 'Unknown'}
                    </Typography>
                    {video?.sourceCreator && (
                      <Typography variant="caption" color="text.secondary">
                        by {video.sourceCreator}
                      </Typography>
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip label={getJobTypeLabel(job.jobType)} size="small" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={job.status}
                    color={getStatusColor(job.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {job.channelId.substring(0, 8)}...
                  </Typography>
                </TableCell>
                <TableCell>
                  {job.status === 'processing' ? (
                    <LinearProgress variant="indeterminate" />
                  ) : job.status === 'completed' ? (
                    <Typography variant="caption" color="success.main">
                      100%
                    </Typography>
                  ) : (
                    <Typography variant="caption" color="text.secondary">
                      -
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {job.duration ? (
                    <Typography variant="body2">
                      {Math.round(job.duration)}s
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      -
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="caption" color="text.secondary">
                    {formatTimeAgo(job.queuedAt)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={0.5}>
                    {video && video.transformedUrl && (
                      <Tooltip title="Preview">
                        <IconButton
                          size="small"
                          onClick={() => onPreview?.(video.id)}
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {job.status === 'failed' && video && (
                      <Tooltip title="Retry">
                        <IconButton
                          size="small"
                          onClick={() => onRetry?.(video.id)}
                        >
                          <Refresh fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {job.status !== 'completed' && (
                      <Tooltip title="Cancel">
                        <IconButton
                          size="small"
                          onClick={() => onCancel?.(job.id)}
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {job.status === 'queued' && (
                      <Tooltip title="Prioritize">
                        <IconButton
                          size="small"
                          onClick={() => onPrioritize?.(job.id)}
                        >
                          <ArrowUpward fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
