# Scheduling & Coordination Documentation

## Overview

This guide explains the multi-channel scheduling and coordination system. The system supports simultaneous, staggered, and independent publication schedules, enabling the "viral wave" effect by coordinating publications across multiple channels.

## Schedule Types

### Simultaneous Publication

Publish the same video on multiple channels at the exact same time.

```python
from src.database import SessionLocal
from src.services.orchestration.scheduling_service import SchedulingService
from datetime import datetime, timedelta

db = SessionLocal()
service = SchedulingService(db)

# Schedule simultaneous publication
schedules = service.create_simultaneous_schedule(
    video_id="video-uuid",
    channel_ids=["channel-1", "channel-2", "channel-3"],
    scheduled_at=datetime.utcnow() + timedelta(hours=1),
    wave_id="wave-123",  # Optional
)

print(f"Created {len(schedules)} simultaneous schedules")
```

### Staggered Publication

Publish the same video on multiple channels with time delays between each publication.

```python
# Schedule staggered publication (1 hour between each channel)
schedules = service.create_staggered_schedule(
    video_id="video-uuid",
    channel_ids=["channel-1", "channel-2", "channel-3"],
    start_time=datetime.utcnow() + timedelta(hours=1),
    delay_seconds=3600,  # 1 hour delay between channels
    wave_id="wave-123",  # Optional
)

print(f"Created {len(schedules)} staggered schedules")
```

### Independent Schedule

Each channel posts on its own schedule (from channel configuration).

```python
# Create independent schedule
schedule = service.create_independent_schedule(
    channel_id="channel-uuid",
    scheduled_at=datetime.utcnow() + timedelta(hours=2),
    video_id="video-uuid",  # Optional, can be assigned later
)

print(f"Created independent schedule: {schedule.id}")
```

## Conflict Detection

The system automatically detects and prevents conflicts:

- **Same video on same channel twice**: Cannot schedule the same video for the same channel at overlapping times
- **Overlapping schedules**: Schedules within 1 minute of each other are considered conflicts
- **Past dates**: Cannot schedule publications in the past

```python
# Validate a schedule
validation = service.validate_schedule("schedule-uuid")

if validation["valid"]:
    print("Schedule is valid")
else:
    print(f"Issues: {validation['issues']}")
```

## Schedule Management

### Pause/Resume

Pause or resume schedules individually or by channel:

```python
# Pause a single schedule
service.pause_schedule("schedule-uuid")

# Resume a schedule
service.resume_schedule("schedule-uuid")

# Pause all schedules for a channel
paused_count = service.pause_channel_schedules("channel-uuid")
print(f"Paused {paused_count} schedules")

# Resume all schedules for a channel
resumed_count = service.resume_channel_schedules("channel-uuid")
print(f"Resumed {resumed_count} schedules")
```

### Cancel Schedule

```python
# Cancel a schedule
service.cancel_schedule("schedule-uuid")
```

## Schedule Execution

### Execute Pending Schedules

The system executes pending schedules automatically (typically via a cron job or scheduled task):

```python
# Execute all pending schedules ready to run
results = service.execute_pending_schedules()

for result in results:
    print(f"Schedule {result['schedule_id']}: {result['status']}")
```

### Execution Methods

Schedules are executed via:

1. **GitHub Actions** (if channel has `github_repo_url`):
   - Triggers `repository_dispatch` event
   - Passes `video_id` and `schedule_id` in payload

2. **Queue Service** (if no GitHub repository):
   - Creates publication job in queue
   - Note: Queue-based publication requires additional implementation

## Querying Schedules

### By Date Range

Get schedules for calendar/timeline view:

```python
from datetime import datetime, timedelta

start_date = datetime.utcnow()
end_date = start_date + timedelta(days=7)

schedules = service.get_schedules_by_date_range(
    start_date=start_date,
    end_date=end_date,
    channel_id="channel-uuid",  # Optional
)

for schedule in schedules:
    print(f"{schedule.scheduled_at}: {schedule.schedule_type} - {schedule.status}")
```

### By Channel

```python
# Get all schedules for a channel
schedules = service.get_schedules_by_channel(
    channel_id="channel-uuid",
    status="pending",  # Optional filter
)
```

### By Wave

Get all schedules for a viral wave:

```python
schedules = service.get_schedules_by_wave("wave-123")
print(f"Wave has {len(schedules)} schedules")
```

## Schedule Status

Schedule status values:

- **pending**: Scheduled but not yet executed
- **scheduled**: Confirmed and ready to execute
- **executing**: Currently being executed
- **completed**: Successfully executed
- **failed**: Execution failed
- **cancelled**: Cancelled before execution

## Coordination Groups

Schedules in a coordination group (simultaneous/staggered) share a `coordination_group_id`. This allows:

- Tracking related schedules together
- Coordinating execution
- Managing wave publications

## Viral Wave Publications

Use `wave_id` to group related schedules for viral wave effects:

```python
# Create simultaneous wave
schedules = service.create_simultaneous_schedule(
    video_id="video-uuid",
    channel_ids=["channel-1", "channel-2", "channel-3"],
    scheduled_at=datetime.utcnow() + timedelta(hours=1),
    wave_id="wave-2026-01-23-001",
)

# Later, query all schedules in the wave
wave_schedules = service.get_schedules_by_wave("wave-2026-01-23-001")
```

## Best Practices

1. **Schedule Validation**: Always validate schedules before creating them
2. **Conflict Prevention**: Check for conflicts before scheduling
3. **Time Zones**: Use UTC for all scheduled times
4. **Error Handling**: Monitor failed schedules and retry if needed
5. **Wave Coordination**: Use `wave_id` to track viral wave publications
6. **Pause Before Changes**: Pause schedules before making major changes

## Automation

### Scheduled Execution

Set up a cron job or scheduled task to execute pending schedules:

```python
# Run every minute
from datetime import datetime

service = SchedulingService(db)
results = service.execute_pending_schedules(before=datetime.utcnow())

# Log results
for result in results:
    if result["status"] == "failed":
        logger.error(f"Schedule {result['schedule_id']} failed: {result.get('error')}")
```

### GitHub Actions Integration

For channels with GitHub repositories, schedules trigger workflows automatically:

```yaml
# In channel repository workflow
on:
  repository_dispatch:
    types: [process-video]

jobs:
  process-video:
    steps:
      - name: Get video ID
        run: echo "${{ github.event.client_payload.video_id }}"
      
      - name: Process and publish
        # ... process video ...
```

## Error Handling

### Failed Schedules

Failed schedules are marked with `status="failed"` and include an `error_message`:

```python
# Query failed schedules
schedules = service.schedule_repo.get_all(status="failed")

for schedule in schedules:
    print(f"Schedule {schedule.id} failed: {schedule.error_message}")
    
    # Retry if needed
    if schedule.attempts < 3:
        schedule.status = "pending"
        service.schedule_repo.update(schedule)
```

## Related Documentation

- [Multi-Repository Architecture](../../docs/MULTI-REPO-ARCHITECTURE.md)
- [GitHub Repository Management](./GITHUB-REPOSITORY-MANAGEMENT.md)
- [Queue Service](./QUEUE.md)
- [Channel Configuration](./CHANNEL-CONFIGURATION.md)
