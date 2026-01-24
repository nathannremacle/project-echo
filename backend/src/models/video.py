"""
Video model - SQLAlchemy ORM model for videos table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class Video(Base):
    """Video model - represents a video throughout its lifecycle"""

    __tablename__ = "videos"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    channel_id = Column(String(36), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)

    # Source information
    source_url = Column(String(1000), nullable=False)
    source_title = Column(String(500), nullable=False)
    source_creator = Column(String(255), nullable=True)
    source_platform = Column(String(100), nullable=False)
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Download status
    download_status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )  # pending, downloading, downloaded, failed
    download_url = Column(String(1000), nullable=True)
    download_size = Column(Integer, nullable=True)  # bytes
    download_duration = Column(Integer, nullable=True)  # seconds
    download_resolution = Column(String(50), nullable=True)

    # Transformation status
    transformation_status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )  # pending, processing, transformed, failed
    transformation_preset_id = Column(String(36), ForeignKey("transformation_presets.id", ondelete="SET NULL"), nullable=True)
    transformation_params = Column(Text, nullable=True)  # JSON string
    transformed_url = Column(String(1000), nullable=True)
    transformed_size = Column(Integer, nullable=True)  # bytes
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_duration = Column(Integer, nullable=True)  # seconds

    # Publication status
    publication_status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )  # pending, scheduled, publishing, published, failed
    scheduled_publication_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    youtube_video_id = Column(String(50), nullable=True)
    youtube_video_url = Column(String(500), nullable=True)

    # Final metadata used on YouTube
    final_title = Column(String(500), nullable=True)
    final_description = Column(Text, nullable=True)
    final_tags = Column(Text, nullable=True)  # JSON array string

    # Phase 2 support
    music_replaced = Column(Boolean, nullable=False, default=False)
    music_track_id = Column(String(36), ForeignKey("music.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="videos")
    transformation_preset = relationship("TransformationPreset", back_populates="videos")
    music_track = relationship("Music", back_populates="videos")
    processing_jobs = relationship("VideoProcessingJob", back_populates="video", cascade="all, delete-orphan")
    statistics = relationship("VideoStatistics", back_populates="video", cascade="all, delete-orphan")
    publication_schedules = relationship("PublicationSchedule", back_populates="video", cascade="all, delete-orphan")
    distributions = relationship("VideoDistribution", back_populates="video", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "download_status IN ('pending', 'downloading', 'downloaded', 'failed')",
            name="check_download_status",
        ),
        CheckConstraint(
            "transformation_status IN ('pending', 'processing', 'transformed', 'failed')",
            name="check_transformation_status",
        ),
        CheckConstraint(
            "publication_status IN ('pending', 'scheduled', 'publishing', 'published', 'failed')",
            name="check_publication_status",
        ),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, source_title={self.source_title[:50]}, status={self.publication_status})>"
