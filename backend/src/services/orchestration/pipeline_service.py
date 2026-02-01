"""
Pipeline orchestration service
Executes complete video processing pipeline: scrape → download → transform → upload
"""

import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.services.scraping.scraping_service import ScrapingService
from src.services.download.download_service import DownloadService
from src.services.transformation.transformation_service import TransformationService
from src.services.youtube.upload_service import YouTubeUploadService
from src.repositories.video_repository import VideoRepository
from src.repositories.channel_repository import ChannelRepository
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ProcessingError

logger = get_logger(__name__)


class PipelineService:
    """Service for orchestrating complete video processing pipeline"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)
        self.scraping_service = ScrapingService(db)
        self.download_service = DownloadService(db)
        self.transformation_service = TransformationService(db)
        self.upload_service = YouTubeUploadService(db)

    def execute_pipeline(
        self,
        channel_id: str,
        source_url: Optional[str] = None,
        video_id: Optional[str] = None,
        skip_upload: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute complete pipeline for a channel
        
        Args:
            channel_id: Channel ID (database ID)
            source_url: Optional source URL to scrape (if not provided, scrapes channel)
            video_id: Optional existing video ID to process (skip scraping)
            skip_upload: If True, skip upload step (for testing)
            
        Returns:
            Dictionary with pipeline execution results
        """
        start_time = time.time()
        pipeline_start = datetime.utcnow()
        
        logger.info(f"Starting pipeline execution for channel {channel_id}")
        
        results = {
            "channel_id": channel_id,
            "started_at": pipeline_start.isoformat(),
            "steps": {},
            "errors": [],
            "video_id": None,
            "youtube_video_id": None,
            "youtube_video_url": None,
        }
        
        try:
            # Validate channel exists
            channel = self.channel_repo.get_by_id(channel_id)
            if not channel:
                raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
            
            # Step 1: Scrape (if video_id not provided)
            if not video_id:
                logger.info("Step 1: Scraping videos...")
                step_start = time.time()
                
                try:
                    if source_url:
                        # Scrape specific URL
                        scrape_result = self.scraping_service.scrape_video_url(source_url, channel_id)
                    else:
                        # Scrape channel sources
                        scrape_result = self.scraping_service.scrape_channel_for_pipeline(channel_id)
                    videos = scrape_result.get("videos", [])
                    
                    if not videos:
                        raise ProcessingError("No videos found during scraping")
                    
                    # Use first video
                    video = videos[0]
                    video_id = video.id
                    
                    step_duration = time.time() - step_start
                    results["steps"]["scrape"] = {
                        "status": "completed",
                        "duration": round(step_duration, 2),
                        "videos_found": len(videos),
                        "video_id": video_id,
                    }
                    logger.info(f"Scraping completed: {len(videos)} videos found, using video {video_id}")
                    
                except Exception as e:
                    step_duration = time.time() - step_start
                    error_msg = str(e)
                    results["steps"]["scrape"] = {
                        "status": "failed",
                        "duration": round(step_duration, 2),
                        "error": error_msg,
                    }
                    results["errors"].append({"step": "scrape", "error": error_msg})
                    logger.error(f"Scraping failed: {error_msg}")
                    raise ProcessingError(f"Pipeline failed at scrape step: {error_msg}")
            
            # Get video
            video = self.video_repo.get_by_id(video_id)
            if not video:
                raise NotFoundError(f"Video {video_id} not found", resource_type="video")
            
            results["video_id"] = video_id
            
            # Step 2: Download
            logger.info("Step 2: Downloading video...")
            step_start = time.time()
            
            try:
                self.download_service.download_video(video_id)
                
                # Refresh video to get updated status
                self.db.refresh(video)
                
                if video.download_status != "downloaded":
                    raise ProcessingError(f"Download failed: status is {video.download_status}")
                
                step_duration = time.time() - step_start
                results["steps"]["download"] = {
                    "status": "completed",
                    "duration": round(step_duration, 2),
                    "download_url": video.download_url,
                    "download_size": video.download_size,
                }
                logger.info(f"Download completed: {video.download_url}")
                
            except Exception as e:
                step_duration = time.time() - step_start
                error_msg = str(e)
                results["steps"]["download"] = {
                    "status": "failed",
                    "duration": round(step_duration, 2),
                    "error": error_msg,
                }
                results["errors"].append({"step": "download", "error": error_msg})
                logger.error(f"Download failed: {error_msg}")
                raise ProcessingError(f"Pipeline failed at download step: {error_msg}")
            
            # Step 3: Transform
            logger.info("Step 3: Transforming video...")
            step_start = time.time()
            
            try:
                # Get transformation preset for channel
                preset_id = channel.effect_preset_id
                
                self.transformation_service.transform_video(video_id, preset_id=preset_id)
                
                # Refresh video to get updated status
                self.db.refresh(video)
                
                if video.transformation_status != "transformed":
                    raise ProcessingError(f"Transformation failed: status is {video.transformation_status}")
                
                step_duration = time.time() - step_start
                results["steps"]["transform"] = {
                    "status": "completed",
                    "duration": round(step_duration, 2),
                    "transformed_url": video.transformed_url,
                    "transformed_size": video.transformed_size,
                }
                logger.info(f"Transformation completed: {video.transformed_url}")
                
            except Exception as e:
                step_duration = time.time() - step_start
                error_msg = str(e)
                results["steps"]["transform"] = {
                    "status": "failed",
                    "duration": round(step_duration, 2),
                    "error": error_msg,
                }
                results["errors"].append({"step": "transform", "error": error_msg})
                logger.error(f"Transformation failed: {error_msg}")
                raise ProcessingError(f"Pipeline failed at transform step: {error_msg}")
            
            # Step 4: Upload (if not skipped)
            if not skip_upload:
                logger.info("Step 4: Uploading video to YouTube...")
                step_start = time.time()
                
                try:
                    upload_result = self.upload_service.upload_video(video_id)
                    
                    # Refresh video to get updated status
                    self.db.refresh(video)
                    
                    if video.publication_status != "published":
                        raise ProcessingError(f"Upload failed: status is {video.publication_status}")
                    
                    step_duration = time.time() - step_start
                    results["steps"]["upload"] = {
                        "status": "completed",
                        "duration": round(step_duration, 2),
                        "youtube_video_id": upload_result["video_id"],
                        "youtube_video_url": upload_result["video_url"],
                    }
                    results["youtube_video_id"] = upload_result["video_id"]
                    results["youtube_video_url"] = upload_result["video_url"]
                    logger.info(f"Upload completed: {upload_result['video_url']}")
                    
                except Exception as e:
                    step_duration = time.time() - step_start
                    error_msg = str(e)
                    results["steps"]["upload"] = {
                        "status": "failed",
                        "duration": round(step_duration, 2),
                        "error": error_msg,
                    }
                    results["errors"].append({"step": "upload", "error": error_msg})
                    logger.error(f"Upload failed: {error_msg}")
                    raise ProcessingError(f"Pipeline failed at upload step: {error_msg}")
            else:
                results["steps"]["upload"] = {
                    "status": "skipped",
                    "duration": 0,
                }
                logger.info("Upload skipped (test mode)")
            
            # Calculate total duration
            total_duration = time.time() - start_time
            results["completed_at"] = datetime.utcnow().isoformat()
            results["total_duration"] = round(total_duration, 2)
            results["status"] = "completed"
            
            logger.info(f"Pipeline execution completed successfully in {total_duration:.2f}s")
            
            return results
            
        except Exception as e:
            total_duration = time.time() - start_time
            results["completed_at"] = datetime.utcnow().isoformat()
            results["total_duration"] = round(total_duration, 2)
            results["status"] = "failed"
            results["errors"].append({"step": "pipeline", "error": str(e)})
            
            logger.error(f"Pipeline execution failed after {total_duration:.2f}s: {e}")
            
            return results
