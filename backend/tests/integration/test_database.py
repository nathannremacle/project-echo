"""
Integration tests for database operations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import Channel, Video, VideoProcessingJob
from src.repositories import ChannelRepository, VideoRepository, JobRepository


@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_channel_video_relationship(db_session):
    """Test relationship between Channel and Video"""
    # Create channel
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
    
    # Create videos
    video1 = Video(
        channel_id=channel.id,
        source_url="https://example.com/video1.mp4",
        source_title="Video 1",
        source_platform="youtube",
    )
    video2 = Video(
        channel_id=channel.id,
        source_url="https://example.com/video2.mp4",
        source_title="Video 2",
        source_platform="youtube",
    )
    db_session.add_all([video1, video2])
    db_session.commit()
    
    # Test relationship
    assert len(channel.videos) == 2
    assert video1.channel.id == channel.id
    assert video2.channel.id == channel.id


def test_cascade_delete(db_session):
    """Test cascade delete (deleting channel deletes videos)"""
    # Create channel and videos
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
    
    video_id = video.id
    
    # Delete channel
    db_session.delete(channel)
    db_session.commit()
    
    # Verify video is also deleted
    video_repo = VideoRepository(db_session)
    deleted_video = video_repo.get_by_id(video_id)
    assert deleted_video is None


def test_job_video_relationship(db_session):
    """Test relationship between VideoProcessingJob and Video"""
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
    
    # Create jobs
    job1 = VideoProcessingJob(
        video_id=video.id,
        channel_id=channel.id,
        job_type="download",
        status="queued",
    )
    job2 = VideoProcessingJob(
        video_id=video.id,
        channel_id=channel.id,
        job_type="transform",
        status="queued",
    )
    db_session.add_all([job1, job2])
    db_session.commit()
    
    # Test relationships
    assert len(video.processing_jobs) == 2
    assert job1.video.id == video.id
    assert job2.video.id == video.id
