import { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  Alert,
  Collapse,
  IconButton,
  InputAdornment,
} from '@mui/material';
import { Save, ExpandMore, ExpandLess, Visibility, VisibilityOff } from '@mui/icons-material';
import { channelService } from '../../services/channels';

interface ChannelCredentialsProps {
  channelId: string;
  onSuccess?: () => void;
  onError?: (message: string) => void;
}

export default function ChannelCredentials({
  channelId,
  onSuccess,
  onError,
}: ChannelCredentialsProps) {
  const [expanded, setExpanded] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showSecret, setShowSecret] = useState(false);
  const [showToken, setShowToken] = useState(false);

  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [refreshToken, setRefreshToken] = useState('');

  const handleSave = async () => {
    if (!clientId.trim() || !clientSecret.trim() || !refreshToken.trim()) {
      setError('Tous les champs sont requis');
      return;
    }

    setError(null);
    setSuccess(false);
    setIsSaving(true);

    try {
      await channelService.updateCredentials(channelId, {
        clientId: clientId.trim(),
        clientSecret: clientSecret.trim(),
        refreshToken: refreshToken.trim(),
      });
      setSuccess(true);
      setClientId('');
      setClientSecret('');
      setRefreshToken('');
      onSuccess?.();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err instanceof Error ? err.message : 'Échec de la sauvegarde');
      setError(String(message));
      onError?.(String(message));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          sx={{ cursor: 'pointer' }}
          onClick={() => setExpanded(!expanded)}
        >
          <Typography variant="h6">Credentials YouTube OAuth</Typography>
          <IconButton size="small">
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Configurez les credentials OAuth 2.0 pour publier des vidéos sur cette chaîne YouTube.
          Obtenez-les via Google Cloud Console et le script setup_youtube_oauth.py.
        </Typography>

        <Collapse in={expanded}>
          <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" onClose={() => setSuccess(false)}>
                Credentials enregistrés avec succès.
              </Alert>
            )}

            <TextField
              label="Client ID"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              fullWidth
              placeholder="xxx.apps.googleusercontent.com"
              helperText="Depuis Google Cloud Console > Credentials > OAuth 2.0 Client ID"
            />

            <TextField
              label="Client Secret"
              type={showSecret ? 'text' : 'password'}
              value={clientSecret}
              onChange={(e) => setClientSecret(e.target.value)}
              fullWidth
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowSecret(!showSecret)}
                      edge="end"
                      size="small"
                    >
                      {showSecret ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Box>
              <TextField
                label="Refresh Token"
                type={showToken ? 'text' : 'password'}
                value={refreshToken}
                onChange={(e) => setRefreshToken(e.target.value)}
                fullWidth
                multiline
                rows={2}
                placeholder="1//xxx..."
                helperText="Obtenu via: python backend/scripts/setup_youtube_oauth.py credentials.json"
              />
              <Button
                size="small"
                startIcon={showToken ? <VisibilityOff /> : <Visibility />}
                onClick={() => setShowToken(!showToken)}
                sx={{ mt: 0.5 }}
              >
                {showToken ? 'Masquer' : 'Afficher'}
              </Button>
            </Box>

            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              disabled={isSaving || !clientId.trim() || !clientSecret.trim() || !refreshToken.trim()}
            >
              {isSaving ? 'Enregistrement...' : 'Enregistrer les credentials'}
            </Button>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
}
