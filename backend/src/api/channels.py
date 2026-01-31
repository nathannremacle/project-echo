"""
Channels API endpoints
"""

import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.orchestration.channel_configuration_service import ChannelConfigurationService
from src.services.youtube.statistics_service import YouTubeStatisticsService
from src.repositories.statistics_repository import StatisticsRepository
from src.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/channels", tags=["Channels"])


class PostingSchedule(BaseModel):
    frequency: Optional[str] = None
    preferredTimes: Optional[list] = None
    timezone: Optional[str] = None
    daysOfWeek: Optional[list] = None


class ContentFilters(BaseModel):
    minResolution: Optional[str] = None
    minViews: Optional[int] = None
    excludeWatermarked: Optional[bool] = None
    preferredSources: Optional[list] = None


class MetadataTemplate(BaseModel):
    titleTemplate: Optional[str] = None
    descriptionTemplate: Optional[str] = None
    defaultTags: Optional[list] = None


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    postingSchedule: Optional[PostingSchedule] = None
    effectPresetId: Optional[str] = None
    contentFilters: Optional[ContentFilters] = None
    metadataTemplate: Optional[MetadataTemplate] = None


class ChannelCreate(BaseModel):
    """Minimal payload for creating a channel (test/demo). Uses placeholder credentials."""
    name: str
    youtubeChannelId: str
    youtubeChannelUrl: Optional[str] = None  # Auto-built from ID if omitted
    isActive: bool = True


class OAuthCredentials(BaseModel):
    """YouTube OAuth 2.0 credentials for channel publication."""
    clientId: str
    clientSecret: str
    refreshToken: str


def _channel_to_dict(channel) -> dict:
    """Convert channel ORM to camelCase dict for frontend"""
    posting = {}
    try:
        posting = json.loads(channel.posting_schedule) if channel.posting_schedule else {}
    except json.JSONDecodeError:
        pass
    content = {}
    try:
        content = json.loads(channel.content_filters) if channel.content_filters else {}
    except json.JSONDecodeError:
        pass
    metadata = {}
    try:
        metadata = json.loads(channel.metadata_template) if channel.metadata_template else {}
    except json.JSONDecodeError:
        pass

    return {
        "id": channel.id,
        "name": channel.name,
        "youtubeChannelId": channel.youtube_channel_id,
        "youtubeChannelUrl": channel.youtube_channel_url,
        "isActive": channel.is_active,
        "postingSchedule": {
            "frequency": posting.get("frequency", "daily"),
            "preferredTimes": posting.get("preferred_times", []),
            "timezone": posting.get("timezone", "UTC"),
            "daysOfWeek": posting.get("days_of_week", []),
        },
        "effectPresetId": channel.effect_preset_id,
        "contentFilters": {
            "minResolution": content.get("min_resolution", "720p"),
            "minViews": content.get("min_views", 0),
            "excludeWatermarked": content.get("exclude_watermarked", True),
            "preferredSources": content.get("preferred_sources", []),
        },
        "metadataTemplate": {
            "titleTemplate": metadata.get("title", "{channel_name} - {source_title}"),
            "descriptionTemplate": metadata.get("description", ""),
            "defaultTags": metadata.get("tags", []),
        },
        "githubRepoUrl": channel.github_repo_url,
        "createdAt": channel.created_at.isoformat() if channel.created_at else None,
        "updatedAt": channel.updated_at.isoformat() if channel.updated_at else None,
        "lastPublicationAt": channel.last_publication_at.isoformat() if channel.last_publication_at else None,
        "phase2Enabled": channel.phase2_enabled,
    }


@router.get("")
async def list_channels(
    active_only: bool = Query(False, description="Filter to active channels only"),
    db: Session = Depends(get_db),
):
    """List all channels"""
    from src.repositories.channel_repository import ChannelRepository
    channel_repo = ChannelRepository(db)
    channels = channel_repo.get_all(active_only=active_only)
    return {"channels": [_channel_to_dict(c) for c in channels]}


@router.post("")
async def create_channel(
    payload: ChannelCreate,
    db: Session = Depends(get_db),
):
    """Create a new channel (test/demo mode with placeholder credentials)"""
    service = ChannelConfigurationService(db)
    youtube_url = payload.youtubeChannelUrl or f"https://www.youtube.com/channel/{payload.youtubeChannelId}"
    api_credentials = {
        "type": "placeholder",
        "test": True,
        "client_id": "placeholder",
        "client_secret": "placeholder",
    }
    try:
        channel = service.create_channel(
            name=payload.name,
            youtube_channel_id=payload.youtubeChannelId,
            youtube_channel_url=youtube_url,
            api_credentials=api_credentials,
            is_active=payload.isActive,
        )
        return _channel_to_dict(channel)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _channel_stats_to_dict(stats) -> dict:
    """Convert channel statistics to camelCase dict"""
    return {
        "id": stats.id,
        "channelId": stats.channel_id,
        "subscriberCount": stats.subscriber_count or 0,
        "viewCount": stats.view_count or 0,
        "videoCount": stats.video_count or 0,
        "totalViews": stats.total_views or 0,
        "totalVideos": stats.total_videos or 0,
        "timestamp": stats.timestamp.isoformat() if stats.timestamp else None,
    }


