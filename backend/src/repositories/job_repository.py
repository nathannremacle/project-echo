"""
VideoProcessingJob repository - data access layer for processing jobs
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.models.job import VideoProcessingJob
from src.utils.exceptions import NotFoundError


class JobRepository:
    """Repository for job data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, job: VideoProcessingJob) -> VideoProcessingJob:
        """Create a new job"""
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: str) -> Optional[VideoProcessingJob]:
        """Get job by ID"""
        return self.db.query(VideoProcessingJob).filter(VideoProcessingJob.id == job_id).first()

    def get_by_video_id(self, video_id: str) -> List[VideoProcessingJob]:
        """Get all jobs for a video"""
        return (
            self.db.query(VideoProcessingJob)
            .filter(VideoProcessingJob.video_id == video_id)
            .order_by(VideoProcessingJob.created_at.desc())
            .all()
        )

    def get_by_channel_id(self, channel_id: str) -> List[VideoProcessingJob]:
        """Get all jobs for a channel"""
        return (
            self.db.query(VideoProcessingJob)
            .filter(VideoProcessingJob.channel_id == channel_id)
            .order_by(VideoProcessingJob.created_at.desc())
            .all()
        )

    def get_queued_jobs(self, job_type: Optional[str] = None, limit: Optional[int] = None) -> List[VideoProcessingJob]:
        """Get queued jobs, optionally filtered by job type, ordered by priority"""
        query = (
            self.db.query(VideoProcessingJob)
            .filter(VideoProcessingJob.status == "queued")
            .order_by(desc(VideoProcessingJob.priority), VideoProcessingJob.queued_at)
        )
        
        if job_type:
            query = query.filter(VideoProcessingJob.job_type == job_type)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def get_failed_jobs(self, max_attempts_reached: bool = False) -> List[VideoProcessingJob]:
        """Get failed jobs, optionally filtered by max attempts reached"""
        query = self.db.query(VideoProcessingJob).filter(VideoProcessingJob.status == "failed")
        
        if max_attempts_reached:
            query = query.filter(
                VideoProcessingJob.attempts >= VideoProcessingJob.max_attempts
            )
        
        return query.all()

    def get_retrying_jobs(self) -> List[VideoProcessingJob]:
        """Get jobs in retrying status"""
        return (
            self.db.query(VideoProcessingJob)
            .filter(VideoProcessingJob.status == "retrying")
            .order_by(VideoProcessingJob.queued_at)
            .all()
        )

    def get_all(
        self,
        status: Optional[str] = None,
        channel_id: Optional[str] = None,
        job_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[List[VideoProcessingJob], int]:
        """Get all jobs with optional filters, ordered by created_at desc"""
        query = self.db.query(VideoProcessingJob)
        if status:
            query = query.filter(VideoProcessingJob.status == status)
        if channel_id:
            query = query.filter(VideoProcessingJob.channel_id == channel_id)
        if job_type:
            query = query.filter(VideoProcessingJob.job_type == job_type)
        total = query.count()
        query = query.order_by(desc(VideoProcessingJob.created_at))
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        jobs = query.all()
        return jobs, total

    def update(self, job: VideoProcessingJob) -> VideoProcessingJob:
        """Update an existing job"""
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job_id: str) -> bool:
        """Delete a job"""
        job = self.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found", resource_type="job")
        self.db.delete(job)
        self.db.commit()
        return True
