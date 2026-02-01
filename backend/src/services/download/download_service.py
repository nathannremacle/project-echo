"""
Download service - orchestrates video download and storage
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from shared.src.download import (
    VideoDownloader,
    S3StorageClient,
    LocalStorageClient,
    DownloadError,
    VideoUnavailableError,
    StorageError,
)
from src.models.video import Video
from src.models.job import VideoProcessingJob
from src.repositories.video_repository import VideoRepository
from src.repositories.job_repository import JobRepository
from src.config import settings
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError
from src.utils.common.constants import MAX_RETRY_ATTEMPTS, RETRY_BACKOFF_BASE

logger = get_logger(__name__)


class DownloadService:
    """Service for video download and storage operations"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.job_repo = JobRepository(db)
        
        # Initialize downloader with temp directory
        temp_dir = os.path.join(os.getcwd(), "temp", "downloads")
        os.makedirs(temp_dir, exist_ok=True)
        self.downloader = VideoDownloader(output_dir=temp_dir, progress_callback=self._progress_callback)
        
        # Initialize storage client: use S3/Spaces if configured; local storage only in dev when S3 not set
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.storage = S3StorageClient(
                bucket_name=settings.AWS_S3_BUCKET,
                access_key_id=settings.AWS_ACCESS_KEY_ID,
                secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region=settings.AWS_REGION,
                endpoint_url=getattr(settings, 'S3_ENDPOINT_URL', None),
            )
        elif settings.is_development():
            logger.info("S3 credentials not configured - using local file storage (development mode)")
            self.storage = LocalStorageClient(
                base_dir=os.path.join(os.getcwd(), "data", "videos"),
            )
        else:
            raise StorageError(
                "S3/Spaces credentials required in production. Configure AWS_ACCESS_KEY_ID, "
                "AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET, and S3_ENDPOINT_URL (for DigitalOcean Spaces)."
            )

    def _progress_callback(self, d: Dict[str, Any]) -> None:
        """Callback for download progress updates"""
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total > 0:
                percent = (downloaded / total) * 100
                logger.debug(f"Download progress: {percent:.1f}% ({downloaded}/{total} bytes)")

    def _update_video_status(self, video: Video, status: str, **kwargs) -> Video:
        """Update video download status"""
        video.download_status = status
        for key, value in kwargs.items():
            if hasattr(video, key):
                setattr(video, key, value)
        video.updated_at = datetime.utcnow()
        return self.video_repo.update(video)

    def _create_job(self, video_id: str, channel_id: str, job_type: str = "download") -> VideoProcessingJob:
        """Create a processing job for tracking"""
        job = VideoProcessingJob(
            video_id=video_id,
            channel_id=channel_id,
            job_type=job_type,
            status="queued",
        )
        return self.job_repo.create(job)

    def _update_job(self, job: VideoProcessingJob, status: str, error: Optional[str] = None) -> VideoProcessingJob:
        """Update job status"""
        job.status = status
        if error:
            job.error_message = error
        if status == "processing" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()
            if job.started_at:
                job.duration = int((job.completed_at - job.started_at).total_seconds())
        return self.job_repo.update(job)

    def download_video(
        self,
        video_id: str,
        max_retries: int = MAX_RETRY_ATTEMPTS,
    ) -> Video:
        """
        Download video and store in cloud storage
        
        Args:
            video_id: Video ID
            max_retries: Maximum number of retry attempts
            
        Returns:
            Updated Video object
            
        Raises:
            NotFoundError: If video not found
            DownloadError: If download fails after retries
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        # Check if already downloaded
        if video.download_status == "downloaded" and video.download_url:
            logger.info(f"Video {video_id} already downloaded")
            return video
        
        # Create job for tracking
        job = self._create_job(video_id, video.channel_id, "download")
        
        # Update video status
        self._update_video_status(video, "downloading")
        self._update_job(job, "processing")
        
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            attempt += 1
            job.attempts = attempt
            
            try:
                logger.info(f"Downloading video {video_id} (attempt {attempt}/{max_retries})")
                
                # Download video
                download_info = self.downloader.download(
                    video.source_url,
                    video_id=video_id,
                )
                
                logger.info(
                    f"Downloaded video {video_id}: {download_info['file_size']} bytes, "
                    f"{download_info['resolution']}, {download_info['duration']}s"
                )
                
                # Upload to S3
                logger.info(f"Uploading video {video_id} to S3")
                s3_url = self.storage.upload_file(
                    download_info["file_path"],
                    video.channel_id,
                    video_id,
                    metadata={
                        "source_url": video.source_url,
                        "source_title": video.source_title,
                        "duration": str(download_info["duration"]),
                        "resolution": download_info["resolution"] or "",
                    },
                )
                
                # Update video with download information
                self._update_video_status(
                    video,
                    "downloaded",
                    download_url=s3_url,
                    download_size=download_info["file_size"],
                    download_duration=download_info["duration"],
                    download_resolution=download_info["resolution"],
                )
                
                # Clean up local file
                try:
                    if os.path.exists(download_info["file_path"]):
                        os.remove(download_info["file_path"])
                        logger.debug(f"Cleaned up local file: {download_info['file_path']}")
                except Exception as e:
                    logger.warning(f"Failed to clean up local file: {e}")
                
                # Mark job as completed
                self._update_job(job, "completed")
                
                logger.info(f"Successfully downloaded and stored video {video_id}")
                return video
                
            except VideoUnavailableError as e:
                logger.warning(f"Video unavailable: {video_id} - {str(e)}")
                last_error = str(e)
                self._update_video_status(video, "failed")
                self._update_job(job, "failed", error=str(e))
                raise DownloadError(f"Video unavailable: {str(e)}") from e
                
            except (DownloadError, StorageError) as e:
                last_error = str(e)
                logger.warning(f"Download attempt {attempt} failed for video {video_id}: {str(e)}")
                
                if attempt < max_retries:
                    # Exponential backoff
                    backoff_time = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    # Final attempt failed
                    self._update_video_status(video, "failed")
                    self._update_job(job, "failed", error=str(e))
                    raise DownloadError(f"Download failed after {max_retries} attempts: {str(e)}") from e
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error downloading video {video_id}: {str(e)}")
                
                if attempt < max_retries:
                    backoff_time = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    time.sleep(backoff_time)
                else:
                    self._update_video_status(video, "failed")
                    self._update_job(job, "failed", error=str(e))
                    raise DownloadError(f"Unexpected error: {str(e)}") from e
        
        # Should not reach here, but just in case
        self._update_video_status(video, "failed")
        self._update_job(job, "failed", error=last_error or "Unknown error")
        raise DownloadError(f"Download failed after {max_retries} attempts")

    def get_storage_usage(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate total storage usage
        
        Args:
            channel_id: Optional channel ID to filter by
            
        Returns:
            Dictionary with storage statistics
        """
        videos = self.video_repo.get_by_status("download", "downloaded", channel_id=channel_id)
        
        total_size = sum(v.download_size or 0 for v in videos)
        video_count = len(videos)
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
            "video_count": video_count,
            "average_size_bytes": total_size / video_count if video_count > 0 else 0,
        }
