import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Paper,
} from '@mui/material';
import { Save, SelectAll } from '@mui/icons-material';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { creatorAttributionService } from '../../services/creatorAttribution';

interface VideoAttributionProps {
  videoIds?: string[];
  onSuccess?: () => void;
}

export default function VideoAttribution({ videoIds, onSuccess }: VideoAttributionProps) {
  const [creatorName, setCreatorName] = useState('');
  const [creatorChannel, setCreatorChannel] = useState('');
  const [selectedVideos, setSelectedVideos] = useState<string[]>(videoIds || []);

  const queryClient = useQueryClient();

  // Single video attribution mutation
  const attributeMutation = useMutation({
    mutationFn: ({ videoId, name, channel }: { videoId: string; name: string; channel?: string }) =>
      creatorAttributionService.attributeVideo(videoId, name, channel),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['creators-list'] });
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      onSuccess?.();
    },
  });

  // Bulk attribution mutation
  const bulkAttributeMutation = useMutation({
    mutationFn: ({ videoIds, name, channel }: { videoIds: string[]; name: string; channel?: string }) =>
      creatorAttributionService.bulkAttributeVideos(videoIds, name, channel),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['creators-list'] });
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      onSuccess?.();
    },
  });

  const handleSave = () => {
    if (!creatorName.trim()) {
      return;
    }

    if (selectedVideos.length === 0) {
      return;
    }

    if (selectedVideos.length === 1) {
      attributeMutation.mutate({
        videoId: selectedVideos[0],
        name: creatorName,
        channel: creatorChannel || undefined,
      });
    } else {
      bulkAttributeMutation.mutate({
        videoIds: selectedVideos,
        name: creatorName,
        channel: creatorChannel || undefined,
      });
    }
  };

  const handleSelectAll = () => {
    if (selectedVideos.length === (videoIds?.length || 0)) {
      setSelectedVideos([]);
    } else {
      setSelectedVideos(videoIds || []);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {selectedVideos.length > 1 ? 'Bulk Attribution' : 'Video Attribution'}
        </Typography>

        <Box display="flex" flexDirection="column" gap={2}>
          <TextField
            label="Creator Name"
            value={creatorName}
            onChange={(e) => setCreatorName(e.target.value)}
            required
            fullWidth
          />

          <TextField
            label="Creator Channel URL (optional)"
            value={creatorChannel}
            onChange={(e) => setCreatorChannel(e.target.value)}
            fullWidth
            placeholder="https://youtube.com/@creator"
          />

          {videoIds && videoIds.length > 1 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2">Select Videos ({selectedVideos.length} selected)</Typography>
                <Button
                  size="small"
                  startIcon={<SelectAll />}
                  onClick={handleSelectAll}
                >
                  {selectedVideos.length === videoIds.length ? 'Deselect All' : 'Select All'}
                </Button>
              </Box>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedVideos.length === videoIds.length && videoIds.length > 0}
                          indeterminate={selectedVideos.length > 0 && selectedVideos.length < videoIds.length}
                          onChange={handleSelectAll}
                        />
                      </TableCell>
                      <TableCell>Video ID</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {videoIds.map((videoId) => (
                      <TableRow key={videoId}>
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedVideos.includes(videoId)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedVideos([...selectedVideos, videoId]);
                              } else {
                                setSelectedVideos(selectedVideos.filter((id) => id !== videoId));
                              }
                            }}
                          />
                        </TableCell>
                        <TableCell>{videoId}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSave}
            disabled={!creatorName.trim() || selectedVideos.length === 0}
          >
            Save Attribution
          </Button>

          {attributeMutation.isSuccess && (
            <Alert severity="success">Attribution saved successfully!</Alert>
          )}

          {attributeMutation.isError && (
            <Alert severity="error">
              Failed to save attribution: {attributeMutation.error?.message}
            </Alert>
          )}

          {bulkAttributeMutation.isSuccess && (
            <Alert severity="success">
              {bulkAttributeMutation.data.updated.length} video(s) updated successfully!
            </Alert>
          )}

          {bulkAttributeMutation.isError && (
            <Alert severity="error">
              Failed to save attribution: {bulkAttributeMutation.error?.message}
            </Alert>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
