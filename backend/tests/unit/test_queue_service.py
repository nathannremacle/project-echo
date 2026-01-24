"""
Unit tests for queue service
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.models.job import VideoProcessingJob
from src.models.video import Video
from src.services.orchestration.queue_service import QueueService


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
def test_video(db_session):
    """Create test video"""
    from src.models.channel import Channel
    import json
    
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        is_active=True,
        content_filters=json.dumps({}),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel)
    db_session.commit()
    
    video = Video(
        channel_id=channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


def test_enqueue_job(db_session, test_video):
    """Test enqueuing a job"""
    service = QueueService(db_session)
    
    job = service.enqueue_job(
        test_video.id,
        "download",
        priority=5,
    )
    
    assert job.id is not None
    assert job.job_type == "download"
    assert job.status == "queued"
    assert job.priority == 5
    assert job.video_id == test_video.id


def test_enqueue_job_invalid_type(db_session, test_video):
    """Test enqueuing with invalid job type"""
    service = QueueService(db_session)
    
    with pytest.raises(ValueError):
        service.enqueue_job(test_video.id, "invalid_type")


def test_enqueue_job_priority_clamping(db_session, test_video):
    """Test priority clamping to 0-10"""
    service = QueueService(db_session)
    
    # Test negative priority
    job1 = service.enqueue_job(test_video.id, "download", priority=-5)
    assert job1.priority == 0
    
    # Test priority > 10
    job2 = service.enqueue_job(test_video.id, "download", priority=15)
    assert job2.priority == 10


def test_get_pending_jobs(db_session, test_video):
    """Test getting pending jobs"""
    service = QueueService(db_session)
    
    # Create multiple jobs with different priorities
    job1 = service.enqueue_job(test_video.id, "download", priority=5)
    job2 = service.enqueue_job(test_video.id, "transform", priority=10)
    job3 = service.enqueue_job(test_video.id, "download", priority=3)
    
    # Get pending jobs (should be ordered by priority)
    pending = service.get_pending_jobs()
    
    assert len(pending) == 3
    # Highest priority first
    assert pending[0].priority == 10
    assert pending[1].priority == 5
    assert pending[2].priority == 3


def test_get_pending_jobs_filtered(db_session, test_video):
    """Test getting pending jobs filtered by type"""
    service = QueueService(db_session)
    
    service.enqueue_job(test_video.id, "download", priority=5)
    service.enqueue_job(test_video.id, "transform", priority=3)
    service.enqueue_job(test_video.id, "download", priority=1)
    
    download_jobs = service.get_pending_jobs(job_type="download")
    
    assert len(download_jobs) == 2
    assert all(job.job_type == "download" for job in download_jobs)


def test_retry_job(db_session, test_video):
    """Test retrying a failed job"""
    service = QueueService(db_session)
    
    # Create and fail a job
    job = service.enqueue_job(test_video.id, "download")
    job.status = "failed"
    job.attempts = 1
    job.max_attempts = 3
    db_session.commit()
    
    # Retry job
    retried = service.retry_job(job.id)
    
    assert retried.status == "queued"
    assert retried.error_message is None
    assert retried.attempts == 1  # Not incremented yet (will be on execution)


def test_retry_job_max_attempts(db_session, test_video):
    """Test retrying job that reached max attempts"""
    service = QueueService(db_session)
    
    job = service.enqueue_job(test_video.id, "download")
    job.status = "failed"
    job.attempts = 3
    job.max_attempts = 3
    db_session.commit()
    
    with pytest.raises(ValueError):
        service.retry_job(job.id)


def test_pause_resume(db_session):
    """Test pausing and resuming queue"""
    service = QueueService(db_session)
    
    # Initially not paused
    assert service.is_paused() is False
    
    # Pause
    service.pause()
    assert service.is_paused() is True
    
    # Resume
    service.resume()
    assert service.is_paused() is False


@patch("src.services.orchestration.queue_service.DownloadService")
def test_process_next_job(db_session, test_video, mock_download_service_class):
    """Test processing next job"""
    mock_download_service = MagicMock()
    mock_download_service_class.return_value = mock_download_service
    
    service = QueueService(db_session)
    
    # Enqueue job
    job = service.enqueue_job(test_video.id, "download")
    
    # Process job
    processed = service.process_next_job()
    
    assert processed is not None
    assert processed.id == job.id
    # Job should be completed or failed
    assert processed.status in ["completed", "failed"]


def test_process_next_job_paused(db_session, test_video):
    """Test processing when queue is paused"""
    service = QueueService(db_session)
    
    service.enqueue_job(test_video.id, "download")
    service.pause()
    
    processed = service.process_next_job()
    
    assert processed is None


def test_get_statistics(db_session, test_video):
    """Test getting queue statistics"""
    service = QueueService(db_session)
    
    # Create jobs in different states
    job1 = service.enqueue_job(test_video.id, "download", priority=5)
    job1.status = "completed"
    job1.duration = 60
    job1.completed_at = datetime.utcnow()
    db_session.commit()
    
    job2 = service.enqueue_job(test_video.id, "transform", priority=3)
    job2.status = "failed"
    db_session.commit()
    
    job3 = service.enqueue_job(test_video.id, "download", priority=1)
    # Still queued
    
    stats = service.get_statistics()
    
    assert stats["total_jobs"] == 3
    assert stats["queued"] == 1
    assert stats["completed"] == 1
    assert stats["failed"] == 1
    assert stats["success_rate"] == 50.0  # 1 completed / (1 completed + 1 failed)
    assert stats["average_processing_time"] == 60.0
