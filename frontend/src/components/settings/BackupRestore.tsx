import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
} from '@mui/material';
import { Download, Upload } from '@mui/icons-material';
import { useState } from 'react';

interface BackupRestoreProps {
  onExport: () => void;
  onImport: (file: File) => void;
}

export default function BackupRestore({ onExport, onImport }: BackupRestoreProps) {
  const [importError, setImportError] = useState<string | null>(null);

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
      setImportError('Please select a valid JSON configuration file');
      return;
    }

    setImportError(null);
    onImport(file);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Backup & Restore
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Export your system configuration for backup or import a previously exported configuration.
        </Typography>

        {importError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setImportError(null)}>
            {importError}
          </Alert>
        )}

        <Box display="flex" gap={2} flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={onExport}
          >
            Export Configuration
          </Button>

          <input
            accept=".json,application/json"
            style={{ display: 'none' }}
            id="import-config-input"
            type="file"
            onChange={handleImport}
          />
          <label htmlFor="import-config-input">
            <Button
              variant="outlined"
              component="span"
              startIcon={<Upload />}
            >
              Import Configuration
            </Button>
          </label>
        </Box>

        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="caption">
            <strong>Note:</strong> Importing a configuration will overwrite your current settings.
            Make sure to export your current configuration first if you want to keep it.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
}
