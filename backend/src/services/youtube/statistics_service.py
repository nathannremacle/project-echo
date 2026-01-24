"""
YouTube statistics service
Retrieves and stores channel and video statistics from YouTube API
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from googleapiclient.errors import HttpError

from src.services.youtube.client import YouTubeClient
from src.repositories.statistics_repository import StatisticsRepository
from src.repositories.video_repository import VideoRepository
from src.repositories.channel_repository import ChannelRepository
from src.models.statistics import ChannelStatistics, VideoStatistics
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, AuthenticationError, ProcessingError

logger = get_logger(__name__)


class YouTubeStatisticsService:
    """Service for retrieving and storing YouTube statistics"""

    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = StatisticsRepository(db)
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)

    def retrieve_channel_statistics(self, channel_id: str) -> ChannelStatistics:
        """
        Retrieve and store channel statistics from YouTube API
        
        Args:
            channel_id: Channel ID (database ID)
            
        Returns:
            Created ChannelStatistics record
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        youtube_client = YouTubeClient(self.db, channel_id)
        
        try:
            # Retrieve channel statistics from YouTube API
            response = youtube_client.youtube.channels().list(
                part="statistics,snippet",
                mine=True,
                maxResults=1,
            ).execute()
            
            if not response.get("items"):
                raise NotFoundError(f"YouTube channel not found for channel {channel_id}", resource_type="youtube_channel")
            
            channel_data = response["items"][0]
            statistics = channel_data.get("statistics", {})
            snippet = channel_data.get("snippet", {})
            
            # Extract statistics
            subscriber_count = int(statistics.get("subscriberCount", 0))
            view_count = int(statistics.get("viewCount", 0))
            video_count = int(statistics.get("videoCount", 0))
            
            # Create statistics record
            stats = ChannelStatistics(
                channel_id=channel_id,
                subscriber_count=subscriber_count,
                view_count=view_count,
                video_count=video_count,
                total_views=view_count,
                total_videos=video_count,
                timestamp=datetime.utcnow(),
            )
            
            stats = self.stats_repo.create_channel_statistics(stats)
            
            logger.info(
                f"Retrieved channel statistics for {channel.name}: "
                f"{subscriber_count} subscribers, {view_count} views, {video_count} videos"
            )
            
            return stats
            
        except HttpError as e:
            youtube_client._handle_api_error(e, "retrieve channel statistics")
            raise
        except Exception as e:
            logger.error(f"Error retrieving channel statistics for channel {channel_id}: {e}")
            raise ProcessingError(f"Failed to retrieve channel statistics: {str(e)}")

    def retrieve_video_statistics(self, video_id: str) -> VideoStatistics:
        """
        Retrieve and store video statistics from YouTube API
        
        Args:
            video_id: Video ID (database ID)
            
        Returns:
            Created VideoStatistics record
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        if not video.youtube_video_id:
            raise ProcessingError(f"Video {video_id} has not been published to YouTube yet")
        
        youtube_client = YouTubeClient(self.db, video.channel_id)
        
        try:
            # Retrieve video statistics from YouTube API
            response = youtube_client.youtube.videos().list(
                part="statistics",
                id=video.youtube_video_id,
            ).execute()
            
            if not response.get("items"):
                raise NotFoundError(f"YouTube video {video.youtube_video_id} not found", resource_type="youtube_video")
            
            video_data = response["items"][0]
            statistics = video_data.get("statistics", {})
            
            # Extract statistics
            view_count = int(statistics.get("viewCount", 0))
            like_count = int(statistics.get("likeCount", 0))
            comment_count = int(statistics.get("commentCount", 0))
            
            # Create statistics record
            stats = VideoStatistics(
                video_id=video_id,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                timestamp=datetime.utcnow(),
            )
            
            stats = self.stats_repo.create_video_statistics(stats)
            
            logger.info(
                f"Retrieved video statistics for {video.source_title}: "
                f"{view_count} views, {like_count} likes, {comment_count} comments"
            )
            
            return stats
            
        except HttpError as e:
            youtube_client._handle_api_error(e, "retrieve video statistics")
            raise
        except Exception as e:
            logger.error(f"Error retrieving video statistics for video {video_id}: {e}")
            raise ProcessingError(f"Failed to retrieve video statistics: {str(e)}")

    def retrieve_all_video_statistics(self, channel_id: str) -> Dict[str, Any]:
        """
        Retrieve statistics for all published videos in a channel
        
        Args:
            channel_id: Channel ID (database ID)
            
        Returns:
            Dictionary with results (successful, failed, errors)
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Get all published videos for channel
        videos = self.video_repo.get_by_status("publication", "published", channel_id=channel_id)
        videos = [v for v in videos if v.youtube_video_id]
        
        successful = []
        failed = []
        errors = {}
        
        for video in videos:
            try:
                stats = self.retrieve_video_statistics(video.id)
                successful.append(video.id)
                logger.info(f"Successfully retrieved statistics for video {video.id}")
            except Exception as e:
                failed.append(video.id)
                errors[video.id] = str(e)
                logger.error(f"Failed to retrieve statistics for video {video.id}: {e}")
        
        return {
            "total": len(videos),
            "successful": len(successful),
            "failed": len(failed),
            "successful_ids": successful,
            "failed_ids": failed,
            "errors": errors,
        }

    def get_channel_statistics(
        self,
        channel_id: str,
        limit: Optional[int] = None,
    ) -> List[ChannelStatistics]:
        """
        Get stored channel statistics
        
        Args:
            channel_id: Channel ID
            limit: Optional limit on number of records
            
        Returns:
            List of ChannelStatistics records
        """
        return self.stats_repo.get_channel_statistics(channel_id, limit=limit)

    def get_latest_channel_statistics(self, channel_id: str) -> Optional[ChannelStatistics]:
        """
        Get latest channel statistics
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Latest ChannelStatistics record or None
        """
        return self.stats_repo.get_latest_channel_statistics(channel_id)

    def get_video_statistics(
        self,
        video_id: str,
        limit: Optional[int] = None,
    ) -> List[VideoStatistics]:
        """
        Get stored video statistics
        
        Args:
            video_id: Video ID
            limit: Optional limit on number of records
            
        Returns:
            List of VideoStatistics records
        """
        return self.stats_repo.get_video_statistics(video_id, limit=limit)

    def get_latest_video_statistics(self, video_id: str) -> Optional[VideoStatistics]:
        """
        Get latest video statistics
        
        Args:
            video_id: Video ID
            
        Returns:
            Latest VideoStatistics record or None
        """
        return self.stats_repo.get_latest_video_statistics(video_id)

    def get_channel_statistics_by_date_range(
        self,
        channel_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[ChannelStatistics]:
        """
        Get channel statistics within a date range
        
        Args:
            channel_id: Channel ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of ChannelStatistics records
        """
        return self.stats_repo.get_channel_statistics_by_date_range(channel_id, start_date, end_date)

    def get_video_statistics_by_date_range(
        self,
        video_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[VideoStatistics]:
        """
        Get video statistics within a date range
        
        Args:
            video_id: Video ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of VideoStatistics records
        """
        return self.stats_repo.get_video_statistics_by_date_range(video_id, start_date, end_date)