@router.get("/{channel_id}")
async def get_channel(
    channel_id: str,
    db: Session = Depends(get_db),
):
    """Get channel by ID"""
    service = ChannelConfigurationService(db)
    try:
        config = service.export_channel_configuration(channel_id)
        channel = service.channel_repo.get_by_id(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
        return _channel_to_dict(channel)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{channel_id}")
async def update_channel(
    channel_id: str,
    updates: ChannelUpdate,
    db: Session = Depends(get_db),
):
    """Update channel configuration"""
    service = ChannelConfigurationService(db)
    try:
        posting = None
        if updates.postingSchedule:
            posting = {
                "frequency": updates.postingSchedule.frequency,
                "preferred_times": updates.postingSchedule.preferredTimes,
                "timezone": updates.postingSchedule.timezone,
                "days_of_week": updates.postingSchedule.daysOfWeek,
            }
        content = None
        if updates.contentFilters:
            content = {
                "min_resolution": updates.contentFilters.minResolution,
                "min_views": updates.contentFilters.minViews,
                "exclude_watermarked": updates.contentFilters.excludeWatermarked,
                "preferred_sources": updates.contentFilters.preferredSources,
            }
        metadata = None
        if updates.metadataTemplate:
            metadata = {
                "title": updates.metadataTemplate.titleTemplate,
                "description": updates.metadataTemplate.descriptionTemplate,
                "tags": updates.metadataTemplate.defaultTags,
            }
        channel = service.update_channel_configuration(
            channel_id=channel_id,
            posting_schedule=posting,
            content_filters=content,
            metadata_template=metadata,
            effect_preset_id=updates.effectPresetId,
        )
        return _channel_to_dict(channel)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{channel_id}/statistics")
async def get_channel_statistics(
    channel_id: str,
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get channel statistics with history and trends"""
    from src.repositories.channel_repository import ChannelRepository

    channel_repo = ChannelRepository(db)
    stats_repo = StatisticsRepository(db)

    channel = channel_repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")

    start_dt = datetime.fromisoformat(startDate) if startDate else None
    end_dt = datetime.fromisoformat(endDate) if endDate else None

    if start_dt and end_dt:
        history = stats_repo.get_channel_statistics_by_date_range(channel_id, start_dt, end_dt)
    else:
        history = stats_repo.get_channel_statistics(channel_id, limit=30)

    history_list = [_channel_stats_to_dict(h) for h in history]
    current = history_list[0] if history_list else {
        "subscriberCount": 0,
        "viewCount": 0,
        "videoCount": 0,
        "totalViews": 0,
        "totalVideos": 0,
    }
    prev = history_list[1] if len(history_list) > 1 else None
    subscriber_growth = 0
    view_growth = 0
    if prev:
        curr_subs = current.get("subscriberCount", 0)
        prev_subs = prev.get("subscriberCount", 0)
        curr_views = current.get("viewCount", 0)
        prev_views = prev.get("viewCount", 0)
        subscriber_growth = (curr_subs - prev_subs) / prev_subs * 100 if prev_subs else 0
        view_growth = (curr_views - prev_views) / prev_views * 100 if prev_views else 0

    return {
        "current": current,
        "history": history_list,
        "trends": {
            "subscriberGrowth": round(subscriber_growth, 2),
            "viewGrowth": round(view_growth, 2),
        },
    }


@router.put("/{channel_id}/credentials")
async def update_channel_credentials(
    channel_id: str,
    credentials: OAuthCredentials,
    db: Session = Depends(get_db),
):
    """Update YouTube OAuth credentials for channel publication"""
    service = ChannelConfigurationService(db)
    api_credentials = {
        "client_id": credentials.clientId,
        "client_secret": credentials.clientSecret,
        "refresh_token": credentials.refreshToken,
    }
    try:
        channel = service.update_api_credentials(
            channel_id=channel_id,
            api_credentials=api_credentials,
        )
        return _channel_to_dict(channel)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        if "ENCRYPTION_KEY" in str(e):
            raise HTTPException(
                status_code=500,
                detail="ENCRYPTION_KEY not configured. Set it in environment variables.",
            )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{channel_id}/activate")
async def activate_channel(
    channel_id: str,
    db: Session = Depends(get_db),
):
    """Activate channel"""
    service = ChannelConfigurationService(db)
    try:
        channel = service.update_channel_configuration(channel_id=channel_id, is_active=True)
        return _channel_to_dict(channel)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{channel_id}/deactivate")
async def deactivate_channel(
    channel_id: str,
    db: Session = Depends(get_db),
):
    """Deactivate channel"""
    service = ChannelConfigurationService(db)
    try:
        channel = service.update_channel_configuration(channel_id=channel_id, is_active=False)
        return _channel_to_dict(channel)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{channel_id}/enable-phase2")
async def enable_phase2(
    channel_id: str,
    db: Session = Depends(get_db),
):
    """Enable Phase 2 (music promotion) for channel"""
    from src.repositories.channel_repository import ChannelRepository
    channel_repo = ChannelRepository(db)
    channel = channel_repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
    channel.phase2_enabled = True
    channel = channel_repo.update(channel)
    return _channel_to_dict(channel)
