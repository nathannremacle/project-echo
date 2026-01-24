"""
Unit tests for Enhanced Analytics service
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.enhanced_analytics.enhanced_analytics_service import EnhancedAnalyticsService
from src.models.video import Video
from src.models.channel import Channel
from src.models.statistics import VideoStatistics


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_video_repo():
    """Mock video repository"""
    repo = Mock()
    return repo


@pytest.fixture
def mock_channel_repo():
    """Mock channel repository"""
    repo = Mock()
    return repo


@pytest.fixture
def enhanced_analytics_service(mock_db, mock_video_repo, mock_channel_repo):
    """Create Enhanced Analytics service with mocked dependencies"""
    with patch("src.services.enhanced_analytics.enhanced_analytics_service.VideoRepository", return_value=mock_video_repo), \
         patch("src.services.enhanced_analytics.enhanced_analytics_service.ChannelRepository", return_value=mock_channel_repo):
        service = EnhancedAnalyticsService(mock_db)
        service.video_repo = mock_video_repo
        service.channel_repo = mock_channel_repo
        return service


def test_get_music_promotion_metrics(enhanced_analytics_service, mock_db):
    """Test getting music promotion metrics"""
    videos = [
        Video(id="1", music_replaced=True, music_track_id="music-1", published_at=datetime.utcnow()),
        Video(id="2", music_replaced=True, music_track_id="music-1", published_at=datetime.utcnow()),
    ]
    
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = videos
    
    mock_db.query.return_value = mock_query
    
    # Mock video statistics
    stats = VideoStatistics(video_id="1", view_count=1000)
    mock_stats_query = Mock()
    mock_stats_query.filter.return_value = mock_stats_query
    mock_stats_query.order_by.return_value = mock_stats_query
    mock_stats_query.first.return_value = stats
    
    mock_db.query.side_effect = [mock_query, mock_stats_query, mock_stats_query]
    
    metrics = enhanced_analytics_service.get_music_promotion_metrics()
    
    assert metrics["total_music_videos"] == 2
    assert metrics["unique_music_tracks"] == 1


def test_get_wave_effect_metrics(enhanced_analytics_service, mock_db):
    """Test getting wave effect metrics"""
    now = datetime.utcnow()
    videos = [
        Video(id="1", publication_status="published", published_at=now),
        Video(id="2", publication_status="published", published_at=now + timedelta(hours=1)),
        Video(id="3", publication_status="published", published_at=now + timedelta(days=2)),
    ]
    
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = videos
    
    mock_db.query.return_value = mock_query
    
    metrics = enhanced_analytics_service.get_wave_effect_metrics()
    
    assert metrics["total_waves"] > 0


def test_get_phase2_comparison(enhanced_analytics_service, mock_video_repo, mock_channel_repo, mock_db):
    """Test getting Phase 2 comparison"""
    channel = Channel(id="1", phase2_enabled=True, updated_at=datetime(2026, 1, 15))
    mock_channel_repo.get_all.return_value = [channel]
    
    videos = [
        Video(id="1", channel_id="1", published_at=datetime(2026, 1, 10)),
        Video(id="2", channel_id="1", published_at=datetime(2026, 1, 20)),
    ]
    mock_video_repo.get_by_channel_id.return_value = videos
    
    # Mock video statistics
    mock_stats_query = Mock()
    mock_stats_query.filter.return_value = mock_stats_query
    mock_stats_query.order_by.return_value = mock_stats_query
    mock_stats_query.first.return_value = None
    
    mock_db.query.return_value = mock_stats_query
    
    comparison = enhanced_analytics_service.get_phase2_comparison()
    
    assert "pre_phase2" in comparison
    assert "post_phase2" in comparison
    assert "improvement" in comparison


def test_get_roi_metrics(enhanced_analytics_service, mock_db):
    """Test getting ROI metrics"""
    # Mock music promotion metrics
    with patch.object(enhanced_analytics_service, 'get_music_promotion_metrics', return_value={
        "total_music_videos": 10,
        "total_views": 20000,
        "average_views_per_video": 2000,
    }):
        roi = enhanced_analytics_service.get_roi_metrics()
        
        assert roi["effort"] == 10
        assert roi["results"] == 20000
        assert roi["roi"] == 2000


def test_get_insights(enhanced_analytics_service):
    """Test getting insights"""
    with patch.object(enhanced_analytics_service, 'get_music_promotion_metrics', return_value={
        "average_views_per_video": 2000,
    }), \
    patch.object(enhanced_analytics_service, 'get_wave_effect_metrics', return_value={
        "largest_wave": {"videos_count": 10, "channels_count": 3},
    }), \
    patch.object(enhanced_analytics_service, 'get_phase2_comparison', return_value={
        "improvement": {"views_per_video": 25},
    }):
        insights = enhanced_analytics_service.get_insights()
        
        assert len(insights) > 0


def test_get_recommendations(enhanced_analytics_service, mock_channel_repo):
    """Test getting recommendations"""
    channels = [
        Channel(id="1", phase2_enabled=False, is_active=True),
        Channel(id="2", phase2_enabled=True, is_active=True),
    ]
    mock_channel_repo.get_all.return_value = channels
    
    with patch.object(enhanced_analytics_service, 'get_music_promotion_metrics', return_value={
        "total_music_videos": 5,
    }):
        recommendations = enhanced_analytics_service.get_recommendations()
        
        assert len(recommendations) > 0
