import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import { PlayArrow, Add } from '@mui/icons-material';
import { orchestrationService } from '../../services/orchestration';

interface ChannelPipelineActionsProps {
  channelId: string;
}

export default function ChannelPipelineActions({ channelId }: ChannelPipelineActionsProps) {
  const queryClient = useQueryClient();
  const [addVideoOpen, setAddVideoOpen] = useState(false);
  const [sourceUrl, setSourceUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  const triggerMutation = useMutation({
    mutationFn: (params: { source_url?: string }) =>
      orchestrationService.triggerPipeline({
        channel_id: channelId,
        source_url: params.source_url,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['queue-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['queue-videos'] });
      setAddVideoOpen(false);
      setSourceUrl('');
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleLancerPipeline = () => {
    setError(null);
    triggerMutation.mutate({});
  };

  const handleAddVideo = () => {
    if (!sourceUrl.trim()) {
      setError('Veuillez entrer une URL de vidéo (YouTube, etc.)');
      return;
    }
    setError(null);
    triggerMutation.mutate({ source_url: sourceUrl.trim() });
  };

  const handleCloseAddVideo = () => {
    setAddVideoOpen(false);
    setSourceUrl('');
    setError(null);
  };

  return (
    <Box display="flex" flexDirection="column" gap={2}>
      <Box display="flex" gap={2} flexWrap="wrap">
        <Button
          variant="contained"
          startIcon={<PlayArrow />}
          onClick={handleLancerPipeline}
          disabled={triggerMutation.isPending}
        >
          {triggerMutation.isPending ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              En cours...
            </>
          ) : (
            'Lancer le pipeline'
          )}
        </Button>
        <Button
          variant="outlined"
          startIcon={<Add />}
          onClick={() => setAddVideoOpen(true)}
          disabled={triggerMutation.isPending}
        >
          Ajouter une vidéo (URL)
        </Button>
      </Box>

      <Dialog open={addVideoOpen} onClose={handleCloseAddVideo} maxWidth="sm" fullWidth>
        <DialogTitle>Ajouter une vidéo à scraper</DialogTitle>
        <DialogContent>
          <Box pt={2}>
            <TextField
              fullWidth
              label="URL de la vidéo"
              placeholder="https://www.youtube.com/watch?v=..."
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              helperText="Collez l'URL d'une vidéo YouTube (ou autre source supportée)"
              sx={{ mb: 2 }}
            />
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddVideo}>Annuler</Button>
          <Button variant="contained" onClick={handleAddVideo} disabled={triggerMutation.isPending}>
            {triggerMutation.isPending ? 'En cours...' : 'Scraper et lancer le pipeline'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
