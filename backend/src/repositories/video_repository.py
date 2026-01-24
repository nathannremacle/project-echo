"""
Video repository - data access layer for videos
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.video import Video
from src.utils.exceptions import NotFoundError


class VideoRepository:
    """Repository for video data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, video: Video) -> Video:
        """Create a new video"""
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def get_by_id(self, video_id: str) -> Optional[Video]:
        """Get video by ID"""
        return self.db.query(Video).filter(Video.id == video_id).first()

    def get_by_channel_id(self, channel_id: str, limit: Optional[int] = None) -> List[Video]:
        """Get all videos for a channel"""
        query = self.db.query(Video).filter(Video.channel_id == channel_id).order_by(Video.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_by_status(
        self,
        status_type: str,
        status_value: str,
        channel_id: Optional[str] = None,
    ) -> List[Video]:
        """Get videos by status (download_status, transformation_status, or publication_status)"""
        query = self.db.query(Video)
        
        if status_type == "download":
            query = query.filter(Video.download_status == status_value)
        elif status_type == "transformation":
            query = query.filter(Video.transformation_status == status_value)
        elif status_type == "publication":
            query = query.filter(Video.publication_status == status_value)
        else:
            raise ValueError(f"Invalid status_type: {status_type}")

        if channel_id:
            query = query.filter(Video.channel_id == channel_id)

        return query.all()

    def get_by_youtube_video_id(self, youtube_video_id: str) -> Optional[Video]:
        """Get video by YouTube video ID"""
        return (
            self.db.query(Video)
            .filter(Video.youtube_video_id == youtube_video_id)
            .first()
        )

    def update(self, video: Video) -> Video:
        """Update an existing video"""
        self.db.commit()
        self.db.refresh(video)
        return video

    def delete(self, video_id: str) -> bool:
        """Delete a video"""
        video = self.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        self.db.delete(video)
        self.db.commit()
        return True

    def count_by_channel(self, channel_id: str) -> int:
        """Count videos for a channel"""
        return self.db.query(Video).filter(Video.channel_id == channel_id).count()
