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
import { VideoLibrary, CheckCircle, Error, Info } from '@mui/icons-material';
import { DashboardData } from '../../services/orchestration';

interface ActivityFeedProps {
  data: DashboardData;
}

// Setup warnings that are not real errors (expected for new/test channels)
const SETUP_WARNINGS = [
  'No GitHub repository configured',
  'GITHUB_TOKEN not configured',
  'GitHub repository not found',
];

export default function ActivityFeed({ data }: ActivityFeedProps) {
  // Generate activity items from dashboard data
  const activities: Array<{
    type: 'publication' | 'system';
    message: string;
    timestamp?: string;
    status?: 'success' | 'error' | 'info';
  }> = [];

  // Add channel activities (only real errors, not setup warnings)
  data.channels.statuses.forEach((channel) => {
    if (channel.statistics?.published_7d > 0) {
      activities.push({
        type: 'publication',
        message: `${channel.name}: ${channel.statistics.published_7d} videos published`,
        status: 'success',
      });
    }
    const realErrors = (channel.errors || []).filter(
      (e) => !SETUP_WARNINGS.some((w) => e.includes(w))
    );
    if (realErrors.length > 0) {
      activities.push({
        type: 'system',
        message: `${channel.name}: ${realErrors[0]}`,
        status: 'error',
      });
    }
  });

  // System status: "stopped" is the default state, not an error
  if (!data.system.status.running) {
    activities.push({
      type: 'system',
      message: 'Orchestration system stopped (click Start to run)',
      status: 'info',
    });
  } else if (data.system.status.paused) {
    activities.push({
      type: 'system',
      message: 'Orchestration system paused',
      status: 'info',
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
                  ) : activity.status === 'error' ? (
                    <Error fontSize="small" color="error" />
                  ) : activity.status === 'info' ? (
                    <Info fontSize="small" color="info" />
                  ) : (
                    <CheckCircle fontSize="small" color="success" />
                  )}
                  <ListItemText
                    primary={activity.message}
                    secondary={activity.timestamp || 'Recently'}
                  />
                  {activity.status && activity.status !== 'info' && (
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
