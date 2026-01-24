"""
YouTube metadata management service
Handles updating video metadata (title, description, tags, category, thumbnail) after upload
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from src.services.youtube.client import YouTubeClient
from src.services.youtube.upload_service import YouTubeUploadService, YOUTUBE_CATEGORIES
from src.repositories.video_repository import VideoRepository
from src.repositories.channel_repository import ChannelRepository
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, AuthenticationError, ProcessingError

logger = get_logger(__name__)


class YouTubeMetadataService:
    """Service for managing YouTube video metadata"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)
        self.upload_service = YouTubeUploadService(db)  # Reuse template processing

    def update_video_metadata(
        self,
        video_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        thumbnail_path: Optional[str] = None,
        use_template: bool = True,
    ) -> Dict[str, Any]:
        """
        Update video metadata on YouTube
        
        Args:
            video_id: Video ID (database ID)
            metadata: Optional metadata dictionary to override template
            thumbnail_path: Optional path to thumbnail image
            use_template: Whether to use channel metadata template (default: True)
            
        Returns:
            Dictionary with update result
        """
        # Get video and channel
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        if not video.youtube_video_id:
            raise ProcessingError(f"Video {video_id} has not been published to YouTube yet")
        
        if video.publication_status != "published":
            raise ProcessingError(f"Video {video_id} is not published (status: {video.publication_status})")
        
        channel = self.channel_repo.get_by_id(video.channel_id)
        if not channel:
            raise NotFoundError(f"Channel {video.channel_id} not found", resource_type="channel")
        
        # Initialize YouTube client
        youtube_client = YouTubeClient(self.db, video.channel_id)
        
        # Get metadata (from template or provided)
        if use_template and not metadata:
            # Process metadata template
            try:
                template = json.loads(channel.metadata_template)
            except (json.JSONDecodeError, TypeError):
                template = {
                    "title": video.final_title or video.source_title,
                    "description": video.final_description or "",
                    "tags": json.loads(video.final_tags) if video.final_tags else [],
                    "category": "entertainment",
                }
            
            processed_metadata = self.upload_service._process_metadata_template(
                template=template,
                channel_name=channel.name,
                source_title=video.source_title,
            )
        elif metadata:
            # Use provided metadata
            processed_metadata = self.upload_service._process_metadata_template(
                template=metadata,
                channel_name=channel.name,
                source_title=video.source_title,
            )
        else:
            # Use existing metadata
            processed_metadata = {
                "title": video.final_title or video.source_title,
                "description": video.final_description or "",
                "tags": json.loads(video.final_tags) if video.final_tags else [],
                "category_id": YOUTUBE_CATEGORIES.get("entertainment", 24),
            }
        
        try:
            # Prepare update body
            body = {
                "id": video.youtube_video_id,
                "snippet": {
                    "title": processed_metadata["title"][:100],  # YouTube limit
                    "description": processed_metadata["description"][:5000],  # YouTube limit
                    "tags": processed_metadata["tags"][:500],  # YouTube limit
                    "categoryId": str(processed_metadata["category_id"]),
                },
            }
            
            # Update video metadata
            update_response = youtube_client.youtube.videos().update(
                part="snippet",
                body=body,
            ).execute()
            
            logger.info(f"Updated metadata for video {video_id} (YouTube ID: {video.youtube_video_id})")
            
            # Update thumbnail if provided
            if thumbnail_path:
                self._update_thumbnail(
                    youtube=youtube_client.youtube,
                    video_id=video.youtube_video_id,
                    thumbnail_path=thumbnail_path,
                )
            
            # Update database with new metadata
            video.final_title = processed_metadata["title"]
            video.final_description = processed_metadata["description"]
            video.final_tags = json.dumps(processed_metadata["tags"])
            video.updated_at = datetime.utcnow()
            self.video_repo.update(video)
            
            return {
                "video_id": video_id,
                "youtube_video_id": video.youtube_video_id,
                "updated_metadata": processed_metadata,
                "updated_at": datetime.utcnow().isoformat(),
            }
            
        except HttpError as e:
            youtube_client._handle_api_error(e, "metadata update")
            raise
        except Exception as e:
            logger.error(f"Error updating metadata for video {video_id}: {e}")
            raise ProcessingError(f"Failed to update metadata: {str(e)}")

    def _update_thumbnail(
        self,
        youtube: Any,
        video_id: str,
        thumbnail_path: str,
    ) -> None:
        """
        Update thumbnail for a video
        
        Args:
            youtube: YouTube API service object
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image file
        """
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path),
            ).execute()
            
            logger.info(f"Updated thumbnail for YouTube video {video_id}")
            
        except HttpError as e:
            logger.warning(f"Failed to update thumbnail for video {video_id}: {e}")
            # Don't fail the entire update if thumbnail fails
        except Exception as e:
            logger.warning(f"Error updating thumbnail for video {video_id}: {e}")

    def bulk_update_metadata(
        self,
        video_ids: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        use_template: bool = True,
    ) -> Dict[str, Any]:
        """
        Update metadata for multiple videos
        
        Args:
            video_ids: List of video IDs (database IDs)
            metadata: Optional metadata dictionary to apply to all videos
            use_template: Whether to use channel metadata template (default: True)
            
        Returns:
            Dictionary with results (successful, failed, errors)
        """
        successful = []
        failed = []
        errors = {}
        
        for video_id in video_ids:
            try:
                result = self.update_video_metadata(
                    video_id=video_id,
                    metadata=metadata,
                    use_template=use_template,
                )
                successful.append(video_id)
                logger.info(f"Successfully updated metadata for video {video_id}")
            except Exception as e:
                failed.append(video_id)
                errors[video_id] = str(e)
                logger.error(f"Failed to update metadata for video {video_id}: {e}")
        
        return {
            "total": len(video_ids),
            "successful": len(successful),
            "failed": len(failed),
            "successful_ids": successful,
            "failed_ids": failed,
            "errors": errors,
        }

    def get_current_metadata(self, video_id: str) -> Dict[str, Any]:
        """
        Get current metadata for a video from YouTube
        
        Args:
            video_id: Video ID (database ID)
            
        Returns:
            Dictionary with current metadata from YouTube
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        if not video.youtube_video_id:
            raise ProcessingError(f"Video {video_id} has not been published to YouTube yet")
        
        youtube_client = YouTubeClient(self.db, video.channel_id)
        
        try:
            response = youtube_client.youtube.videos().list(
                part="snippet",
                id=video.youtube_video_id,
            ).execute()
            
            if not response.get("items"):
                raise NotFoundError(f"YouTube video {video.youtube_video_id} not found", resource_type="youtube_video")
            
            snippet = response["items"][0]["snippet"]
            
            return {
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId"),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            }
            
        except HttpError as e:
            youtube_client._handle_api_error(e, "get metadata")
            raise
        except Exception as e:
            logger.error(f"Error getting metadata for video {video_id}: {e}")
            raise ProcessingError(f"Failed to get metadata: {str(e)}")
