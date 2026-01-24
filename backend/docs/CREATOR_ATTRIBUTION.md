# Creator Attribution System Documentation

## Overview

The Creator Attribution System tracks and manages attribution for original creators of scraped videos. This helps reduce legal risks by properly crediting creators and improves content quality by maintaining creator information.

## Features

### Creator Management

- **List Creators**: View all unique creators with video counts
- **Search Creators**: Search creators by name (partial match)
- **Creator Details**: View all videos by a specific creator
- **Export**: Export creator list with video details

### Video Attribution

- **Manual Attribution**: Add or update creator attribution for individual videos
- **Bulk Attribution**: Update attribution for multiple videos at once
- **Template Integration**: Get attribution string for use in description templates

## API Endpoints

### List Creators

```http
GET /api/creators
```

**Response:**
```json
{
  "creators": [
    {
      "name": "Creator Name",
      "video_count": 10
    }
  ],
  "total": 1
}
```

### Search Creators

```http
GET /api/creators/search?q=query&limit=50
```

**Response:**
```json
{
  "creators": [
    {
      "name": "Creator Name",
      "video_count": 10
    }
  ],
  "total": 1,
  "query": "query"
}
```

### Get Videos by Creator

```http
GET /api/creators/{creator_name}/videos?limit=20&offset=0
```

**Response:**
```json
{
  "creator": "Creator Name",
  "videos": [
    {
      "id": "uuid",
      "source_title": "Video Title",
      "source_url": "https://...",
      "channel_id": "uuid",
      "publication_status": "published",
      "created_at": "2026-01-23T00:00:00Z"
    }
  ],
  "total": 10,
  "limit": 20,
  "offset": 0
}
```

### Attribute Video

```http
POST /api/creators/videos/{video_id}/attribute
Content-Type: application/json

{
  "creator_name": "Creator Name",
  "creator_channel": "https://youtube.com/@creator"  // optional
}
```

**Response:**
```json
{
  "video_id": "uuid",
  "creator_name": "Creator Name",
  "message": "Attribution updated successfully"
}
```

### Bulk Attribute Videos

```http
POST /api/creators/videos/bulk-attribute
Content-Type: application/json

{
  "video_ids": ["uuid1", "uuid2"],
  "creator_name": "Creator Name",
  "creator_channel": "https://youtube.com/@creator"  // optional
}
```

**Response:**
```json
{
  "updated": [
    {
      "video_id": "uuid1",
      "video_title": "Video Title"
    }
  ],
  "failed": [],
  "total": 2
}
```

### Export Creators

```http
GET /api/creators/export?format=json
```

**Response:**
```json
{
  "exported_at": "2026-01-23T00:00:00Z",
  "total_creators": 5,
  "creators": [
    {
      "name": "Creator Name",
      "video_count": 10,
      "videos": [...]
    }
  ]
}
```

### Get Attribution Template

```http
GET /api/creators/videos/{video_id}/attribution-template
```

**Response:**
```json
{
  "video_id": "uuid",
  "attribution": "Original video by: Creator Name"
}
```

## Usage

### Adding Attribution

```python
from src.services.creator_attribution.creator_attribution_service import CreatorAttributionService

service = CreatorAttributionService(db)

# Single video
video = service.attribute_video(
    video_id="video-uuid",
    creator_name="Creator Name",
    creator_channel="https://youtube.com/@creator",
)

# Bulk update
result = service.bulk_attribute_videos(
    video_ids=["video-1", "video-2"],
    creator_name="Creator Name",
)
```

### Searching Creators

```python
creators = service.search_creators(query="creator", limit=50)
```

### Getting Attribution for Templates

```python
attribution = service.get_attribution_template_variable(video_id="video-uuid")
# Returns: "Original video by: Creator Name" or empty string
```

## Description Template Integration

The attribution can be included in video descriptions using the template variable:

```python
# In metadata template processing
attribution = creator_attribution_service.get_attribution_template_variable(video_id)
description = f"{base_description}\n\n{attribution}"
```

Or in channel metadata templates, you can use:
```
{description}

{creator_attribution}
```

## Best Practices

1. **Attribute Early**: Add creator attribution when scraping or downloading videos
2. **Verify Creators**: Manually verify creator information when possible
3. **Include in Descriptions**: Always include attribution in video descriptions
4. **Bulk Updates**: Use bulk attribution for efficiency when updating multiple videos
5. **Export Regularly**: Export creator lists for backup and record-keeping
6. **Search Before Adding**: Search for existing creators before adding new ones

## Legal Considerations

- **Proper Credit**: Always credit original creators to reduce legal risks
- **Creator Information**: Store accurate creator names and channel URLs
- **Attribution Format**: Use consistent attribution format in descriptions
- **Export Records**: Keep exports of creator lists for documentation

## Related Documentation

- [Video Model](./VIDEOS.md)
- [Metadata Management](./METADATA.md)
- [YouTube Upload](./YOUTUBE.md)
