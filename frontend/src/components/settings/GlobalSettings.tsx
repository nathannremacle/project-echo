import {
  Card,
  CardContent,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Box,
  Grid,
  Alert,
} from '@mui/material';
import { Save, Restore } from '@mui/icons-material';
import { useState } from 'react';
import { SystemConfiguration } from '../../services/settings';

interface GlobalSettingsProps {
  configs: SystemConfiguration[];
  onSave: (updates: Array<{ key: string; value: any }>) => void;
  onReset: () => void;
}

export default function GlobalSettings({ configs, onSave, onReset }: GlobalSettingsProps) {
  const [formData, setFormData] = useState<Record<string, any>>(() => {
    const initial: Record<string, any> = {};
    configs.forEach((config) => {
      initial[config.key] = config.value;
    });
    return initial;
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (key: string, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    // Clear error for this field
    if (errors[key]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
  };

  const handleSave = () => {
    const updates: Array<{ key: string; value: any }> = [];
    const newErrors: Record<string, string> = {};

    // Validate and collect updates
    Object.entries(formData).forEach(([key, value]) => {
      const config = configs.find((c) => c.key === key);
      if (!config) return;

      // Basic validation
      if (value === undefined || value === null || value === '') {
        newErrors[key] = 'This field is required';
        return;
      }

      updates.push({ key, value });
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSave(updates);
  };

  const handleReset = () => {
    const initial: Record<string, any> = {};
    configs.forEach((config) => {
      initial[config.key] = config.value;
    });
    setFormData(initial);
    setErrors({});
    onReset();
  };

  const getConfigValue = (key: string) => {
    return formData[key] ?? configs.find((c) => c.key === key)?.value;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Global Default Settings</Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              startIcon={<Restore />}
              onClick={handleReset}
              size="small"
            >
              Reset to Defaults
            </Button>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              size="small"
            >
              Save Changes
            </Button>
          </Box>
        </Box>

        {Object.keys(errors).length > 0 && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Please fix the errors before saving.
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Default Effect Preset */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Default Effect Preset</InputLabel>
              <Select
                value={getConfigValue('default_effect_preset') || ''}
                label="Default Effect Preset"
                onChange={(e) => handleChange('default_effect_preset', e.target.value)}
                error={!!errors['default_effect_preset']}
              >
                <MenuItem value="">None</MenuItem>
                {/* Presets would be loaded from API */}
              </Select>
            </FormControl>
          </Grid>

          {/* Video Quality */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Default Video Quality</InputLabel>
              <Select
                value={getConfigValue('default_video_quality') || '1080p'}
                label="Default Video Quality"
                onChange={(e) => handleChange('default_video_quality', e.target.value)}
                error={!!errors['default_video_quality']}
              >
                <MenuItem value="720p">720p</MenuItem>
                <MenuItem value="1080p">1080p</MenuItem>
                <MenuItem value="1440p">1440p</MenuItem>
                <MenuItem value="2160p">2160p (4K)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Processing Quality */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Processing Quality</InputLabel>
              <Select
                value={getConfigValue('processing_quality') || 'high'}
                label="Processing Quality"
                onChange={(e) => handleChange('processing_quality', e.target.value)}
                error={!!errors['processing_quality']}
              >
                <MenuItem value="low">Low (Faster)</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High (Slower)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Auto-publish */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Auto-publish After Processing</InputLabel>
              <Select
                value={getConfigValue('auto_publish') || 'false'}
                label="Auto-publish After Processing"
                onChange={(e) => handleChange('auto_publish', e.target.value)}
                error={!!errors['auto_publish']}
              >
                <MenuItem value="true">Yes</MenuItem>
                <MenuItem value="false">No</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
