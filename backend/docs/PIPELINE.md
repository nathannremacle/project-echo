# Video Processing Pipeline Documentation

## Overview

This guide explains how to execute the complete video processing pipeline end-to-end: scrape → download → transform → upload. The pipeline can be run via CLI script, programmatically, or via GitHub Actions workflow.

## Pipeline Steps

The complete pipeline consists of four main steps:

1. **Scrape**: Discover videos for a channel or scrape a specific video URL
2. **Download**: Download the video to cloud storage (S3)
3. **Transform**: Apply transformations to the video (color grading, effects, etc.)
4. **Upload**: Upload the transformed video to YouTube

## Prerequisites

1. **Channel Configuration**: Channel must be configured with:
   - YouTube API credentials (OAuth)
   - Metadata template
   - Transformation preset (optional)
   - Content filters

2. **Environment Variables**: Required environment variables:
   - `ENCRYPTION_KEY`: For credential decryption
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_BUCKET`: For S3 storage
   - Database connection configured

3. **Dependencies**: All Python dependencies installed (see `requirements.txt`)

## CLI Usage

### Basic Pipeline Execution

Execute complete pipeline for a channel:

```bash
python backend/scripts/run_pipeline.py --channel-id <channel_id>
```

### Scrape Specific URL

Scrape and process a specific video URL:

```bash
python backend/scripts/run_pipeline.py \
  --channel-id <channel_id> \
  --source-url "https://youtube.com/watch?v=VIDEO_ID"
```

### Process Existing Video

Process an existing video (skip scraping):

```bash
python backend/scripts/run_pipeline.py \
  --channel-id <channel_id> \
  --video-id <video_id>
```

### Test Mode (Skip Upload)

Test pipeline without uploading to YouTube:

```bash
python backend/scripts/run_pipeline.py \
  --channel-id <channel_id> \
  --skip-upload
```

### Verbose Logging

Enable verbose logging for debugging:

```bash
python backend/scripts/run_pipeline.py \
  --channel-id <channel_id> \
  --verbose
```

## Programmatic Usage

### Execute Pipeline

```python
from src.database import SessionLocal
from src.services.orchestration.pipeline_service import PipelineService

db = SessionLocal()
pipeline_service = PipelineService(db)

# Execute complete pipeline
results = pipeline_service.execute_pipeline(
    channel_id="channel-uuid",
    source_url="https://youtube.com/watch?v=VIDEO_ID",  # Optional
    video_id="video-uuid",  # Optional (skip scraping)
    skip_upload=False,  # Set to True for testing
)

print(f"Status: {results['status']}")
print(f"Duration: {results['total_duration']}s")
print(f"YouTube URL: {results.get('youtube_video_url')}")
```

### Pipeline Results

The pipeline returns a dictionary with:

- `status`: "completed" or "failed"
- `total_duration`: Total execution time in seconds
- `video_id`: Database video ID
- `youtube_video_id`: YouTube video ID (if uploaded)
- `youtube_video_url`: YouTube video URL (if uploaded)
- `steps`: Dictionary with results for each step:
  - `scrape`: Scraping results
  - `download`: Download results
  - `transform`: Transformation results
  - `upload`: Upload results
- `errors`: List of errors encountered

### Example Results

```python
{
    "status": "completed",
    "total_duration": 245.67,
    "video_id": "video-uuid",
    "youtube_video_id": "youtube_video_id_123",
    "youtube_video_url": "https://www.youtube.com/watch?v=youtube_video_id_123",
    "steps": {
        "scrape": {
            "status": "completed",
            "duration": 12.34,
            "videos_found": 1,
            "video_id": "video-uuid"
        },
        "download": {
            "status": "completed",
            "duration": 45.67,
            "download_url": "s3://bucket/video.mp4",
            "download_size": 104857600
        },
        "transform": {
            "status": "completed",
            "duration": 123.45,
            "transformed_url": "s3://bucket/transformed.mp4",
            "transformed_size": 105267200
        },
        "upload": {
            "status": "completed",
            "duration": 64.21,
            "youtube_video_id": "youtube_video_id_123",
            "youtube_video_url": "https://www.youtube.com/watch?v=youtube_video_id_123"
        }
    },
    "errors": []
}
```

## GitHub Actions Workflow

### Workflow Configuration

Create a workflow file (e.g., `.github/workflows/run-pipeline.yaml`):

```yaml
name: Run Video Processing Pipeline

