import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import { settingsService, SettingsUpdate } from '../services/settings';
import GlobalSettings from '../components/settings/GlobalSettings';
import SystemInformation from '../components/settings/SystemInformation';
import ProcessingSettings from '../components/settings/ProcessingSettings';
import MusicManagement from '../components/settings/MusicManagement';
import EffectPresetsManagement from '../components/settings/EffectPresetsManagement';
import BackupRestore from '../components/settings/BackupRestore';
import Phase2Activation from '../components/phase2/Phase2Activation';
import Phase2Status from '../components/phase2/Phase2Status';
import CreatorList from '../components/creatorAttribution/CreatorList';
import VideoAttribution from '../components/creatorAttribution/VideoAttribution';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Settings() {
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const queryClient = useQueryClient();

  // Fetch system configuration
  const { data: configs, isLoading: isLoadingConfigs } = useQuery({
    queryKey: ['system-config'],
    queryFn: () => settingsService.getConfiguration(),
  });

  // Fetch system health
  const { data: health } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => settingsService.getSystemHealth(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch Phase 2 status
  const { data: phase2Status } = useQuery({
    queryKey: ['phase2-status'],
    queryFn: async () => {
      const { phase2Service } = await import('../services/phase2');
      return phase2Service.getStatus();
    },
    refetchInterval: 30000,
  });

  // Fetch presets
  const { data: presets } = useQuery({
    queryKey: ['transformation-presets'],
    queryFn: () => settingsService.getPresets(),
  });

  // Fetch music tracks
  const { data: musicTracks } = useQuery({
    queryKey: ['music-tracks'],
    queryFn: () => settingsService.getMusicTracks(),
  });

  // Update configuration mutation
  const updateConfigMutation = useMutation({
    mutationFn: async (updates: SettingsUpdate[]) => {
      await Promise.all(
        updates.map((update) => settingsService.updateConfiguration(update))
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-config'] });
      setSnackbar({ open: true, message: 'Settings saved successfully', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to save settings', severity: 'error' });
    },
  });

  // Preset mutations
  const createPresetMutation = useMutation({
    mutationFn: settingsService.createPreset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transformation-presets'] });
      setSnackbar({ open: true, message: 'Preset created successfully', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to create preset', severity: 'error' });
    },
  });

  const updatePresetMutation = useMutation({
    mutationFn: ({ id, preset }: { id: string; preset: any }) =>
      settingsService.updatePreset(id, preset),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transformation-presets'] });
      setSnackbar({ open: true, message: 'Preset updated successfully', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to update preset', severity: 'error' });
    },
  });

  const deletePresetMutation = useMutation({
    mutationFn: settingsService.deletePreset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transformation-presets'] });
      setSnackbar({ open: true, message: 'Preset deleted successfully', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to delete preset', severity: 'error' });
    },
  });

  // Music mutations
  const uploadMusicMutation = useMutation({
    mutationFn: ({ file, metadata }: { file: File; metadata: any }) =>
      settingsService.uploadMusic(file, metadata),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['music-tracks'] });
      setSnackbar({ open: true, message: 'Music uploaded successfully', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to upload music', severity: 'error' });
    },
  });

  const deleteMusicMutation = useMutation({
    mutationFn: settingsService.deleteMusic,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['music-tracks'] });
      setSnackbar({ open: true, message: 'Music deleted successfully', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to delete music', severity: 'error' });
    },
  });

  const handleConfigSave = (updates: Array<{ key: string; value: any }>) => {
    updateConfigMutation.mutate(
      updates.map((u) => ({ key: u.key, value: u.value }))
    );
  };

  const handleConfigReset = () => {
    // Reset to defaults - would need API endpoint for this
    setSnackbar({ open: true, message: 'Reset to defaults (not implemented)', severity: 'info' });
  };

  const handleExport = () => {
    // Export configuration as JSON
    const exportData = {
      configs: configs || [],
      presets: presets || [],
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `project-echo-config-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setSnackbar({ open: true, message: 'Configuration exported successfully', severity: 'success' });
  };

  const handleImport = async (file: File) => {
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      // Import logic would go here
      setSnackbar({ open: true, message: 'Configuration imported (not fully implemented)', severity: 'info' });
    } catch (error) {
      setSnackbar({ open: true, message: 'Failed to import configuration', severity: 'error' });
    }
  };

  if (isLoadingConfigs) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="General" />
          <Tab label="Processing" />
          <Tab label="Music" />
          <Tab label="Presets" />
          <Tab label="Phase 2" />
          <Tab label="System Info" />
          <Tab label="Attribution" />
          <Tab label="Backup" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <GlobalSettings
          configs={configs || []}
          onSave={handleConfigSave}
          onReset={handleConfigReset}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <ProcessingSettings
          configs={configs || []}
          onSave={handleConfigSave}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <MusicManagement
          tracks={musicTracks || []}
          onUpload={(file, metadata) => uploadMusicMutation.mutate({ file, metadata })}
          onDelete={(id) => deleteMusicMutation.mutate(id)}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <EffectPresetsManagement
          presets={presets || []}
          onCreate={(preset) => createPresetMutation.mutate(preset)}
          onUpdate={(id, preset) => updatePresetMutation.mutate({ id, preset })}
          onDelete={(id) => deletePresetMutation.mutate(id)}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Box mb={3}>
          {phase2Status && <Phase2Status status={phase2Status} />}
        </Box>
        <Phase2Activation />
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        <SystemInformation
          version="1.0.0"
          health={health || { status: 'healthy', components: {} }}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={6}>
        <Box display="flex" flexDirection="column" gap={3}>
          <CreatorList />
          <VideoAttribution />
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={7}>
        <BackupRestore onExport={handleExport} onImport={handleImport} />
      </TabPanel>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
