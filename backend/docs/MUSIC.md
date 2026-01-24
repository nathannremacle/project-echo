# Music File Management Documentation

## Overview

The Music Service handles upload, storage, and management of personal music files for Phase 2 (music replacement feature). Music files are validated, stored securely in cloud storage (S3), and can be previewed before use.

## Features

### File Upload

- **Supported Formats**: MP3, WAV, M4A, OGG, FLAC, AAC
- **File Size Limit**: 50MB maximum
- **Duration Limits**: 30 seconds to 10 minutes
- **Validation**: Format, size, and duration validation before upload
- **Metadata**: Track name, artist, Spotify URL, and additional metadata

### Storage

- **Cloud Storage**: Files stored in AWS S3
- **Organization**: Files organized as `music/{music_id}/{filename}`
- **Security**: Secure storage with access control
- **Tracking**: File size, location, and usage count tracked

### Management

- **List Tracks**: Get all music tracks (with optional active filter)
- **Get Track**: Retrieve specific track details
- **Delete Track**: Remove track and file from storage
- **Preview**: Generate presigned URLs for preview

## API Endpoints

### List Music Tracks

```http
GET /api/music?active_only=true
```

**Response:**
```json
{
  "tracks": [
    {
      "id": "uuid",
      "name": "Track Name",
      "artist": "Artist Name",
      "spotifyUrl": "https://open.spotify.com/track/...",
      "fileSize": 5242880,
      "duration": 180,
      "usageCount": 5,
      "isActive": true,
      "uploadedAt": "2026-01-23T10:00:00Z"
    }
  ]
}
```

### Upload Music Track

```http
POST /api/music
Content-Type: multipart/form-data

file: <audio file>
name: Track Name
artist: Artist Name (optional)
spotifyUrl: https://open.spotify.com/track/... (optional)
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Track Name",
  "artist": "Artist Name",
  "spotifyUrl": "https://open.spotify.com/track/...",
  "fileSize": 5242880,
  "duration": 180,
  "usageCount": 0,
  "isActive": true,
  "uploadedAt": "2026-01-23T10:00:00Z"
}
```

### Get Music Track

```http
GET /api/music/{music_id}
```

**Response:** Same as upload response

### Delete Music Track

```http
DELETE /api/music/{music_id}
```

**Response:**
```json
{
  "message": "Music track deleted successfully"
}
```

### Get Preview URL

```http
GET /api/music/{music_id}/preview?expires_in=3600
```

**Response:**
```json
{
  "previewUrl": "https://s3.amazonaws.com/...",
  "expiresIn": 3600
}
```

## Usage

### Uploading Music

```python
from src.services.music.music_service import MusicService

service = MusicService(db)

with open("track.mp3", "rb") as file:
    music = service.upload_music(
        file=file,
        filename="track.mp3",
        name="My Track",
        artist="My Artist",
        spotify_url="https://open.spotify.com/track/...",
    )
```

### Listing Music

```python
tracks = service.list_music(active_only=True)
```

### Getting Preview URL

```python
preview_url = service.get_preview_url(music_id, expires_in=3600)
```

### Deleting Music

```python
service.delete_music(music_id)
```

## Validation

### Format Validation

- Only supported formats are accepted
- File extension must match actual file format
- Unsupported formats return validation error

### Size Validation

- Maximum file size: 50MB
- Empty files are rejected
- File size is tracked in database

### Duration Validation

- Minimum duration: 30 seconds
- Maximum duration: 10 minutes
- Duration extracted using ffmpeg (if available) or estimated

## Storage Organization

Files are organized in S3 as:
```
s3://bucket-name/music/{music_id}/{filename}
```

This organization:
- Groups files by music track
- Makes deletion straightforward
- Supports easy access control

## Error Handling

### Validation Errors

- **Unsupported Format**: Returns 400 with format error
- **File Too Large**: Returns 400 with size error
- **Invalid Duration**: Returns 400 with duration error

### Processing Errors

- **Upload Failure**: Returns 500 with error details
- **Storage Error**: Returns 500 with storage error
- **Database Error**: Returns 500 with database error

## Best Practices

1. **Validate Before Upload**: Check file format and size client-side
2. **Provide Metadata**: Include track name, artist, and Spotify URL
3. **Monitor Usage**: Track which tracks are used most
4. **Clean Up**: Delete unused tracks to save storage
5. **Preview Before Use**: Use preview URLs to verify tracks

## Related Documentation

- [Storage Service](../docs/STORAGE.md)
- [API Documentation](../docs/API.md)
- [Phase 2 Features](../docs/PHASE2.md)
