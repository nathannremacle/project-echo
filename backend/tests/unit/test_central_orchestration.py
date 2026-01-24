"""
Unit tests for central orchestration service
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from src.services.orchestration.central_orchestration_service import CentralOrchestrationService
from src.models.channel import Channel
from src.models.video import Video
from src.utils.exceptions import ValidationError, NotFoundError


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
        source_url="https://youtube.com/watch?v=test",
        source_title="Test Video",
        source_platform="youtube",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


def test_start_orchestration(db_session):
    """Test starting orchestration system"""
    service = CentralOrchestrationService(db_session)
    
    result = service.start()
    
    assert result["status"] == "started"
    assert "started_at" in result
    
    status = service.get_status()
    assert status["running"] is True
    assert status["paused"] is False


def test_stop_orchestration(db_session):
    """Test stopping orchestration system"""
    service = CentralOrchestrationService(db_session)
    
    service.start()
    result = service.stop()
    
    assert result["status"] == "stopped"
    assert "stopped_at" in result
    
    status = service.get_status()
    assert status["running"] is False


def test_pause_resume_orchestration(db_session):
    """Test pausing and resuming orchestration"""
    service = CentralOrchestrationService(db_session)
    
    service.start()
    
    result = service.pause()
    assert result["status"] == "paused"
    
    status = service.get_status()
    assert status["paused"] is True
    
    result = service.resume()
    assert result["status"] == "resumed"
    
    status = service.get_status()
    assert status["paused"] is False


def test_start_when_running(db_session):
    """Test starting when already running"""
    service = CentralOrchestrationService(db_session)
    
    service.start()
    
    with pytest.raises(ValidationError) as exc_info:
        service.start()
    
    assert "already running" in str(exc_info.value).lower()


def test_coordinate_publication(db_session, test_channel, test_video):
    """Test coordinating publication"""
    import json
    channel2 = Channel(
        name="Test Channel 2",
        youtube_channel_id="UC456",
        youtube_channel_url="https://youtube.com/channel/UC456",
        is_active=True,
        api_credentials_encrypted="encrypted_creds",
        posting_schedule=json.dumps({}),
        content_filters=json.dumps({}),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel2)
    db_session.commit()
    db_session.refresh(channel2)
    
    service = CentralOrchestrationService(db_session)
    service.start()
    
    result = service.coordinate_publication(
        video_id=test_video.id,
        channel_ids=[test_channel.id, channel2.id],
        timing="simultaneous",
    )
    
    assert result["video_id"] == test_video.id
    assert len(result["channel_ids"]) == 2
    assert result["timing"] == "simultaneous"
    assert result["schedules_created"] == 2


def test_coordinate_publication_not_running(db_session, test_channel, test_video):
    """Test coordinating publication when not running"""
    service = CentralOrchestrationService(db_session)
    
    with pytest.raises(ValidationError) as exc_info:
        service.coordinate_publication(
            video_id=test_video.id,
            channel_ids=[test_channel.id],
        )
    
    assert "not running" in str(exc_info.value).lower()


def test_monitor_channels(db_session, test_channel):
    """Test monitoring channels"""
    service = CentralOrchestrationService(db_session)
    
    channel_statuses = service.monitor_channels()
    
    assert len(channel_statuses) == 1
    assert channel_statuses[0]["channel_id"] == test_channel.id
    assert channel_statuses[0]["name"] == test_channel.name
    assert "health" in channel_statuses[0]
    assert "status" in channel_statuses[0]


def test_get_dashboard_data(db_session, test_channel):
    """Test getting dashboard data"""
    service = CentralOrchestrationService(db_session)
    
    dashboard = service.get_dashboard_data()
    
    assert "system" in dashboard
    assert "channels" in dashboard
    assert "statistics" in dashboard
    assert "schedules" in dashboard
    assert dashboard["channels"]["total"] == 1


def test_distribute_videos(db_session, test_channel, test_video):
    """Test auto-distributing videos"""
    service = CentralOrchestrationService(db_session)
    service.start()
    
    with patch.object(service.distribution_service, "auto_distribute_by_filters", return_value=[]), \
         patch.object(service.distribution_service, "auto_distribute_by_schedule", return_value=[]):
        result = service.distribute_videos()
        
        assert "total_distributed" in result
        assert "by_filters" in result
        assert "by_schedule" in result
