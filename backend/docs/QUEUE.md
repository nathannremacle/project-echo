# Video Processing Queue Documentation

## Overview

The video processing queue manages the workflow of videos through the pipeline: scraping → downloading → transforming → publishing. The queue system ensures efficient processing, proper prioritization, retry handling, and monitoring capabilities.

## Queue Architecture

The queue is database-based, using the `VideoProcessingJob` model to track all processing jobs. This approach provides:

- **Persistence**: Jobs survive system restarts
- **Monitoring**: Easy to query and monitor job status
- **Scalability**: Can be extended with message queues (Redis, RabbitMQ) in the future
- **Simplicity**: No additional infrastructure required for MVP

## Job Types

The queue supports four job types:

1. **scrape**: Scrape videos for a channel
2. **download**: Download a specific video
3. **transform**: Transform a downloaded video
4. **publish**: Publish a transformed video to YouTube (Epic 3)

## Job Status

Jobs progress through the following statuses:

- **queued**: Job is waiting to be processed
- **processing**: Job is currently being executed
- **completed**: Job completed successfully
- **failed**: Job failed (may be retried)
- **retrying**: Job is scheduled for retry after backoff delay

## Priority System

Jobs are processed in priority order (higher priority first):

- **0**: Normal priority (default)
- **1-5**: Medium priority
- **6-9**: High priority
- **10**: Urgent (scheduled publications, manual triggers)

When priorities are equal, jobs are processed in FIFO order (oldest first).

## Usage Examples

### Enqueue a Job

```python
from src.services.orchestration.queue_service import QueueService

service = QueueService(db)

# Enqueue download job with normal priority
job = service.enqueue_job(
    video_id="video-123",
    job_type="download",
    priority=0,
)

# Enqueue urgent transform job
job = service.enqueue_job(
    video_id="video-123",
    job_type="transform",
    priority=10,  # Urgent
)
```

### Process Jobs

```python
# Process next job
job = service.process_next_job()

# Process batch of jobs
jobs = service.process_batch(batch_size=5)

# Process specific job type
job = service.process_next_job(job_type="download")
```

### Monitor Queue

```python
# Get pending jobs
pending = service.get_pending_jobs(limit=10)

# Get processing jobs
processing = service.get_processing_jobs()

# Get failed jobs
failed = service.get_failed_jobs(max_attempts_reached=True)

# Get queue statistics
stats = service.get_statistics()
print(f"Queue length: {stats['queue_length']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average processing time: {stats['average_processing_time']}s")
```

### Retry Failed Jobs

```python
# Retry a specific job
retried = service.retry_job(job_id)

# Process retrying jobs (after backoff delay)
ready_jobs = service.process_retrying_jobs()
```

### Pause/Resume Queue

```python
# Pause queue processing
service.pause()

# Resume queue processing
service.resume()

# Check if paused
if service.is_paused():
    print("Queue is paused")
```

## Retry Mechanism

### Automatic Retry

When a job fails:

1. Job status → "failed"
2. If `attempts < max_attempts`:
   - Job status → "retrying"
   - Backoff delay calculated: `1s * 2^(attempts-1)`
   - Job queued_at updated to current time + backoff delay
3. When backoff delay elapses, job moves back to "queued"
4. Job is retried with incremented attempt count

### Manual Retry

```python
# Retry a failed job manually
retried = service.retry_job(job_id)
```

### Retry Limits

- Default `max_attempts`: 3
- Configurable per job when enqueuing
- Jobs that reach max attempts are permanently failed

## Batch Processing

Process multiple jobs in sequence:

```python
# Process batch of 5 jobs
jobs = service.process_batch(batch_size=5, job_type="download")
```

Batch processing:
- Processes jobs in priority order
- Continues even if individual jobs fail
- Returns list of processed jobs
- Respects queue pause state

## Queue Statistics

Get comprehensive queue statistics:

```python
stats = service.get_statistics()

# Available statistics:
# - total_jobs: Total number of jobs
# - queued: Number of queued jobs
# - processing: Number of currently processing jobs
# - completed: Number of completed jobs
# - failed: Number of failed jobs
# - retrying: Number of retrying jobs
# - success_rate: Percentage of successful jobs
# - average_processing_time: Average time to complete jobs (seconds)
# - average_wait_time: Average time jobs wait before processing (seconds)
# - queue_length: Current queue length (same as queued)
```

Filter statistics by job type:

```python
# Get statistics for download jobs only
stats = service.get_statistics(job_type="download")
```

## GitHub Actions Integration

Link jobs to GitHub Actions workflows:

```python
# Enqueue job with workflow run ID
job = service.enqueue_job(
    video_id="video-123",
    job_type="download",
    github_workflow_run_id="12345678",
)

# Update job status from workflow
updated = service.update_job_from_workflow(
    job_id=job.id,
    status="completed",
)
```

## Asynchronous Processing

The queue service provides structure for asynchronous processing:

- **Current**: Synchronous processing via `process_next_job()` and `process_batch()`
- **Future**: Can be extended with:
  - Background worker threads
  - Async/await with asyncio
  - Celery or RQ for distributed processing
  - Message queue integration (Redis, RabbitMQ)

### Background Worker Example (Future)

```python
import threading
import time

def queue_worker(service: QueueService):
    """Background worker to process jobs"""
    while True:
        if not service.is_paused():
            job = service.process_next_job()
            if not job:
                time.sleep(5)  # Wait if no jobs
        else:
            time.sleep(10)  # Wait longer if paused

# Start worker thread
worker = threading.Thread(target=queue_worker, args=(service,))
worker.daemon = True
worker.start()
```

## Error Handling

The queue service handles errors gracefully:

1. **Job Execution Errors**: Caught and logged, job marked as failed
2. **Retry Logic**: Automatic retry with exponential backoff
3. **Max Attempts**: Jobs that exceed max attempts are permanently failed
4. **Error Details**: Stored in `error_message` and `error_details` (JSON)

## Best Practices

1. **Set Appropriate Priorities**: Use higher priorities for urgent jobs (scheduled publications)
2. **Monitor Queue Statistics**: Regularly check queue length and success rates
3. **Handle Failed Jobs**: Review and retry failed jobs manually if needed
4. **Pause for Maintenance**: Pause queue before system maintenance
5. **Batch Processing**: Use batch processing for efficiency when processing many jobs
6. **Monitor Processing Times**: Track average processing times to identify bottlenecks

## Troubleshooting

### Jobs Not Processing

1. Check if queue is paused: `service.is_paused()`
2. Check for queued jobs: `service.get_pending_jobs()`
3. Verify job status is "queued"
4. Check for processing errors in logs

### High Failure Rate

1. Review failed jobs: `service.get_failed_jobs()`
2. Check error messages and details
3. Verify dependencies (S3, FFmpeg, etc.)
4. Review retry attempts and backoff delays

### Slow Processing

1. Check queue statistics for average processing times
2. Review batch size (may need adjustment)
3. Check system resources (CPU, disk I/O)
4. Consider parallel processing (future enhancement)

## Related Documentation

- [Video Processing Pipeline](../../docs/stories/2.5.video-processing-queue-workflow.md)
- [Database Models](../../src/models/job.py)
- [Job Repository](../../src/repositories/job_repository.py)
