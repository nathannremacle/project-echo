import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
} from '@mui/material';
import { WaveEffectMetrics } from '../../services/enhancedAnalytics';

interface WaveEffectMetricsProps {
  metrics: WaveEffectMetrics;
}

export default function WaveEffectMetricsComponent({ metrics }: WaveEffectMetricsProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Wave Effect Metrics
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Total Waves
              </Typography>
              <Typography variant="h4">{metrics.total_waves}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Largest Wave
              </Typography>
              <Typography variant="h4">
                {metrics.largest_wave ? `${metrics.largest_wave.videos_count} videos` : 'N/A'}
              </Typography>
              {metrics.largest_wave && (
                <Typography variant="caption" color="text.secondary">
                  {metrics.largest_wave.channels_count} channels
                </Typography>
              )}
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Avg Wave Size
              </Typography>
              <Typography variant="h4">
                {metrics.average_wave_size.toLocaleString(undefined, { maximumFractionDigits: 1 })}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Total Reach
              </Typography>
              <Typography variant="h4">{metrics.total_reach}</Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
