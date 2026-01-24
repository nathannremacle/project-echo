"""
Phase 2 API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.phase2.phase2_service import Phase2Service
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

router = APIRouter(prefix="/api/phase2", tags=["Phase 2"])


class ActivatePhase2Request(BaseModel):
    channel_ids: List[str] = []  # Empty = all channels
    music_id: str
    video_filter: Optional[dict] = None
    apply_retroactive: bool = False
    normalize: bool = True
    loop_audio: bool = True


class DeactivatePhase2Request(BaseModel):
    channel_ids: Optional[List[str]] = None  # None = all channels


class ApplyRetroactiveRequest(BaseModel):
    channel_ids: List[str]
    music_id: str
    video_filter: Optional[dict] = None
    normalize: bool = True
    loop_audio: bool = True


class CheckReadinessRequest(BaseModel):
    channel_id: str
    min_subscribers: Optional[int] = None
    min_views: Optional[int] = None


@router.post("/activate")
async def activate_phase2(
    request: ActivatePhase2Request,
    db: Session = Depends(get_db),
):
    """Activate Phase 2 (music promotion) for channels"""
    service = Phase2Service(db)
    try:
        result = service.activate_phase2(
            channel_ids=request.channel_ids,
            music_id=request.music_id,
            video_filter=request.video_filter,
            apply_retroactive=request.apply_retroactive,
            normalize=request.normalize,
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
        raise HTTPException(status_code=500, detail=f"Failed to activate Phase 2: {str(e)}")


@router.post("/deactivate")
async def deactivate_phase2(
    request: DeactivatePhase2Request,
    db: Session = Depends(get_db),
):
    """Deactivate Phase 2 for channels"""
    service = Phase2Service(db)
    try:
        result = service.deactivate_phase2(channel_ids=request.channel_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate Phase 2: {str(e)}")


@router.get("/status")
async def get_phase2_status(
    db: Session = Depends(get_db),
):
    """Get Phase 2 status across all channels"""
    service = Phase2Service(db)
    try:
        status = service.get_phase2_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Phase 2 status: {str(e)}")


@router.post("/apply-retroactive")
async def apply_retroactive(
    request: ApplyRetroactiveRequest,
    db: Session = Depends(get_db),
):
    """Apply Phase 2 retroactively to published videos"""
    service = Phase2Service(db)
    try:
        result = service.apply_retroactive(
            channel_ids=request.channel_ids,
            music_id=request.music_id,
            video_filter=request.video_filter,
            normalize=request.normalize,
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
        raise HTTPException(status_code=500, detail=f"Failed to apply retroactive: {str(e)}")


@router.post("/check-readiness")
async def check_channel_readiness(
    request: CheckReadinessRequest,
    db: Session = Depends(get_db),
):
    """Check if channel is ready for Phase 2"""
    service = Phase2Service(db)
    try:
        result = service.check_channel_readiness(
            channel_id=request.channel_id,
            min_subscribers=request.min_subscribers,
            min_views=request.min_views,
        )
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check readiness: {str(e)}")
