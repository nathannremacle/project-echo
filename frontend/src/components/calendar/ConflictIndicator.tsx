import { Alert, AlertTitle, Box, Typography } from '@mui/material';
import { Warning } from '@mui/icons-material';
import { PublicationSchedule } from '../../services/schedules';

interface ConflictIndicatorProps {
  schedules: PublicationSchedule[];
}

export default function ConflictIndicator({ schedules }: ConflictIndicatorProps) {
  // Detect conflicts: same video on same channel at same time
  const detectConflicts = () => {
    const conflicts: Array<{
      videoId: string;
      channelId: string;
      schedules: PublicationSchedule[];
    }> = [];

    const scheduleMap = new Map<string, PublicationSchedule[]>();

    schedules.forEach((schedule) => {
      if (schedule.videoId && schedule.status !== 'completed' && schedule.status !== 'cancelled') {
        const key = `${schedule.videoId}-${schedule.channelId}`;
        if (!scheduleMap.has(key)) {
          scheduleMap.set(key, []);
        }
        scheduleMap.get(key)!.push(schedule);
      }
    });

    scheduleMap.forEach((scheduleList, key) => {
      if (scheduleList.length > 1) {
        const [videoId, channelId] = key.split('-');
        conflicts.push({
          videoId,
          channelId,
          schedules: scheduleList,
        });
      }
    });

    return conflicts;
  };

  const conflicts = detectConflicts();

  if (conflicts.length === 0) {
    return null;
  }

  return (
    <Alert severity="warning" icon={<Warning />} sx={{ mb: 2 }}>
      <AlertTitle>Conflicts Detected</AlertTitle>
      {conflicts.map((conflict, idx) => (
        <Box key={idx} sx={{ mt: 1 }}>
          <Typography variant="body2">
            Video {conflict.videoId.substring(0, 8)}... is scheduled multiple times on channel{' '}
            {conflict.channelId.substring(0, 8)}...
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {conflict.schedules.length} conflicting schedules
          </Typography>
        </Box>
      ))}
    </Alert>
  );
}
