"""
Queue service - manages video processing queue
Orchestrates job creation, processing, retries, and monitoring
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.job import VideoProcessingJob
from src.models.video import Video
from src.repositories.job_repository import JobRepository
from src.repositories.video_repository import VideoRepository
from src.repositories.config_repository import ConfigRepository
from src.services.scraping.scraping_service import ScrapingService
from src.services.download.download_service import DownloadService
from src.services.transformation.transformation_service import TransformationService
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError
from src.utils.common.constants import MAX_RETRY_ATTEMPTS, RETRY_BACKOFF_BASE

logger = get_logger(__name__)


class QueueService:
    """Service for managing video processing queue"""

    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.video_repo = VideoRepository(db)
        self.config_repo = ConfigRepository(db)
        
        # Initialize processing services
        self.scraping_service = ScrapingService(db)
        self.download_service = DownloadService(db)
        self.transformation_service = TransformationService(db)
        
        # Queue state
        self._paused = False

    def is_paused(self) -> bool:
        """Check if queue is paused"""
        # Check database config first
        queue_paused = self.config_repo.get("queue_paused")
        if queue_paused is not None:
            return bool(queue_paused)
        return self._paused

    def pause(self) -> None:
        """Pause queue processing"""
        self.config_repo.set("queue_paused", True, description="Queue processing paused")
        self._paused = True
        logger.info("Queue processing paused")

    def resume(self) -> None:
        """Resume queue processing"""
        self.config_repo.set("queue_paused", False, description="Queue processing resumed")
        self._paused = False
        logger.info("Queue processing resumed")

    def enqueue_job(
        self,
        video_id: str,
        job_type: str,
        priority: int = 0,
        max_attempts: int = MAX_RETRY_ATTEMPTS,
        github_workflow_run_id: Optional[str] = None,
    ) -> VideoProcessingJob:
        """
        Enqueue a new processing job
        
        Args:
            video_id: Video ID
            job_type: Type of job (scrape, download, transform, publish)
            priority: Job priority (0-10, higher = more urgent)
            max_attempts: Maximum retry attempts
            github_workflow_run_id: Optional GitHub Actions workflow run ID
            
        Returns:
            Created VideoProcessingJob object
        """
        # Validate video exists
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        # Validate job type
        valid_types = ["scrape", "download", "transform", "publish"]
        if job_type not in valid_types:
            raise ValueError(f"Invalid job_type: {job_type}. Must be one of {valid_types}")
        
        # Clamp priority to 0-10
        priority = max(0, min(10, priority))
        
        job = VideoProcessingJob(
            video_id=video_id,
            channel_id=video.channel_id,
            job_type=job_type,
            status="queued",
            priority=priority,
            max_attempts=max_attempts,
            github_workflow_run_id=github_workflow_run_id,
        )
        
        job = self.job_repo.create(job)
        logger.info(f"Enqueued {job_type} job for video {video_id} (priority: {priority})")
        
        return job

    def get_pending_jobs(self, job_type: Optional[str] = None, limit: Optional[int] = None) -> List[VideoProcessingJob]:
        """
        Get pending (queued) jobs
        
        Args:
            job_type: Optional job type filter
            limit: Optional limit on number of jobs
            
        Returns:
            List of queued jobs ordered by priority
        """
        return self.job_repo.get_queued_jobs(job_type=job_type, limit=limit)

    def get_processing_jobs(self, job_type: Optional[str] = None) -> List[VideoProcessingJob]:
        """
        Get currently processing jobs
        
        Args:
            job_type: Optional job type filter
            
        Returns:
            List of processing jobs
        """
        from src.models.job import VideoProcessingJob
        
        query = self.db.query(VideoProcessingJob).filter(VideoProcessingJob.status == "processing")
        
        if job_type:
            query = query.filter(VideoProcessingJob.job_type == job_type)
        
        return query.order_by(VideoProcessingJob.started_at).all()

    def get_failed_jobs(
        self,
        max_attempts_reached: bool = False,
        job_type: Optional[str] = None,
    ) -> List[VideoProcessingJob]:
        """
        Get failed jobs
        
        Args:
            max_attempts_reached: Only return jobs that reached max attempts
            job_type: Optional job type filter
            
        Returns:
            List of failed jobs
        """
        jobs = self.job_repo.get_failed_jobs(max_attempts_reached=max_attempts_reached)
        
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        
        return jobs

    def retry_job(self, job_id: str) -> VideoProcessingJob:
        """
        Retry a failed job
        
        Args:
            job_id: Job ID
            
        Returns:
            Updated VideoProcessingJob object
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found", resource_type="job")
        
        if job.status != "failed":
            raise ValueError(f"Job {job_id} is not in failed status (current: {job.status})")
        
        if job.attempts >= job.max_attempts:
            raise ValueError(f"Job {job_id} has reached max attempts ({job.max_attempts})")
        
        # Reset job for retry
        job.status = "queued"
        job.error_message = None
        job.error_details = None
        job.queued_at = datetime.utcnow()
        
        job = self.job_repo.update(job)
        logger.info(f"Retrying job {job_id} (attempt {job.attempts + 1}/{job.max_attempts})")
        
        return job

    def _execute_job(self, job: VideoProcessingJob) -> None:
        """
        Execute a processing job
        
        Args:
            job: VideoProcessingJob to execute
        """
        job.status = "processing"
        job.started_at = datetime.utcnow()
        job.attempts += 1
        self.job_repo.update(job)
        
        try:
            logger.info(f"Executing {job.job_type} job {job.id} for video {job.video_id}")
            
            if job.job_type == "scrape":
                # Scraping is typically done per-channel, not per-video
                # This would trigger channel scraping
                self.scraping_service.scrape_for_channel(job.channel_id)
                
            elif job.job_type == "download":
                self.download_service.download_video(job.video_id)
                
            elif job.job_type == "transform":
                # Get video to check for preset
                video = self.video_repo.get_by_id(job.video_id)
                preset_id = video.transformation_preset_id if video else None
                self.transformation_service.transform_video(job.video_id, preset_id=preset_id)
                
            elif job.job_type == "publish":
                # Publication will be implemented in Epic 3
                logger.warning(f"Publish job type not yet implemented for job {job.id}")
                raise NotImplementedError("Publish job type not yet implemented")
            
            # Mark job as completed
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            if job.started_at:
                job.duration = int((job.completed_at - job.started_at).total_seconds())
            self.job_repo.update(job)
            
            logger.info(f"Job {job.id} completed successfully in {job.duration}s")
            
        except Exception as e:
            error_message = str(e)
            error_details = json.dumps({"exception_type": type(e).__name__, "traceback": str(e)})
            
            job.status = "failed"
            job.error_message = error_message
            job.error_details = error_details
            job.completed_at = datetime.utcnow()
            if job.started_at:
                job.duration = int((job.completed_at - job.started_at).total_seconds())
            self.job_repo.update(job)
            
            logger.error(f"Job {job.id} failed: {error_message}")
            
            # Auto-retry if attempts remaining
            if job.attempts < job.max_attempts:
                # Exponential backoff - calculate delay
                backoff_time = RETRY_BACKOFF_BASE * (2 ** (job.attempts - 1))
                logger.info(f"Scheduling retry for job {job.id} in {backoff_time}s (attempt {job.attempts + 1}/{job.max_attempts})")
                
                # Update job to retrying status
                # In a real async implementation, you'd schedule the retry with the delay
                # For now, we mark it as retrying and it will be picked up by process_retrying_jobs
                job.status = "retrying"
                # Update queued_at to current time for retry scheduling
                job.queued_at = datetime.utcnow() + timedelta(seconds=backoff_time)
                self.job_repo.update(job)
            else:
                logger.warning(f"Job {job.id} has reached max attempts ({job.max_attempts}), marking as permanently failed")

    def process_retrying_jobs(self) -> List[VideoProcessingJob]:
        """
        Process jobs that are ready to retry (backoff time elapsed)
        
        Returns:
            List of processed jobs
        """
        if self.is_paused():
            return []
        
        retrying_jobs = self.job_repo.get_retrying_jobs()
        ready_jobs = [
            job for job in retrying_jobs
            if job.queued_at and job.queued_at <= datetime.utcnow()
        ]
        
        processed = []
        for job in ready_jobs:
            # Move back to queued status
            job.status = "queued"
            self.job_repo.update(job)
            processed.append(job)
        
        return processed

    def process_next_job(self, job_type: Optional[str] = None) -> Optional[VideoProcessingJob]:
        """
        Process the next queued job
        
        Args:
            job_type: Optional job type filter
            
        Returns:
            Processed VideoProcessingJob or None if no jobs available
        """
        if self.is_paused():
            logger.debug("Queue is paused, skipping job processing")
            return None
        
        # First, process any retrying jobs that are ready
        self.process_retrying_jobs()
        
        # Get next queued job
        jobs = self.get_pending_jobs(job_type=job_type, limit=1)
        
        if not jobs:
            return None
        
        job = jobs[0]
        self._execute_job(job)
        
        return job

    def process_batch(self, batch_size: int = 5, job_type: Optional[str] = None) -> List[VideoProcessingJob]:
        """
        Process a batch of jobs
        
        Args:
            batch_size: Number of jobs to process
            job_type: Optional job type filter
            
        Returns:
            List of processed jobs
        """
        if self.is_paused():
            logger.debug("Queue is paused, skipping batch processing")
            return []
        
        jobs = self.get_pending_jobs(job_type=job_type, limit=batch_size)
        processed = []
        
        for job in jobs:
            try:
                self._execute_job(job)
                processed.append(job)
            except Exception as e:
                logger.error(f"Error processing job {job.id} in batch: {str(e)}")
                # Continue with next job
        
        logger.info(f"Processed batch of {len(processed)} jobs")
        return processed

    def get_statistics(self, job_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get queue statistics
        
        Args:
            job_type: Optional job type filter
            
        Returns:
            Dictionary with queue statistics
        """
        from src.models.job import VideoProcessingJob
        
        # Base query
        base_query = self.db.query(VideoProcessingJob)
        if job_type:
            base_query = base_query.filter(VideoProcessingJob.job_type == job_type)
        
        # Count jobs by status
        total_jobs = base_query.count()
        queued_count = base_query.filter(VideoProcessingJob.status == "queued").count()
        processing_count = base_query.filter(VideoProcessingJob.status == "processing").count()
        completed_count = base_query.filter(VideoProcessingJob.status == "completed").count()
        failed_count = base_query.filter(VideoProcessingJob.status == "failed").count()
        retrying_count = base_query.filter(VideoProcessingJob.status == "retrying").count()
        
        # Calculate success rate
        success_rate = 0.0
        if completed_count + failed_count > 0:
            success_rate = completed_count / (completed_count + failed_count) * 100
        
        # Calculate average processing time for completed jobs
        completed_jobs = base_query.filter(
            VideoProcessingJob.status == "completed",
            VideoProcessingJob.duration.isnot(None),
        ).all()
        
        avg_processing_time = 0.0
        if completed_jobs:
            total_time = sum(job.duration for job in completed_jobs if job.duration)
            avg_processing_time = total_time / len(completed_jobs)
        
        # Calculate average wait time (queued to started)
        processing_jobs = base_query.filter(
            VideoProcessingJob.status == "processing",
            VideoProcessingJob.started_at.isnot(None),
            VideoProcessingJob.queued_at.isnot(None),
        ).all()
        
        avg_wait_time = 0.0
        if processing_jobs:
            total_wait = sum(
                (job.started_at - job.queued_at).total_seconds()
                for job in processing_jobs
                if job.started_at and job.queued_at
            )
            avg_wait_time = total_wait / len(processing_jobs)
        
        return {
            "total_jobs": total_jobs,
            "queued": queued_count,
            "processing": processing_count,
            "completed": completed_count,
            "failed": failed_count,
            "retrying": retrying_count,
            "success_rate": round(success_rate, 2),
            "average_processing_time": round(avg_processing_time, 2),
            "average_wait_time": round(avg_wait_time, 2),
            "queue_length": queued_count,
        }

    def update_job_from_workflow(
        self,
        job_id: str,
        status: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> VideoProcessingJob:
        """
        Update job status from GitHub Actions workflow
        
        Args:
            job_id: Job ID
            status: New status (optional)
            error_message: Error message if failed (optional)
            
        Returns:
            Updated VideoProcessingJob object
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found", resource_type="job")
        
        if status:
            job.status = status
            if status == "processing" and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in ["completed", "failed"]:
                job.completed_at = datetime.utcnow()
                if job.started_at:
                    job.duration = int((job.completed_at - job.started_at).total_seconds())
        
        if error_message:
            job.error_message = error_message
        
        job = self.job_repo.update(job)
        logger.info(f"Updated job {job_id} from workflow: status={status}")
        
        return job
