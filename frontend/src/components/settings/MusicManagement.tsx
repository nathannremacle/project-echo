import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { Upload, Delete, Add } from '@mui/icons-material';
import { useState } from 'react';
import { MusicTrack } from '../../services/settings';

interface MusicManagementProps {
  tracks: MusicTrack[];
  onUpload: (file: File, metadata: { name: string; artist: string; spotifyUrl?: string }) => void;
  onDelete: (id: string) => void;
}

export default function MusicManagement({ tracks, onUpload, onDelete }: MusicManagementProps) {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadMetadata, setUploadMetadata] = useState({
    name: '',
    artist: '',
    spotifyUrl: '',
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadFile(file);
    }
  };

  const handleUpload = () => {
    if (uploadFile && uploadMetadata.name && uploadMetadata.artist) {
      onUpload(uploadFile, {
        name: uploadMetadata.name,
        artist: uploadMetadata.artist,
        spotifyUrl: uploadMetadata.spotifyUrl || undefined,
      });
      setUploadDialogOpen(false);
      setUploadFile(null);
      setUploadMetadata({ name: '', artist: '', spotifyUrl: '' });
    }
  };

  return (
    <>
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Music Management</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setUploadDialogOpen(true)}
              size="small"
            >
              Upload Music
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload your personal music tracks for Phase 2 (music replacement feature).
          </Typography>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Artist</TableCell>
                  <TableCell>Spotify URL</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tracks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No music tracks uploaded yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  tracks.map((track) => (
                    <TableRow key={track.id}>
                      <TableCell>
                        <Typography variant="body2">{track.name}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{track.artist}</Typography>
                      </TableCell>
                      <TableCell>
                        {track.spotifyUrl ? (
                          <Typography variant="caption" color="primary">
                            {track.spotifyUrl}
                          </Typography>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            Not set
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(track.uploadedAt).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => onDelete(track.id)}
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Music Track</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <input
              accept="audio/*"
              style={{ display: 'none' }}
              id="music-upload-input"
              type="file"
              onChange={handleFileSelect}
            />
            <label htmlFor="music-upload-input">
              <Button variant="outlined" component="span" startIcon={<Upload />} fullWidth sx={{ mb: 2 }}>
                {uploadFile ? uploadFile.name : 'Select Audio File'}
              </Button>
            </label>

            <TextField
              fullWidth
              label="Track Name"
              value={uploadMetadata.name}
              onChange={(e) => setUploadMetadata({ ...uploadMetadata, name: e.target.value })}
              required
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Artist"
              value={uploadMetadata.artist}
              onChange={(e) => setUploadMetadata({ ...uploadMetadata, artist: e.target.value })}
              required
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Spotify URL (optional)"
              value={uploadMetadata.spotifyUrl}
              onChange={(e) => setUploadMetadata({ ...uploadMetadata, spotifyUrl: e.target.value })}
              placeholder="https://open.spotify.com/track/..."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!uploadFile || !uploadMetadata.name || !uploadMetadata.artist}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
