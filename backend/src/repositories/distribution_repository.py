"""
Distribution repository - data access layer for video distributions
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.models.distribution import VideoDistribution
from src.utils.exceptions import NotFoundError


class DistributionRepository:
    """Repository for video distribution data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, distribution: VideoDistribution) -> VideoDistribution:
        """Create a new video distribution"""
        self.db.add(distribution)
        self.db.commit()
        self.db.refresh(distribution)
        return distribution

    def get_by_id(self, distribution_id: str) -> Optional[VideoDistribution]:
        """Get distribution by ID"""
        return self.db.query(VideoDistribution).filter(VideoDistribution.id == distribution_id).first()

    def get_by_video(self, video_id: str) -> List[VideoDistribution]:
        """Get all distributions for a video"""
        return (
            self.db.query(VideoDistribution)
            .filter(VideoDistribution.video_id == video_id)
            .order_by(VideoDistribution.assigned_at)
            .all()
        )

    def get_by_channel(self, channel_id: str, status: Optional[str] = None) -> List[VideoDistribution]:
        """Get all distributions for a channel"""
        query = self.db.query(VideoDistribution).filter(VideoDistribution.channel_id == channel_id)
        
        if status:
            query = query.filter(VideoDistribution.status == status)
        
        return query.order_by(VideoDistribution.assigned_at.desc()).all()

    def get_by_video_and_channel(self, video_id: str, channel_id: str) -> Optional[VideoDistribution]:
        """Get distribution for a specific video and channel"""
        return (
            self.db.query(VideoDistribution)
            .filter(
                and_(
                    VideoDistribution.video_id == video_id,
                    VideoDistribution.channel_id == channel_id,
                )
            )
            .first()
        )

    def check_duplicate(self, video_id: str, channel_id: str) -> bool:
        """Check if video is already distributed to channel"""
        distribution = self.get_by_video_and_channel(video_id, channel_id)
        if not distribution:
            return False
        
        # Check if already published or scheduled
        return distribution.status in ["scheduled", "published"]

    def get_statistics(
        self,
        channel_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Get distribution statistics"""
        query = self.db.query(VideoDistribution)
        
        if channel_id:
            query = query.filter(VideoDistribution.channel_id == channel_id)
        
        if start_date:
            query = query.filter(VideoDistribution.assigned_at >= start_date)
        
        if end_date:
            query = query.filter(VideoDistribution.assigned_at <= end_date)
        
        total = query.count()
        
        # Count by status
        status_counts = (
            query.with_entities(VideoDistribution.status, func.count(VideoDistribution.id))
            .group_by(VideoDistribution.status)
            .all()
        )
        
        # Count by method
        method_counts = (
            query.with_entities(VideoDistribution.distribution_method, func.count(VideoDistribution.id))
            .group_by(VideoDistribution.distribution_method)
            .all()
        )
        
        # Calculate success rate
        published_count = sum(count for status, count in status_counts if status == "published")
        success_rate = (published_count / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "by_status": {status: count for status, count in status_counts},
            "by_method": {method: count for method, count in method_counts},
            "success_rate": round(success_rate, 2),
            "published_count": published_count,
        }

    def update(self, distribution: VideoDistribution) -> VideoDistribution:
        """Update an existing distribution"""
        self.db.commit()
        self.db.refresh(distribution)
        return distribution

    def delete(self, distribution_id: str) -> bool:
        """Delete a distribution"""
        distribution = self.get_by_id(distribution_id)
        if not distribution:
            raise NotFoundError(f"Distribution {distribution_id} not found", resource_type="distribution")
        self.db.delete(distribution)
        self.db.commit()
        return True

    def get_all(
        self,
        status: Optional[str] = None,
        distribution_method: Optional[str] = None,
    ) -> List[VideoDistribution]:
        """Get all distributions, optionally filtered"""
        query = self.db.query(VideoDistribution)
        
        if status:
            query = query.filter(VideoDistribution.status == status)
        
        if distribution_method:
            query = query.filter(VideoDistribution.distribution_method == distribution_method)
        
        return query.order_by(VideoDistribution.assigned_at.desc()).all()
