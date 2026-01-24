"""
Enhanced analytics service - tracks music promotion effectiveness and wave metrics
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.models.video import Video
from src.models.channel import Channel
from src.models.statistics import ChannelStatistics, VideoStatistics
from src.repositories.video_repository import VideoRepository
from src.repositories.channel_repository import ChannelRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)


class EnhancedAnalyticsService:
    """Service for enhanced analytics and music promotion metrics"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)

    def get_music_promotion_metrics(
        self,
        channel_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get music promotion metrics
        
        Args:
            channel_ids: Optional list of channel IDs to filter
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dictionary with music promotion metrics
        """
        # Get videos with music replacement
        query = self.db.query(Video).filter(Video.music_replaced == True)
        
        if channel_ids:
            query = query.filter(Video.channel_id.in_(channel_ids))
        
        if start_date:
            query = query.filter(Video.published_at >= start_date)
        
        if end_date:
            query = query.filter(Video.published_at <= end_date)
        
        music_videos = query.all()
        
        # Get total views for music videos (from video statistics)
        total_views = 0
        for video in music_videos:
            latest_stats = (
                self.db.query(VideoStatistics)
                .filter(VideoStatistics.video_id == video.id)
                .order_by(VideoStatistics.timestamp.desc())
                .first()
            )
            if latest_stats:
                total_views += latest_stats.view_count
        
        # Get unique music tracks used
        music_tracks = set()
        for video in music_videos:
            if video.music_track_id:
                music_tracks.add(video.music_track_id)
        
        return {
            "total_music_videos": len(music_videos),
            "total_views": total_views,
            "unique_music_tracks": len(music_tracks),
            "average_views_per_video": total_views / len(music_videos) if music_videos else 0,
            "videos": [
                {
                    "id": v.id,
                    "title": v.source_title,
                    "channel_id": v.channel_id,
                    "published_at": v.published_at.isoformat() if v.published_at else None,
                    "music_track_id": v.music_track_id,
                }
                for v in music_videos[:10]  # Limit to 10 for response size
            ],
        }

    def get_wave_effect_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        time_window_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Get wave effect metrics (simultaneous publications)
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            time_window_hours: Time window in hours to consider simultaneous
            
        Returns:
            Dictionary with wave effect metrics
        """
        # Get all published videos
        query = self.db.query(Video).filter(Video.publication_status == "published")
        
        if start_date:
            query = query.filter(Video.published_at >= start_date)
        
        if end_date:
            query = query.filter(Video.published_at <= end_date)
        
        published_videos = query.all()
        
        # Group videos by time windows
        waves = []
        time_window = timedelta(hours=time_window_hours)
        
        for video in published_videos:
            if not video.published_at:
                continue
            
            # Find or create wave
            wave_found = False
            for wave in waves:
                wave_start = wave["start_time"]
                wave_end = wave_start + time_window
                
                if wave_start <= video.published_at <= wave_end:
                    wave["videos"].append(video.id)
                    wave["channels"].add(video.channel_id)
                    wave_found = True
                    break
            
            if not wave_found:
                waves.append({
                    "start_time": video.published_at,
                    "videos": [video.id],
                    "channels": {video.channel_id},
                })
        
        # Calculate wave metrics
        if waves:
            largest_wave = max(waves, key=lambda w: len(w["videos"]))
            total_reach = sum(len(w["channels"]) for w in waves)
            
            return {
                "total_waves": len(waves),
                "largest_wave": {
                    "videos_count": len(largest_wave["videos"]),
                    "channels_count": len(largest_wave["channels"]),
                    "start_time": largest_wave["start_time"].isoformat(),
                },
                "average_wave_size": sum(len(w["videos"]) for w in waves) / len(waves),
                "total_reach": total_reach,
                "average_reach_per_wave": total_reach / len(waves) if waves else 0,
            }
        else:
            return {
                "total_waves": 0,
                "largest_wave": None,
                "average_wave_size": 0,
                "total_reach": 0,
                "average_reach_per_wave": 0,
            }

    def get_phase2_comparison(
        self,
        channel_ids: Optional[List[str]] = None,
        phase2_start_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Compare pre-Phase 2 and post-Phase 2 performance
        
        Args:
            channel_ids: Optional list of channel IDs
            phase2_start_date: Date when Phase 2 started (if None, uses channel phase2_enabled)
            
        Returns:
            Dictionary with pre/post comparison
        """
        # Get channels
        if channel_ids:
            channels = [self.channel_repo.get_by_id(cid) for cid in channel_ids]
            channels = [c for c in channels if c]
        else:
            channels = self.channel_repo.get_all(active_only=True)
        
        pre_phase2_metrics = {
            "total_videos": 0,
            "total_views": 0,
            "average_views_per_video": 0,
        }
        
        post_phase2_metrics = {
            "total_videos": 0,
            "total_views": 0,
            "average_views_per_video": 0,
        }
        
        for channel in channels:
            # Determine Phase 2 start date
            if phase2_start_date:
                phase2_start = phase2_start_date
            else:
                # Use channel updated_at when phase2_enabled was set (simplified)
                phase2_start = channel.updated_at if channel.phase2_enabled else None
            
            if not phase2_start:
                continue
            
            # Get videos
            videos = self.video_repo.get_by_channel_id(channel.id)
            
            for video in videos:
                if not video.published_at:
                    continue
                
                # Get latest stats
                latest_stats = (
                    self.db.query(VideoStatistics)
                    .filter(VideoStatistics.video_id == video.id)
                    .order_by(VideoStatistics.timestamp.desc())
                    .first()
                )
                
                views = latest_stats.view_count if latest_stats else 0
                
                if video.published_at < phase2_start:
                    pre_phase2_metrics["total_videos"] += 1
                    pre_phase2_metrics["total_views"] += views
                else:
                    post_phase2_metrics["total_videos"] += 1
                    post_phase2_metrics["total_views"] += views
        
        # Calculate averages
        if pre_phase2_metrics["total_videos"] > 0:
            pre_phase2_metrics["average_views_per_video"] = (
                pre_phase2_metrics["total_views"] / pre_phase2_metrics["total_videos"]
            )
        
        if post_phase2_metrics["total_videos"] > 0:
            post_phase2_metrics["average_views_per_video"] = (
                post_phase2_metrics["total_views"] / post_phase2_metrics["total_videos"]
            )
        
        # Calculate improvement
        improvement = {}
        if pre_phase2_metrics["average_views_per_video"] > 0:
            improvement["views_per_video"] = (
                (post_phase2_metrics["average_views_per_video"] - pre_phase2_metrics["average_views_per_video"])
                / pre_phase2_metrics["average_views_per_video"]
                * 100
            )
        else:
            improvement["views_per_video"] = 0
        
        return {
            "pre_phase2": pre_phase2_metrics,
            "post_phase2": post_phase2_metrics,
            "improvement": improvement,
        }

    def get_roi_metrics(
        self,
        channel_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate ROI metrics for music promotion
        
        Args:
            channel_ids: Optional list of channel IDs
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dictionary with ROI metrics
        """
        # Get music promotion metrics
        music_metrics = self.get_music_promotion_metrics(
            channel_ids=channel_ids,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Estimate effort (number of videos processed)
        effort = music_metrics["total_music_videos"]
        
        # Estimate results (total views)
        results = music_metrics["total_views"]
        
        # Calculate ROI (simplified: views per video processed)
        roi = results / effort if effort > 0 else 0
        
        return {
            "effort": effort,
            "results": results,
            "roi": roi,
            "efficiency": {
                "views_per_video": roi,
                "average_views": music_metrics["average_views_per_video"],
            },
        }

    def get_insights(
        self,
        channel_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get key insights from analytics
        
        Args:
            channel_ids: Optional list of channel IDs
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Get music promotion metrics
        music_metrics = self.get_music_promotion_metrics(
            channel_ids=channel_ids,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Insight: High performing music videos
        if music_metrics["average_views_per_video"] > 1000:
            insights.append({
                "type": "success",
                "title": "High Performing Music Videos",
                "message": f"Music videos average {music_metrics['average_views_per_video']:.0f} views per video",
                "metric": "average_views",
                "value": music_metrics["average_views_per_video"],
            })
        
        # Get wave metrics
        wave_metrics = self.get_wave_effect_metrics(start_date=start_date, end_date=end_date)
        
        # Insight: Large wave detected
        if wave_metrics["largest_wave"] and wave_metrics["largest_wave"]["videos_count"] > 5:
            insights.append({
                "type": "info",
                "title": "Large Wave Detected",
                "message": f"Largest wave had {wave_metrics['largest_wave']['videos_count']} videos across {wave_metrics['largest_wave']['channels_count']} channels",
                "metric": "wave_size",
                "value": wave_metrics["largest_wave"]["videos_count"],
            })
        
        # Get Phase 2 comparison
        comparison = self.get_phase2_comparison(channel_ids=channel_ids)
        
        # Insight: Phase 2 improvement
        if comparison["improvement"]["views_per_video"] > 20:
            insights.append({
                "type": "success",
                "title": "Phase 2 Success",
                "message": f"Phase 2 improved views per video by {comparison['improvement']['views_per_video']:.1f}%",
                "metric": "phase2_improvement",
                "value": comparison["improvement"]["views_per_video"],
            })
        
        return insights

    def get_recommendations(
        self,
        channel_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on analytics
        
        Args:
            channel_ids: Optional list of channel IDs
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Get channels
        if channel_ids:
            channels = [self.channel_repo.get_by_id(cid) for cid in channel_ids]
            channels = [c for c in channels if c]
        else:
            channels = self.channel_repo.get_all(active_only=True)
        
        # Recommendation: Enable Phase 2 for channels without it
        channels_without_phase2 = [c for c in channels if not c.phase2_enabled and c.is_active]
        if channels_without_phase2:
            recommendations.append({
                "type": "action",
                "title": "Enable Phase 2",
                "message": f"Consider enabling Phase 2 for {len(channels_without_phase2)} active channel(s)",
                "action": "enable_phase2",
                "channels": [c.id for c in channels_without_phase2],
            })
        
        # Get music promotion metrics
        music_metrics = self.get_music_promotion_metrics(channel_ids=channel_ids)
        
        # Recommendation: Increase music video production
        if music_metrics["total_music_videos"] < 10:
            recommendations.append({
                "type": "suggestion",
                "title": "Increase Music Video Production",
                "message": f"Only {music_metrics['total_music_videos']} music videos published. Consider increasing production for better reach.",
                "action": "increase_production",
            })
        
        return recommendations
