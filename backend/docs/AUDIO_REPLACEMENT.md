# Audio Replacement Documentation

## Overview

The Audio Replacement Service handles replacing audio tracks in videos with user's personal music tracks. This is a core feature of Phase 2, enabling the "viral wave" music promotion strategy.

## Features

### Audio Replacement

- **FFmpeg-based**: Uses FFmpeg for high-quality audio replacement
- **Quality Preservation**: Copies video stream without re-encoding to maintain quality
- **Format Support**: Handles various audio formats (MP3, WAV, M4A, OGG, etc.)
- **Audio Processing**: Normalization, volume matching, and quality settings
- **Duration Management**: Loops or trims audio to match video duration

### Processing Options

- **Single Video**: Replace audio in one video
- **Batch Processing**: Replace audio in multiple videos
- **Channel-wide**: Replace audio for all videos in a channel
- **Queue Integration**: Process videos from queue

## API Endpoints

### Replace Audio for Single Video

```http
POST /api/videos/{video_id}/replace-audio
Content-Type: application/json

{
  "music_id": "uuid",
  "normalize": true,
  "match_volume": false,
  "audio_bitrate": "192k",
  "audio_sample_rate": 44100,
  "loop_audio": true
}
```

**Response:**
```json
{
  "video_id": "uuid",
  "music_id": "uuid",
  "output_url": "s3://bucket/...",
  "audio_duration": 180,
  "video_duration": 200
}
```

### Batch Replace Audio

```http
POST /api/videos/batch-replace-audio
Content-Type: application/json

{
  "video_ids": ["uuid1", "uuid2", "uuid3"],
  "music_id": "uuid",
  "normalize": true,
  "loop_audio": true
}
```

**Response:**
```json
{
  "success": [
    {"video_id": "uuid1", "music_id": "uuid", "output_url": "..."},
    {"video_id": "uuid2", "music_id": "uuid", "output_url": "..."}
  ],
  "failed": [
    {"video_id": "uuid3", "error": "..."}
  ],
  "total": 3
}
```

### Replace Audio for Channel

```http
POST /api/videos/channels/{channel_id}/replace-audio
Content-Type: application/json

{
  "music_id": "uuid",
  "normalize": true,
  "loop_audio": true
}
```

**Response:** Same as batch replace response

## Usage

### Basic Audio Replacement

```python
from src.services.audio_replacement.audio_replacement_service import AudioReplacementService

service = AudioReplacementService(db)

result = service.replace_audio_for_video(
    video_id="video-uuid",
    music_id="music-uuid",
    normalize=True,
    loop_audio=True,
)
```

### Batch Processing

```python
result = service.replace_audio_batch(
    video_ids=["video1", "video2", "video3"],
    music_id="music-uuid",
    normalize=True,
)
```

### Channel-wide Replacement

```python
result = service.replace_audio_for_channel(
    channel_id="channel-uuid",
    music_id="music-uuid",
    normalize=True,
)
```

## Audio Processing Options

### Normalization

- **Purpose**: Normalize audio levels for consistent volume
- **Default**: Enabled
- **Implementation**: Uses FFmpeg `loudnorm` filter
- **Settings**: I=-16.0, TP=-1.5, LRA=11.0

### Volume Matching

- **Purpose**: Match volume to original video audio
- **Default**: Disabled
- **Note**: Requires audio analysis (simplified in MVP)

### Audio Quality

- **Bitrate**: Audio bitrate (e.g., "192k", "256k")
- **Sample Rate**: Audio sample rate in Hz (e.g., 44100, 48000)
- **Codec**: AAC (default, widely supported)

### Duration Management

- **Loop Audio**: If audio is shorter than video, loop it
- **Trim Audio**: If audio is longer than video, trim to match
- **Default**: Loop enabled

## Technical Details

### FFmpeg Processing

1. **Video Stream**: Copied without re-encoding (`vcodec=copy`)
2. **Audio Stream**: Replaced with music track
3. **Audio Encoding**: AAC codec with configurable bitrate/sample rate
4. **Duration**: Audio looped or trimmed to match video

### Quality Preservation

- Video stream is copied (no re-encoding)
- Original video quality maintained
- Only audio track is replaced
- Fast processing (no video encoding)

### Storage

- Output files stored in S3
- Organization: `{channel_id}/{video_id}/{filename}`
- Original files preserved
- New files replace `transformed_url` in video record

## Error Handling

### Common Errors

- **Video Not Found**: 404 if video doesn't exist
- **Music Not Found**: 404 if music track doesn't exist
- **No File URL**: 400 if video has no file to process
- **FFmpeg Error**: 500 if processing fails
- **Storage Error**: 500 if S3 upload fails

### Job Tracking

- Jobs created with type `music_replace`
- Status tracked: processing, completed, failed
- Error messages logged
- Retry logic supported

## Best Practices

1. **Test First**: Test with sample videos before batch processing
2. **Normalize Audio**: Enable normalization for consistent volume
3. **Monitor Jobs**: Track job status for batch operations
4. **Quality Settings**: Use appropriate bitrate/sample rate for quality
5. **Backup**: Original files preserved in S3
6. **Incremental**: Process videos incrementally for large batches

## Related Documentation

- [Music File Management](./MUSIC.md)
- [Video Transformation](./TRANSFORMATION.md)
- [Queue Service](./QUEUE.md)
- [Phase 2 Features](./PHASE2.md)
