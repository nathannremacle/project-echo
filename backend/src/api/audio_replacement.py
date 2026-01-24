"""
Audio replacement API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.audio_replacement.audio_replacement_service import AudioReplacementService
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

router = APIRouter(prefix="/api/videos", tags=["Audio Replacement"])


class ReplaceAudioRequest(BaseModel):
    music_id: str
    normalize: bool = True
    match_volume: bool = False
    audio_bitrate: Optional[str] = None
    audio_sample_rate: Optional[int] = None
    loop_audio: bool = True


class BatchReplaceAudioRequest(BaseModel):
    video_ids: List[str]
    music_id: str
    normalize: bool = True
    match_volume: bool = False
    audio_bitrate: Optional[str] = None
    audio_sample_rate: Optional[int] = None
    loop_audio: bool = True


@router.post("/{video_id}/replace-audio")
async def replace_audio_for_video(
    video_id: str,
    request: ReplaceAudioRequest,
    db: Session = Depends(get_db),
):
    """Replace audio in a single video with music track"""
    service = AudioReplacementService(db)
    try:
        result = service.replace_audio_for_video(
            video_id=video_id,
            music_id=request.music_id,
            normalize=request.normalize,
            match_volume=request.match_volume,
            audio_bitrate=request.audio_bitrate,
            audio_sample_rate=request.audio_sample_rate,
            loop_audio=request.loop_audio,
        )
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replace audio: {str(e)}")


@router.post("/batch-replace-audio")
async def batch_replace_audio(
    request: BatchReplaceAudioRequest,
    db: Session = Depends(get_db),
):
    """Replace audio for multiple videos"""
    service = AudioReplacementService(db)
    try:
        result = service.replace_audio_batch(
            video_ids=request.video_ids,
            music_id=request.music_id,
            normalize=request.normalize,
            match_volume=request.match_volume,
            audio_bitrate=request.audio_bitrate,
            audio_sample_rate=request.audio_sample_rate,
            loop_audio=request.loop_audio,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch replace audio: {str(e)}")


@router.post("/channels/{channel_id}/replace-audio")
async def replace_audio_for_channel(
    channel_id: str,
    request: ReplaceAudioRequest,
    db: Session = Depends(get_db),
):
    """Replace audio for all videos in a channel"""
    service = AudioReplacementService(db)
    try:
        result = service.replace_audio_for_channel(
            channel_id=channel_id,
            music_id=request.music_id,
            normalize=request.normalize,
            match_volume=request.match_volume,
            audio_bitrate=request.audio_bitrate,
            audio_sample_rate=request.audio_sample_rate,
            loop_audio=request.loop_audio,
        )
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replace audio for channel: {str(e)}")
