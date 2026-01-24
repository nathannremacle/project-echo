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
  Grid,
} from '@mui/material';
import { Edit, Delete, Add } from '@mui/icons-material';
import { useState } from 'react';
import { TransformationPreset } from '../../services/settings';

interface EffectPresetsManagementProps {
  presets: TransformationPreset[];
  onCreate: (preset: Omit<TransformationPreset, 'id' | 'createdAt' | 'updatedAt'>) => void;
  onUpdate: (id: string, preset: Partial<TransformationPreset>) => void;
  onDelete: (id: string) => void;
}

export default function EffectPresetsManagement({
  presets,
  onCreate,
  onUpdate,
  onDelete,
}: EffectPresetsManagementProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPreset, setEditingPreset] = useState<TransformationPreset | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    effects: {
      brightness: 0,
      contrast: 0,
      saturation: 0,
      hue: 0,
      blur: 0,
      sharpen: 0,
      noise: 0,
    },
  });

  const handleOpenCreate = () => {
    setEditingPreset(null);
    setFormData({
      name: '',
      description: '',
      effects: {
        brightness: 0,
        contrast: 0,
        saturation: 0,
        hue: 0,
        blur: 0,
        sharpen: 0,
        noise: 0,
      },
    });
    setDialogOpen(true);
  };

  const handleOpenEdit = (preset: TransformationPreset) => {
    setEditingPreset(preset);
    setFormData({
      name: preset.name,
      description: preset.description || '',
      effects: preset.effects,
    });
    setDialogOpen(true);
  };

  const handleSave = () => {
    if (!formData.name) return;

    if (editingPreset) {
      onUpdate(editingPreset.id, formData);
    } else {
      onCreate(formData);
    }
    setDialogOpen(false);
  };

  const handleEffectChange = (key: string, value: number) => {
    setFormData((prev) => ({
      ...prev,
      effects: {
        ...prev.effects,
        [key]: value,
      },
    }));
  };

  return (
    <>
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Effect Presets Library</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleOpenCreate}
              size="small"
            >
              Create Preset
            </Button>
          </Box>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Effects</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {presets.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No presets created yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  presets.map((preset) => (
                    <TableRow key={preset.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {preset.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {preset.description || 'No description'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {Object.entries(preset.effects)
                            .filter(([_, v]) => v !== 0)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(', ') || 'No effects'}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenEdit(preset)}
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => onDelete(preset.id)}
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

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editingPreset ? 'Edit Preset' : 'Create Preset'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Preset Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={2}
              sx={{ mb: 2 }}
            />

            <Typography variant="subtitle2" gutterBottom>
              Effects
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Brightness"
                  type="number"
                  value={formData.effects.brightness}
                  onChange={(e) => handleEffectChange('brightness', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: -1, max: 1 }}
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Contrast"
                  type="number"
                  value={formData.effects.contrast}
                  onChange={(e) => handleEffectChange('contrast', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: -1, max: 1 }}
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Saturation"
                  type="number"
                  value={formData.effects.saturation}
                  onChange={(e) => handleEffectChange('saturation', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: -1, max: 1 }}
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Hue"
                  type="number"
                  value={formData.effects.hue}
                  onChange={(e) => handleEffectChange('hue', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: -180, max: 180 }}
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Blur"
                  type="number"
                  value={formData.effects.blur}
                  onChange={(e) => handleEffectChange('blur', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: 0, max: 10 }}
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Sharpen"
                  type="number"
                  value={formData.effects.sharpen}
                  onChange={(e) => handleEffectChange('sharpen', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: 0, max: 10 }}
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <TextField
                  fullWidth
                  label="Noise"
                  type="number"
                  value={formData.effects.noise}
                  onChange={(e) => handleEffectChange('noise', parseFloat(e.target.value) || 0)}
                  inputProps={{ step: 0.1, min: 0, max: 1 }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={!formData.name}>
            {editingPreset ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
