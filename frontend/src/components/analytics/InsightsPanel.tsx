import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  Alert,
} from '@mui/material';
import { Insight } from '../../services/enhancedAnalytics';

interface InsightsPanelProps {
  insights: Insight[];
}

export default function InsightsPanel({ insights }: InsightsPanelProps) {
  if (insights.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Key Insights
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No insights available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Key Insights
        </Typography>

        <List>
          {insights.map((insight, index) => (
            <ListItem key={index} sx={{ px: 0 }}>
              <Alert
                severity={insight.type === 'success' ? 'success' : insight.type === 'warning' ? 'warning' : 'info'}
                sx={{ width: '100%' }}
              >
                <Typography variant="subtitle2">{insight.title}</Typography>
                <Typography variant="body2">{insight.message}</Typography>
              </Alert>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}
