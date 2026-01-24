"""
SystemConfiguration model - SQLAlchemy ORM model for system_configuration table
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Boolean

from src.database import Base


class SystemConfiguration(Base):
    """SystemConfiguration model - stores global system configuration"""

    __tablename__ = "system_configuration"

    # Primary key
    key = Column(String(255), primary_key=True)

    # Value (JSON string for complex data)
    value = Column(Text, nullable=False)

    # Metadata
    description = Column(Text, nullable=True)
    encrypted = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SystemConfiguration(key={self.key}, encrypted={self.encrypted})>"
