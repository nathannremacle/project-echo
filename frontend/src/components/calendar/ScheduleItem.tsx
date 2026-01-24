import {
  Box,
  Typography,
  Chip,
  Card,
  CardContent,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Edit,
  Cancel,
  CheckCircle,
  Error,
  Schedule,
} from '@mui/icons-material';
import { PublicationSchedule } from '../../services/schedules';

interface ScheduleItemProps {
  schedule: PublicationSchedule;
  compact?: boolean;
  onClick?: () => void;
  onReschedule?: (newDate: Date) => void;
  onCancel?: () => void;
}

export default function ScheduleItem({
  schedule,
  compact = false,
  onClick,
  onReschedule,
  onCancel,
}: ScheduleItemProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'executing':
        return 'info';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'default';
      case 'pending':
      case 'scheduled':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle fontSize="small" />;
      case 'failed':
        return <Error fontSize="small" />;
      case 'pending':
      case 'scheduled':
        return <Schedule fontSize="small" />;
      default:
        return null;
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (compact) {
    return (
      <Chip
        label={`${formatTime(schedule.scheduledAt)}`}
        size="small"
        color={getStatusColor(schedule.status) as any}
        icon={getStatusIcon(schedule.status)}
        onClick={onClick}
        sx={{ cursor: 'pointer', width: '100%' }}
      />
    );
  }

  return (
    <Card
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? { boxShadow: 2 } : {},
        mb: 1,
      }}
      onClick={onClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <Typography variant="body2" fontWeight="medium">
                {formatTime(schedule.scheduledAt)}
              </Typography>
              <Chip
                label={schedule.status}
                color={getStatusColor(schedule.status) as any}
                size="small"
                icon={getStatusIcon(schedule.status)}
              />
              {schedule.scheduleType && (
                <Chip
                  label={schedule.scheduleType}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
            {schedule.videoId && (
              <Typography variant="caption" color="text.secondary">
                Video: {schedule.videoId.substring(0, 8)}...
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary" display="block">
              Channel: {schedule.channelId.substring(0, 8)}...
            </Typography>
            {schedule.waveId && (
              <Typography variant="caption" color="primary" display="block">
                Wave: {schedule.waveId.substring(0, 8)}...
              </Typography>
            )}
          </Box>
          <Box display="flex" gap={0.5}>
            {onReschedule && schedule.status === 'pending' && (
              <Tooltip title="Reschedule">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    // For MVP, just trigger reschedule with current date
                    // In full implementation, would open a date picker
                    const newDate = new Date(schedule.scheduledAt);
                    newDate.setHours(newDate.getHours() + 1);
                    onReschedule(newDate);
                  }}
                >
                  <Edit fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {onCancel && schedule.status !== 'completed' && schedule.status !== 'cancelled' && (
              <Tooltip title="Cancel">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onCancel();
                  }}
                >
                  <Cancel fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
