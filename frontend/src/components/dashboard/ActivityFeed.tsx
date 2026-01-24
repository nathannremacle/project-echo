import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
} from '@mui/material';
import { VideoLibrary, CheckCircle, Error } from '@mui/icons-material';
import { DashboardData } from '../../services/orchestration';

interface ActivityFeedProps {
  data: DashboardData;
}

export default function ActivityFeed({ data }: ActivityFeedProps) {
  // Generate activity items from dashboard data
  const activities: Array<{
    type: 'publication' | 'system';
    message: string;
    timestamp?: string;
    status?: 'success' | 'error';
  }> = [];

  // Add channel activities
  data.channels.statuses.forEach((channel) => {
    if (channel.statistics.published_7d > 0) {
      activities.push({
        type: 'publication',
        message: `${channel.name}: ${channel.statistics.published_7d} videos published`,
        status: 'success',
      });
    }
    if (channel.errors && channel.errors.length > 0) {
      activities.push({
        type: 'system',
        message: `${channel.name}: ${channel.errors[0]}`,
        status: 'error',
      });
    }
  });

  // Add system activities
  if (!data.system.status.running) {
    activities.push({
      type: 'system',
      message: 'Orchestration system stopped',
      status: 'error',
    });
  } else if (data.system.status.paused) {
    activities.push({
      type: 'system',
      message: 'Orchestration system paused',
      status: 'error',
    });
  }

  // Sort by timestamp (most recent first) - limited implementation
  const recentActivities = activities.slice(0, 10);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        {recentActivities.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No recent activity
          </Typography>
        ) : (
          <List dense>
            {recentActivities.map((activity, idx) => (
              <ListItem key={idx}>
                <Box display="flex" alignItems="center" gap={1} width="100%">
                  {activity.type === 'publication' ? (
                    <VideoLibrary fontSize="small" color="primary" />
                  ) : (
                    activity.status === 'error' ? (
                      <Error fontSize="small" color="error" />
                    ) : (
                      <CheckCircle fontSize="small" color="success" />
                    )
                  )}
                  <ListItemText
                    primary={activity.message}
                    secondary={activity.timestamp || 'Recently'}
                  />
                  {activity.status && (
                    <Chip
                      label={activity.status}
                      color={activity.status === 'success' ? 'success' : 'error'}
                      size="small"
                    />
                  )}
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
