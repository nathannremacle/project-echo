import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Link as LinkIcon,
  CalendarToday,
} from '@mui/icons-material';
import { Channel } from '../../services/channels';

interface ChannelInfoProps {
  channel: Channel;
}

export default function ChannelInfo({ channel }: ChannelInfoProps) {
  const getCredentialsStatus = () => {
    // TODO: Check actual credentials status from API
    // For now, assume valid if channel exists
    return 'valid';
  };

  const credentialsStatus = getCredentialsStatus();

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h5">{channel.name}</Typography>
          <Chip
            label={channel.isActive ? 'Active' : 'Inactive'}
            color={channel.isActive ? 'success' : 'default'}
            size="small"
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box display="flex" flexDirection="column" gap={2}>
          <Box>
            <Typography variant="caption" color="text.secondary">
              YouTube Channel ID
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
              <LinkIcon fontSize="small" color="action" />
              <Typography variant="body2">{channel.youtubeChannelId}</Typography>
            </Box>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              Channel URL
            </Typography>
            <Typography variant="body2" component="a" href={channel.youtubeChannelUrl} target="_blank" rel="noopener noreferrer">
              {channel.youtubeChannelUrl}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              Credentials Status
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
              {credentialsStatus === 'valid' ? (
                <>
                  <CheckCircle fontSize="small" color="success" />
                  <Typography variant="body2" color="success.main">Valid</Typography>
                </>
              ) : (
                <>
                  <Error fontSize="small" color="error" />
                  <Typography variant="body2" color="error.main">Invalid</Typography>
                </>
              )}
            </Box>
          </Box>

          {channel.lastPublicationAt && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                Last Publication
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                <CalendarToday fontSize="small" color="action" />
                <Typography variant="body2">
                  {new Date(channel.lastPublicationAt).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          )}

          <Box>
            <Typography variant="caption" color="text.secondary">
              Phase 2 (Music Replacement)
            </Typography>
            <Chip
              label={channel.phase2Enabled ? 'Enabled' : 'Disabled'}
              color={channel.phase2Enabled ? 'primary' : 'default'}
              size="small"
              sx={{ mt: 0.5 }}
            />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
