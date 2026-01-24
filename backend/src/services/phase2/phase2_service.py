"""
Phase 2 service - handles music promotion activation and configuration
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.models.channel import Channel
from src.models.video import Video
from src.repositories.channel_repository import ChannelRepository
from src.repositories.video_repository import VideoRepository
from src.repositories.music_repository import MusicRepository
from src.services.audio_replacement.audio_replacement_service import AudioReplacementService
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

logger = get_logger(__name__)


class Phase2Service:
    """Service for managing Phase 2 (music promotion) activation"""

    def __init__(self, db: Session):
        self.db = db
        self.channel_repo = ChannelRepository(db)
        self.video_repo = VideoRepository(db)
        self.music_repo = MusicRepository(db)
        self.audio_replacement_service = AudioReplacementService(db)

    def check_channel_readiness(
        self,
        channel_id: str,
        min_subscribers: Optional[int] = None,
        min_views: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Check if channel is ready for Phase 2
        
        Args:
            channel_id: Channel ID
            min_subscribers: Minimum subscriber count (optional)
            min_views: Minimum total views (optional)
            
        Returns:
            Dictionary with readiness status
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Get latest channel statistics
        # For MVP, we'll use a simplified check
        # In production, would query ChannelStatistics table
        readiness = {
            "channel_id": channel_id,
            "ready": True,
            "checks": {},
        }
        
        # Check subscriber count (if threshold provided)
        if min_subscribers:
            # Would query statistics in production
            # For MVP, assume ready if channel is active
            readiness["checks"]["subscribers"] = {
                "required": min_subscribers,
                "current": None,  # Would be from statistics
                "met": True,  # Simplified for MVP
            }
        
        # Check view count (if threshold provided)
        if min_views:
            # Would query statistics in production
            readiness["checks"]["views"] = {
                "required": min_views,
                "current": None,  # Would be from statistics
                "met": True,  # Simplified for MVP
            }
        
        # Overall readiness
        readiness["ready"] = all(
            check.get("met", True) for check in readiness["checks"].values()
        )
        
        return readiness

    def activate_phase2(
        self,
        channel_ids: List[str],
        music_id: str,
        video_filter: Optional[Dict[str, Any]] = None,
        apply_retroactive: bool = False,
        normalize: bool = True,
        loop_audio: bool = True,
    ) -> Dict[str, Any]:
        """
        Activate Phase 2 for selected channels
        
        Args:
            channel_ids: List of channel IDs (empty list = all channels)
            music_id: Music track ID to use
            video_filter: Optional filter for which videos to process
            apply_retroactive: Whether to apply to already published videos
            normalize: Normalize audio levels
            loop_audio: Loop audio if shorter than video
            
        Returns:
            Dictionary with activation results
        """
        # Validate music track
        music = self.music_repo.get_by_id(music_id)
        if not music:
            raise NotFoundError(f"Music track {music_id} not found", resource_type="music")
        
        # Get channels to activate
        if not channel_ids:
            # All active channels
            channels = self.channel_repo.get_all(active_only=True)
            channel_ids = [c.id for c in channels]
        else:
            # Selected channels
            channels = [self.channel_repo.get_by_id(cid) for cid in channel_ids]
            channels = [c for c in channels if c]
            if len(channels) != len(channel_ids):
                raise ValidationError("Some channel IDs not found")
        
        results = {
            "activated": [],
            "failed": [],
            "total": len(channel_ids),
        }
        
        for channel in channels:
            try:
                # Enable Phase 2 for channel
                channel.phase2_enabled = True
                channel = self.channel_repo.update(channel)
                
                # Get videos to process
                videos = self._get_videos_for_phase2(
                    channel_id=channel.id,
                    video_filter=video_filter,
                    include_published=apply_retroactive,
                )
                
                # Replace audio for videos
                if videos:
                    video_ids = [v.id for v in videos]
                    audio_results = self.audio_replacement_service.replace_audio_batch(
                        video_ids=video_ids,
                        music_id=music_id,
                        normalize=normalize,
                        loop_audio=loop_audio,
                    )
                    
                    results["activated"].append({
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                        "videos_processed": len(audio_results["success"]),
                        "videos_failed": len(audio_results["failed"]),
                    })
                else:
                    results["activated"].append({
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                        "videos_processed": 0,
                        "videos_failed": 0,
                    })
                
                logger.info(f"Phase 2 activated for channel {channel.id}")
                
            except Exception as e:
                logger.error(f"Failed to activate Phase 2 for channel {channel.id}: {e}")
                results["failed"].append({
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                    "error": str(e),
                })
        
        return results

    def deactivate_phase2(
        self,
        channel_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Deactivate Phase 2 for channels
        
        Args:
            channel_ids: List of channel IDs (None = all channels)
            
        Returns:
            Dictionary with deactivation results
        """
        if channel_ids is None:
            # All channels with Phase 2 enabled
            channels = self.channel_repo.get_all(active_only=False)
            channels = [c for c in channels if c.phase2_enabled]
        else:
            channels = [self.channel_repo.get_by_id(cid) for cid in channel_ids]
            channels = [c for c in channels if c]
        
        results = {
            "deactivated": [],
            "failed": [],
            "total": len(channels),
        }
        
        for channel in channels:
            try:
                channel.phase2_enabled = False
                channel = self.channel_repo.update(channel)
                
                results["deactivated"].append({
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                })
                
                logger.info(f"Phase 2 deactivated for channel {channel.id}")
                
            except Exception as e:
                logger.error(f"Failed to deactivate Phase 2 for channel {channel.id}: {e}")
                results["failed"].append({
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                    "error": str(e),
                })
        
        return results

    def get_phase2_status(self) -> Dict[str, Any]:
        """
        Get Phase 2 status across all channels
        
        Returns:
            Dictionary with Phase 2 status
        """
        all_channels = self.channel_repo.get_all(active_only=False)
        
        phase2_channels = [c for c in all_channels if c.phase2_enabled]
        active_channels = [c for c in all_channels if c.is_active]
        
        # Get music tracks
        music_tracks = self.music_repo.get_all(active_only=True)
        
        return {
            "phase2_enabled": len(phase2_channels) > 0,
            "phase2_channels_count": len(phase2_channels),
            "total_channels": len(all_channels),
            "active_channels": len(active_channels),
            "channels": [
                {
                    "id": c.id,
                    "name": c.name,
                    "phase2_enabled": c.phase2_enabled,
                    "is_active": c.is_active,
                }
                for c in all_channels
            ],
            "available_music_tracks": len(music_tracks),
        }

    def apply_retroactive(
        self,
        channel_ids: List[str],
        music_id: str,
        video_filter: Optional[Dict[str, Any]] = None,
        normalize: bool = True,
        loop_audio: bool = True,
    ) -> Dict[str, Any]:
        """
        Apply Phase 2 retroactively to already published videos
        
        Args:
            channel_ids: List of channel IDs
            music_id: Music track ID
            video_filter: Optional filter for videos
            normalize: Normalize audio levels
            loop_audio: Loop audio if shorter
            
        Returns:
            Dictionary with results
        """
        results = {
            "processed": [],
            "failed": [],
            "total": 0,
        }
        
        for channel_id in channel_ids:
            channel = self.channel_repo.get_by_id(channel_id)
            if not channel:
                results["failed"].append({
                    "channel_id": channel_id,
                    "error": "Channel not found",
                })
                continue
            
            # Get published videos
            videos = self._get_videos_for_phase2(
                channel_id=channel_id,
                video_filter=video_filter,
                include_published=True,
                only_published=True,
            )
            
            if videos:
                video_ids = [v.id for v in videos]
                audio_results = self.audio_replacement_service.replace_audio_batch(
                    video_ids=video_ids,
                    music_id=music_id,
                    normalize=normalize,
                    loop_audio=loop_audio,
                )
                
                results["processed"].append({
                    "channel_id": channel_id,
                    "channel_name": channel.name,
                    "videos_processed": len(audio_results["success"]),
                    "videos_failed": len(audio_results["failed"]),
                })
                results["total"] += len(audio_results["success"])
        
        return results

    def _get_videos_for_phase2(
        self,
        channel_id: str,
        video_filter: Optional[Dict[str, Any]] = None,
        include_published: bool = False,
        only_published: bool = False,
    ) -> List[Video]:
        """
        Get videos to process for Phase 2
        
        Args:
            channel_id: Channel ID
            video_filter: Optional filter dictionary
            include_published: Include already published videos
            only_published: Only get published videos
            
        Returns:
            List of videos to process
        """
        # Get videos by channel
        if only_published:
            videos = self.video_repo.get_by_status("publication", "published", channel_id=channel_id)
        else:
            videos = self.video_repo.get_by_channel_id(channel_id)
        
        # Filter out videos that already have music replaced
        videos = [v for v in videos if not v.music_replaced]
        
        # Apply additional filters if provided
        if video_filter:
            # Filter by transformation status
            if "transformation_status" in video_filter:
                status = video_filter["transformation_status"]
                videos = [v for v in videos if v.transformation_status == status]
            
            # Filter by date range
            if "created_after" in video_filter:
                from datetime import datetime
                after_date = datetime.fromisoformat(video_filter["created_after"])
                videos = [v for v in videos if v.created_at >= after_date]
            
            if "created_before" in video_filter:
                from datetime import datetime
                before_date = datetime.fromisoformat(video_filter["created_before"])
                videos = [v for v in videos if v.created_at <= before_date]
        
        # Exclude published videos unless include_published is True
        if not include_published and not only_published:
            videos = [v for v in videos if v.publication_status != "published"]
        
        return videos
