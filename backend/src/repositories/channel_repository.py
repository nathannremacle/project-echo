"""
Channel repository - data access layer for channels
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.channel import Channel
from src.utils.exceptions import NotFoundError


class ChannelRepository:
    """Repository for channel data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, channel: Channel) -> Channel:
        """Create a new channel"""
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def get_by_id(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID"""
        return self.db.query(Channel).filter(Channel.id == channel_id).first()

    def get_by_youtube_channel_id(self, youtube_channel_id: str) -> Optional[Channel]:
        """Get channel by YouTube channel ID"""
        return (
            self.db.query(Channel)
            .filter(Channel.youtube_channel_id == youtube_channel_id)
            .first()
        )

    def get_all(self, active_only: bool = False) -> List[Channel]:
        """Get all channels, optionally filtered by active status"""
        query = self.db.query(Channel)
        if active_only:
            query = query.filter(Channel.is_active == True)
        return query.all()

    def update(self, channel: Channel) -> Channel:
        """Update an existing channel"""
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def delete(self, channel_id: str) -> bool:
        """Delete a channel"""
        channel = self.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        self.db.delete(channel)
        self.db.commit()
        return True

    def exists(self, channel_id: str) -> bool:
        """Check if channel exists"""
        return self.get_by_id(channel_id) is not None
