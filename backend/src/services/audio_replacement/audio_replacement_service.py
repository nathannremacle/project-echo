"""
Audio replacement service - handles replacing video audio with music tracks
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

import boto3
from botocore.exceptions import ClientError

from shared.src.transformation import VideoTransformer, TransformationError
from shared.src.download import S3StorageClient, StorageError
from src.models.video import Video
from src.models.music import Music
from src.models.job import VideoProcessingJob
from src.repositories.video_repository import VideoRepository
from src.repositories.music_repository import MusicRepository
from src.repositories.job_repository import JobRepository
from src.config import settings
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

logger = get_logger(__name__)


class AudioReplacementService:
    """Service for replacing audio in videos with music tracks"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.music_repo = MusicRepository(db)
        self.job_repo = JobRepository(db)
        
        # Initialize transformer
        temp_dir = os.path.join(os.getcwd(), "temp", "audio_replacement")
        os.makedirs(temp_dir, exist_ok=True)
        self.transformer = VideoTransformer(output_dir=temp_dir)
        
        # Initialize storage client
        self.storage = S3StorageClient(
            bucket_name=settings.AWS_S3_BUCKET,
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region=settings.AWS_REGION,
            endpoint_url=getattr(settings, 'S3_ENDPOINT_URL', None),
        )
        
        # S3 client for direct operations
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def _download_file_from_s3(self, s3_url: str, local_path: str) -> None:
        """Download file from S3 to local path"""
        try:
            # Parse S3 URL
            if s3_url.startswith("s3://"):
                parts = s3_url.replace("s3://", "").split("/", 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ""
            else:
                # Extract from full URL
                bucket = settings.AWS_S3_BUCKET
                key = s3_url.split(f"{bucket}/")[-1] if settings.AWS_S3_BUCKET in s3_url else s3_url
            
            # Download file
            self.s3_client.download_file(bucket, key, local_path)
            logger.debug(f"Downloaded {s3_url} to {local_path}")
        except ClientError as e:
            raise StorageError(f"Failed to download from S3: {str(e)}") from e

    def replace_audio_for_video(
        self,
        video_id: str,
        music_id: str,
        normalize: bool = True,
        match_volume: bool = False,
        audio_bitrate: Optional[str] = None,
        audio_sample_rate: Optional[int] = None,
        loop_audio: bool = True,
    ) -> Dict[str, Any]:
        """
        Replace audio in a single video with music track
        
        Args:
            video_id: Video ID
            music_id: Music track ID
            normalize: Normalize audio levels
            match_volume: Match volume to original
            audio_bitrate: Audio bitrate (e.g., "192k")
            audio_sample_rate: Audio sample rate (e.g., 44100)
            loop_audio: Loop audio if shorter than video
            
        Returns:
            Dictionary with replacement results
        """
        # Get video and music
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        music = self.music_repo.get_by_id(music_id)
        if not music:
            raise NotFoundError(f"Music track {music_id} not found", resource_type="music")
        
        if not music.file_path:
            raise ValidationError(f"Music track {music_id} has no file path")
        
        # Determine which video file to use (transformed if available, otherwise original)
        video_file_url = video.transformed_url or video.download_url
        if not video_file_url:
            raise ValidationError(f"Video {video_id} has no file URL")
        
        # Create job for tracking
        job = VideoProcessingJob(
            video_id=video_id,
            channel_id=video.channel_id,
            job_type="music_replace",
            status="processing",
        )
        job = self.job_repo.create(job)
        
        try:
            # Download video and audio to temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video_path = temp_video.name
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(music.file_path).suffix or ".mp3") as temp_audio:
                temp_audio_path = temp_audio.name
            
            try:
                # Download files
                self._download_file_from_s3(video_file_url, temp_video_path)
                self._download_file_from_s3(music.file_path, temp_audio_path)
                
                # Replace audio
                result = self.transformer.replace_audio(
                    input_file=temp_video_path,
                    audio_file=temp_audio_path,
                    normalize=normalize,
                    match_volume=match_volume,
                    audio_bitrate=audio_bitrate,
                    audio_sample_rate=audio_sample_rate,
                    loop_audio=loop_audio,
                )
                
                # Upload result to S3
                s3_url = self.storage.upload_file(
                    local_file_path=result["output_file"],
                    channel_id=video.channel_id,
                    video_id=video_id,
                )
                
                # Update video record
                video.music_replaced = True
                video.music_track_id = music_id
                # Store the URL in transformed_url if it was transformed, or create a new field
                # For now, we'll update transformed_url to point to the version with music
                if video.transformed_url:
                    # Keep original transformed URL reference, update to new one
                    video.transformed_url = s3_url
                else:
                    video.transformed_url = s3_url
                video = self.video_repo.update(video)
                
                # Increment music usage
                self.music_repo.increment_usage(music_id)
                
                # Update job
                job.status = "completed"
                job = self.job_repo.update(job)
                
                logger.info(f"Audio replaced for video {video_id} with music {music_id}")
                
                return {
                    "video_id": video_id,
                    "music_id": music_id,
                    "output_url": s3_url,
                    "audio_duration": result.get("audio_duration"),
                    "video_duration": result.get("video_duration"),
                }
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_video_path)
                    os.unlink(temp_audio_path)
                    if os.path.exists(result["output_file"]):
                        os.unlink(result["output_file"])
                except:
                    pass
                    
        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.error_message = str(e)
            self.job_repo.update(job)
            logger.error(f"Failed to replace audio for video {video_id}: {e}")
            raise ProcessingError(f"Failed to replace audio: {str(e)}") from e

    def replace_audio_batch(
        self,
        video_ids: List[str],
        music_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Replace audio for multiple videos
        
        Args:
            video_ids: List of video IDs
            music_id: Music track ID
            **kwargs: Additional arguments for replace_audio_for_video
            
        Returns:
            Dictionary with batch results
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(video_ids),
        }
        
        for video_id in video_ids:
            try:
                result = self.replace_audio_for_video(video_id, music_id, **kwargs)
                results["success"].append(result)
            except Exception as e:
                logger.error(f"Failed to replace audio for video {video_id}: {e}")
                results["failed"].append({
                    "video_id": video_id,
                    "error": str(e),
                })
        
        return results

    def replace_audio_for_channel(
        self,
        channel_id: str,
        music_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Replace audio for all videos in a channel
        
        Args:
            channel_id: Channel ID
            music_id: Music track ID
            **kwargs: Additional arguments for replace_audio_for_video
            
        Returns:
            Dictionary with channel results
        """
        # Get all videos for channel that haven't had audio replaced
        videos = self.video_repo.get_by_channel_id(channel_id)
        videos_to_process = [v for v in videos if not v.music_replaced and (v.transformed_url or v.download_url)]
        
        video_ids = [v.id for v in videos_to_process]
        
        return self.replace_audio_batch(video_ids, music_id, **kwargs)
