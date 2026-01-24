import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Visibility,
  People,
  VideoLibrary,
} from '@mui/icons-material';
import { ChannelStatus } from '../../services/orchestration';

interface ChannelCardProps {
  channel: ChannelStatus;
}

export default function ChannelCard({ channel }: ChannelCardProps) {
  const navigate = useNavigate();

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle />;
      case 'warning':
        return <Warning />;
      case 'error':
        return <Error />;
      default:
        return null;
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        cursor: 'pointer',
        '&:hover': {
          boxShadow: 4,
        },
      }}
      onClick={() => navigate(`/channels/${channel.channel_id}`)}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h6" component="div">
            {channel.name}
          </Typography>
          <Chip
            icon={getHealthIcon(channel.health)}
            label={channel.health}
            color={getHealthColor(channel.health) as any}
            size="small"
          />
        </Box>

        <Box display="flex" flexDirection="column" gap={1}>
          <Box display="flex" alignItems="center" gap={1}>
            <People fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Subscribers: {channel.statistics?.distributions_7d || 0}
            </Typography>
          </Box>

          <Box display="flex" alignItems="center" gap={1}>
            <Visibility fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Published (7d): {channel.statistics?.published_7d || 0}
            </Typography>
          </Box>

          <Box display="flex" alignItems="center" gap={1}>
            <VideoLibrary fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Success Rate: {channel.statistics?.success_rate?.toFixed(1) || 0}%
            </Typography>
          </Box>

          {channel.last_publication_at && (
            <Typography variant="caption" color="text.secondary">
              Last published: {new Date(channel.last_publication_at).toLocaleDateString()}
            </Typography>
          )}

          {channel.errors && channel.errors.length > 0 && (
            <Box mt={1}>
              {channel.errors.map((error, idx) => (
                <Chip
                  key={idx}
                  label={error}
                  color="error"
                  size="small"
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              ))}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
