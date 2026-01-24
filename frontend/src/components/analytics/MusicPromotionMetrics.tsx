import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import { MusicPromotionMetrics } from '../../services/enhancedAnalytics';

interface MusicPromotionMetricsProps {
  metrics: MusicPromotionMetrics;
}

export default function MusicPromotionMetricsComponent({ metrics }: MusicPromotionMetricsProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Music Promotion Metrics
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Total Music Videos
              </Typography>
              <Typography variant="h4">{metrics.total_music_videos}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Total Views
              </Typography>
              <Typography variant="h4">{metrics.total_views.toLocaleString()}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Unique Music Tracks
              </Typography>
              <Typography variant="h4">{metrics.unique_music_tracks}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Avg Views/Video
              </Typography>
              <Typography variant="h4">
                {metrics.average_views_per_video.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
