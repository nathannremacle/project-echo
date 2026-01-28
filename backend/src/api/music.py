"""
Music API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.music.music_service import MusicService
from src.utils.exceptions import ValidationError, ProcessingError

router = APIRouter(prefix="/music", tags=["Music"])


@router.get("")
async def list_music_tracks(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all music tracks"""
    service = MusicService(db)
    try:
        tracks = service.list_music(active_only=active_only)
        return {
            "tracks": [
                {
                    "id": track.id,
                    "name": track.name,
                    "artist": track.artist,
                    "spotifyUrl": track.spotify_track_url,
                    "fileSize": track.file_size,
                    "duration": track.duration,
                    "usageCount": track.usage_count,
                    "isActive": track.is_active,
                    "uploadedAt": track.created_at.isoformat() if track.created_at else None,
                }
                for track in tracks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list music tracks: {str(e)}")


@router.post("")
async def upload_music_track(
    file: UploadFile = File(...),
    name: str = Form(...),
    artist: Optional[str] = Form(None),
    spotifyUrl: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a new music track"""
    service = MusicService(db)
    try:
        music = service.upload_music(
            file=file.file,
            filename=file.filename or "unknown",
            name=name,
            artist=artist,
            spotify_url=spotifyUrl,
        )
        return {
            "id": music.id,
            "name": music.name,
            "artist": music.artist,
            "spotifyUrl": music.spotify_track_url,
            "fileSize": music.file_size,
            "duration": music.duration,
            "usageCount": music.usage_count,
            "isActive": music.is_active,
            "uploadedAt": music.created_at.isoformat() if music.created_at else None,
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload music track: {str(e)}")


@router.get("/{music_id}")
async def get_music_track(
    music_id: str,
    db: Session = Depends(get_db),
):
    """Get music track by ID"""
    service = MusicService(db)
    try:
        track = service.get_music(music_id)
        if not track:
            raise HTTPException(status_code=404, detail=f"Music track {music_id} not found")
        
        return {
            "id": track.id,
            "name": track.name,
            "artist": track.artist,
            "spotifyUrl": track.spotify_track_url,
            "fileSize": track.file_size,
            "duration": track.duration,
            "usageCount": track.usage_count,
            "isActive": track.is_active,
            "uploadedAt": track.created_at.isoformat() if track.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get music track: {str(e)}")


@router.delete("/{music_id}")
async def delete_music_track(
    music_id: str,
    db: Session = Depends(get_db),
):
    """Delete a music track"""
    service = MusicService(db)
    try:
        service.delete_music(music_id)
        return {"message": "Music track deleted successfully"}
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete music track: {str(e)}")


@router.get("/{music_id}/preview")
async def get_music_preview(
    music_id: str,
    expires_in: int = 3600,
    db: Session = Depends(get_db),
):
    """Get presigned URL for music preview"""
    service = MusicService(db)
    try:
        preview_url = service.get_preview_url(music_id, expires_in=expires_in)
        if not preview_url:
            raise HTTPException(status_code=404, detail=f"Music track {music_id} not found or has no file")
        return {"previewUrl": preview_url, "expiresIn": expires_in}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preview URL: {str(e)}")
