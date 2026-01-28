"""
Enhanced analytics API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.enhanced_analytics.enhanced_analytics_service import EnhancedAnalyticsService

router = APIRouter(prefix="/analytics", tags=["Enhanced Analytics"])


@router.get("/music-promotion")
async def get_music_promotion_metrics(
    channel_ids: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get music promotion metrics"""
    service = EnhancedAnalyticsService(db)
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        metrics = service.get_music_promotion_metrics(
            channel_ids=channel_ids,
            start_date=start,
            end_date=end,
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get music promotion metrics: {str(e)}")


@router.get("/wave-effect")
async def get_wave_effect_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    time_window_hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Get wave effect metrics"""
    service = EnhancedAnalyticsService(db)
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        metrics = service.get_wave_effect_metrics(
            start_date=start,
            end_date=end,
            time_window_hours=time_window_hours,
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wave effect metrics: {str(e)}")


@router.get("/phase2-comparison")
async def get_phase2_comparison(
    channel_ids: Optional[List[str]] = Query(None),
    phase2_start_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get pre/post Phase 2 comparison"""
    service = EnhancedAnalyticsService(db)
    try:
        phase2_start = datetime.fromisoformat(phase2_start_date) if phase2_start_date else None
        comparison = service.get_phase2_comparison(
            channel_ids=channel_ids,
            phase2_start_date=phase2_start,
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Phase 2 comparison: {str(e)}")


@router.get("/roi")
async def get_roi_metrics(
    channel_ids: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get ROI metrics for music promotion"""
    service = EnhancedAnalyticsService(db)
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        metrics = service.get_roi_metrics(
            channel_ids=channel_ids,
            start_date=start,
            end_date=end,
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ROI metrics: {str(e)}")


@router.get("/insights")
async def get_insights(
    channel_ids: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get key insights from analytics"""
    service = EnhancedAnalyticsService(db)
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        insights = service.get_insights(
            channel_ids=channel_ids,
            start_date=start,
            end_date=end,
        )
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.get("/recommendations")
async def get_recommendations(
    channel_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
):
    """Get recommendations based on analytics"""
    service = EnhancedAnalyticsService(db)
    try:
        recommendations = service.get_recommendations(channel_ids=channel_ids)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/export")
async def export_analytics(
    channel_ids: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Export analytics data"""
    service = EnhancedAnalyticsService(db)
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "music_promotion": service.get_music_promotion_metrics(
                channel_ids=channel_ids,
                start_date=start,
                end_date=end,
            ),
            "wave_effect": service.get_wave_effect_metrics(
                start_date=start,
                end_date=end,
            ),
            "phase2_comparison": service.get_phase2_comparison(channel_ids=channel_ids),
            "roi": service.get_roi_metrics(
                channel_ids=channel_ids,
                start_date=start,
                end_date=end,
            ),
            "insights": service.get_insights(
                channel_ids=channel_ids,
                start_date=start,
                end_date=end,
            ),
            "recommendations": service.get_recommendations(channel_ids=channel_ids),
        }
        
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}")
