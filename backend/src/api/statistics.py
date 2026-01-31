"""
Statistics API endpoints
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.video import Video
from src.repositories.channel_repository import ChannelRepository
from src.repositories.statistics_repository import StatisticsRepository

router = APIRouter(prefix="/statistics", tags=["Statistics"])


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


def _video_stats_to_dict(stats) -> dict:
    """Convert video statistics to camelCase dict"""
    return {
        "id": stats.id,
        "videoId": stats.video_id,
        "views": stats.view_count or 0,
        "likes": stats.like_count or 0,
        "comments": stats.comment_count or 0,
        "shares": 0,
        "watchTime": None,
        "averageViewDuration": None,
        "recordedAt": stats.timestamp.isoformat() if stats.timestamp else None,
    }


@router.get("/overview")
async def get_statistics_overview(db: Session = Depends(get_db)):
    """Get overview statistics"""
    channel_repo = ChannelRepository(db)
    stats_repo = StatisticsRepository(db)

    channels = channel_repo.get_all()
    active_channels = [c for c in channels if c.is_active]
    total_videos = db.query(Video).count()

    total_views = 0
    total_subscribers = 0
    for channel in channels:
        latest = stats_repo.get_latest_channel_statistics(channel.id)
        if latest:
            total_views += latest.total_views or 0
            total_subscribers += latest.subscriber_count or 0

    return {
        "totalChannels": len(channels),
        "activeChannels": len(active_channels),
        "totalVideos": total_videos,
        "totalViews": total_views,
        "totalSubscribers": total_subscribers,
        "recentActivity": {
            "videosPublished": 0,
            "viewsGained": 0,
            "subscribersGained": 0,
            "period": "7d",
        },
    }
