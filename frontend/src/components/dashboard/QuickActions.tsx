import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Stack,
} from '@mui/material';
import {
  Add,
  MusicNote,
  Description,
} from '@mui/icons-material';

export default function QuickActions() {
  const navigate = useNavigate();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Stack spacing={2}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/channels?action=create')}
            fullWidth
          >
            Add New Channel
          </Button>
          <Button
            variant="outlined"
            startIcon={<MusicNote />}
            onClick={() => {
              // TODO: Implement phase 2 trigger
              console.log('Trigger Phase 2');
            }}
            fullWidth
          >
            Trigger Phase 2
          </Button>
          <Button
            variant="outlined"
            startIcon={<Description />}
            onClick={() => navigate('/settings?tab=logs')}
            fullWidth
          >
            View Logs
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
