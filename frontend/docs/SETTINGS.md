# Settings Documentation

## Overview

The Settings page provides comprehensive system configuration and management capabilities. Users can configure global settings, manage music tracks, handle effect presets, monitor system health, and perform backup/restore operations.

## Features

### General Settings

Configure global default settings:

- **Default Effect Preset**: Select default transformation preset for new videos
- **Default Video Quality**: Set default video quality (720p, 1080p, 1440p, 2160p)
- **Processing Quality**: Choose processing quality (low, medium, high)
- **Auto-publish**: Enable/disable automatic publishing after processing

### Processing Settings

Configure video processing parameters:

- **Queue Max Size**: Maximum number of jobs in processing queue (1-10000)
- **Parallel Processing Limit**: Maximum simultaneous video processing (1-10)
- **Retry Attempts**: Number of retry attempts for failed jobs
- **Retry Delay**: Delay between retry attempts in seconds

### Music Management

Manage personal music tracks for Phase 2:

- **Upload Music**: Upload audio files for music replacement feature
- **Track Metadata**: Set track name, artist, and Spotify URL
- **Track List**: View all uploaded tracks
- **Delete Tracks**: Remove uploaded music tracks

### Effect Presets Management

Manage transformation effect presets:

- **Create Preset**: Create new effect presets with custom parameters
- **Edit Preset**: Modify existing presets
- **Delete Preset**: Remove presets
- **Preset Effects**: Configure brightness, contrast, saturation, hue, blur, sharpen, noise

### System Information

Monitor system health and status:

- **System Version**: Display current system version
- **System Status**: Overall health status (healthy, degraded, unhealthy)
- **Component Status**: Database, storage, YouTube API status
- **Resource Usage**: CPU, memory, and disk usage (if available)

### Backup & Restore

Export and import system configuration:

- **Export Configuration**: Download configuration as JSON file
- **Import Configuration**: Restore configuration from JSON file
- **Backup Safety**: Warnings about overwriting current settings

## Usage

### Configuring Settings

1. Navigate to Settings from the sidebar
2. Select the appropriate tab (General, Processing, etc.)
3. Modify settings as needed
4. Click "Save Changes" to apply
5. Use "Reset to Defaults" to restore original values

### Managing Music Tracks

1. Go to the Music tab
2. Click "Upload Music"
3. Select audio file
4. Enter track name, artist, and optional Spotify URL
5. Click "Upload"
6. Tracks appear in the list
7. Use delete button to remove tracks

### Managing Effect Presets

1. Go to the Presets tab
2. Click "Create Preset" to add new preset
3. Enter preset name and description
4. Configure effect parameters
5. Click "Create" or "Update"
6. Use edit/delete buttons to manage existing presets

### Exporting/Importing Configuration

1. Go to the Backup tab
2. Click "Export Configuration" to download JSON file
3. To import, click "Import Configuration"
4. Select previously exported JSON file
5. Configuration will be restored

## Components

### GlobalSettings

Global default settings form:
- Effect preset selection
- Video quality settings
- Processing quality
- Auto-publish toggle
- Save and reset buttons

### ProcessingSettings

Processing configuration form:
- Queue size limits
- Parallel processing limits
- Retry configuration
- Validation and error handling

### MusicManagement

Music track management:
- Upload dialog
- Track list table
- Delete functionality
- Metadata management

### EffectPresetsManagement

Preset library management:
- Preset list table
- Create/edit dialog
- Effect parameter configuration
- Delete functionality

### SystemInformation

System health display:
- Version information
- Status indicators
- Component health
- Resource usage graphs

### BackupRestore

Configuration backup/restore:
- Export button
- Import file picker
- Error handling
- Safety warnings

## API Endpoints

The settings page uses the following endpoints:

- `GET /api/config` - Get system configuration
- `PUT /api/config` - Update system configuration
- `GET /api/health` - Get system health
- `GET /api/transformation-presets` - Get presets
- `POST /api/transformation-presets` - Create preset
- `PUT /api/transformation-presets/{id}` - Update preset
- `DELETE /api/transformation-presets/{id}` - Delete preset
- `GET /api/music` - Get music tracks
- `POST /api/music` - Upload music track
- `DELETE /api/music/{id}` - Delete music track

## Best Practices

1. **Backup Before Changes**: Always export configuration before making major changes
2. **Test Settings**: Test new settings on a small scale before applying globally
3. **Monitor Resources**: Check system information regularly to monitor health
4. **Preset Management**: Create reusable presets for common transformations
5. **Music Organization**: Keep music tracks organized with proper metadata
6. **Validation**: Settings are validated before saving - fix errors before proceeding

## Related Documentation

- [Frontend README](../README.md)
- [Dashboard Documentation](./DASHBOARD.md)
- [Channel Detail Documentation](./CHANNEL-DETAIL.md)
