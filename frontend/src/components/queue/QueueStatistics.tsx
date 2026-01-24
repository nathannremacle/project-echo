import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
} from '@mui/material';
import {
  Queue,
  CheckCircle,
  Error,
  Schedule,
} from '@mui/icons-material';
import { QueueStatistics as QueueStats } from '../../services/queue';

interface QueueStatisticsProps {
  statistics: QueueStats;
}

export default function QueueStatistics({ statistics }: QueueStatisticsProps) {
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Queue color="primary" />
              <Typography variant="h6">Total</Typography>
            </Box>
            <Typography variant="h4">{statistics.total}</Typography>
            <Typography variant="caption" color="text.secondary">
              Items in queue
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <CheckCircle color="success" />
              <Typography variant="h6">Success Rate</Typography>
            </Box>
            <Typography variant="h4">
              {statistics.successRate.toFixed(1)}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Completed successfully
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Error color="error" />
              <Typography variant="h6">Failed</Typography>
            </Box>
            <Typography variant="h4">{statistics.failedCount}</Typography>
            <Typography variant="caption" color="text.secondary">
              Failed jobs
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Schedule color="info" />
              <Typography variant="h6">Avg Time</Typography>
            </Box>
            <Typography variant="h4">
              {formatDuration(statistics.averageProcessingTime)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Average processing time
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
