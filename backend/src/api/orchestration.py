"""
Orchestration API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.orchestration.central_orchestration_service import CentralOrchestrationService

router = APIRouter(prefix="/api/orchestration", tags=["Orchestration"])


class CoordinatePublicationRequest(BaseModel):
    video_id: str
    channel_ids: List[str]
    timing: str = "simultaneous"  # simultaneous, staggered, independent
    scheduled_at: Optional[str] = None  # ISO format datetime


class ScheduleWaveRequest(BaseModel):
    video_ids: List[str]
    channel_ids: List[str]
    wave_config: Dict[str, Any]


class TriggerPipelineRequest(BaseModel):
    channel_id: str
    video_id: Optional[str] = None


@router.post("/start")
async def start_orchestration(db: Session = Depends(get_db)):
    """Start the orchestration system"""
    service = CentralOrchestrationService(db)
    try:
        result = service.start()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stop")
async def stop_orchestration(db: Session = Depends(get_db)):
    """Stop the orchestration system"""
    service = CentralOrchestrationService(db)
    try:
        result = service.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pause")
async def pause_orchestration(db: Session = Depends(get_db)):
    """Pause the orchestration system"""
    service = CentralOrchestrationService(db)
    try:
        result = service.pause()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resume")
async def resume_orchestration(db: Session = Depends(get_db)):
    """Resume the orchestration system"""
    service = CentralOrchestrationService(db)
    try:
        result = service.resume()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def get_orchestration_status(db: Session = Depends(get_db)):
    """Get orchestration system status"""
    service = CentralOrchestrationService(db)
    return service.get_status()


@router.post("/coordinate-publication")
async def coordinate_publication(
    request: CoordinatePublicationRequest,
    db: Session = Depends(get_db),
):
    """Coordinate publication across multiple channels"""
    service = CentralOrchestrationService(db)
    
    scheduled_at = None
    if request.scheduled_at:
        scheduled_at = datetime.fromisoformat(request.scheduled_at)
    
    try:
        result = service.coordinate_publication(
            video_id=request.video_id,
            channel_ids=request.channel_ids,
            timing=request.timing,
            scheduled_at=scheduled_at,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trigger-pipeline")
async def trigger_pipeline(
    request: TriggerPipelineRequest,
    db: Session = Depends(get_db),
):
    """Trigger pipeline for a channel"""
    service = CentralOrchestrationService(db)
    try:
        result = service.trigger_pipeline(
            channel_id=request.channel_id,
            video_id=request.video_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/schedule-wave")
async def schedule_wave(
    request: ScheduleWaveRequest,
    db: Session = Depends(get_db),
):
    """Schedule viral wave publication"""
    service = CentralOrchestrationService(db)
    try:
        result = service.schedule_wave_publication(
            video_ids=request.video_ids,
            channel_ids=request.channel_ids,
            wave_config=request.wave_config,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/monitor-channels")
async def monitor_channels(db: Session = Depends(get_db)):
    """Monitor health and status of all channels"""
    service = CentralOrchestrationService(db)
    return service.monitor_channels()


@router.post("/distribute-videos")
async def distribute_videos(db: Session = Depends(get_db)):
    """Automatically assign videos to channels"""
    service = CentralOrchestrationService(db)
    try:
        result = service.distribute_videos()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get status dashboard data"""
    service = CentralOrchestrationService(db)
    return service.get_dashboard_data()


@router.post("/sync-configs")
async def sync_channel_configs(db: Session = Depends(get_db)):
    """Sync configurations across channel repositories"""
    service = CentralOrchestrationService(db)
    try:
        result = service.sync_channel_configs()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
