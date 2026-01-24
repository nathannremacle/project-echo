import { Alert, AlertTitle, Box, Typography } from '@mui/material';
import { Warning, TrendingUp, TrendingDown } from '@mui/icons-material';
import { ChannelStatistics } from '../../services/statistics';

interface AnomalyIndicatorProps {
  history: ChannelStatistics[];
  metric: 'subscribers' | 'views';
}

export default function AnomalyIndicator({ history, metric }: AnomalyIndicatorProps) {
  const detectAnomalies = () => {
    if (history.length < 3) return [];

    const anomalies: Array<{
      type: 'spike' | 'drop';
      date: Date;
      value: number;
      change: number;
      changePercent: number;
    }> = [];

    for (let i = 1; i < history.length; i++) {
      const prev = history[i - 1];
      const curr = history[i];

      const prevValue = metric === 'subscribers' ? prev.subscriberCount : prev.totalViews;
      const currValue = metric === 'subscribers' ? curr.subscriberCount : curr.totalViews;

      const change = currValue - prevValue;
      const changePercent = prevValue > 0 ? (change / prevValue) * 100 : 0;

      // Detect significant changes (>50% increase or >30% decrease)
      if (changePercent > 50) {
        anomalies.push({
          type: 'spike',
          date: new Date(curr.timestamp),
          value: currValue,
          change,
          changePercent,
        });
      } else if (changePercent < -30) {
        anomalies.push({
          type: 'drop',
          date: new Date(curr.timestamp),
          value: currValue,
          change,
          changePercent,
        });
      }
    }

    return anomalies;
  };

  const anomalies = detectAnomalies();

  if (anomalies.length === 0) {
    return null;
  }

  return (
    <Alert severity="warning" sx={{ mb: 2 }}>
      <AlertTitle>Notable Changes Detected</AlertTitle>
      {anomalies.slice(0, 3).map((anomaly, idx) => (
        <Box key={idx} sx={{ mt: 1 }}>
          <Box display="flex" alignItems="center" gap={1}>
            {anomaly.type === 'spike' ? (
              <TrendingUp fontSize="small" color="success" />
            ) : (
              <TrendingDown fontSize="small" color="error" />
            )}
            <Typography variant="body2">
              {anomaly.type === 'spike' ? 'Spike' : 'Drop'} on{' '}
              {anomaly.date.toLocaleDateString()}: {anomaly.changePercent.toFixed(1)}% change
            </Typography>
          </Box>
        </Box>
      ))}
      {anomalies.length > 3 && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          +{anomalies.length - 3} more anomalies
        </Typography>
      )}
    </Alert>
  );
}
