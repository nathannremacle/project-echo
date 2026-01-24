"""
Statistics models - SQLAlchemy ORM models for channel_statistics and video_statistics tables
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class ChannelStatistics(Base):
    """ChannelStatistics model - tracks channel statistics over time"""

    __tablename__ = "channel_statistics"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    channel_id = Column(String(36), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)

    # Statistics (snapshot at timestamp)
    subscriber_count = Column(BigInteger, nullable=False, default=0)
    view_count = Column(BigInteger, nullable=False, default=0)
    video_count = Column(Integer, nullable=False, default=0)
    total_views = Column(BigInteger, nullable=False, default=0)
    total_videos = Column(Integer, nullable=False, default=0)

    # Timestamp for this snapshot
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="statistics")

    def __repr__(self) -> str:
        return f"<ChannelStatistics(id={self.id}, channel_id={self.channel_id}, timestamp={self.timestamp})>"


class VideoStatistics(Base):
    """VideoStatistics model - tracks video statistics over time"""

    __tablename__ = "video_statistics"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    # Statistics (snapshot at timestamp)
    view_count = Column(BigInteger, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)

    # Timestamp for this snapshot
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="statistics")

    def __repr__(self) -> str:
        return f"<VideoStatistics(id={self.id}, video_id={self.video_id}, timestamp={self.timestamp})>"
