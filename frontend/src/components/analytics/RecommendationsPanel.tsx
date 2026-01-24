import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  Button,
  Chip,
} from '@mui/material';
import { Lightbulb, PlayArrow } from '@mui/icons-material';
import { Recommendation } from '../../services/enhancedAnalytics';

interface RecommendationsPanelProps {
  recommendations: Recommendation[];
}

export default function RecommendationsPanel({ recommendations }: RecommendationsPanelProps) {
  if (recommendations.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No recommendations at this time
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recommendations
        </Typography>

        <List>
          {recommendations.map((rec, index) => (
            <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start', px: 0, pb: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                {rec.type === 'action' ? <PlayArrow color="primary" /> : <Lightbulb color="warning" />}
                <Typography variant="subtitle2">{rec.title}</Typography>
                <Chip
                  label={rec.type === 'action' ? 'Action' : 'Suggestion'}
                  size="small"
                  color={rec.type === 'action' ? 'primary' : 'default'}
                />
              </Box>
              <Typography variant="body2" color="text.secondary" mb={1}>
                {rec.message}
              </Typography>
              {rec.type === 'action' && (
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    // Handle action
                    console.log('Action:', rec.action, rec.channels);
                  }}
                >
                  Take Action
                </Button>
              )}
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}
