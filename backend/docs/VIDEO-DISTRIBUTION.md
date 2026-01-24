# Video Distribution Documentation

## Overview

This guide explains the multi-channel video distribution system. The system automatically assigns videos to channels based on content filters, posting schedules, or manual assignment, enabling efficient content distribution across multiple YouTube channels.

## Distribution Methods

### Auto Distribution by Content Filters

Automatically assign videos to channels based on channel content filter criteria (resolution, duration, views, watermarks).

```python
from src.database import SessionLocal
from src.services.orchestration.video_distribution_service import VideoDistributionService

db = SessionLocal()
service = VideoDistributionService(db)

# Auto-distribute all ready videos
distributions = service.auto_distribute_by_filters()

# Auto-distribute specific video
distributions = service.auto_distribute_by_filters(video_id="video-uuid")

# Auto-distribute to specific channels
distributions = service.auto_distribute_by_filters(channel_ids=["channel-1", "channel-2"])
```

### Auto Distribution by Schedule

Automatically assign videos to channels based on posting schedule availability.

```python
# Auto-distribute based on schedules
distributions = service.auto_distribute_by_schedule()

# Creates schedules automatically for matched channels
for dist in distributions:
    if dist.status == "scheduled":
        print(f"Video {dist.video_id} scheduled for channel {dist.channel_id}")
```

### Manual Distribution

Manually assign videos to specific channels.

```python
from datetime import datetime, timedelta

# Manual assignment
distributions = service.manual_distribute(
    video_id="video-uuid",
    channel_ids=["channel-1", "channel-2"],
    scheduled_at=datetime.utcnow() + timedelta(hours=2),
)

# Force assignment (override duplicates)
distributions = service.manual_distribute(
    video_id="video-uuid",
    channel_ids=["channel-1"],
    force=True,  # Override duplicate check
)
```

## Content Filter Matching

Videos are matched to channels based on channel content filters:

- **min_resolution**: Minimum video resolution (e.g., "720p", "1080p")
- **min_views**: Minimum view count
- **max_duration**: Maximum duration in seconds
- **exclude_watermarked**: Whether to exclude watermarked videos

Example channel content filters:

```json
{
  "min_resolution": "720p",
  "min_views": 1000,
  "max_duration": 300,
  "exclude_watermarked": true
}
```

## Duplicate Prevention

The system automatically prevents duplicate distributions:

- Checks if video already assigned to channel
- Checks if video already published on channel
- Prevents duplicate assignments (unless `force=True`)

```python
# Check for duplicates
is_duplicate = service.distribution_repo.check_duplicate(
    video_id="video-uuid",
    channel_id="channel-uuid",
)
```

## Distribution Logging

All distribution decisions are logged with:

- **Video ID**: Which video was distributed
- **Channel ID**: Which channel received the video
- **Method**: How it was assigned (auto_filter, auto_schedule, manual)
- **Reason**: Why it was assigned (filter match details, schedule slot, etc.)
- **Timestamp**: When it was assigned

```python
# Get distribution history for a video
distributions = service.distribution_repo.get_by_video("video-uuid")

for dist in distributions:
    print(f"Channel: {dist.channel_id}, Method: {dist.distribution_method}")
    print(f"Reason: {dist.assignment_reason}")
```

## Error Handling and Retries

### Failed Distributions

Distributions can fail due to:
- Channel unavailable
- Upload failures
- Schedule conflicts
- Validation errors

Failed distributions are marked with `status="failed"` and include an `error_message`.

### Retry Failed Distributions

```python
# Retry a failed distribution
distribution = service.retry_failed_distribution("distribution-uuid")

# Check retry count
retry_count = int(distribution.retry_count)
max_retries = int(distribution.max_retries)

if retry_count < max_retries:
    print(f"Retrying (attempt {retry_count + 1}/{max_retries})")
```

## Distribution Statistics

### Get Statistics

```python
# Overall statistics
stats = service.get_distribution_statistics()

print(f"Total distributions: {stats['total']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"By status: {stats['by_status']}")
print(f"By method: {stats['by_method']}")

# Channel-specific statistics
channel_stats = service.get_distribution_statistics(
    channel_id="channel-uuid",
    start_date=datetime.utcnow() - timedelta(days=30),
)
```

### Statistics Breakdown

- **Total**: Total number of distributions
- **By Status**: Count by status (assigned, scheduled, published, failed, cancelled)
- **By Method**: Count by method (auto_filter, auto_schedule, manual)
- **Success Rate**: Percentage of published distributions
- **Published Count**: Number of successfully published videos

## Distribution Status

Distribution status values:

- **assigned**: Video assigned to channel (not yet scheduled)
- **scheduled**: Video scheduled for publication
- **published**: Video successfully published
- **failed**: Distribution failed
- **cancelled**: Distribution cancelled

## Best Practices

1. **Content Filters**: Configure channel content filters to match desired content
2. **Schedule Management**: Ensure channels have valid posting schedules
3. **Monitor Statistics**: Regularly check distribution statistics for issues
4. **Retry Failures**: Monitor and retry failed distributions
5. **Manual Override**: Use manual distribution for special cases
6. **Duplicate Prevention**: Let the system prevent duplicates automatically

## Automation

### Automated Distribution

Set up a cron job or scheduled task to run automatic distribution:

```python
# Run every hour
from datetime import datetime

service = VideoDistributionService(db)

# Auto-distribute by filters
filter_distributions = service.auto_distribute_by_filters()

# Auto-distribute by schedule
schedule_distributions = service.auto_distribute_by_schedule()

# Log results
print(f"Filter distributions: {len(filter_distributions)}")
print(f"Schedule distributions: {len(schedule_distributions)}")
```

### Distribution Workflow

1. **Video Ready**: Video downloaded and transformed
2. **Auto Distribution**: System matches videos to channels
3. **Schedule Creation**: Schedules created for matched channels
4. **Publication**: Videos published at scheduled times
5. **Statistics**: Track success rates and performance

## Related Documentation

- [Scheduling & Coordination](./SCHEDULING.md)
- [Channel Configuration](./CHANNEL-CONFIGURATION.md)
- [Queue Service](./QUEUE.md)
- [Multi-Repository Architecture](../../docs/MULTI-REPO-ARCHITECTURE.md)
