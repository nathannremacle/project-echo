import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Alert,
} from '@mui/material';
import { Save } from '@mui/icons-material';
import { useState } from 'react';
import { SystemConfiguration } from '../../services/settings';

interface ProcessingSettingsProps {
  configs: SystemConfiguration[];
  onSave: (updates: Array<{ key: string; value: any }>) => void;
}

export default function ProcessingSettings({ configs, onSave }: ProcessingSettingsProps) {
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

    // Validate
    const queueSize = parseInt(formData['queue_max_size'] || '0', 10);
    if (isNaN(queueSize) || queueSize < 1 || queueSize > 10000) {
      newErrors['queue_max_size'] = 'Queue size must be between 1 and 10000';
    }

    const parallelLimit = parseInt(formData['parallel_processing_limit'] || '0', 10);
    if (isNaN(parallelLimit) || parallelLimit < 1 || parallelLimit > 10) {
      newErrors['parallel_processing_limit'] = 'Parallel limit must be between 1 and 10';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Collect updates
    Object.entries(formData).forEach(([key, value]) => {
      const config = configs.find((c) => c.key === key);
      if (!config) return;
      updates.push({ key, value });
    });

    onSave(updates);
  };

  const getConfigValue = (key: string, defaultValue: any = '') => {
    return formData[key] ?? configs.find((c) => c.key === key)?.value ?? defaultValue;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Processing Settings</Typography>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSave}
            size="small"
          >
            Save Changes
          </Button>
        </Box>

        {Object.keys(errors).length > 0 && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Please fix the errors before saving.
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Queue Max Size"
              type="number"
              value={getConfigValue('queue_max_size', 100)}
              onChange={(e) => handleChange('queue_max_size', e.target.value)}
              error={!!errors['queue_max_size']}
              helperText={errors['queue_max_size'] || 'Maximum number of jobs in the processing queue (1-10000)'}
              inputProps={{ min: 1, max: 10000 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Parallel Processing Limit"
              type="number"
              value={getConfigValue('parallel_processing_limit', 2)}
              onChange={(e) => handleChange('parallel_processing_limit', e.target.value)}
              error={!!errors['parallel_processing_limit']}
              helperText={errors['parallel_processing_limit'] || 'Maximum number of videos to process simultaneously (1-10)'}
              inputProps={{ min: 1, max: 10 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Retry Attempts"
              type="number"
              value={getConfigValue('processing_retry_attempts', 3)}
              onChange={(e) => handleChange('processing_retry_attempts', e.target.value)}
              helperText="Number of retry attempts for failed processing jobs"
              inputProps={{ min: 0, max: 10 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Retry Delay (seconds)"
              type="number"
              value={getConfigValue('processing_retry_delay', 60)}
              onChange={(e) => handleChange('processing_retry_delay', e.target.value)}
              helperText="Delay between retry attempts in seconds"
              inputProps={{ min: 1 }}
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
