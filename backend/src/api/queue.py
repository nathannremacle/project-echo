"""
Queue API endpoints - jobs and videos for the processing queue
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.orchestration.queue_service import QueueService
from src.repositories.job_repository import JobRepository
from src.repositories.video_repository import VideoRepository
from src.repositories.statistics_repository import StatisticsRepository
from src.utils.exceptions import NotFoundError, ValidationError


def _job_to_dict(job) -> dict:
    """Convert job ORM to camelCase dict for frontend"""
    return {
        "id": job.id,
        "videoId": job.video_id,
        "channelId": job.channel_id,
        "jobType": job.job_type,
        "status": job.status,
        "priority": job.priority,
        "attempts": job.attempts,
        "maxAttempts": job.max_attempts,
        "errorMessage": job.error_message,
        "errorDetails": job.error_details,
        "queuedAt": job.queued_at.isoformat() if job.queued_at else None,
        "startedAt": job.started_at.isoformat() if job.started_at else None,
        "completedAt": job.completed_at.isoformat() if job.completed_at else None,
        "duration": job.duration,
        "githubWorkflowRunId": job.github_workflow_run_id,
        "createdAt": job.created_at.isoformat() if job.created_at else None,
        "updatedAt": job.updated_at.isoformat() if job.updated_at else None,
    }


def _video_to_dict(video) -> dict:
    """Convert video ORM to camelCase dict for frontend"""
    return {
        "id": video.id,
        "channelId": video.channel_id,
        "sourceUrl": video.source_url,
        "sourceTitle": video.source_title,
        "sourceCreator": video.source_creator,
        "sourcePlatform": video.source_platform,
        "scrapedAt": video.scraped_at.isoformat() if video.scraped_at else None,
        "downloadStatus": video.download_status,
        "downloadUrl": video.download_url,
        "downloadSize": video.download_size,
        "downloadDuration": video.download_duration,
        "downloadResolution": video.download_resolution,
        "transformationStatus": video.transformation_status,
        "transformedUrl": video.transformed_url,
        "transformedSize": video.transformed_size,
        "processingDuration": video.processing_duration,
        "publicationStatus": video.publication_status,
        "youtubeVideoId": video.youtube_video_id,
        "youtubeUrl": video.youtube_video_url,
        "createdAt": video.created_at.isoformat() if video.created_at else None,
        "updatedAt": video.updated_at.isoformat() if video.updated_at else None,
    }


router = APIRouter(tags=["Queue"])


# --- Jobs ---

@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    channelId: Optional[str] = Query(None, description="Filter by channel ID"),
    jobType: Optional[str] = Query(None, description="Filter by job type"),
    limit: Optional[int] = Query(None, description="Max number of jobs"),
    offset: Optional[int] = Query(None, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """List processing jobs with optional filters"""
    job_repo = JobRepository(db)
    jobs, total = job_repo.get_all(
        status=status,
        channel_id=channelId,
        job_type=jobType,
        limit=limit,
        offset=offset,
    )
    return {
        "jobs": [_job_to_dict(j) for j in jobs],
        "total": total,
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    """Get job by ID"""
    job_repo = JobRepository(db)
    job = job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return _job_to_dict(job)


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    """Cancel a queued or retrying job"""
    service = QueueService(db)
    try:
        service.cancel_job(job_id)
        return {"message": "Job cancelled successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Videos ---

@router.get("/videos")
async def list_videos(
    status: Optional[str] = Query(None, description="Filter by status (download/transformation/publication)"),
    channelId: Optional[str] = Query(None, description="Filter by channel ID"),
    limit: Optional[int] = Query(None, description="Max number of videos"),
    offset: Optional[int] = Query(None, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """List videos with optional filters"""
    video_repo = VideoRepository(db)
    videos, total = video_repo.get_all(
        channel_id=channelId,
        status=status,
        limit=limit,
        offset=offset,
    )
    return {
        "videos": [_video_to_dict(v) for v in videos],
        "total": total,
    }


@router.get("/videos/{video_id}")
async def get_video(
    video_id: str,
    db: Session = Depends(get_db),
):
    """Get video by ID"""
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
    return _video_to_dict(video)


@router.get("/videos/{video_id}/statistics")
async def get_video_statistics(
    video_id: str,
    db: Session = Depends(get_db),
):
    """Get video statistics with history"""
    video_repo = VideoRepository(db)
    stats_repo = StatisticsRepository(db)
    video = video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
    history = stats_repo.get_video_statistics(video_id, limit=30)

    def _stats_to_dict(s):
        return {
            "id": s.id,
            "videoId": s.video_id,
            "views": s.view_count or 0,
            "likes": s.like_count or 0,
            "comments": s.comment_count or 0,
            "shares": 0,
            "watchTime": None,
            "averageViewDuration": None,
            "recordedAt": s.timestamp.isoformat() if s.timestamp else None,
        }

    history_list = [_stats_to_dict(h) for h in history]
    current = history_list[0] if history_list else None
    return {
        "current": current,
        "history": history_list,
    }


@router.post("/videos/{video_id}/retry")
async def retry_video(
    video_id: str,
    db: Session = Depends(get_db),
):
    """Retry the most recent failed job for a video"""
    service = QueueService(db)
    try:
        video = service.retry_video(video_id)
        return _video_to_dict(video)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db),
):
    """Delete a video"""
    video_repo = VideoRepository(db)
    try:
        video_repo.delete(video_id)
        return {"message": "Video deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
