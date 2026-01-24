# Phase 2 Activation & Music Promotion Documentation

## Overview

Phase 2 is the music promotion feature that enables the "viral wave" strategy. It allows users to activate music replacement across selected channels and videos, replacing original audio with the creator's personal music tracks to promote their music on Spotify.

## Features

### Activation & Configuration

- **Enable/Disable**: Activate or deactivate Phase 2 for channels
- **Channel Selection**: Choose all channels or specific channels
- **Video Filtering**: Select which videos get music replacement
- **Music Selection**: Choose which music track to use
- **Retroactive Application**: Apply to already published videos
- **Scheduling**: Schedule activation for future (future enhancement)

### Status & Monitoring

- **Status Dashboard**: View Phase 2 status across all channels
- **Channel Readiness**: Check if channels meet readiness criteria
- **Activity Tracking**: Track activation and processing results

## API Endpoints

### Get Phase 2 Status

```http
GET /api/phase2/status
```

**Response:**
```json
{
  "phase2_enabled": true,
  "phase2_channels_count": 3,
  "total_channels": 5,
  "active_channels": 4,
  "channels": [
    {
      "id": "uuid",
      "name": "Channel Name",
      "phase2_enabled": true,
      "is_active": true
    }
  ],
  "available_music_tracks": 2
}
```

### Activate Phase 2

```http
POST /api/phase2/activate
Content-Type: application/json

{
  "channel_ids": ["uuid1", "uuid2"],  // Empty array = all channels
  "music_id": "uuid",
  "video_filter": {
    "transformation_status": "transformed",
    "created_after": "2026-01-01T00:00:00Z"
  },
  "apply_retroactive": false,
  "normalize": true,
  "loop_audio": true
}
```

**Response:**
```json
{
  "activated": [
    {
      "channel_id": "uuid",
      "channel_name": "Channel Name",
      "videos_processed": 10,
      "videos_failed": 0
    }
  ],
  "failed": [],
  "total": 1
}
```

### Deactivate Phase 2

```http
POST /api/phase2/deactivate
Content-Type: application/json

{
  "channel_ids": ["uuid1", "uuid2"]  // null = all channels
}
```

**Response:**
```json
{
  "deactivated": [
    {
      "channel_id": "uuid",
      "channel_name": "Channel Name"
    }
  ],
  "failed": [],
  "total": 1
}
```

### Apply Retroactive

```http
POST /api/phase2/apply-retroactive
Content-Type: application/json

{
  "channel_ids": ["uuid1"],
  "music_id": "uuid",
  "normalize": true,
  "loop_audio": true
}
```

**Response:**
```json
{
  "processed": [
    {
      "channel_id": "uuid",
      "channel_name": "Channel Name",
      "videos_processed": 5,
      "videos_failed": 0
    }
  ],
  "failed": [],
  "total": 5
}
```

### Check Channel Readiness

```http
POST /api/phase2/check-readiness
Content-Type: application/json

{
  "channel_id": "uuid",
  "min_subscribers": 1000,
  "min_views": 10000
}
```

**Response:**
```json
{
  "channel_id": "uuid",
  "ready": true,
  "checks": {
    "subscribers": {
      "required": 1000,
      "current": 1500,
      "met": true
    },
    "views": {
      "required": 10000,
      "current": 25000,
      "met": true
    }
  }
}
```

## Usage

### Activating Phase 2

```python
from src.services.phase2.phase2_service import Phase2Service

service = Phase2Service(db)

result = service.activate_phase2(
    channel_ids=["channel-1", "channel-2"],  # Empty list = all channels
    music_id="music-uuid",
    apply_retroactive=False,
    normalize=True,
    loop_audio=True,
)
```

### Checking Status

```python
status = service.get_phase2_status()
print(f"Phase 2 is {'active' if status['phase2_enabled'] else 'inactive'}")
print(f"{status['phase2_channels_count']} channels have Phase 2 enabled")
```

### Applying Retroactive

```python
result = service.apply_retroactive(
    channel_ids=["channel-1"],
    music_id="music-uuid",
    normalize=True,
)
```

## Channel Readiness

Phase 2 can check if channels are ready based on:
- **Subscriber Count**: Minimum subscriber threshold
- **View Count**: Minimum total views threshold

Readiness checks help ensure channels have enough audience before launching the music promotion strategy.

## Video Filtering

Videos can be filtered by:
- **Transformation Status**: Only transformed videos
- **Date Range**: Videos created after/before specific dates
- **Publication Status**: Include/exclude published videos

## Best Practices

1. **Test First**: Test Phase 2 on a single channel before activating globally
2. **Check Readiness**: Verify channels meet readiness criteria
3. **Select Music**: Choose appropriate music track for promotion
4. **Monitor Results**: Track processing results and failures
5. **Gradual Rollout**: Activate on a few channels first, then expand
6. **Retroactive Care**: Be careful with retroactive application on published videos

## Related Documentation

- [Audio Replacement](./AUDIO_REPLACEMENT.md)
- [Music File Management](./MUSIC.md)
- [Channel Management](./CHANNELS.md)
- [Orchestration](./ORCHESTRATION.md)
