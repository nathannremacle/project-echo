"""
PublicationSchedule model - SQLAlchemy ORM model for publication_schedules table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class PublicationSchedule(Base):
    """PublicationSchedule model - represents a scheduled video publication"""

    __tablename__ = "publication_schedules"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    channel_id = Column(String(36), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)  # Optional for independent schedules

    # Schedule information
    schedule_type = Column(
        String(50),
        nullable=False,
    )  # simultaneous, staggered, independent
    scheduled_at = Column(DateTime, nullable=False)  # When to execute
    delay_seconds = Column(Integer, nullable=True)  # Delay for staggered (relative to first channel)
    
    # Status
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )  # pending, scheduled, executing, completed, failed, cancelled

    # Coordination metadata
    coordination_group_id = Column(String(36), nullable=True)  # For simultaneous/staggered coordination
    wave_id = Column(String(36), nullable=True)  # For viral wave publications
    
    # Additional metadata (JSON) - attribute named metadata_info to avoid SQLAlchemy reserved "metadata"
    metadata_info = Column(Text, nullable=True)  # JSON string for additional data

    # Pause/resume
    is_paused = Column(Boolean, nullable=False, default=False, server_default="0")

    # Execution information
    executed_at = Column(DateTime, nullable=True)
    execution_result = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="publication_schedules")
    video = relationship("Video", back_populates="publication_schedules")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "schedule_type IN ('simultaneous', 'staggered', 'independent')",
            name="check_schedule_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'scheduled', 'executing', 'completed', 'failed', 'cancelled')",
            name="check_schedule_status",
        ),
        CheckConstraint("delay_seconds >= 0", name="check_delay_positive"),
    )

    def __repr__(self) -> str:
        return f"<PublicationSchedule(id={self.id}, schedule_type={self.schedule_type}, scheduled_at={self.scheduled_at}, status={self.status})>"
