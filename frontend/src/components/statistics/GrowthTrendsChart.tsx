import {
  Card,
  CardContent,
  Typography,
  Box,
} from '@mui/material';
import { ChannelStatistics } from '../../services/statistics';

interface GrowthTrendsChartProps {
  history: ChannelStatistics[];
  metric: 'subscribers' | 'views';
  title: string;
}

export default function GrowthTrendsChart({ history, metric, title }: GrowthTrendsChartProps) {
  // Simple line chart using Material-UI (no external chart library for MVP)
  // In production, would use recharts or similar

  const getDataPoint = (stat: ChannelStatistics) => {
    return metric === 'subscribers' ? stat.subscriberCount : stat.totalViews;
  };

  const dataPoints = history.map((stat) => ({
    date: new Date(stat.timestamp),
    value: getDataPoint(stat),
  }));

  const maxValue = Math.max(...dataPoints.map((d) => d.value), 1);
  const minValue = Math.min(...dataPoints.map((d) => d.value), 0);

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatValue = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toString();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        {dataPoints.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            No data available
          </Typography>
        ) : (
          <Box sx={{ mt: 2, position: 'relative', height: 200 }}>
            {/* Simple line chart visualization */}
            <Box
              sx={{
                position: 'relative',
                width: '100%',
                height: '100%',
                borderLeft: '1px solid',
                borderBottom: '1px solid',
                borderColor: 'divider',
              }}
            >
              {dataPoints.map((point, idx) => {
                const x = (idx / (dataPoints.length - 1 || 1)) * 100;
                const y = 100 - ((point.value - minValue) / (maxValue - minValue || 1)) * 100;

                return (
                  <Box
                    key={idx}
                    sx={{
                      position: 'absolute',
                      left: `${x}%`,
                      bottom: `${y}%`,
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: 'primary.main',
                      transform: 'translate(-50%, 50%)',
                    }}
                    title={`${formatDate(point.date)}: ${formatValue(point.value)}`}
                  />
                );
              })}

              {/* Connect points with lines */}
              {dataPoints.length > 1 && (
                <svg
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    pointerEvents: 'none',
                  }}
                >
                  {dataPoints.slice(1).map((point, idx) => {
                    const prevPoint = dataPoints[idx];
                    const x1 = (idx / (dataPoints.length - 1)) * 100;
                    const y1 = 100 - ((prevPoint.value - minValue) / (maxValue - minValue || 1)) * 100;
                    const x2 = ((idx + 1) / (dataPoints.length - 1)) * 100;
                    const y2 = 100 - ((point.value - minValue) / (maxValue - minValue || 1)) * 100;

                    return (
                      <line
                        key={idx}
                        x1={`${x1}%`}
                        y1={`${y1}%`}
                        x2={`${x2}%`}
                        y2={`${y2}%`}
                        stroke="currentColor"
                        strokeWidth="2"
                        style={{ color: 'var(--mui-palette-primary-main)' }}
                      />
                    );
                  })}
                </svg>
              )}
            </Box>

            {/* X-axis labels */}
            <Box display="flex" justifyContent="space-between" mt={1}>
              {dataPoints.length > 0 && (
                <>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(dataPoints[0].date)}
                  </Typography>
                  {dataPoints.length > 1 && (
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(dataPoints[dataPoints.length - 1].date)}
                    </Typography>
                  )}
                </>
              )}
            </Box>

            {/* Y-axis labels */}
            <Box
              sx={{
                position: 'absolute',
                left: -40,
                top: 0,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <Typography variant="caption" color="text.secondary">
                {formatValue(maxValue)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatValue(minValue)}
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
