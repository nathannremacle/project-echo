import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Grid,
} from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';
import { Phase2Status as Phase2StatusType } from '../../services/phase2';

interface Phase2StatusProps {
  status: Phase2StatusType;
}

export default function Phase2Status({ status }: Phase2StatusProps) {
  const phase2Channels = status.channels.filter((c) => c.phase2_enabled);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Phase 2 Status
        </Typography>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Overall Status
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                {status.phase2_enabled ? (
                  <CheckCircle color="success" />
                ) : (
                  <Cancel color="disabled" />
                )}
                <Typography variant="body1" fontWeight="medium">
                  {status.phase2_enabled ? 'Active' : 'Inactive'}
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Phase 2 Channels
              </Typography>
              <Typography variant="h6">{status.phase2_channels_count}</Typography>
              <Typography variant="caption" color="text.secondary">
                of {status.total_channels} total
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Active Channels
              </Typography>
              <Typography variant="h6">{status.active_channels}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Music Tracks
              </Typography>
              <Typography variant="h6">{status.available_music_tracks}</Typography>
            </Box>
          </Grid>
        </Grid>

        {phase2Channels.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Channels with Phase 2 Enabled
            </Typography>
            <List dense>
              {phase2Channels.map((channel) => (
                <ListItem key={channel.id}>
                  <ListItemText
                    primary={channel.name}
                    secondary={
                      <Box display="flex" gap={1} mt={0.5}>
                        <Chip
                          label={channel.is_active ? 'Active' : 'Inactive'}
                          size="small"
                          color={channel.is_active ? 'success' : 'default'}
                        />
                        <Chip label="Phase 2 Enabled" size="small" color="primary" />
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
