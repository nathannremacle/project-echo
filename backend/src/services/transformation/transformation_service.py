"""
Transformation service - orchestrates video transformation and storage
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from shared.src.transformation import (
    VideoTransformer,
    get_preset,
    randomize_preset_params,
    QualityValidator,
    TransformationError,
    PresetNotFoundError,
)
from shared.src.download import S3StorageClient
from src.models.video import Video
from src.models.job import VideoProcessingJob
from src.repositories.video_repository import VideoRepository
from src.repositories.job_repository import JobRepository
from src.repositories.preset_repository import PresetRepository
from src.config import settings
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError

logger = get_logger(__name__)


class TransformationService:
    """Service for video transformation operations"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.job_repo = JobRepository(db)
        self.preset_repo = PresetRepository(db)
        
        # Initialize transformer with temp directory
        temp_dir = os.path.join(os.getcwd(), "temp", "transformations")
        os.makedirs(temp_dir, exist_ok=True)
        self.transformer = VideoTransformer(output_dir=temp_dir)
        
        # Initialize quality validator
        self.quality_validator = QualityValidator()
        
        # Initialize storage client
        self.storage = S3StorageClient(
            bucket_name=settings.AWS_S3_BUCKET,
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region=settings.AWS_REGION,
            endpoint_url=getattr(settings, 'S3_ENDPOINT_URL', None),
        )

    def _load_preset_params(self, preset_id: Optional[str]) -> Dict[str, Any]:
        """
        Load transformation parameters from preset
        
        Args:
            preset_id: Preset ID (None to use default)
            
        Returns:
            Transformation parameters dictionary
        """
        if preset_id:
            preset = self.preset_repo.get_by_id(preset_id)
            if not preset:
                raise PresetNotFoundError(f"Preset {preset_id} not found")
            
            try:
                params = json.loads(preset.parameters)
                return params
            except json.JSONDecodeError:
                logger.warning(f"Invalid preset parameters JSON for preset {preset_id}")
                return {}
        else:
            # Use default preset
            return get_preset("moderate")

    def _create_job(self, video_id: str, channel_id: str) -> VideoProcessingJob:
        """Create a processing job for tracking"""
        job = VideoProcessingJob(
            video_id=video_id,
            channel_id=channel_id,
            job_type="transform",
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

    def _update_video_status(
        self,
        video: Video,
        status: str,
        preset_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Video:
        """Update video transformation status"""
        video.transformation_status = status
        if preset_id:
            video.transformation_preset_id = preset_id
        if params:
            video.transformation_params = json.dumps(params)
        for key, value in kwargs.items():
            if hasattr(video, key):
                setattr(video, key, value)
        video.updated_at = datetime.utcnow()
        return self.video_repo.update(video)

    def transform_video(
        self,
        video_id: str,
        preset_id: Optional[str] = None,
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Video:
        """
        Transform video with specified preset or custom parameters
        
        Args:
            video_id: Video ID
            preset_id: Optional preset ID (uses default if not provided)
            custom_params: Optional custom transformation parameters (overrides preset)
            
        Returns:
            Updated Video object
            
        Raises:
            NotFoundError: If video not found
            TransformationError: If transformation fails
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        # Check if video is downloaded
        if video.download_status != "downloaded" or not video.download_url:
            raise TransformationError(f"Video {video_id} must be downloaded before transformation")
        
        # Check if already transformed
        if video.transformation_status == "transformed" and video.transformed_url:
            logger.info(f"Video {video_id} already transformed")
            return video
        
        # Create job for tracking
        job = self._create_job(video_id, video.channel_id)
        
        # Update video status
        self._update_video_status(video, "processing", processing_started_at=datetime.utcnow())
        self._update_job(job, "processing")
        
        try:
            logger.info(f"Transforming video {video_id} with preset {preset_id or 'default'}")
            
            # Load preset parameters
            if custom_params:
                params = custom_params
            else:
                params = self._load_preset_params(preset_id)
            
            # Apply randomization if enabled
            if "randomization" in params and params["randomization"].get("enabled", False):
                randomization_config = params.pop("randomization")
                params = randomize_preset_params(params, randomization_config)
                logger.debug(f"Applied parameter randomization for video {video_id}")
            
            # Download video from S3 to local temp file
            import tempfile
            import boto3
            from urllib.parse import urlparse
            
            # Parse S3 URL
            s3_url = video.download_url
            if not s3_url.startswith("s3://"):
                raise TransformationError(f"Invalid S3 URL: {s3_url}")
            
            # Extract bucket and key from S3 URL
            parsed = urlparse(s3_url)
            bucket_name = parsed.netloc
            s3_key = parsed.path.lstrip("/")
            
            # Download to temp file
            temp_input_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_input_file.close()
            
            try:
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                )
                s3_client.download_file(bucket_name, s3_key, temp_input_file.name)
                local_input_file = temp_input_file.name
                logger.debug(f"Downloaded video from S3 to {local_input_file}")
            except Exception as e:
                os.unlink(temp_input_file.name)  # Clean up on error
                raise TransformationError(f"Failed to download video from S3: {str(e)}") from e
            
            # Transform video with fallback on error
            start_time = time.time()
            transform_result = None
            used_fallback = False
            
            try:
                # Try advanced transformation first
                transform_result = self.transformer.transform(
                    local_input_file,
                    params=params,
                )
            except TransformationError as e:
                logger.warning(f"Advanced transformation failed for video {video_id}: {str(e)}")
                logger.info(f"Falling back to basic transformation for video {video_id}")
                
                # Fallback to basic effects only
                fallback_params = {
                    "color_grading": params.get("color_grading", {}),
                    "flip": params.get("flip", {}),
                    "filters": params.get("filters", {}),
                }
                # Remove advanced effects (frame_rate, aspect_ratio)
                
                try:
                    transform_result = self.transformer.transform(
                        local_input_file,
                        params=fallback_params,
                    )
                    used_fallback = True
                    params = fallback_params  # Update params to reflect what was actually used
                    logger.info(f"Fallback transformation successful for video {video_id}")
                except TransformationError as fallback_error:
                    logger.error(f"Fallback transformation also failed for video {video_id}: {str(fallback_error)}")
                    raise TransformationError(f"Both advanced and fallback transformations failed: {str(fallback_error)}") from fallback_error
            
            processing_time = time.time() - start_time
            
            # Validate transformed video quality
            validation_result = self.quality_validator.validate_video(transform_result["output_file"])
            if not validation_result.get("valid", False):
                errors = validation_result.get("errors", [])
                logger.warning(f"Quality validation warnings for video {video_id}: {errors}")
                # Continue anyway, but log the warnings
            else:
                logger.debug(f"Quality validation passed for video {video_id}: {validation_result.get('resolution')}")
            
            logger.info(
                f"Transformed video {video_id} in {processing_time:.2f}s: "
                f"{transform_result['file_size']} bytes, effects: {list(params.keys())}, "
                f"fallback: {used_fallback}, validation: {validation_result.get('valid', False)}"
            )
            
            # Upload transformed video to S3
            logger.info(f"Uploading transformed video {video_id} to S3")
            # Rename file for S3 upload (add transformed prefix)
            transformed_output_file = transform_result["output_file"]
            output_path = Path(transformed_output_file)
            renamed_output_file = str(output_path.parent / f"transformed_{output_path.name}")
            os.rename(transformed_output_file, renamed_output_file)
            
            s3_url = self.storage.upload_file(
                renamed_output_file,
                video.channel_id,
                video_id,
                metadata={
                    "transformation_preset_id": preset_id or "default",
                    "transformation_params": json.dumps(params),
                    "processing_time": str(processing_time),
                },
            )
            
            # Update video with transformation information
            self._update_video_status(
                video,
                "transformed",
                preset_id=preset_id,
                params=params,
                transformed_url=s3_url,
                transformed_size=transform_result["file_size"],
                processing_completed_at=datetime.utcnow(),
                processing_duration=int(processing_time),
            )
            
            # Clean up local files
            try:
                # Remove input temp file
                if os.path.exists(local_input_file):
                    os.unlink(local_input_file)
                    logger.debug(f"Cleaned up input temp file: {local_input_file}")
                # Remove output file
                if os.path.exists(renamed_output_file):
                    os.remove(renamed_output_file)
                    logger.debug(f"Cleaned up output file: {renamed_output_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up local files: {e}")
            
            # Mark job as completed
            self._update_job(job, "completed")
            
            logger.info(f"Successfully transformed and stored video {video_id}")
            return video
            
        except TransformationError as e:
            logger.error(f"Transformation error for video {video_id}: {str(e)}")
            self._update_video_status(video, "failed")
            self._update_job(job, "failed", error=str(e))
            # Clean up temp file on error
            try:
                if 'local_input_file' in locals() and os.path.exists(local_input_file):
                    os.unlink(local_input_file)
            except Exception:
                pass
            raise
        except Exception as e:
            logger.error(f"Unexpected error transforming video {video_id}: {str(e)}")
            self._update_video_status(video, "failed")
            self._update_job(job, "failed", error=str(e))
            # Clean up temp file on error
            try:
                if 'local_input_file' in locals() and os.path.exists(local_input_file):
                    os.unlink(local_input_file)
            except Exception:
                pass
            raise TransformationError(f"Unexpected error: {str(e)}") from e
