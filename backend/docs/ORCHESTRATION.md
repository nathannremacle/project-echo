# Central Orchestration System Documentation

## Overview

This guide explains the central orchestration system that coordinates all multi-channel operations. The system provides a unified interface for managing video scraping, processing, scheduling, publication, configuration, and statistics across all channels.

## System Status

### Start/Stop Control

```python
from src.database import SessionLocal
from src.services.orchestration.central_orchestration_service import CentralOrchestrationService

db = SessionLocal()
service = CentralOrchestrationService(db)

# Start orchestration
result = service.start()
print(f"Orchestration started: {result['status']}")

# Stop orchestration
result = service.stop()
print(f"Orchestration stopped: {result['status']}")

# Pause/Resume
service.pause()
service.resume()

# Get status
status = service.get_status()
print(f"Running: {status['running']}, Paused: {status['paused']}")
```

## API Endpoints

### System Control

- `POST /api/orchestration/start` - Start orchestration system
- `POST /api/orchestration/stop` - Stop orchestration system
- `POST /api/orchestration/pause` - Pause orchestration
- `POST /api/orchestration/resume` - Resume orchestration
- `GET /api/orchestration/status` - Get system status

### Coordination

- `POST /api/orchestration/coordinate-publication` - Coordinate publication across channels
- `POST /api/orchestration/schedule-wave` - Schedule viral wave publication
- `POST /api/orchestration/trigger-pipeline` - Trigger pipeline for a channel

### Monitoring

- `GET /api/orchestration/monitor-channels` - Monitor all channels
- `GET /api/orchestration/dashboard` - Get status dashboard data

### Distribution

- `POST /api/orchestration/distribute-videos` - Auto-distribute videos to channels

### Configuration

- `POST /api/orchestration/sync-configs` - Sync channel configurations

## Coordinate Publication

Coordinate publication of a video across multiple channels:

```python
# Via API
POST /api/orchestration/coordinate-publication
{
  "video_id": "video-uuid",
  "channel_ids": ["channel-1", "channel-2", "channel-3"],
  "timing": "simultaneous",  # or "staggered", "independent"
  "scheduled_at": "2026-01-24T12:00:00Z"  # Optional
}

# Via service
result = service.coordinate_publication(
    video_id="video-uuid",
    channel_ids=["channel-1", "channel-2"],
    timing="simultaneous",
    scheduled_at=datetime.utcnow() + timedelta(hours=1),
)
```

## Schedule Viral Wave

Schedule a viral wave publication (multiple videos to multiple channels):

```python
# Via API
POST /api/orchestration/schedule-wave
{
  "video_ids": ["video-1", "video-2", "video-3"],
  "channel_ids": ["channel-1", "channel-2", "channel-3"],
  "wave_config": {
    "timing": "simultaneous",
    "scheduled_at": "2026-01-24T12:00:00Z",
    "delay_seconds": 3600  # For staggered
  }
}

# Via service
result = service.schedule_wave_publication(
    video_ids=["video-1", "video-2"],
    channel_ids=["channel-1", "channel-2"],
    wave_config={
        "timing": "simultaneous",
        "scheduled_at": datetime.utcnow() + timedelta(hours=1),
    },
)
```

## Trigger Pipeline

Trigger a pipeline for a channel (via GitHub Actions or queue):

```python
# Via API
POST /api/orchestration/trigger-pipeline
{
  "channel_id": "channel-uuid",
  "video_id": "video-uuid"  # Optional
}

# Via service
result = service.trigger_pipeline(
    channel_id="channel-uuid",
    video_id="video-uuid",  # Optional
)
```

## Monitor Channels

Monitor health and status of all channels:

```python
# Via API
GET /api/orchestration/monitor-channels

# Via service
channel_statuses = service.monitor_channels()

for status in channel_statuses:
    print(f"Channel: {status['name']}")
    print(f"  Health: {status['health']}")
    print(f"  Status: {status['status']}")
    print(f"  Statistics: {status['statistics']}")
```

## Status Dashboard

Get comprehensive status dashboard data:

```python
# Via API
GET /api/orchestration/dashboard

# Via service
dashboard = service.get_dashboard_data()

print(f"System running: {dashboard['system']['status']['running']}")
print(f"Active channels: {dashboard['channels']['active']}")
print(f"Total distributions: {dashboard['statistics']['overall']['total']}")
print(f"Pending schedules: {dashboard['schedules']['pending']}")
```

## Auto-Distribute Videos

Automatically assign videos to channels:

```python
# Via API
POST /api/orchestration/distribute-videos

# Via service
result = service.distribute_videos()

print(f"Distributed {result['total_distributed']} videos")
print(f"  By filters: {result['by_filters']}")
print(f"  By schedule: {result['by_schedule']}")
```

## Sync Channel Configs

Sync configurations across channel repositories:

```python
# Via API
POST /api/orchestration/sync-configs

# Via service
result = service.sync_channel_configs()

print(f"Synced {result['synced']} channels")
if result['errors']:
    print(f"Errors: {result['errors']}")
```

## Channel Monitoring

The orchestration system monitors:

- **Health**: Channel repository status, API credentials
- **Status**: Active, inactive, paused
- **Errors**: Recent errors and issues
- **Statistics**: Distribution counts, success rates
- **Last Publication**: Last successful publication time

## Coordination Conflicts

The system handles conflicts:

- **Resource Contention**: Shared processing resources
- **Timing Conflicts**: Overlapping schedules
- **Priority-Based Scheduling**: Higher priority operations first

## Orchestration Logging

All coordination activities are logged:

- Publication coordination
- Pipeline triggers
- Wave scheduling
- Distribution decisions
- Configuration syncs
- System events

## Best Practices

1. **Start Before Operations**: Always start orchestration before running operations
2. **Monitor Regularly**: Check channel status regularly
3. **Use Dashboard**: Use dashboard endpoint for overview
4. **Handle Errors**: Monitor and handle errors promptly
5. **Sync Configs**: Sync configurations after changes
6. **Coordinate Waves**: Use wave scheduling for viral effects

## Related Documentation

- [Scheduling & Coordination](./SCHEDULING.md)
- [Video Distribution](./VIDEO-DISTRIBUTION.md)
- [Channel Configuration](./CHANNEL-CONFIGURATION.md)
- [GitHub Repository Management](./GITHUB-REPOSITORY-MANAGEMENT.md)
- [Queue Service](./QUEUE.md)
