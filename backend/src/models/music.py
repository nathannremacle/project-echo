"""
Music model - SQLAlchemy ORM model for music table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.orm import relationship

from src.database import Base


class Music(Base):
    """Music model - represents creator's personal music tracks (Phase 2)"""

    __tablename__ = "music"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic information
    name = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=True)
    spotify_track_id = Column(String(100), nullable=True, unique=True)
    spotify_track_url = Column(String(500), nullable=True)

    # File information
    file_path = Column(String(1000), nullable=True)  # Path in cloud storage
    file_size = Column(Integer, nullable=True)  # bytes
    duration = Column(Integer, nullable=True)  # seconds

    # Metadata (JSON)
    metadata = Column(Text, nullable=True)  # JSON string with additional metadata

    # Usage tracking
    usage_count = Column(Integer, nullable=False, default=0)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    videos = relationship("Video", back_populates="music_track")

    def __repr__(self) -> str:
        return f"<Music(id={self.id}, name={self.name}, spotify_track_id={self.spotify_track_id})>"
