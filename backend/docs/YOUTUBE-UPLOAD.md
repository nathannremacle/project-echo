# YouTube Video Upload Documentation

## Overview

This guide explains how to upload videos to YouTube using the Project Echo upload service. The service handles video uploads with metadata, thumbnails, progress tracking, and error handling.

## Prerequisites

1. **Authenticated YouTube Channel**: Channel must have valid OAuth credentials (see [YOUTUBE-AUTH.md](./YOUTUBE-AUTH.md))
2. **Transformed Video**: Video must be in `transformed` status with a valid `transformed_url` (S3 URL)
3. **S3 Access**: AWS credentials configured for downloading videos from S3

## Basic Usage

### Upload a Video

```python
from src.services.youtube.upload_service import YouTubeUploadService

service = YouTubeUploadService(db)

# Upload video (uses channel metadata template)
result = service.upload_video(video_id="video-uuid")

print(f"Video uploaded: {result['video_url']}")
print(f"YouTube Video ID: {result['video_id']}")
```

### Upload with Custom Metadata

```python
# Override metadata template
result = service.upload_video(
    video_id="video-uuid",
    metadata_override={
        "title": "Custom Video Title",
        "description": "Custom description",
        "tags": ["tag1", "tag2", "tag3"],
        "privacy": "public",
        "category": "gaming",
    },
)
```

### Upload with Thumbnail

```python
result = service.upload_video(
    video_id="video-uuid",
    thumbnail_path="/path/to/thumbnail.jpg",
)
```

## Metadata Templates

Each channel has a metadata template stored in `Channel.metadata_template` (JSON). The template supports variables:

### Template Variables

- `{channel_name}`: Channel name
- `{date}`: Current date (YYYY-MM-DD format)
- `{source_title}`: Original source video title
- `{video_number}`: Sequential video number (if provided)

### Example Template

```json
{
  "title": "{channel_name} - {source_title} - {date}",
  "description": "Video from {channel_name}\n\nOriginal: {source_title}\nDate: {date}",
  "tags": ["edit", "music", "viral"],
  "category": "entertainment",
  "privacy": "unlisted"
}
```

### Supported Categories

- `entertainment` (24) - Default
- `music` (10)
- `gaming` (20)
- `sports` (17)
- `news` (25)
- `education` (27)
- `science` (28)
- `technology` (28)
- `autos` (2)
- `comedy` (23)
- `people` (22)
- `pets` (15)
- `travel` (19)

### Privacy Settings

- `private`: Only owner can view
- `unlisted`: Anyone with link can view (default)
- `public`: Everyone can view

## Upload Process

The upload process follows these steps:

1. **Validation**: Check video is transformed and has `transformed_url`
2. **Status Update**: Set `publication_status` to `publishing`
3. **Metadata Processing**: Process template with variables
4. **Download from S3**: Download video to local temp file
5. **Upload to YouTube**: Upload video with resumable upload support
6. **Thumbnail Upload**: Upload thumbnail if provided
7. **Database Update**: Store YouTube video ID, URL, and metadata
8. **Cleanup**: Remove temp file

## Progress Tracking

Upload progress is automatically logged:

```
Upload progress for video abc-123: 25%
Upload progress for video abc-123: 50%
Upload progress for video abc-123: 75%
Upload progress for video abc-123: 100%
```

You can also provide a custom progress callback:

```python
def progress_callback(bytes_uploaded: int, total_size: int):
    progress = int((bytes_uploaded / total_size) * 100)
    print(f"Upload: {progress}%")

# Note: Currently progress callback is internal, but can be extended
```

## Resumable Uploads

The service automatically uses resumable uploads for all videos:

- **Benefits**: Can resume interrupted uploads
- **Automatic**: No configuration needed
- **Large Files**: Handles files of any size efficiently

## Error Handling

### Common Errors

#### Video Not Transformed

```python
ProcessingError: Video abc-123 is not transformed yet (status: pending)
```

**Solution**: Ensure video has been transformed before uploading.

#### No Transformed URL

```python
ProcessingError: Video abc-123 has no transformed URL
```

