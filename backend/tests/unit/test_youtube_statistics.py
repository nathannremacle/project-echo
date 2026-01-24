"""
Unit tests for YouTube statistics service
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.services.youtube.statistics_service import YouTubeStatisticsService
from src.models.video import Video
from src.models.channel import Channel
from src.utils.exceptions import NotFoundError, ProcessingError


@pytest.fixture
def db_session():
    """Create test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database import Base
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def test_channel(db_session):
    """Create test channel"""
    import json
    
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        is_active=True,
        api_credentials_encrypted="encrypted_creds",
        posting_schedule=json.dumps({}),
        content_filters=json.dumps({}),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@pytest.fixture
def test_video(db_session, test_channel):
    """Create test video"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        publication_status="published",
        youtube_video_id="youtube_video_id_123",
        youtube_video_url="https://www.youtube.com/watch?v=youtube_video_id_123",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


@patch("src.services.youtube.statistics_service.YouTubeClient")
def test_retrieve_channel_statistics_success(
    db_session, test_channel, mock_youtube_client
):
    """Test successful channel statistics retrieval"""
    # Mock YouTube client
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [{
            "statistics": {
                "subscriberCount": "1000",
                "viewCount": "50000",
                "videoCount": "25",
            },
            "snippet": {
                "title": "Test Channel",
            },
        }]
    }
    mock_youtube.channels.return_value.list.return_value = mock_list
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    service = YouTubeStatisticsService(db_session)
    
    stats = service.retrieve_channel_statistics(test_channel.id)
    
    assert stats is not None
    assert stats.subscriber_count == 1000
    assert stats.view_count == 50000
    assert stats.video_count == 25
    assert stats.channel_id == test_channel.id


@patch("src.services.youtube.statistics_service.YouTubeClient")
def test_retrieve_video_statistics_success(
    db_session, test_video, test_channel, mock_youtube_client
):
    """Test successful video statistics retrieval"""
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [{
            "statistics": {
                "viewCount": "10000",
                "likeCount": "500",
                "commentCount": "100",
            },
        }]
    }
    mock_youtube.videos.return_value.list.return_value = mock_list
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    service = YouTubeStatisticsService(db_session)
    
    stats = service.retrieve_video_statistics(test_video.id)
    
    assert stats is not None
    assert stats.view_count == 10000
    assert stats.like_count == 500
    assert stats.comment_count == 100
    assert stats.video_id == test_video.id


def test_retrieve_channel_statistics_not_found(db_session):
    """Test retrieving statistics for non-existent channel"""
    service = YouTubeStatisticsService(db_session)
    
    with pytest.raises(NotFoundError):
        service.retrieve_channel_statistics("non-existent-id")


def test_retrieve_video_statistics_not_published(db_session, test_channel):
    """Test retrieving statistics for video not published"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        publication_status="pending",  # Not published
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    
    service = YouTubeStatisticsService(db_session)
    
    with pytest.raises(ProcessingError) as exc_info:
        service.retrieve_video_statistics(video.id)
    
    assert "not been published" in str(exc_info.value).lower()


@patch("src.services.youtube.statistics_service.YouTubeClient")
def test_retrieve_all_video_statistics(
    db_session, test_video, test_channel, mock_youtube_client
):
    """Test retrieving statistics for all videos in channel"""
    # Create second published video
    video2 = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test456",
        source_title="Test Video 2",
        source_platform="youtube",
        publication_status="published",
        youtube_video_id="youtube_video_id_456",
    )
    db_session.add(video2)
    db_session.commit()
    
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [{
            "statistics": {
                "viewCount": "5000",
                "likeCount": "250",
                "commentCount": "50",
            },
        }]
    }
    mock_youtube.videos.return_value.list.return_value = mock_list
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    service = YouTubeStatisticsService(db_session)
    
    result = service.retrieve_all_video_statistics(test_channel.id)
    
    assert result["total"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0


def test_get_latest_channel_statistics(db_session, test_channel):
    """Test getting latest channel statistics"""
    from src.models.statistics import ChannelStatistics
    
    # Create statistics records
    stats1 = ChannelStatistics(
        channel_id=test_channel.id,
        subscriber_count=1000,
        view_count=50000,
        video_count=25,
        timestamp=datetime.utcnow() - timedelta(days=2),
    )
    stats2 = ChannelStatistics(
        channel_id=test_channel.id,
        subscriber_count=1100,
        view_count=55000,
        video_count=26,
        timestamp=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(stats1)
    db_session.add(stats2)
    db_session.commit()
    
    service = YouTubeStatisticsService(db_session)
    
    latest = service.get_latest_channel_statistics(test_channel.id)
    
    assert latest is not None
    assert latest.subscriber_count == 1100  # Latest should be stats2


def test_get_channel_statistics_by_date_range(db_session, test_channel):
    """Test getting channel statistics by date range"""
    from src.models.statistics import ChannelStatistics
    
    start_date = datetime.utcnow() - timedelta(days=7)
    end_date = datetime.utcnow()
    
    # Create statistics records
    stats1 = ChannelStatistics(
        channel_id=test_channel.id,
        subscriber_count=1000,
        view_count=50000,
        video_count=25,
        timestamp=datetime.utcnow() - timedelta(days=5),  # Within range
    )
    stats2 = ChannelStatistics(
        channel_id=test_channel.id,
        subscriber_count=1100,
        view_count=55000,
        video_count=26,
        timestamp=datetime.utcnow() - timedelta(days=10),  # Outside range
    )
    db_session.add(stats1)
    db_session.add(stats2)
    db_session.commit()
    
    service = YouTubeStatisticsService(db_session)
    
    stats = service.get_channel_statistics_by_date_range(
        test_channel.id,
        start_date,
        end_date,
    )
    
    assert len(stats) == 1
    assert stats[0].subscriber_count == 1000
