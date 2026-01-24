import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { Phase2Comparison } from '../../services/enhancedAnalytics';

interface Phase2ComparisonProps {
  comparison: Phase2Comparison;
}

export default function Phase2ComparisonComponent({ comparison }: Phase2ComparisonProps) {
  const improvement = comparison.improvement.views_per_video;
  const isPositive = improvement > 0;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Phase 2 Comparison
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Pre-Phase 2
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Videos: {comparison.pre_phase2.total_videos}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Views: {comparison.pre_phase2.total_views.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Views/Video: {comparison.pre_phase2.average_views_per_video.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Post-Phase 2
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Videos: {comparison.post_phase2.total_videos}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Views: {comparison.post_phase2.total_views.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Views/Video: {comparison.post_phase2.average_views_per_video.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center" gap={1}>
              {isPositive ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
              <Typography variant="h6" color={isPositive ? 'success.main' : 'error.main'}>
                {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}% improvement
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
