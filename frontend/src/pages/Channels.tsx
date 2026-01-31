import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { Add, VideoLibrary } from '@mui/icons-material';
import { useState } from 'react';
import { channelService, Channel, ChannelCreate } from '../services/channels';

export default function Channels() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const action = searchParams.get('action');
  const queryClient = useQueryClient();
  const [addOpen, setAddOpen] = useState(action === 'create');
  const [formData, setFormData] = useState<ChannelCreate>({
    name: '',
    youtubeChannelId: '',
    youtubeChannelUrl: '',
    isActive: true,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['channels'],
    queryFn: () => channelService.getChannels(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: ChannelCreate) => channelService.createChannel(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['channels'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setAddOpen(false);
      setFormData({ name: '', youtubeChannelId: '', youtubeChannelUrl: '', isActive: true });
    },
  });

  const handleAddChannel = () => {
    if (!formData.name.trim() || !formData.youtubeChannelId.trim()) return;
    createMutation.mutate({
      name: formData.name.trim(),
      youtubeChannelId: formData.youtubeChannelId.trim(),
      youtubeChannelUrl: formData.youtubeChannelUrl?.trim() || undefined,
      isActive: formData.isActive,
    });
  };

  const handleAddTestChannel = () => {
    setFormData({
      name: 'Chaîne de test',
      youtubeChannelId: 'UC_test_channel_' + Date.now().toString(36),
      youtubeChannelUrl: '',
      isActive: true,
    });
    setAddOpen(true);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Erreur lors du chargement des chaînes : {error instanceof Error ? error.message : 'Erreur inconnue'}
      </Alert>
    );
  }

  const channels = data?.channels ?? [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Chaînes</Typography>
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<Add />} onClick={handleAddTestChannel}>
            Ajouter une chaîne de test
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => setAddOpen(true)}>
            Ajouter une chaîne
          </Button>
        </Box>
      </Box>

      {channels.length === 0 ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          Aucune chaîne configurée. Cliquez sur « Ajouter une chaîne de test » pour créer une chaîne d'exemple,
          ou « Ajouter une chaîne » pour en configurer une avec vos identifiants YouTube.
        </Alert>
      ) : null}

      <Grid container spacing={2}>
        {channels.map((channel) => (
          <Grid item xs={12} sm={6} md={4} key={channel.id}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                '&:hover': { boxShadow: 4 },
              }}
              onClick={() => navigate(`/channels/${channel.id}`)}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6">{channel.name}</Typography>
                  <Chip
                    label={channel.isActive ? 'Active' : 'Inactive'}
                    color={channel.isActive ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                <Box display="flex" alignItems="center" gap={1} color="text.secondary">
                  <VideoLibrary fontSize="small" />
                  <Typography variant="body2">{channel.youtubeChannelId}</Typography>
                </Box>
                {channel.youtubeChannelUrl && (
                  <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
                    {channel.youtubeChannelUrl}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={addOpen} onClose={() => setAddOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Ajouter une chaîne</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <TextField
              label="Nom de la chaîne"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              fullWidth
            />
            <TextField
              label="YouTube Channel ID"
              value={formData.youtubeChannelId}
              onChange={(e) => setFormData({ ...formData, youtubeChannelId: e.target.value })}
              placeholder="UC..."
              required
              fullWidth
              helperText="Ex: UCxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            />
            <TextField
              label="URL YouTube (optionnel)"
              value={formData.youtubeChannelUrl || ''}
              onChange={(e) => setFormData({ ...formData, youtubeChannelUrl: e.target.value })}
              placeholder="https://www.youtube.com/channel/UC..."
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)}>Annuler</Button>
          <Button
            variant="contained"
            onClick={handleAddChannel}
            disabled={!formData.name.trim() || !formData.youtubeChannelId.trim() || createMutation.isPending}
          >
            {createMutation.isPending ? 'Création...' : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
