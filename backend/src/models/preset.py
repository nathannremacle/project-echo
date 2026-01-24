"""
TransformationPreset model - SQLAlchemy ORM model for transformation_presets table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

from src.database import Base


class TransformationPreset(Base):
    """TransformationPreset model - reusable transformation presets"""

    __tablename__ = "transformation_presets"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Transformation parameters (JSON)
    parameters = Column(Text, nullable=False)  # JSON string with effect parameters

    # Metadata
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    channels = relationship("Channel", back_populates="transformation_preset")
    videos = relationship("Video", back_populates="preset")

    def __repr__(self) -> str:
        return f"<TransformationPreset(id={self.id}, name={self.name})>"
