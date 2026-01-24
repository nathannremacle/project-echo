"""
Unit tests for database models
"""

import pytest
from datetime import datetime

from src.database import Base, SessionLocal, init_db
from src.models import (
    Channel,
    Video,
    VideoProcessingJob,
    TransformationPreset,
    Music,
    ChannelStatistics,
    VideoStatistics,
    SystemConfiguration,
)


@pytest.fixture
def db_session():
    """Create test database session"""
    # Use in-memory SQLite for tests
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_channel_model(db_session):
    """Test Channel model creation"""
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC1234567890123456789012",
        youtube_channel_url="https://youtube.com/channel/UC1234567890123456789012",
        api_credentials_encrypted='{"clientId": "encrypted", "clientSecret": "encrypted"}',
        posting_schedule='{"frequency": "daily"}',
        content_filters='{"minResolution": "720p"}',
        metadata_template='{"titleTemplate": "Test"}',
    )
    
    db_session.add(channel)
    db_session.commit()
    
    assert channel.id is not None
    assert channel.name == "Test Channel"
    assert channel.is_active is False  # Default value


def test_video_model(db_session):
    """Test Video model creation"""
    # Create channel first
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
    
    # Create video
    video = Video(
        channel_id=channel.id,
        source_url="https://example.com/video.mp4",
        source_title="Test Video",
        source_platform="youtube",
    )
    
    db_session.add(video)
    db_session.commit()
    
    assert video.id is not None
    assert video.channel_id == channel.id
    assert video.download_status == "pending"  # Default value


def test_video_processing_job_model(db_session):
    """Test VideoProcessingJob model creation"""
    # Create channel and video
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
    
    video = Video(
        channel_id=channel.id,
        source_url="https://example.com/video.mp4",
        source_title="Test Video",
        source_platform="youtube",
    )
    db_session.add(video)
    db_session.commit()
    
    # Create job
    job = VideoProcessingJob(
        video_id=video.id,
        channel_id=channel.id,
        job_type="transform",
        status="queued",
    )
    
    db_session.add(job)
    db_session.commit()
    
    assert job.id is not None
    assert job.attempts == 0  # Default value
    assert job.max_attempts == 3  # Default value


def test_transformation_preset_model(db_session):
    """Test TransformationPreset model creation"""
    preset = TransformationPreset(
        name="Default Preset",
        description="Default transformation preset",
        parameters='{"brightness": 1.1, "contrast": 1.2}',
    )
    
    db_session.add(preset)
    db_session.commit()
    
    assert preset.id is not None
    assert preset.is_active is True  # Default value


def test_system_configuration_model(db_session):
    """Test SystemConfiguration model creation"""
    config = SystemConfiguration(
        key="test_key",
        value='"test_value"',
        description="Test configuration",
    )
    
    db_session.add(config)
    db_session.commit()
    
    assert config.key == "test_key"
    assert config.encrypted is False  # Default value
