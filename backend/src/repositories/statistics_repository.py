"""
Statistics repository - data access layer for channel and video statistics
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.statistics import ChannelStatistics, VideoStatistics
from src.utils.exceptions import NotFoundError


class StatisticsRepository:
    """Repository for statistics data access"""

    def __init__(self, db: Session):
        self.db = db

    # Channel Statistics

    def create_channel_statistics(self, stats: ChannelStatistics) -> ChannelStatistics:
        """Create a new channel statistics record"""
        self.db.add(stats)
        self.db.commit()
        self.db.refresh(stats)
        return stats

    def get_channel_statistics_by_id(self, stats_id: str) -> Optional[ChannelStatistics]:
        """Get channel statistics by ID"""
        return self.db.query(ChannelStatistics).filter(ChannelStatistics.id == stats_id).first()

    def get_channel_statistics(
        self,
        channel_id: str,
        limit: Optional[int] = None,
        order_by_date: bool = True,
    ) -> List[ChannelStatistics]:
        """Get channel statistics for a channel, ordered by timestamp"""
        query = self.db.query(ChannelStatistics).filter(ChannelStatistics.channel_id == channel_id)
        
        if order_by_date:
            query = query.order_by(desc(ChannelStatistics.timestamp))
        else:
            query = query.order_by(ChannelStatistics.timestamp)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def get_latest_channel_statistics(self, channel_id: str) -> Optional[ChannelStatistics]:
        """Get latest channel statistics for a channel"""
        return (
            self.db.query(ChannelStatistics)
            .filter(ChannelStatistics.channel_id == channel_id)
            .order_by(desc(ChannelStatistics.timestamp))
            .first()
        )

    def get_channel_statistics_by_date_range(
        self,
        channel_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[ChannelStatistics]:
        """Get channel statistics within a date range"""
        return (
            self.db.query(ChannelStatistics)
            .filter(
                ChannelStatistics.channel_id == channel_id,
                ChannelStatistics.timestamp >= start_date,
                ChannelStatistics.timestamp <= end_date,
            )
            .order_by(ChannelStatistics.timestamp)
            .all()
        )

    # Video Statistics

    def create_video_statistics(self, stats: VideoStatistics) -> VideoStatistics:
        """Create a new video statistics record"""
        self.db.add(stats)
        self.db.commit()
        self.db.refresh(stats)
        return stats

    def get_video_statistics_by_id(self, stats_id: str) -> Optional[VideoStatistics]:
        """Get video statistics by ID"""
        return self.db.query(VideoStatistics).filter(VideoStatistics.id == stats_id).first()

    def get_video_statistics(
        self,
        video_id: str,
        limit: Optional[int] = None,
        order_by_date: bool = True,
    ) -> List[VideoStatistics]:
        """Get video statistics for a video, ordered by timestamp"""
        query = self.db.query(VideoStatistics).filter(VideoStatistics.video_id == video_id)
        
        if order_by_date:
            query = query.order_by(desc(VideoStatistics.timestamp))
        else:
            query = query.order_by(VideoStatistics.timestamp)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def get_latest_video_statistics(self, video_id: str) -> Optional[VideoStatistics]:
        """Get latest video statistics for a video"""
        return (
            self.db.query(VideoStatistics)
            .filter(VideoStatistics.video_id == video_id)
            .order_by(desc(VideoStatistics.timestamp))
            .first()
        )

    def get_video_statistics_by_date_range(
        self,
        video_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[VideoStatistics]:
        """Get video statistics within a date range"""
        return (
            self.db.query(VideoStatistics)
            .filter(
                VideoStatistics.video_id == video_id,
                VideoStatistics.timestamp >= start_date,
                VideoStatistics.timestamp <= end_date,
            )
            .order_by(VideoStatistics.timestamp)
            .all()
        )

    def get_statistics_for_published_videos(
        self,
        channel_id: str,
        limit: Optional[int] = None,
    ) -> List[VideoStatistics]:
        """Get latest statistics for all published videos in a channel"""
        from src.models.video import Video
        
        # Get published videos for channel
        videos = (
            self.db.query(Video)
            .filter(
                Video.channel_id == channel_id,
                Video.publication_status == "published",
                Video.youtube_video_id.isnot(None),
            )
            .all()
        )
        
        # Get latest statistics for each video
        video_ids = [video.id for video in videos]
        if not video_ids:
            return []
        
        # Get latest statistics for each video
        stats_list = []
        for video_id in video_ids[:limit] if limit else video_ids:
            latest = self.get_latest_video_statistics(video_id)
            if latest:
                stats_list.append(latest)
        
        return stats_list
