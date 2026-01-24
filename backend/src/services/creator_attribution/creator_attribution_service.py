"""
Creator attribution service - handles tracking and attribution of original creators
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from src.models.video import Video
from src.repositories.video_repository import VideoRepository
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError

logger = get_logger(__name__)


class CreatorAttributionService:
    """Service for managing creator attribution"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)

    def get_all_creators(self) -> List[Dict[str, Any]]:
        """
        Get list of all unique creators with video counts
        
        Returns:
            List of creator dictionaries with name and video count
        """
        # Get distinct creators with counts
        creators_query = (
            self.db.query(
                Video.source_creator,
                func.count(Video.id).label('video_count')
            )
            .filter(Video.source_creator.isnot(None))
            .filter(Video.source_creator != '')
            .group_by(Video.source_creator)
            .order_by(Video.source_creator)
        )
        
        creators = []
        for creator_name, video_count in creators_query.all():
            creators.append({
                "name": creator_name,
                "video_count": video_count,
            })
        
        return creators

    def get_videos_by_creator(
        self,
        creator_name: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get videos by creator name
        
        Args:
            creator_name: Creator name to search for
            limit: Maximum number of videos to return
            offset: Offset for pagination
            
        Returns:
            Dictionary with videos and total count
        """
        videos = (
            self.db.query(Video)
            .filter(Video.source_creator == creator_name)
            .order_by(Video.created_at.desc())
            .offset(offset)
        )
        
        if limit:
            videos = videos.limit(limit)
        
        video_list = videos.all()
        total_count = (
            self.db.query(func.count(Video.id))
            .filter(Video.source_creator == creator_name)
            .scalar()
        )
        
        return {
            "creator": creator_name,
            "videos": [
                {
                    "id": v.id,
                    "source_title": v.source_title,
                    "source_url": v.source_url,
                    "channel_id": v.channel_id,
                    "publication_status": v.publication_status,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in video_list
            ],
            "total": total_count,
            "limit": limit,
            "offset": offset,
        }

    def search_creators(
        self,
        query: str,
        limit: Optional[int] = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search creators by name
        
        Args:
            query: Search query (partial match)
            limit: Maximum number of results
            
        Returns:
            List of matching creators
        """
        creators_query = (
            self.db.query(
                Video.source_creator,
                func.count(Video.id).label('video_count')
            )
            .filter(Video.source_creator.isnot(None))
            .filter(Video.source_creator != '')
            .filter(Video.source_creator.ilike(f"%{query}%"))
            .group_by(Video.source_creator)
            .order_by(Video.source_creator)
        )
        
        if limit:
            creators_query = creators_query.limit(limit)
        
        creators = []
        for creator_name, video_count in creators_query.all():
            creators.append({
                "name": creator_name,
                "video_count": video_count,
            })
        
        return creators

    def attribute_video(
        self,
        video_id: str,
        creator_name: str,
        creator_channel: Optional[str] = None,
    ) -> Video:
        """
        Add or update creator attribution for a video
        
        Args:
            video_id: Video ID
            creator_name: Creator name
            creator_channel: Optional creator channel URL
            
        Returns:
            Updated video
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        video.source_creator = creator_name
        
        # Store creator channel in metadata if provided
        # For MVP, we'll store it in transformation_params or create a new field
        # For now, we'll just update source_creator
        video = self.video_repo.update(video)
        
        logger.info(f"Attributed video {video_id} to creator {creator_name}")
        return video

    def bulk_attribute_videos(
        self,
        video_ids: List[str],
        creator_name: str,
        creator_channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Bulk update creator attribution for multiple videos
        
        Args:
            video_ids: List of video IDs
            creator_name: Creator name
            creator_channel: Optional creator channel URL
            
        Returns:
            Dictionary with results
        """
        results = {
            "updated": [],
            "failed": [],
            "total": len(video_ids),
        }
        
        for video_id in video_ids:
            try:
                video = self.video_repo.get_by_id(video_id)
                if not video:
                    results["failed"].append({
                        "video_id": video_id,
                        "error": "Video not found",
                    })
                    continue
                
                video.source_creator = creator_name
                video = self.video_repo.update(video)
                
                results["updated"].append({
                    "video_id": video_id,
                    "video_title": video.source_title,
                })
                
            except Exception as e:
                logger.error(f"Failed to attribute video {video_id}: {e}")
                results["failed"].append({
                    "video_id": video_id,
                    "error": str(e),
                })
        
        return results

    def export_creator_list(
        self,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Export list of all creators and their videos
        
        Args:
            format: Export format ("json" or "csv")
            
        Returns:
            Dictionary with export data
        """
        creators = self.get_all_creators()
        
        # Get videos for each creator
        export_data = {
            "exported_at": None,  # Will be set in API
            "total_creators": len(creators),
            "creators": [],
        }
        
        for creator_info in creators:
            creator_name = creator_info["name"]
            videos_data = self.get_videos_by_creator(creator_name, limit=None)
            
            export_data["creators"].append({
                "name": creator_name,
                "video_count": creator_info["video_count"],
                "videos": videos_data["videos"],
            })
        
        return export_data

    def get_attribution_template_variable(
        self,
        video_id: str,
    ) -> str:
        """
        Get creator attribution string for use in description templates
        
        Args:
            video_id: Video ID
            
        Returns:
            Attribution string (empty if no creator)
        """
        video = self.video_repo.get_by_id(video_id)
        if not video or not video.source_creator:
            return ""
        
        # Format: "Original video by: {creator_name}"
        return f"Original video by: {video.source_creator}"
