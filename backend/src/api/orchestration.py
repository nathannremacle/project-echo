"""
Orchestration API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.orchestration.central_orchestration_service import CentralOrchestrationService
from src.services.orchestration.scheduling_service import SchedulingService
from src.repositories.schedule_repository import ScheduleRepository
from src.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])


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
    source_url: Optional[str] = None


class BulkScheduleRequest(BaseModel):
    videoIds: List[str]
    channelIds: List[str]
    scheduledAt: str
    scheduleType: str = "simultaneous"
    delaySeconds: Optional[int] = None


class ScheduleUpdateRequest(BaseModel):
    scheduledAt: Optional[str] = None
    delaySeconds: Optional[int] = None
    status: Optional[str] = None
    isPaused: Optional[bool] = None


def _schedule_to_dict(schedule) -> dict:
    """Convert schedule ORM to camelCase dict for frontend"""
    return {
        "id": schedule.id,
        "channelId": schedule.channel_id,
        "videoId": schedule.video_id,
        "scheduleType": schedule.schedule_type,
        "scheduledAt": schedule.scheduled_at.isoformat() if schedule.scheduled_at else None,
        "delaySeconds": schedule.delay_seconds,
        "status": schedule.status,
        "coordinationGroupId": schedule.coordination_group_id,
        "waveId": schedule.wave_id,
        "isPaused": schedule.is_paused,
        "executedAt": schedule.executed_at.isoformat() if schedule.executed_at else None,
        "errorMessage": schedule.error_message,
        "createdAt": schedule.created_at.isoformat() if schedule.created_at else None,
        "updatedAt": schedule.updated_at.isoformat() if schedule.updated_at else None,
    }


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
    """Trigger pipeline for a channel (scrape → download → transform → upload).
    Works without orchestration running - runs directly in central mode."""
    service = CentralOrchestrationService(db)
    try:
        result = service.trigger_pipeline(
            channel_id=request.channel_id,
            video_id=request.video_id,
            source_url=request.source_url,
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


# --- Schedules ---

@router.get("/schedules")
async def list_schedules(
    channelId: Optional[str] = Query(None),
    videoId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    scheduleType: Optional[str] = Query(None),
    includeHistory: bool = Query(True),
    db: Session = Depends(get_db),
):
    """List publication schedules with optional filters"""
    schedule_repo = ScheduleRepository(db)
    start_dt = datetime.fromisoformat(startDate) if startDate else None
    end_dt = datetime.fromisoformat(endDate) if endDate else None
    schedules = schedule_repo.get_with_filters(
        channel_id=channelId,
        video_id=videoId,
        status=status,
        schedule_type=scheduleType,
        start_date=start_dt,
        end_date=end_dt,
        include_history=includeHistory,
    )
    return [_schedule_to_dict(s) for s in schedules]


@router.get("/schedules/{schedule_id}")
async def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
):
    """Get schedule by ID"""
    schedule_repo = ScheduleRepository(db)
    schedule = schedule_repo.get_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule {schedule_id} not found")
    return _schedule_to_dict(schedule)


@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    updates: ScheduleUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update schedule"""
    schedule_repo = ScheduleRepository(db)
    schedule = schedule_repo.get_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule {schedule_id} not found")
    if updates.scheduledAt:
        schedule.scheduled_at = datetime.fromisoformat(updates.scheduledAt)
    if updates.delaySeconds is not None:
        schedule.delay_seconds = updates.delaySeconds
    if updates.status:
        schedule.status = updates.status
    if updates.isPaused is not None:
        schedule.is_paused = updates.isPaused
    schedule = schedule_repo.update(schedule)
    return _schedule_to_dict(schedule)


@router.post("/schedules/{schedule_id}/cancel")
async def cancel_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
):
    """Cancel schedule"""
    service = SchedulingService(db)
    try:
        schedule = service.cancel_schedule(schedule_id)
        return {"message": "Schedule cancelled successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/schedules/bulk")
async def bulk_schedule(
    request: BulkScheduleRequest,
    db: Session = Depends(get_db),
):
    """Create bulk publication schedules"""
    service = SchedulingService(db)
    scheduled_at = datetime.fromisoformat(request.scheduledAt)
    all_schedules = []
    try:
        for video_id in request.videoIds:
            if request.scheduleType == "simultaneous":
                schedules = service.create_simultaneous_schedule(
                    video_id=video_id,
                    channel_ids=request.channelIds,
                    scheduled_at=scheduled_at,
                )
            elif request.scheduleType == "staggered":
                delay = request.delaySeconds or 3600
                schedules = service.create_staggered_schedule(
                    video_id=video_id,
                    channel_ids=request.channelIds,
                    start_time=scheduled_at,
                    delay_seconds=delay,
                )
            else:
                for channel_id in request.channelIds:
                    schedule = service.create_independent_schedule(
                        channel_id=channel_id,
                        scheduled_at=scheduled_at,
                        video_id=video_id,
                    )
                    all_schedules.append(schedule)
                continue
            all_schedules.extend(schedules)
        return [_schedule_to_dict(s) for s in all_schedules]
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
