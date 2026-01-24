"""
Video distribution service - manages automatic and manual video assignments to channels
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.distribution import VideoDistribution
from src.repositories.distribution_repository import DistributionRepository
from src.repositories.channel_repository import ChannelRepository
from src.repositories.video_repository import VideoRepository
from src.repositories.schedule_repository import ScheduleRepository
from src.services.orchestration.scheduling_service import SchedulingService
from src.services.orchestration.channel_configuration_service import ChannelConfigurationService
from src.utils.logging import get_logger

# Import filters - try relative import first, then absolute
try:
    from shared.src.scraping.filters import apply_filters
except ImportError:
    # Fallback: import from shared module if available
    import sys
    from pathlib import Path
    shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "src"
    if shared_path.exists():
        sys.path.insert(0, str(shared_path))
        from scraping.filters import apply_filters
    else:
        # Fallback implementation if shared module not available
        def apply_filters(metadata, min_resolution="720p", min_views=None, max_duration=None, exclude_watermarked=True):
            """Fallback filter implementation"""
            return True
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

logger = get_logger(__name__)


class VideoDistributionService:
    """Service for managing video distribution across channels"""

    def __init__(self, db: Session):
        self.db = db
        self.distribution_repo = DistributionRepository(db)
        self.channel_repo = ChannelRepository(db)
        self.video_repo = VideoRepository(db)
        self.schedule_repo = ScheduleRepository(db)
        self.scheduling_service = SchedulingService(db)
        self.config_service = ChannelConfigurationService(db)

    def auto_distribute_by_filters(
        self,
        video_id: Optional[str] = None,
        channel_ids: Optional[List[str]] = None,
    ) -> List[VideoDistribution]:
        """
        Automatically distribute videos to channels based on content filters
        
        Args:
            video_id: Optional specific video ID (if None, processes all ready videos)
            channel_ids: Optional list of channel IDs to consider (if None, uses all active channels)
            
        Returns:
            List of created distributions
        """
        distributions = []
        
        # Get videos to distribute
        if video_id:
            video = self.video_repo.get_by_id(video_id)
            if not video:
                raise NotFoundError(f"Video {video_id} not found", resource_type="video")
            videos = [video]
        else:
            # Get all videos that are ready (downloaded and transformed)
            videos = self.video_repo.get_by_status("download", "downloaded")
            videos = [v for v in videos if v.transformation_status == "transformed"]
        
        # Get channels to consider
        if channel_ids:
            channels = [self.channel_repo.get_by_id(cid) for cid in channel_ids]
            channels = [c for c in channels if c and c.is_active]
        else:
            channels = self.channel_repo.get_all(active_only=True)
        
        # Distribute each video
        for video in videos:
            # Get video metadata (from source or stored metadata)
            video_metadata = self._get_video_metadata(video)
            
            # Match video to channels based on content filters
            matching_channels = self._match_channels_by_filters(video_metadata, channels)
            
            for channel in matching_channels:
                # Check for duplicates
                if self.distribution_repo.check_duplicate(video.id, channel.id):
                    logger.info(f"Skipping duplicate: Video {video.id} already distributed to channel {channel.id}")
                    continue
                
                # Create distribution
                distribution = self._create_distribution(
                    video_id=video.id,
                    channel_id=channel.id,
                    method="auto_filter",
                    reason=matching_channels[channel],
                )
                distributions.append(distribution)
                logger.info(f"Auto-distributed video {video.id} to channel {channel.id} (filter match)")
        
        return distributions

    def auto_distribute_by_schedule(
        self,
        video_id: Optional[str] = None,
        channel_ids: Optional[List[str]] = None,
    ) -> List[VideoDistribution]:
        """
        Automatically distribute videos to channels based on posting schedules
        
        Args:
            video_id: Optional specific video ID
            channel_ids: Optional list of channel IDs to consider
            
        Returns:
            List of created distributions
        """
        distributions = []
        
        # Get videos to distribute
        if video_id:
            video = self.video_repo.get_by_id(video_id)
            if not video:
                raise NotFoundError(f"Video {video_id} not found", resource_type="video")
            videos = [video]
        else:
            videos = self.video_repo.get_by_status("download", "downloaded")
            videos = [v for v in videos if v.transformation_status == "transformed"]
        
        # Get channels to consider
        if channel_ids:
            channels = [self.channel_repo.get_by_id(cid) for cid in channel_ids]
            channels = [c for c in channels if c and c.is_active]
        else:
            channels = self.channel_repo.get_all(active_only=True)
        
        # Distribute each video
        for video in videos:
            for channel in channels:
                # Check for duplicates
                if self.distribution_repo.check_duplicate(video.id, channel.id):
                    continue
                
                # Check channel schedule availability
                next_slot = self._get_next_schedule_slot(channel)
                if not next_slot:
                    logger.info(f"No available schedule slot for channel {channel.id}")
                    continue
                
                # Create distribution
                distribution = self._create_distribution(
                    video_id=video.id,
                    channel_id=channel.id,
                    method="auto_schedule",
                    reason={"next_slot": next_slot.isoformat()},
                )
                distributions.append(distribution)
                
                # Create schedule for publication
                try:
                    schedule = self.scheduling_service.create_independent_schedule(
                        channel_id=channel.id,
                        scheduled_at=next_slot,
                        video_id=video.id,
                    )
                    distribution.schedule_id = schedule.id
                    distribution.status = "scheduled"
                    self.distribution_repo.update(distribution)
                    logger.info(f"Scheduled video {video.id} for channel {channel.id} at {next_slot}")
                except Exception as e:
                    logger.error(f"Failed to create schedule: {e}")
                    distribution.status = "failed"
                    distribution.error_message = str(e)
                    self.distribution_repo.update(distribution)
        
        return distributions

    def manual_distribute(
        self,
        video_id: str,
        channel_ids: List[str],
        scheduled_at: Optional[datetime] = None,
        force: bool = False,
    ) -> List[VideoDistribution]:
        """
        Manually distribute video to specified channels
        
        Args:
            video_id: Video ID to distribute
            channel_ids: List of channel IDs
            scheduled_at: Optional scheduled publication time
            force: If True, override duplicate checks
            
        Returns:
            List of created distributions
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        distributions = []
        
        for channel_id in channel_ids:
            channel = self.channel_repo.get_by_id(channel_id)
            if not channel:
                raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
            
            if not channel.is_active and not force:
                logger.warning(f"Channel {channel_id} is not active, skipping")
                continue
            
            # Check for duplicates
            if not force and self.distribution_repo.check_duplicate(video_id, channel_id):
                raise ValidationError(f"Video {video_id} already distributed to channel {channel_id}")
            
            # Create distribution
            distribution = self._create_distribution(
                video_id=video_id,
                channel_id=channel_id,
                method="manual",
                reason={"forced": force, "scheduled_at": scheduled_at.isoformat() if scheduled_at else None},
            )
            distributions.append(distribution)
            
            # Create schedule if specified
            if scheduled_at:
                try:
                    schedule = self.scheduling_service.create_independent_schedule(
                        channel_id=channel_id,
                        scheduled_at=scheduled_at,
                        video_id=video_id,
                    )
                    distribution.schedule_id = schedule.id
                    distribution.status = "scheduled"
                    self.distribution_repo.update(distribution)
                except Exception as e:
                    logger.error(f"Failed to create schedule: {e}")
                    distribution.status = "failed"
                    distribution.error_message = str(e)
                    self.distribution_repo.update(distribution)
        
        return distributions

    def _match_channels_by_filters(
        self,
        video_metadata: Dict[str, Any],
        channels: List,
    ) -> Dict[Any, Dict[str, Any]]:
        """
        Match video to channels based on content filters
        
        Returns:
            Dictionary mapping channel to match reason
        """
        matching_channels = {}
        
        for channel in channels:
            try:
                # Get channel content filters
                content_filters = json.loads(channel.content_filters)
                
                # Apply filters
                min_resolution = content_filters.get("min_resolution", "720p")
                min_views = content_filters.get("min_views")
                max_duration = content_filters.get("max_duration")
                exclude_watermarked = content_filters.get("exclude_watermarked", True)
                
                if apply_filters(
                    video_metadata,
                    min_resolution=min_resolution,
                    min_views=min_views,
                    max_duration=max_duration,
                    exclude_watermarked=exclude_watermarked,
                ):
                    matching_channels[channel] = {
                        "matched_filters": {
                            "min_resolution": min_resolution,
                            "min_views": min_views,
                            "max_duration": max_duration,
                            "exclude_watermarked": exclude_watermarked,
                        }
                    }
            except Exception as e:
                logger.warning(f"Error matching channel {channel.id} filters: {e}")
                continue
        
        return matching_channels

    def _get_video_metadata(self, video) -> Dict[str, Any]:
        """Get video metadata for filtering"""
        # Try to get metadata from video model or source
        metadata = {
            "title": video.source_title,
            "resolution": video.download_resolution or "720p",
            "duration": video.download_duration or 0,
            "view_count": 0,  # May not be available
        }
        
        # Try to parse transformation params for additional metadata
        if video.transformation_params:
            try:
                params = json.loads(video.transformation_params)
                if "source_metadata" in params:
                    metadata.update(params["source_metadata"])
            except:
                pass
        
        return metadata

    def _get_next_schedule_slot(self, channel) -> Optional[datetime]:
        """Get next available schedule slot for channel"""
        try:
            posting_schedule = json.loads(channel.posting_schedule)
            frequency = posting_schedule.get("frequency", "daily")
            preferred_times = posting_schedule.get("preferred_times", ["12:00"])
            
            # Simple implementation: next preferred time
            now = datetime.utcnow()
            next_slot = now.replace(hour=12, minute=0, second=0, microsecond=0)
            
            if next_slot <= now:
                next_slot += timedelta(days=1)
            
            # Check if slot is available (no existing schedule)
            existing = self.schedule_repo.get_by_channel(
                channel.id,
                start_date=next_slot,
                end_date=next_slot + timedelta(minutes=1),
            )
            
            if existing:
                # Try next day
                next_slot += timedelta(days=1)
            
            return next_slot
        except Exception as e:
            logger.warning(f"Error getting schedule slot for channel {channel.id}: {e}")
            return None

    def _create_distribution(
        self,
        video_id: str,
        channel_id: str,
        method: str,
        reason: Dict[str, Any],
    ) -> VideoDistribution:
        """Create a video distribution record"""
        distribution = VideoDistribution(
            video_id=video_id,
            channel_id=channel_id,
            distribution_method=method,
            assignment_reason=json.dumps(reason),
            status="assigned",
        )
        return self.distribution_repo.create(distribution)

    def get_distribution_statistics(
        self,
        channel_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get distribution statistics"""
        return self.distribution_repo.get_statistics(channel_id, start_date, end_date)

    def retry_failed_distribution(self, distribution_id: str) -> VideoDistribution:
        """Retry a failed distribution"""
        distribution = self.distribution_repo.get_by_id(distribution_id)
        if not distribution:
            raise NotFoundError(f"Distribution {distribution_id} not found", resource_type="distribution")
        
        if distribution.status != "failed":
            raise ValidationError(f"Distribution {distribution_id} is not in failed status")
        
        retry_count = int(distribution.retry_count)
        max_retries = int(distribution.max_retries)
        
        if retry_count >= max_retries:
            raise ValidationError(f"Distribution {distribution_id} has exceeded max retries")
        
        # Reset status and increment retry count
        distribution.status = "assigned"
        distribution.retry_count = str(retry_count + 1)
        distribution.error_message = None
        distribution = self.distribution_repo.update(distribution)
        
        logger.info(f"Retrying distribution {distribution_id} (attempt {retry_count + 1}/{max_retries})")
        
        return distribution