on:
  workflow_dispatch:
    inputs:
      channel_id:
        description: 'Channel ID to process'
        required: true
      source_url:
        description: 'Optional source URL to scrape'
        required: false
      skip_upload:
        description: 'Skip upload step (for testing)'
        type: boolean
        default: false

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run pipeline
        env:
          ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          AWS_S3_BUCKET: ${{ secrets.AWS_S3_BUCKET }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          cd backend
          python scripts/run_pipeline.py \
            --channel-id "${{ inputs.channel_id }}" \
            ${{ inputs.source_url && format('--source-url {0}', inputs.source_url) || '' }} \
            ${{ inputs.skip_upload && '--skip-upload' || '' }}
```

### Triggering Workflow

1. Go to GitHub Actions tab
2. Select "Run Video Processing Pipeline"
3. Click "Run workflow"
4. Enter channel ID and optional parameters
5. Click "Run workflow"

## Error Handling

### Pipeline Errors

The pipeline handles errors at each step:

- **Scrape Error**: Pipeline stops, error logged
- **Download Error**: Pipeline stops, error logged
- **Transform Error**: Pipeline stops, error logged
- **Upload Error**: Pipeline stops, error logged

### Error Recovery

If pipeline fails:

1. Check error messages in results
2. Fix the underlying issue
3. Re-run pipeline with `--video-id` to resume from failed step

### Common Errors

#### Channel Not Found

```
NotFoundError: Channel <channel_id> not found
```

**Solution**: Verify channel ID is correct and channel exists in database.

#### Scraping Failed

```
ProcessingError: Pipeline failed at scrape step: No videos found
```

**Solution**: Check source URL is valid, or channel has videos to scrape.

#### Download Failed

```
ProcessingError: Pipeline failed at download step: Failed to download video
```

**Solution**: Check S3 credentials and network connectivity.

#### Transformation Failed

```
ProcessingError: Pipeline failed at transform step: FFmpeg error
```

**Solution**: Check FFmpeg is installed and video file is valid.

#### Upload Failed

```
ProcessingError: Pipeline failed at upload step: Authentication failed
```

**Solution**: Check YouTube API credentials are valid and channel is authenticated.

## Performance

### Typical Execution Times

- **Scrape**: 5-15 seconds
- **Download**: 30-120 seconds (depends on video size)
- **Transform**: 60-300 seconds (depends on video length and effects)
- **Upload**: 60-300 seconds (depends on video size)
- **Total**: 2-10 minutes (typical)

### Optimization Tips

1. **Use Existing Videos**: Skip scraping with `--video-id` to save time
2. **Test Mode**: Use `--skip-upload` for faster testing
3. **Parallel Processing**: Process multiple videos in parallel (future enhancement)

## Monitoring

### Logging

Pipeline execution is logged at each step:

```
INFO: Starting pipeline execution for channel abc-123
INFO: Step 1: Scraping videos...
INFO: Scraping completed: 1 videos found, using video xyz-456
INFO: Step 2: Downloading video...
INFO: Download completed: s3://bucket/video.mp4
INFO: Step 3: Transforming video...
INFO: Transformation completed: s3://bucket/transformed.mp4
INFO: Step 4: Uploading video to YouTube...
INFO: Upload completed: https://www.youtube.com/watch?v=VIDEO_ID
INFO: Pipeline execution completed successfully in 245.67s
```

### Status Tracking

Video status is updated at each step:

- `pending` → `scraped` → `downloaded` → `transformed` → `published`

Check video status in database or via API.

## Testing

### Test Pipeline

Test pipeline without uploading:

```bash
python backend/scripts/run_pipeline.py \
  --channel-id <channel_id> \
  --skip-upload
```

### Test with Sample Video

Use a known video URL for testing:

```bash
python backend/scripts/run_pipeline.py \
  --channel-id <channel_id> \
  --source-url "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --skip-upload
```

## Troubleshooting

### Pipeline Stuck

- Check logs for errors
- Verify all services are running
- Check database connectivity
- Verify S3 credentials

### Slow Execution

- Check network connectivity
- Verify S3 upload/download speeds
- Check FFmpeg performance
- Monitor system resources

### Upload Failures

- Verify YouTube API credentials
- Check API quota not exceeded
- Verify video meets YouTube requirements
- Check network connectivity

## Related Documentation

- [Queue Service](./QUEUE.md)
- [Video Upload](./YOUTUBE-UPLOAD.md)
- [Transformation](./TRANSFORMATION.md)
- [GitHub Actions Setup](../../docs/GITHUB-ACTIONS-SETUP.md)