**Solution**: Ensure video has a valid `transformed_url` pointing to S3.

#### S3 Download Failure

```python
ProcessingError: Failed to download video from S3: ...
```

**Solution**: Check AWS credentials and S3 URL format.

#### YouTube API Quota Exceeded

```python
AuthenticationError: YouTube API quota exceeded for upload. Please wait or request quota increase.
```

**Solution**: Wait for quota reset (daily) or request quota increase from Google.

#### Authentication Failed

```python
AuthenticationError: Authentication failed for upload: Unauthorized. Please re-authenticate.
```

**Solution**: Re-authenticate channel (see [YOUTUBE-AUTH.md](./YOUTUBE-AUTH.md)).

### Error Recovery

When an upload fails:

1. Video `publication_status` is set to `failed`
2. Error is logged with details
3. Temp files are cleaned up
4. You can retry the upload after fixing the issue

## Database Updates

After successful upload, the video record is updated with:

- `publication_status`: `published`
- `youtube_video_id`: YouTube video ID
- `youtube_video_url`: Public YouTube URL
- `published_at`: Publication timestamp
- `final_title`: Title used on YouTube
- `final_description`: Description used on YouTube
- `final_tags`: JSON array of tags used

## Rate Limits

YouTube Data API v3 has rate limits:

- **Upload Quota**: 1,600 units per upload
- **Daily Quota**: 10,000 units (free tier)
- **Best Practice**: Monitor quota usage to avoid exhaustion

The service handles quota errors gracefully and provides clear error messages.

## Thumbnail Upload

### Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)

### Thumbnail Requirements

- **Size**: Recommended 1280x720 (16:9 aspect ratio)
- **File Size**: Max 2MB
- **Format**: JPEG or PNG recommended

### Thumbnail Upload Process

1. Video is uploaded first
2. Thumbnail is uploaded separately using video ID
3. If thumbnail upload fails, video upload still succeeds (warning logged)

## Best Practices

1. **Test with Unlisted Videos**: Use `privacy: "unlisted"` for testing
2. **Monitor Quota**: Track API quota usage to avoid exhaustion
3. **Error Handling**: Always handle `ProcessingError` and `AuthenticationError`
4. **Progress Monitoring**: Check logs for upload progress
5. **Metadata Templates**: Use templates for consistent metadata
6. **Thumbnail Quality**: Use high-quality thumbnails (1280x720 recommended)

## Example: Complete Upload Workflow

```python
from src.services.youtube.upload_service import YouTubeUploadService
from src.repositories.video_repository import VideoRepository

# Get video
video_repo = VideoRepository(db)
video = video_repo.get_by_id("video-uuid")

# Check video is ready
if video.transformation_status != "transformed":
    print("Video not transformed yet")
    return

# Upload video
upload_service = YouTubeUploadService(db)
try:
    result = upload_service.upload_video(
        video_id=video.id,
        thumbnail_path="/path/to/thumbnail.jpg",
        metadata_override={
            "title": "My Custom Title",
            "privacy": "unlisted",  # Test with unlisted
        },
    )
    
    print(f"Success! Video URL: {result['video_url']}")
    
except ProcessingError as e:
    print(f"Upload failed: {e}")
except AuthenticationError as e:
    print(f"Authentication error: {e}")
```

## Troubleshooting

### Upload Stuck at 0%

- Check network connectivity
- Verify S3 download succeeded
- Check YouTube API status

### Quota Exceeded

- Wait for daily quota reset (midnight Pacific Time)
- Request quota increase from Google Cloud Console
- Reduce upload frequency

### Authentication Errors

- Re-authenticate channel (see [YOUTUBE-AUTH.md](./YOUTUBE-AUTH.md))
- Check OAuth scopes include `youtube.upload`
- Verify credentials are valid

### S3 Download Errors

- Verify AWS credentials are configured
- Check S3 URL format is correct
- Ensure video file exists in S3 bucket

## Related Documentation

- [YouTube Authentication](./YOUTUBE-AUTH.md)
- [Video Processing Pipeline](../../docs/stories/2.5.video-processing-queue-workflow.md)
- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3/docs/videos/insert)
