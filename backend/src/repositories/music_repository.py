"""
Music repository - data access layer for music tracks
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.music import Music
from src.utils.exceptions import NotFoundError


class MusicRepository:
    """Repository for music track data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, music: Music) -> Music:
        """Create a new music track"""
        self.db.add(music)
        self.db.commit()
        self.db.refresh(music)
        return music

    def get_by_id(self, music_id: str) -> Optional[Music]:
        """Get music track by ID"""
        return self.db.query(Music).filter(Music.id == music_id).first()

    def get_by_spotify_id(self, spotify_track_id: str) -> Optional[Music]:
        """Get music track by Spotify track ID"""
        return (
            self.db.query(Music)
            .filter(Music.spotify_track_id == spotify_track_id)
            .first()
        )

    def get_all(self, active_only: bool = False) -> List[Music]:
        """Get all music tracks, optionally filtered by active status"""
        query = self.db.query(Music)
        if active_only:
            query = query.filter(Music.is_active == True)
        return query.order_by(Music.usage_count.desc()).all()

    def update(self, music: Music) -> Music:
        """Update an existing music track"""
        self.db.commit()
        self.db.refresh(music)
        return music

    def delete(self, music_id: str) -> bool:
        """Delete a music track"""
        music = self.get_by_id(music_id)
        if not music:
            raise NotFoundError(f"Music track {music_id} not found", resource_type="music")
        self.db.delete(music)
        self.db.commit()
        return True

    def increment_usage(self, music_id: str) -> Music:
        """Increment usage count for a music track"""
        music = self.get_by_id(music_id)
        if not music:
            raise NotFoundError(f"Music track {music_id} not found", resource_type="music")
        music.usage_count += 1
        return self.update(music)
