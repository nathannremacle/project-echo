import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
} from '@mui/icons-material';
import { SystemHealth } from '../../services/settings';

interface SystemInformationProps {
  version: string;
  health: SystemHealth;
  resourceUsage?: {
    cpu?: number;
    memory?: number;
    disk?: number;
  };
}

export default function SystemInformation({
  version,
  health,
  resourceUsage,
}: SystemInformationProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle color="success" />;
      case 'degraded':
        return <Warning color="warning" />;
      case 'unhealthy':
        return <Error color="error" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Information
        </Typography>

        <Grid container spacing={2}>
          {/* Version */}
          <Grid item xs={12} sm={6}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Version
              </Typography>
              <Typography variant="body1">{version}</Typography>
            </Box>
          </Grid>

          {/* System Status */}
          <Grid item xs={12} sm={6}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                System Status
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                {getStatusIcon(health.status)}
                <Chip
                  label={health.status.toUpperCase()}
                  color={getStatusColor(health.status)}
                  size="small"
                />
              </Box>
            </Box>
          </Grid>

          {/* Component Status */}
          {health.components && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Component Status
              </Typography>
              <Grid container spacing={2}>
                {health.components.database && (
                  <Grid item xs={12} sm={4}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Database
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                        {getStatusIcon(health.components.database.status)}
                        <Typography variant="body2">
                          {health.components.database.status}
                        </Typography>
                        {health.components.database.responseTime && (
                          <Typography variant="caption" color="text.secondary">
                            ({health.components.database.responseTime}ms)
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Grid>
                )}

                {health.components.storage && (
                  <Grid item xs={12} sm={4}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Storage
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                        {getStatusIcon(health.components.storage.status)}
                        <Typography variant="body2">
                          {health.components.storage.status}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}

                {health.components.youtubeApi && (
                  <Grid item xs={12} sm={4}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        YouTube API
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                        {getStatusIcon(health.components.youtubeApi.status)}
                        <Typography variant="body2">
                          {health.components.youtubeApi.status}
                        </Typography>
                        {health.components.youtubeApi.quotaRemaining !== undefined && (
                          <Typography variant="caption" color="text.secondary">
                            ({health.components.youtubeApi.quotaRemaining} quota remaining)
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Grid>
          )}

          {/* Resource Usage */}
          {resourceUsage && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Resource Usage
              </Typography>
              <Grid container spacing={2}>
                {resourceUsage.cpu !== undefined && (
                  <Grid item xs={12} sm={4}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        CPU Usage
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resourceUsage.cpu}
                        sx={{ mt: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                        {resourceUsage.cpu.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>
                )}

                {resourceUsage.memory !== undefined && (
                  <Grid item xs={12} sm={4}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Memory Usage
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resourceUsage.memory}
                        sx={{ mt: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                        {resourceUsage.memory.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>
                )}

                {resourceUsage.disk !== undefined && (
                  <Grid item xs={12} sm={4}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Disk Usage
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resourceUsage.disk}
                        sx={{ mt: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                        {resourceUsage.disk.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
}
