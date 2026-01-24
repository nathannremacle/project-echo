"""
Channel model - SQLAlchemy ORM model for channels table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class Channel(Base):
    """Channel model - represents a YouTube channel managed by the system"""

    __tablename__ = "channels"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic information
    name = Column(String(255), nullable=False)
    youtube_channel_id = Column(String(255), nullable=False, unique=True)
    youtube_channel_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)

    # Encrypted OAuth credentials (stored as encrypted JSON string)
    api_credentials_encrypted = Column(Text, nullable=False)

    # Posting schedule (JSON)
    posting_schedule = Column(Text, nullable=False)  # JSON string

    # Content filters (JSON)
    content_filters = Column(Text, nullable=False)  # JSON string

    # Metadata template (JSON)
    metadata_template = Column(Text, nullable=False)  # JSON string

    # Optional references
    effect_preset_id = Column(String(36), ForeignKey("transformation_presets.id", ondelete="SET NULL"), nullable=True)
    github_repo_url = Column(String(500), nullable=True)
    github_secret_key_encrypted = Column(Text, nullable=True)  # Encrypted

    # Phase 2 support
    phase2_enabled = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_publication_at = Column(DateTime, nullable=True)

    # Relationships
    videos = relationship("Video", back_populates="channel", cascade="all, delete-orphan")
    processing_jobs = relationship("VideoProcessingJob", back_populates="channel", cascade="all, delete-orphan")
    statistics = relationship("ChannelStatistics", back_populates="channel", cascade="all, delete-orphan")
    transformation_preset = relationship("TransformationPreset", back_populates="channels")
    publication_schedules = relationship("PublicationSchedule", back_populates="channel", cascade="all, delete-orphan")
    distributions = relationship("VideoDistribution", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, name={self.name}, youtube_channel_id={self.youtube_channel_id})>"
