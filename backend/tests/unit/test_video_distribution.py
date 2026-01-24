"""
Unit tests for video distribution service
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from src.services.orchestration.video_distribution_service import VideoDistributionService
from src.models.channel import Channel
from src.models.video import Video
from src.models.distribution import VideoDistribution
from src.utils.exceptions import NotFoundError, ValidationError


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
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        is_active=True,
        api_credentials_encrypted="encrypted_creds",
        posting_schedule=json.dumps({"frequency": "daily", "preferred_times": ["12:00"]}),
        content_filters=json.dumps({"min_resolution": "720p", "exclude_watermarked": True}),
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
        source_url="https://youtube.com/watch?v=test",
        source_title="Test Video",
        source_platform="youtube",
        download_status="downloaded",
        transformation_status="transformed",
        download_resolution="1080p",
        download_duration=120,
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


@patch("src.services.orchestration.video_distribution_service.apply_filters")
def test_auto_distribute_by_filters(db_session, test_channel, test_video, mock_apply_filters):
    """Test auto distribution by content filters"""
    mock_apply_filters.return_value = True
    
    service = VideoDistributionService(db_session)
    
    distributions = service.auto_distribute_by_filters(video_id=test_video.id)
    
    assert len(distributions) == 1
    assert distributions[0].video_id == test_video.id
    assert distributions[0].channel_id == test_channel.id
    assert distributions[0].distribution_method == "auto_filter"
    assert distributions[0].status == "assigned"


@patch("src.services.orchestration.video_distribution_service.apply_filters")
def test_auto_distribute_by_filters_no_match(db_session, test_channel, test_video, mock_apply_filters):
    """Test auto distribution when filters don't match"""
    mock_apply_filters.return_value = False
    
    service = VideoDistributionService(db_session)
    
    distributions = service.auto_distribute_by_filters(video_id=test_video.id)
    
    assert len(distributions) == 0


def test_auto_distribute_by_filters_duplicate(db_session, test_channel, test_video):
    """Test auto distribution skips duplicates"""
    from src.repositories.distribution_repository import DistributionRepository
    
    # Create existing distribution
    existing_dist = VideoDistribution(
        video_id=test_video.id,
        channel_id=test_channel.id,
        distribution_method="manual",
        status="published",
    )
    db_session.add(existing_dist)
    db_session.commit()
    
    service = VideoDistributionService(db_session)
    
    with patch.object(service, "_match_channels_by_filters", return_value={test_channel: {}}):
        distributions = service.auto_distribute_by_filters(video_id=test_video.id)
        
        # Should skip duplicate
        assert len(distributions) == 0


def test_manual_distribute(db_session, test_channel, test_video):
    """Test manual distribution"""
    service = VideoDistributionService(db_session)
    
    distributions = service.manual_distribute(
        video_id=test_video.id,
        channel_ids=[test_channel.id],
    )
    
    assert len(distributions) == 1
    assert distributions[0].video_id == test_video.id
    assert distributions[0].channel_id == test_channel.id
    assert distributions[0].distribution_method == "manual"


def test_manual_distribute_duplicate(db_session, test_channel, test_video):
    """Test manual distribution with duplicate"""
    from src.repositories.distribution_repository import DistributionRepository
    
    # Create existing distribution
    existing_dist = VideoDistribution(
        video_id=test_video.id,
        channel_id=test_channel.id,
        distribution_method="manual",
        status="published",
    )
    db_session.add(existing_dist)
    db_session.commit()
    
    service = VideoDistributionService(db_session)
    
    # Should raise error without force
    with pytest.raises(ValidationError) as exc_info:
        service.manual_distribute(
            video_id=test_video.id,
            channel_ids=[test_channel.id],
        )
    
    assert "already distributed" in str(exc_info.value).lower()
    
    # Should succeed with force
    distributions = service.manual_distribute(
        video_id=test_video.id,
        channel_ids=[test_channel.id],
        force=True,
    )
    
    assert len(distributions) == 1


def test_get_distribution_statistics(db_session, test_channel, test_video):
    """Test getting distribution statistics"""
    # Create distributions
    dist1 = VideoDistribution(
        video_id=test_video.id,
        channel_id=test_channel.id,
        distribution_method="auto_filter",
        status="published",
    )
    dist2 = VideoDistribution(
        video_id=test_video.id,
        channel_id=test_channel.id,
        distribution_method="manual",
        status="assigned",
    )
    db_session.add_all([dist1, dist2])
    db_session.commit()
    
    service = VideoDistributionService(db_session)
    
    stats = service.get_distribution_statistics()
    
    assert stats["total"] == 2
    assert stats["published_count"] == 1
    assert "auto_filter" in stats["by_method"]
    assert "manual" in stats["by_method"]


def test_retry_failed_distribution(db_session, test_channel, test_video):
    """Test retrying failed distribution"""
    failed_dist = VideoDistribution(
        video_id=test_video.id,
        channel_id=test_channel.id,
        distribution_method="auto_filter",
        status="failed",
        error_message="Test error",
        retry_count="0",
        max_retries="3",
    )
    db_session.add(failed_dist)
    db_session.commit()
    
    service = VideoDistributionService(db_session)
    
    distribution = service.retry_failed_distribution(failed_dist.id)
    
    assert distribution.status == "assigned"
    assert int(distribution.retry_count) == 1
    assert distribution.error_message is None


def test_retry_failed_distribution_max_retries(db_session, test_channel, test_video):
    """Test retry fails when max retries exceeded"""
    failed_dist = VideoDistribution(
        video_id=test_video.id,
        channel_id=test_channel.id,
        distribution_method="auto_filter",
        status="failed",
        retry_count="3",
        max_retries="3",
    )
    db_session.add(failed_dist)
    db_session.commit()
    
    service = VideoDistributionService(db_session)
    
    with pytest.raises(ValidationError) as exc_info:
        service.retry_failed_distribution(failed_dist.id)
    
    assert "exceeded max retries" in str(exc_info.value).lower()
