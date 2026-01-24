"""
YouTube video upload service
Handles video uploads to YouTube with metadata, thumbnails, and progress tracking
"""

import json
import os
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from sqlalchemy.orm import Session
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
import boto3
from botocore.exceptions import ClientError

from src.services.youtube.client import YouTubeClient
from src.repositories.video_repository import VideoRepository
from src.repositories.channel_repository import ChannelRepository
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, AuthenticationError, ProcessingError
from src.config import settings

logger = get_logger(__name__)

# YouTube category IDs (common categories)
YOUTUBE_CATEGORIES = {
    "entertainment": 24,
    "music": 10,
    "gaming": 20,
    "sports": 17,
    "news": 25,
    "education": 27,
    "science": 28,
    "technology": 28,
    "autos": 2,
    "comedy": 23,
    "people": 22,
    "pets": 15,
    "travel": 19,
}


class YouTubeUploadService:
    """Service for uploading videos to YouTube"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)

    def _process_metadata_template(
        self,
        template: Dict[str, Any],
        channel_name: str,
        source_title: str,
        video_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process metadata template with variables
        
        Args:
            template: Metadata template dictionary
            channel_name: Channel name
            source_title: Original source title
            video_number: Optional sequential video number
            
        Returns:
            Processed metadata dictionary
        """
        title = template.get("title", source_title)
        description = template.get("description", "")
        tags = template.get("tags", [])
        category = template.get("category", "entertainment")
        privacy = template.get("privacy", "unlisted")
        
        # Replace variables in title
        title = title.replace("{channel_name}", channel_name)
        title = title.replace("{date}", datetime.utcnow().strftime("%Y-%m-%d"))
        title = title.replace("{source_title}", source_title[:100])  # Limit length
        if video_number:
            title = title.replace("{video_number}", str(video_number))
        
        # Replace variables in description
        description = description.replace("{channel_name}", channel_name)
        description = description.replace("{date}", datetime.utcnow().strftime("%Y-%m-%d"))
        description = description.replace("{source_title}", source_title)
        if video_number:
            description = description.replace("{video_number}", str(video_number))
        
        # Get category ID
        category_id = YOUTUBE_CATEGORIES.get(category.lower(), 24)  # Default: Entertainment
        
        return {
            "title": title[:100],  # YouTube title limit
            "description": description[:5000],  # YouTube description limit
            "tags": tags[:500] if isinstance(tags, list) else [],  # YouTube tags limit
            "category_id": category_id,
            "privacy_status": privacy,
        }

    def _download_video_from_s3(self, s3_url: str, local_path: str) -> None:
        """
        Download video from S3 to local file
        
        Args:
            s3_url: S3 URL (s3://bucket/key or https://bucket.s3.region.amazonaws.com/key)
            local_path: Local file path to save video
        """
        try:
            # Parse S3 URL
            if s3_url.startswith("s3://"):
                # s3://bucket/key format
                parts = s3_url.replace("s3://", "").split("/", 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ""
            elif "s3.amazonaws.com" in s3_url or "s3." in s3_url:
                # https://bucket.s3.region.amazonaws.com/key format
                # Extract bucket and key from URL
                from urllib.parse import urlparse
                parsed = urlparse(s3_url)
                bucket = parsed.netloc.split(".")[0]
                key = parsed.path.lstrip("/")
            else:
                raise ValueError(f"Invalid S3 URL format: {s3_url}")
            
            # Download from S3
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            
            s3_client.download_file(bucket, key, local_path)
            logger.info(f"Downloaded video from S3: {s3_url} to {local_path}")
            
        except ClientError as e:
            logger.error(f"Failed to download video from S3: {e}")
            raise ProcessingError(f"Failed to download video from S3: {str(e)}")
        except Exception as e:
            logger.error(f"Error downloading video from S3: {e}")
            raise ProcessingError(f"Error downloading video from S3: {str(e)}")

    def _upload_video_with_progress(
        self,
        youtube: Any,
        video_path: str,
        metadata: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Upload video to YouTube with progress tracking
        
        Args:
            youtube: YouTube API service object
            video_path: Local path to video file
            metadata: Video metadata dictionary
            progress_callback: Optional callback for progress updates (receives bytes_uploaded, total_size)
            
        Returns:
            Upload response dictionary with video ID and URL
        """
        try:
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": metadata["title"],
                    "description": metadata["description"],
                    "tags": metadata["tags"],
                    "categoryId": str(metadata["category_id"]),
                },
                "status": {
                    "privacyStatus": metadata["privacy_status"],
                },
            }
            
            # Create media upload object
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Use resumable upload for large files
                resumable=True,
            )
            
            # Start resumable upload
            insert_request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media,
            )
            
            # Execute upload with progress tracking
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    if progress_callback:
                        progress = int(status.progress() * 100)
                        progress_callback(status.resumable_progress, status.total_size)
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            # Extract video information
            video_id = response["id"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"Video uploaded successfully: {video_id}")
            
            return {
                "video_id": video_id,
                "video_url": video_url,
                "published_at": response.get("snippet", {}).get("publishedAt"),
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error during upload: {e}")
            raise AuthenticationError(f"Failed to upload video to YouTube: {str(e)}")
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise ProcessingError(f"Error uploading video: {str(e)}")

    def _upload_thumbnail(
        self,
        youtube: Any,
        video_id: str,
        thumbnail_path: Optional[str] = None,
    ) -> None:
        """
        Upload thumbnail image for a video
        
        Args:
            youtube: YouTube API service object
            video_id: YouTube video ID
            thumbnail_path: Optional path to thumbnail image file
        """
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            logger.info(f"No thumbnail provided for video {video_id}, skipping thumbnail upload")
            return
        
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path),
            ).execute()
            
            logger.info(f"Thumbnail uploaded successfully for video {video_id}")
            
        except HttpError as e:
            logger.warning(f"Failed to upload thumbnail for video {video_id}: {e}")
            # Don't fail the entire upload if thumbnail fails
        except Exception as e:
            logger.warning(f"Error uploading thumbnail for video {video_id}: {e}")

    def upload_video(
        self,
        video_id: str,
        thumbnail_path: Optional[str] = None,
        metadata_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a video to YouTube
        
        Args:
            video_id: Video ID (database ID)
            thumbnail_path: Optional path to thumbnail image
            metadata_override: Optional metadata to override template
            
        Returns:
            Dictionary with upload result (video_id, video_url, published_at)
        """
        # Get video and channel
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        channel = self.channel_repo.get_by_id(video.channel_id)
        if not channel:
            raise NotFoundError(f"Channel {video.channel_id} not found", resource_type="channel")
        
        # Check video is ready for upload
        if video.transformation_status != "transformed":
            raise ProcessingError(f"Video {video_id} is not transformed yet (status: {video.transformation_status})")
        
        if not video.transformed_url:
            raise ProcessingError(f"Video {video_id} has no transformed URL")
        
        # Update status to publishing
        video.publication_status = "publishing"
        self.video_repo.update(video)
        
        # Initialize YouTube client
        youtube_client = YouTubeClient(self.db, video.channel_id)
        
        # Get metadata template
        try:
            template = json.loads(channel.metadata_template)
        except (json.JSONDecodeError, TypeError):
            template = {
                "title": "{source_title}",
                "description": "",
                "tags": [],
                "category": "entertainment",
                "privacy": "unlisted",
            }
        
        # Override with provided metadata if any
        if metadata_override:
            template.update(metadata_override)
        
        # Process metadata template
        metadata = self._process_metadata_template(
            template=template,
            channel_name=channel.name,
            source_title=video.source_title,
        )
        
        # Download video from S3 to local temp file
        temp_video_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                temp_video_path = temp_file.name
            
            self._download_video_from_s3(video.transformed_url, temp_video_path)
            
            # Upload video with progress tracking
            def progress_callback(bytes_uploaded: int, total_size: int):
                if total_size > 0:
                    progress = int((bytes_uploaded / total_size) * 100)
                    logger.info(f"Upload progress for video {video_id}: {progress}%")
            
            upload_result = self._upload_video_with_progress(
                youtube=youtube_client.youtube,
                video_path=temp_video_path,
                metadata=metadata,
                progress_callback=progress_callback,
            )
            
            # Upload thumbnail if provided
            if thumbnail_path:
                self._upload_thumbnail(
                    youtube=youtube_client.youtube,
                    video_id=upload_result["video_id"],
                    thumbnail_path=thumbnail_path,
                )
            
            # Update video record
            video.publication_status = "published"
            video.youtube_video_id = upload_result["video_id"]
            video.youtube_video_url = upload_result["video_url"]
            video.published_at = datetime.utcnow()
            video.final_title = metadata["title"]
            video.final_description = metadata["description"]
            video.final_tags = json.dumps(metadata["tags"])
            self.video_repo.update(video)
            
            logger.info(f"Video {video_id} uploaded successfully to YouTube: {upload_result['video_url']}")
            
            return upload_result
            
        except Exception as e:
            # Update status to failed
            video.publication_status = "failed"
            self.video_repo.update(video)
            
            logger.error(f"Failed to upload video {video_id}: {e}")
            raise ProcessingError(f"Failed to upload video to YouTube: {str(e)}")
        
        finally:
            # Clean up temp file
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {temp_video_path}: {e}")
