# Channel Configuration Management Documentation

## Overview

This guide explains how to manage configurations for multiple YouTube channels. Each channel has independent settings for posting schedules, content filters, metadata templates, and transformation presets.

## Channel Configuration Components

Each channel configuration includes:

1. **YouTube API Credentials**: OAuth credentials for YouTube API access
2. **Posting Schedule**: When and how often to post videos
3. **Content Filters**: What types of videos to scrape
4. **Metadata Template**: Templates for video titles, descriptions, tags
5. **Effect Preset**: Transformation preset to apply to videos
6. **Active Status**: Whether channel is currently active

## Creating a Channel

### Basic Channel Creation

```python
from src.database import SessionLocal
from src.services.orchestration.channel_configuration_service import ChannelConfigurationService

db = SessionLocal()
service = ChannelConfigurationService(db)

# Create channel with default configurations
channel = service.create_channel(
    name="My Channel",
    youtube_channel_id="UC1234567890",
    youtube_channel_url="https://youtube.com/channel/UC1234567890",
    api_credentials={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "refresh_token": "your-refresh-token",
    },
)
```

### Custom Configuration

```python
# Create channel with custom configurations
channel = service.create_channel(
    name="My Channel",
    youtube_channel_id="UC1234567890",
    youtube_channel_url="https://youtube.com/channel/UC1234567890",
    api_credentials={...},
    posting_schedule={
        "frequency": "weekly",
        "preferred_times": ["18:00", "20:00"],
        "timezone": "America/New_York",
        "days_of_week": [1, 3, 5],  # Monday, Wednesday, Friday
    },
    content_filters={
        "min_resolution": "1080p",
        "min_views": 10000,
        "exclude_watermarked": True,
        "preferred_sources": ["source1", "source2"],
    },
    metadata_template={
        "title": "{channel_name} - {source_title} - {date}",
        "description": "Amazing edit from {channel_name}",
        "tags": ["edit", "music", "viral", "trending"],
        "category": "entertainment",
        "privacy": "public",
    },
    effect_preset_id="preset-uuid",
    is_active=True,
)
```

## Updating Configuration

### Update Specific Fields

```python
# Update posting schedule
service.update_channel_configuration(
    channel_id="channel-uuid",
    posting_schedule={
        "frequency": "daily",
        "preferred_times": ["12:00"],
        "timezone": "UTC",
    },
)

# Update content filters
service.update_channel_configuration(
    channel_id="channel-uuid",
    content_filters={
        "min_resolution": "1440p",
        "min_views": 50000,
    },
)

# Update active status
service.update_channel_configuration(
    channel_id="channel-uuid",
    is_active=False,  # Pause channel
)
```

### Update API Credentials

```python
service.update_api_credentials(
    channel_id="channel-uuid",
    api_credentials={
        "client_id": "new-client-id",
        "client_secret": "new-client-secret",
        "refresh_token": "new-refresh-token",
    },
)
```

## Default Configurations

### Default Posting Schedule

```python
{
    "frequency": "daily",
    "preferred_times": ["12:00"],
    "timezone": "UTC",
    "days_of_week": [0, 1, 2, 3, 4, 5, 6],  # All days
}
```

### Default Content Filters

```python
{
    "min_resolution": "720p",
    "min_views": 0,
    "exclude_watermarked": True,
    "preferred_sources": [],
}
```

### Default Metadata Template

```python
{
    "title": "{channel_name} - {source_title}",
    "description": "Video from {channel_name}\n\nOriginal: {source_title}",
    "tags": ["edit", "music", "viral"],
    "category": "entertainment",
    "privacy": "unlisted",
}
```

### Get Defaults

```python
defaults = service.get_default_configuration()
# Returns: {"posting_schedule": {...}, "content_filters": {...}, "metadata_template": {...}}
```

## Configuration Validation

### Validate Channel Configuration

```python
results = service.validate_channel_configuration("channel-uuid")

# Results structure:
# {
#     "channel_id": "channel-uuid",
#     "valid": True/False,
#     "errors": ["error1", "error2"],
#     "warnings": ["warning1"],
# }
```

Validation checks:
- Posting schedule format and values
- Content filters format and values
- Metadata template format
- Effect preset exists (if set)
- YouTube API credentials are valid

## Export/Import Configuration

### Export Configuration

```python
# Export without credentials (safe for sharing)
config = service.export_channel_configuration("channel-uuid", include_credentials=False)

# Export with credentials (for backup)
config = service.export_channel_configuration("channel-uuid", include_credentials=True)

# Save to file
import json
with open("channel_backup.json", "w") as f:
    json.dump(config, f, indent=2)
```

### Import Configuration

```python
# Load from file
with open("channel_backup.json", "r") as f:
    config = json.load(f)

# Import (create new channel)
channel = service.import_channel_configuration(config, update_existing=False)

# Import (update existing channel)
channel = service.import_channel_configuration(config, update_existing=True)
```

## Configuration Schema

### Posting Schedule

```python
{
    "frequency": "daily" | "weekly" | "custom",
    "preferred_times": ["HH:MM", ...],  # ISO time format
    "timezone": "UTC" | "America/New_York" | ...,  # IANA timezone
    "days_of_week": [0, 1, 2, 3, 4, 5, 6],  # 0=Sunday, 6=Saturday
}
```

### Content Filters

```python
{
    "min_resolution": "720p" | "1080p" | "1440p" | "2160p",
    "min_views": int,  # Minimum view count
    "exclude_watermarked": bool,  # Exclude watermarked videos
    "preferred_sources": [str, ...],  # Preferred source channels/creators
}
```

### Metadata Template

```python
{
    "title": str,  # Can include variables: {channel_name}, {source_title}, {date}, {video_number}
    "description": str,  # Can include same variables
    "tags": [str, ...],  # List of tags
    "category": str,  # YouTube category (entertainment, music, gaming, etc.)
    "privacy": "private" | "unlisted" | "public",
}
```

## Best Practices

1. **Validate Before Creating**: Always validate configuration before creating channels
2. **Use Defaults**: Start with defaults and customize as needed
3. **Backup Configurations**: Export configurations regularly for backup
4. **Test Credentials**: Validate API credentials after updating
5. **Monitor Active Status**: Use `is_active` to pause/resume channels
6. **Version Control**: Track configuration changes via `updated_at` timestamp

## Error Handling

### Common Errors

#### Duplicate YouTube Channel ID

```python
ValidationError: YouTube channel ID UC123 already exists
```

**Solution**: Use different YouTube channel ID or update existing channel.

#### Invalid Posting Schedule

```python
ValidationError: Invalid frequency: invalid. Must be 'daily', 'weekly', or 'custom'
```

**Solution**: Use valid frequency value.

#### Invalid Content Filters

```python
ValidationError: Invalid min_resolution: 480p
```

**Solution**: Use valid resolution: 720p, 1080p, 1440p, or 2160p.

#### Invalid Metadata Template

```python
ValidationError: Metadata template must include 'title'
```

**Solution**: Ensure template includes required fields.

#### Invalid API Credentials

```python
AuthenticationError: YouTube API credentials are invalid
```

**Solution**: Re-authenticate channel (see [YOUTUBE-AUTH.md](./YOUTUBE-AUTH.md)).

## Related Documentation

- [YouTube Authentication](./YOUTUBE-AUTH.md)
- [Transformation Presets](./TRANSFORMATION.md)
- [Multi-Repository Architecture](../../docs/MULTI-REPO-ARCHITECTURE.md)
