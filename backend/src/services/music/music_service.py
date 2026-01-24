"""
Music service - handles music file upload, storage, and management
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
from sqlalchemy.orm import Session

from src.models.music import Music
from src.repositories.music_repository import MusicRepository
from shared.src.download import S3StorageClient, StorageError
from src.utils.logging import get_logger
from src.utils.exceptions import ValidationError, ProcessingError
from src.config import settings

logger = get_logger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MIN_DURATION = 30  # 30 seconds
MAX_DURATION = 600  # 10 minutes


class MusicService:
    """Service for managing music files"""

    def __init__(self, db: Session):
        self.db = db
        self.music_repo = MusicRepository(db)
        
        # Initialize storage client
        self.storage = S3StorageClient(
            bucket_name=settings.AWS_S3_BUCKET,
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region=settings.AWS_REGION,
            endpoint_url=getattr(settings, 'S3_ENDPOINT_URL', None),
        )

    def _validate_file(self, file: BinaryIO, filename: str) -> Dict[str, Any]:
        """
        Validate music file
        
        Args:
            file: File object
            filename: Original filename
            
        Returns:
            Dictionary with validation results
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported file format: {file_ext}. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            )
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise ValidationError(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum ({MAX_FILE_SIZE / 1024 / 1024}MB)")
        
        if file_size == 0:
            raise ValidationError("File is empty")
        
        # Extract duration and metadata (simplified - would use mutagen or ffmpeg in production)
        duration = self._extract_duration(file, file_ext)
        
        if duration and (duration < MIN_DURATION or duration > MAX_DURATION):
            raise ValidationError(f"Duration ({duration}s) must be between {MIN_DURATION} and {MAX_DURATION} seconds")
        
        return {
            "format": file_ext,
            "size": file_size,
            "duration": duration,
        }

    def _extract_duration(self, file: BinaryIO, file_ext: str) -> Optional[int]:
        """
        Extract audio duration (simplified implementation)
        In production, would use mutagen or ffmpeg-python
        
        Args:
            file: File object
            file_ext: File extension
            
        Returns:
            Duration in seconds or None if extraction fails
        """
        # For MVP, we'll use a simplified approach
        # In production, would use:
        # - mutagen for MP3, M4A, OGG
        # - ffmpeg-python for all formats
        try:
            # Save to temp file for analysis
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                file.seek(0)
                temp_file.write(file.read())
                temp_file_path = temp_file.name
            
            # Try to use ffmpeg to get duration
            try:
                import ffmpeg
                probe = ffmpeg.probe(temp_file_path)
                duration = float(probe['format']['duration'])
                os.unlink(temp_file_path)
                return int(duration)
            except (ImportError, Exception):
                # Fallback: estimate based on file size (very rough)
                # This is a placeholder - should use proper audio analysis
                logger.warning(f"Could not extract duration for {file_ext}, using estimate")
                os.unlink(temp_file_path)
                # Rough estimate: ~1MB per minute for MP3
                file.seek(0, os.SEEK_END)
                size = file.tell()
                file.seek(0)
                estimated_duration = int((size / (1024 * 1024)) * 60)  # Very rough estimate
                return estimated_duration if estimated_duration > 0 else None
        except Exception as e:
            logger.error(f"Failed to extract duration: {e}")
            return None

    def upload_music(
        self,
        file: BinaryIO,
        filename: str,
        name: str,
        artist: Optional[str] = None,
        spotify_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Music:
        """
        Upload music file to storage
        
        Args:
            file: File object
            filename: Original filename
            name: Track name
            artist: Artist name
            spotify_url: Spotify track URL
            metadata: Additional metadata
            
        Returns:
            Music object
        """
        # Validate file
        validation_result = self._validate_file(file, filename)
        
        # Create music record
        music = Music(
            name=name,
            artist=artist,
            spotify_track_url=spotify_url,
            file_size=validation_result["size"],
            duration=validation_result.get("duration"),
            metadata=json.dumps(metadata or {}),
        )
        
        # Save to database first to get ID
        music = self.music_repo.create(music)
        
        try:
            # Save file to temporary location for upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                file.seek(0)
                temp_file.write(file.read())
                temp_file_path = temp_file.name
            
            try:
                # Upload to S3 (using music.id as both channel_id and video_id for organization)
                logger.info(f"Uploading music file {filename} to S3")
                s3_url = self.storage.upload_file(
                    local_file_path=temp_file_path,
                    channel_id="music",
                    video_id=music.id,
                    metadata={
                        "name": name,
                        "artist": artist or "",
                        "format": validation_result["format"],
                    },
                )
                
                # Update music record with file path
                music.file_path = s3_url
                music = self.music_repo.update(music)
                
                logger.info(f"Music file uploaded successfully: {music.id}")
                return music
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
        except StorageError as e:
            # Delete music record if upload fails
            self.music_repo.delete(music.id)
            logger.error(f"Failed to upload music file to S3: {e}")
            raise ProcessingError(f"Failed to upload music file: {str(e)}")
        except Exception as e:
            # Delete music record if upload fails
            try:
                self.music_repo.delete(music.id)
            except:
                pass
            logger.error(f"Unexpected error uploading music file: {e}")
            raise ProcessingError(f"Failed to upload music file: {str(e)}")

    def get_music(self, music_id: str) -> Optional[Music]:
        """Get music track by ID"""
        return self.music_repo.get_by_id(music_id)

    def list_music(self, active_only: bool = True) -> list[Music]:
        """List all music tracks"""
        return self.music_repo.get_all(active_only=active_only)

    def delete_music(self, music_id: str) -> bool:
        """
        Delete music track and file
        
        Args:
            music_id: Music track ID
            
        Returns:
            True if deleted successfully
        """
        music = self.music_repo.get_by_id(music_id)
        if not music:
            raise ValidationError(f"Music track {music_id} not found")
        
        # Delete from S3
        if music.file_path:
            try:
                # Extract filename from file_path (format: s3://bucket/music/{music_id}/{filename})
                # Or use the original filename if stored in metadata
                filename = Path(music.file_path).name if "/" in music.file_path else "music_file"
                self.storage.delete_file(
                    channel_id="music",
                    video_id=music.id,
                    filename=filename,
                )
                logger.info(f"Deleted music file from S3: {music.id}")
            except Exception as e:
                logger.warning(f"Failed to delete music file from S3: {e}")
                # Continue with database deletion even if S3 deletion fails
        
        # Delete from database
        return self.music_repo.delete(music_id)

    def get_preview_url(self, music_id: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get presigned URL for music preview
        
        Args:
            music_id: Music track ID
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL or None
        """
        music = self.music_repo.get_by_id(music_id)
        if not music or not music.file_path:
            return None
        
        try:
            # Generate presigned URL using boto3 directly
            import boto3
            from botocore.exceptions import ClientError
            
            # Extract filename from file_path
            filename = Path(music.file_path).name if "/" in music.file_path else "music_file"
            s3_key = self.storage._generate_s3_key("music", music_id, filename)
            
            # Generate presigned URL
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.storage.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate preview URL: {e}")
            return None

    def increment_usage(self, music_id: str) -> Music:
        """Increment usage count for a music track"""
        return self.music_repo.increment_usage(music_id)
