# Video Processing Queue Documentation

## Overview

The Video Processing Queue page provides a comprehensive view of all videos and processing jobs in the system. Users can monitor processing status, manage the queue, and take actions on individual items.

## Features

### Queue Display

The queue displays:

- **Video Information**: Source title, creator, platform
- **Job Type**: Scrape, Download, Transform, or Publish
- **Status**: Queued, Processing, Completed, Failed, or Retrying
- **Channel Assignment**: Which channel the video is assigned to
- **Progress Indicators**: Visual progress for processing jobs
- **Duration**: Processing time for completed jobs
- **Queue Time**: How long the item has been in queue

### Queue Actions

Available actions for queue items:

- **Preview**: View transformed video before publication (if available)
- **Retry**: Retry failed videos/jobs
- **Cancel**: Cancel processing jobs
- **Delete**: Remove videos from queue
- **Prioritize**: Move items to top of queue

### Queue Filters

Filter queue items by:

- **Status**: Queued, Processing, Completed, Failed, Retrying
- **Channel**: Filter by specific channel
- **Job Type**: Scrape, Download, Transform, Publish
- **Date Range**: Filter by start and end dates

### Queue Statistics

Display key metrics:

- **Total Items**: Total number of items in queue
- **Success Rate**: Percentage of successfully completed jobs
- **Failed Count**: Number of failed jobs
- **Average Processing Time**: Average time to process jobs

## Usage

### Viewing the Queue

1. Navigate to the Queue page from the sidebar
2. View all processing jobs and videos
3. Use filters to narrow down the list
4. Check statistics for overall queue health

### Managing Queue Items

1. **Retry Failed Items**: Click the retry button on failed items
2. **Cancel Processing**: Click cancel to stop a processing job
3. **Delete Items**: Click delete to remove items from queue
4. **Prioritize Items**: Click prioritize to move items to top

### Filtering

1. Select filters from the filter bar
2. Queue automatically updates based on filters
3. Click "Clear" to reset all filters

## Auto-Refresh

The queue automatically refreshes every 10 seconds to show the latest status. Statistics refresh every 30 seconds. You can also manually refresh using the refresh button.

## Components

### QueueList

Displays the queue in a table format:
- Video information
- Job type and status
- Channel assignment
- Progress indicators
- Action buttons

### QueueFilters

Filter controls:
- Status dropdown
- Channel dropdown
- Job type dropdown
- Date range inputs
- Clear button

### QueueStatistics

Statistics cards:
- Total items
- Success rate
- Failed count
- Average processing time

## API Endpoints

The queue uses the following endpoints:

- `GET /api/jobs` - List processing jobs
- `GET /api/jobs/{jobId}` - Get job details
- `POST /api/jobs/{jobId}/cancel` - Cancel job
- `GET /api/videos` - List videos
- `GET /api/videos/{videoId}` - Get video details
- `POST /api/videos/{videoId}/retry` - Retry failed video
- `DELETE /api/videos/{videoId}` - Delete video

## Best Practices

1. **Monitor Regularly**: Check the queue regularly to identify issues
2. **Review Failed Items**: Investigate and retry failed items promptly
3. **Use Filters**: Use filters to focus on specific items
4. **Check Statistics**: Monitor statistics to track queue health
5. **Prioritize Important Items**: Use prioritize for urgent items

## Related Documentation

- [Frontend README](../README.md)
- [Dashboard Documentation](./DASHBOARD.md)
- [Queue Service API](../../backend/docs/QUEUE-SERVICE.md)
