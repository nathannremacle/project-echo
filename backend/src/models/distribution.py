"""
VideoDistribution model - SQLAlchemy ORM model for video distribution tracking
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class VideoDistribution(Base):
    """VideoDistribution model - tracks video assignments to channels"""

    __tablename__ = "video_distributions"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(String(36), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)

    # Distribution information
    distribution_method = Column(
        String(50),
        nullable=False,
    )  # auto_filter, auto_schedule, manual
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Assignment reason/details (JSON)
    assignment_reason = Column(Text, nullable=True)  # JSON string explaining why assigned
    
    # Status
    status = Column(
        String(50),
        nullable=False,
        default="assigned",
        server_default="assigned",
    )  # assigned, scheduled, published, failed, cancelled

    # Publication tracking
    schedule_id = Column(String(36), ForeignKey("publication_schedules.id", ondelete="SET NULL"), nullable=True)
    published_at = Column(DateTime, nullable=True)
    youtube_video_id = Column(String(50), nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(String(10), nullable=False, default="0", server_default="0")
    max_retries = Column(String(10), nullable=False, default="3", server_default="3")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="distributions")
    channel = relationship("Channel", back_populates="distributions")
    schedule = relationship("PublicationSchedule", foreign_keys=[schedule_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "distribution_method IN ('auto_filter', 'auto_schedule', 'manual')",
            name="check_distribution_method",
        ),
        CheckConstraint(
            "status IN ('assigned', 'scheduled', 'published', 'failed', 'cancelled')",
            name="check_distribution_status",
        ),
    )

    def __repr__(self) -> str:
        return f"<VideoDistribution(id={self.id}, video_id={self.video_id}, channel_id={self.channel_id}, method={self.distribution_method}, status={self.status})>"
