"""
Unit tests for scheduling service
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.services.orchestration.scheduling_service import SchedulingService
from src.models.channel import Channel
from src.models.video import Video
from src.models.schedule import PublicationSchedule
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
        source_url="https://youtube.com/watch?v=test",
        source_title="Test Video",
        source_platform="youtube",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


def test_create_simultaneous_schedule(db_session, test_channel, test_video):
    """Test creating simultaneous publication schedule"""
    # Create additional channels
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
    
    service = SchedulingService(db_session)
    
    scheduled_at = datetime.utcnow() + timedelta(hours=1)
    schedules = service.create_simultaneous_schedule(
        video_id=test_video.id,
        channel_ids=[test_channel.id, channel2.id],
        scheduled_at=scheduled_at,
        wave_id="wave-123",
    )
    
    assert len(schedules) == 2
    assert all(s.schedule_type == "simultaneous" for s in schedules)
    assert all(s.scheduled_at == scheduled_at for s in schedules)
    assert all(s.video_id == test_video.id for s in schedules)
    assert all(s.coordination_group_id == schedules[0].coordination_group_id for s in schedules)
    assert all(s.wave_id == "wave-123" for s in schedules)


def test_create_staggered_schedule(db_session, test_channel, test_video):
    """Test creating staggered publication schedule"""
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
    
    service = SchedulingService(db_session)
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    delay_seconds = 3600  # 1 hour
    schedules = service.create_staggered_schedule(
        video_id=test_video.id,
        channel_ids=[test_channel.id, channel2.id],
        start_time=start_time,
        delay_seconds=delay_seconds,
    )
    
    assert len(schedules) == 2
    assert all(s.schedule_type == "staggered" for s in schedules)
    assert schedules[0].scheduled_at == start_time
    assert schedules[1].scheduled_at == start_time + timedelta(seconds=delay_seconds)
    assert schedules[0].delay_seconds == 0
    assert schedules[1].delay_seconds == delay_seconds
    assert all(s.coordination_group_id == schedules[0].coordination_group_id for s in schedules)


def test_create_independent_schedule(db_session, test_channel, test_video):
    """Test creating independent schedule"""
    service = SchedulingService(db_session)
    
    scheduled_at = datetime.utcnow() + timedelta(hours=2)
    schedule = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=scheduled_at,
        video_id=test_video.id,
    )
    
    assert schedule.schedule_type == "independent"
    assert schedule.scheduled_at == scheduled_at
    assert schedule.video_id == test_video.id
    assert schedule.coordination_group_id is None


def test_create_schedule_conflict(db_session, test_channel, test_video):
    """Test schedule conflict detection"""
    service = SchedulingService(db_session)
    
    scheduled_at = datetime.utcnow() + timedelta(hours=1)
    
    # Create first schedule
    schedule1 = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=scheduled_at,
        video_id=test_video.id,
    )
    
    # Try to create conflicting schedule
    with pytest.raises(ValidationError) as exc_info:
        service.create_independent_schedule(
            channel_id=test_channel.id,
            scheduled_at=scheduled_at,  # Same time
            video_id=test_video.id,  # Same video
        )
    
    assert "conflict" in str(exc_info.value).lower()


def test_validate_schedule(db_session, test_channel, test_video):
    """Test schedule validation"""
    service = SchedulingService(db_session)
    
    scheduled_at = datetime.utcnow() + timedelta(hours=1)
    schedule = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=scheduled_at,
        video_id=test_video.id,
    )
    
    validation = service.validate_schedule(schedule.id)
    assert validation["valid"] is True
    assert len(validation["issues"]) == 0


def test_validate_schedule_past_date(db_session, test_channel, test_video):
    """Test validation detects past dates"""
    service = SchedulingService(db_session)
    
    # Create schedule in the past
    past_time = datetime.utcnow() - timedelta(hours=1)
    schedule = PublicationSchedule(
        channel_id=test_channel.id,
        video_id=test_video.id,
        schedule_type="independent",
        scheduled_at=past_time,
        status="pending",
    )
    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)
    
    validation = service.validate_schedule(schedule.id)
    assert validation["valid"] is False
    assert any("past" in issue.lower() for issue in validation["issues"])


def test_pause_resume_schedule(db_session, test_channel, test_video):
    """Test pausing and resuming schedules"""
    service = SchedulingService(db_session)
    
    scheduled_at = datetime.utcnow() + timedelta(hours=1)
    schedule = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=scheduled_at,
        video_id=test_video.id,
    )
    
    assert schedule.is_paused is False
    
    # Pause
    schedule = service.pause_schedule(schedule.id)
    assert schedule.is_paused is True
    
    # Resume
    schedule = service.resume_schedule(schedule.id)
    assert schedule.is_paused is False


def test_cancel_schedule(db_session, test_channel, test_video):
    """Test cancelling a schedule"""
    service = SchedulingService(db_session)
    
    scheduled_at = datetime.utcnow() + timedelta(hours=1)
    schedule = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=scheduled_at,
        video_id=test_video.id,
    )
    
    assert schedule.status == "pending"
    
    schedule = service.cancel_schedule(schedule.id)
    assert schedule.status == "cancelled"


@patch("src.services.orchestration.scheduling_service.GitHubRepositoryService")
def test_execute_schedule_github(db_session, test_channel, test_video, mock_github_service_class):
    """Test executing schedule via GitHub Actions"""
    test_channel.github_repo_url = "https://github.com/user/repo"
    db_session.commit()
    
    mock_github_service = MagicMock()
    mock_github_service_class.return_value = mock_github_service
    
    service = SchedulingService(db_session)
    service.github_service = mock_github_service
    
    scheduled_at = datetime.utcnow() - timedelta(minutes=1)  # In the past, ready to execute
    schedule = PublicationSchedule(
        channel_id=test_channel.id,
        video_id=test_video.id,
        schedule_type="independent",
        scheduled_at=scheduled_at,
        status="pending",
    )
    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)
    
    results = service.execute_pending_schedules()
    
    assert len(results) == 1
    assert results[0]["status"] == "completed"
    mock_github_service.trigger_workflow.assert_called_once()


def test_get_schedules_by_date_range(db_session, test_channel, test_video):
    """Test getting schedules by date range"""
    service = SchedulingService(db_session)
    
    now = datetime.utcnow()
    schedule1 = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=now + timedelta(hours=1),
        video_id=test_video.id,
    )
    schedule2 = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=now + timedelta(days=2),
        video_id=test_video.id,
    )
    
    schedules = service.get_schedules_by_date_range(
        start_date=now,
        end_date=now + timedelta(days=1),
    )
    
    assert len(schedules) == 1
    assert schedules[0].id == schedule1.id


def test_get_schedules_by_channel(db_session, test_channel, test_video):
    """Test getting schedules by channel"""
    service = SchedulingService(db_session)
    
    schedule = service.create_independent_schedule(
        channel_id=test_channel.id,
        scheduled_at=datetime.utcnow() + timedelta(hours=1),
        video_id=test_video.id,
    )
    
    schedules = service.get_schedules_by_channel(test_channel.id)
    
    assert len(schedules) == 1
    assert schedules[0].id == schedule.id


def test_get_schedules_by_wave(db_session, test_channel, test_video):
    """Test getting schedules by wave ID"""
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
    
    service = SchedulingService(db_session)
    
    wave_id = "wave-123"
    schedules = service.create_simultaneous_schedule(
        video_id=test_video.id,
        channel_ids=[test_channel.id, channel2.id],
        scheduled_at=datetime.utcnow() + timedelta(hours=1),
        wave_id=wave_id,
    )
    
    wave_schedules = service.get_schedules_by_wave(wave_id)
    
    assert len(wave_schedules) == 2
    assert all(s.wave_id == wave_id for s in wave_schedules)
