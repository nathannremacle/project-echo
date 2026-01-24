import { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Divider,
  Grid,
  Alert,
} from '@mui/material';
import { Save, Cancel, Edit } from '@mui/icons-material';
import { Channel, ChannelUpdate, PostingSchedule, ContentFilters, MetadataTemplate } from '../../services/channels';

interface ChannelConfigurationProps {
  channel: Channel;
  onSave: (updates: ChannelUpdate) => Promise<void>;
  onCancel?: () => void;
}

export default function ChannelConfiguration({ channel, onSave, onCancel }: ChannelConfigurationProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState(channel.name);
  const [postingSchedule, setPostingSchedule] = useState<PostingSchedule>(channel.postingSchedule);
  const [contentFilters, setContentFilters] = useState<ContentFilters>(channel.contentFilters);
  const [metadataTemplate, setMetadataTemplate] = useState<MetadataTemplate>(channel.metadataTemplate);
  const [effectPresetId, setEffectPresetId] = useState(channel.effectPresetId || '');

  const handleSave = async () => {
    setError(null);
    setIsSaving(true);

    try {
      const updates: ChannelUpdate = {
        name,
        postingSchedule,
        contentFilters,
        metadataTemplate,
        effectPresetId: effectPresetId || undefined,
      };

      await onSave(updates);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setName(channel.name);
    setPostingSchedule(channel.postingSchedule);
    setContentFilters(channel.contentFilters);
    setMetadataTemplate(channel.metadataTemplate);
    setEffectPresetId(channel.effectPresetId || '');
    setError(null);
    setIsEditing(false);
    onCancel?.();
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Configuration</Typography>
          {!isEditing && (
            <Button
              startIcon={<Edit />}
              onClick={() => setIsEditing(true)}
              size="small"
            >
              Edit
            </Button>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Channel Name */}
          <TextField
            label="Channel Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={!isEditing}
            fullWidth
            required
          />

          {/* Posting Schedule */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Posting Schedule
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth disabled={!isEditing}>
                  <InputLabel>Frequency</InputLabel>
                  <Select
                    value={postingSchedule.frequency}
                    label="Frequency"
                    onChange={(e) =>
                      setPostingSchedule({
                        ...postingSchedule,
                        frequency: e.target.value as 'daily' | 'weekly' | 'custom',
                      })
                    }
                  >
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="custom">Custom</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Timezone"
                  value={postingSchedule.timezone}
                  onChange={(e) =>
                    setPostingSchedule({ ...postingSchedule, timezone: e.target.value })
                  }
                  disabled={!isEditing}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Preferred Times (comma-separated, 24h format)"
                  value={postingSchedule.preferredTimes.join(', ')}
                  onChange={(e) =>
                    setPostingSchedule({
                      ...postingSchedule,
                      preferredTimes: e.target.value.split(',').map((t) => t.trim()),
                    })
                  }
                  disabled={!isEditing}
                  fullWidth
                  placeholder="10:00, 18:00"
                />
              </Grid>
            </Grid>
          </Box>

          <Divider />

          {/* Content Filters */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Content Filters
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth disabled={!isEditing}>
                  <InputLabel>Min Resolution</InputLabel>
                  <Select
                    value={contentFilters.minResolution}
                    label="Min Resolution"
                    onChange={(e) =>
                      setContentFilters({
                        ...contentFilters,
                        minResolution: e.target.value as '720p' | '1080p' | '1440p' | '2160p',
                      })
                    }
                  >
                    <MenuItem value="720p">720p</MenuItem>
                    <MenuItem value="1080p">1080p</MenuItem>
                    <MenuItem value="1440p">1440p</MenuItem>
                    <MenuItem value="2160p">2160p</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Min Views"
                  type="number"
                  value={contentFilters.minViews || ''}
                  onChange={(e) =>
                    setContentFilters({
                      ...contentFilters,
                      minViews: e.target.value ? parseInt(e.target.value, 10) : undefined,
                    })
                  }
                  disabled={!isEditing}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={contentFilters.excludeWatermarked}
                      onChange={(e) =>
                        setContentFilters({
                          ...contentFilters,
                          excludeWatermarked: e.target.checked,
                        })
                      }
                      disabled={!isEditing}
                    />
                  }
                  label="Exclude Watermarked Videos"
                />
              </Grid>
            </Grid>
          </Box>

          <Divider />

          {/* Metadata Template */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Metadata Template
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  label="Title Template"
                  value={metadataTemplate.titleTemplate}
                  onChange={(e) =>
                    setMetadataTemplate({
                      ...metadataTemplate,
                      titleTemplate: e.target.value,
                    })
                  }
                  disabled={!isEditing}
                  fullWidth
                  multiline
                  rows={2}
                  placeholder="{{video_title}} | Edit"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description Template"
                  value={metadataTemplate.descriptionTemplate}
                  onChange={(e) =>
                    setMetadataTemplate({
                      ...metadataTemplate,
                      descriptionTemplate: e.target.value,
                    })
                  }
                  disabled={!isEditing}
                  fullWidth
                  multiline
                  rows={4}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Default Tags (comma-separated)"
                  value={metadataTemplate.defaultTags.join(', ')}
                  onChange={(e) =>
                    setMetadataTemplate({
                      ...metadataTemplate,
                      defaultTags: e.target.value.split(',').map((t) => t.trim()).filter(Boolean),
                    })
                  }
                  disabled={!isEditing}
                  fullWidth
                  placeholder="edit, shorts, viral"
                />
              </Grid>
            </Grid>
          </Box>

          {/* Action Buttons */}
          {isEditing && (
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button
                startIcon={<Cancel />}
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={handleSave}
                disabled={isSaving}
              >
                Save
              </Button>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
