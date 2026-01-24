"""
Unit tests for repository classes
"""

import pytest

from src.database import Base, SessionLocal
from src.models import Channel, Video, VideoProcessingJob, SystemConfiguration
from src.repositories import (
    ChannelRepository,
    VideoRepository,
    JobRepository,
    ConfigRepository,
)
from src.utils.exceptions import NotFoundError


@pytest.fixture
def db_session():
    """Create test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
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
        youtube_channel_id="UC1234567890123456789012",
        youtube_channel_url="https://youtube.com/channel/UC1234567890123456789012",
        api_credentials_encrypted='{}',
        posting_schedule='{}',
        content_filters='{}',
        metadata_template='{}',
    )
    db_session.add(channel)
    db_session.commit()
    return channel


def test_channel_repository_create(db_session):
    """Test ChannelRepository.create"""
    repo = ChannelRepository(db_session)
    channel = Channel(
        name="New Channel",
        youtube_channel_id="UC9876543210987654321098",
        youtube_channel_url="https://youtube.com/channel/UC9876543210987654321098",
        api_credentials_encrypted='{}',
        posting_schedule='{}',
        content_filters='{}',
        metadata_template='{}',
    )
    
    created = repo.create(channel)
    assert created.id is not None
    assert created.name == "New Channel"


def test_channel_repository_get_by_id(db_session, test_channel):
    """Test ChannelRepository.get_by_id"""
    repo = ChannelRepository(db_session)
    found = repo.get_by_id(test_channel.id)
    
    assert found is not None
    assert found.id == test_channel.id
    assert found.name == test_channel.name


def test_channel_repository_get_all(db_session, test_channel):
    """Test ChannelRepository.get_all"""
    repo = ChannelRepository(db_session)
    channels = repo.get_all()
    
    assert len(channels) == 1
    assert channels[0].id == test_channel.id


def test_channel_repository_delete(db_session, test_channel):
    """Test ChannelRepository.delete"""
    repo = ChannelRepository(db_session)
    repo.delete(test_channel.id)
    
    found = repo.get_by_id(test_channel.id)
    assert found is None


def test_channel_repository_delete_not_found(db_session):
    """Test ChannelRepository.delete with non-existent channel"""
    repo = ChannelRepository(db_session)
    
    with pytest.raises(NotFoundError):
        repo.delete("non-existent-id")


def test_video_repository_create(db_session, test_channel):
    """Test VideoRepository.create"""
    repo = VideoRepository(db_session)
    video = Video(
        channel_id=test_channel.id,
        source_url="https://example.com/video.mp4",
        source_title="Test Video",
        source_platform="youtube",
    )
    
    created = repo.create(video)
    assert created.id is not None
    assert created.channel_id == test_channel.id


def test_video_repository_get_by_channel_id(db_session, test_channel):
    """Test VideoRepository.get_by_channel_id"""
    repo = VideoRepository(db_session)
    
    # Create test videos
    video1 = Video(
        channel_id=test_channel.id,
        source_url="https://example.com/video1.mp4",
        source_title="Video 1",
        source_platform="youtube",
    )
    video2 = Video(
        channel_id=test_channel.id,
        source_url="https://example.com/video2.mp4",
        source_title="Video 2",
        source_platform="youtube",
    )
    db_session.add_all([video1, video2])
    db_session.commit()
    
    videos = repo.get_by_channel_id(test_channel.id)
    assert len(videos) == 2


def test_config_repository_get_set(db_session):
    """Test ConfigRepository get and set"""
    repo = ConfigRepository(db_session)
    
    # Set value
    repo.set("test_key", "test_value", description="Test")
    
    # Get value
    value = repo.get("test_key")
    assert value == "test_value"
    
    # Get non-existent key
    value = repo.get("non_existent")
    assert value is None


def test_config_repository_json_value(db_session):
    """Test ConfigRepository with JSON values"""
    repo = ConfigRepository(db_session)
    
    # Set JSON value
    repo.set("json_key", {"nested": {"value": 123}})
    
    # Get JSON value
    value = repo.get("json_key")
    assert value == {"nested": {"value": 123}}
