"""
Creator attribution API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.creator_attribution.creator_attribution_service import CreatorAttributionService
from src.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/creators", tags=["Creator Attribution"])


class AttributeVideoRequest(BaseModel):
    creator_name: str
    creator_channel: Optional[str] = None


class BulkAttributeRequest(BaseModel):
    video_ids: List[str]
    creator_name: str
    creator_channel: Optional[str] = None


@router.get("")
async def list_creators(
    db: Session = Depends(get_db),
):
    """Get list of all creators with video counts"""
    service = CreatorAttributionService(db)
    try:
        creators = service.get_all_creators()
        return {
            "creators": creators,
            "total": len(creators),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list creators: {str(e)}")


@router.get("/search")
async def search_creators(
    q: str = Query(..., description="Search query"),
    limit: Optional[int] = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search creators by name"""
    service = CreatorAttributionService(db)
    try:
        creators = service.search_creators(query=q, limit=limit)
        return {
            "creators": creators,
            "total": len(creators),
            "query": q,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search creators: {str(e)}")


@router.get("/{creator_name}/videos")
async def get_videos_by_creator(
    creator_name: str,
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get videos by creator name"""
    service = CreatorAttributionService(db)
    try:
        result = service.get_videos_by_creator(
            creator_name=creator_name,
            limit=limit,
            offset=offset,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get videos: {str(e)}")


@router.post("/videos/{video_id}/attribute")
async def attribute_video(
    video_id: str,
    request: AttributeVideoRequest,
    db: Session = Depends(get_db),
):
    """Add or update creator attribution for a video"""
    service = CreatorAttributionService(db)
    try:
        video = service.attribute_video(
            video_id=video_id,
            creator_name=request.creator_name,
            creator_channel=request.creator_channel,
        )
        return {
            "video_id": video.id,
            "creator_name": video.source_creator,
            "message": "Attribution updated successfully",
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to attribute video: {str(e)}")


@router.post("/videos/bulk-attribute")
async def bulk_attribute_videos(
    request: BulkAttributeRequest,
    db: Session = Depends(get_db),
):
    """Bulk update creator attribution for multiple videos"""
    service = CreatorAttributionService(db)
    try:
        result = service.bulk_attribute_videos(
            video_ids=request.video_ids,
            creator_name=request.creator_name,
            creator_channel=request.creator_channel,
        )
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk attribute videos: {str(e)}")


@router.get("/export")
async def export_creators(
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    """Export list of all creators and their videos"""
    service = CreatorAttributionService(db)
    try:
        from datetime import datetime
        export_data = service.export_creator_list(format=format)
        export_data["exported_at"] = datetime.utcnow().isoformat()
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export creators: {str(e)}")


@router.get("/videos/{video_id}/attribution-template")
async def get_attribution_template(
    video_id: str,
    db: Session = Depends(get_db),
):
    """Get creator attribution string for use in description templates"""
    service = CreatorAttributionService(db)
    try:
        attribution = service.get_attribution_template_variable(video_id=video_id)
        return {
            "video_id": video_id,
            "attribution": attribution,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attribution template: {str(e)}")
