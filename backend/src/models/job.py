"""
VideoProcessingJob model - SQLAlchemy ORM model for video_processing_jobs table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class VideoProcessingJob(Base):
    """VideoProcessingJob model - represents a job in the processing queue"""

    __tablename__ = "video_processing_jobs"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(String(36), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)

    # Job information
    job_type = Column(String(50), nullable=False)  # scrape, download, transform, publish, music_replace
    status = Column(
        String(50),
        nullable=False,
        default="queued",
        server_default="queued",
    )  # queued, processing, completed, failed, retrying

    # Retry logic
    priority = Column(Integer, nullable=False, default=0)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)

    # Error information
    error_message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)  # JSON string

    # Timing
    queued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds

    # GitHub Actions integration
    github_workflow_run_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="processing_jobs")
    channel = relationship("Channel", back_populates="processing_jobs")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "job_type IN ('scrape', 'download', 'transform', 'publish', 'music_replace')",
            name="check_job_type",
        ),
        CheckConstraint(
            "status IN ('queued', 'processing', 'completed', 'failed', 'retrying')",
            name="check_job_status",
        ),
        CheckConstraint("attempts >= 0", name="check_attempts_positive"),
        CheckConstraint("max_attempts > 0", name="check_max_attempts_positive"),
    )

    def __repr__(self) -> str:
        return f"<VideoProcessingJob(id={self.id}, job_type={self.job_type}, status={self.status})>"
