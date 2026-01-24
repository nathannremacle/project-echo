"""
Integration tests for queue workflow
"""

import pytest
from datetime import datetime, timedelta

from src.database import Base, SessionLocal
from src.models.channel import Channel
from src.models.video import Video
from src.models.job import VideoProcessingJob
from src.services.orchestration.queue_service import QueueService


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
        download_status="pending",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


def test_queue_workflow_priority_ordering(db_session, test_video):
    """Test that jobs are processed in priority order"""
    service = QueueService(db_session)
    
    # Create jobs with different priorities
    job1 = service.enqueue_job(test_video.id, "download", priority=3)
    job2 = service.enqueue_job(test_video.id, "transform", priority=10)
    job3 = service.enqueue_job(test_video.id, "download", priority=5)
    
    # Get pending jobs (should be ordered by priority)
    pending = service.get_pending_jobs()
    
    assert len(pending) == 3
    assert pending[0].id == job2.id  # Priority 10
    assert pending[1].id == job3.id  # Priority 5
    assert pending[2].id == job1.id  # Priority 3


def test_batch_processing(db_session, test_video):
    """Test batch processing of jobs"""
    service = QueueService(db_session)
    
    # Create multiple jobs
    jobs = []
    for i in range(5):
        job = service.enqueue_job(test_video.id, "download", priority=i)
        jobs.append(job)
    
    # Process batch
    with patch("src.services.orchestration.queue_service.DownloadService"):
        processed = service.process_batch(batch_size=3)
        
        # Should process up to batch_size jobs
        assert len(processed) <= 3


def test_retry_workflow(db_session, test_video):
    """Test retry workflow"""
    service = QueueService(db_session)
    
    # Create and fail a job
    job = service.enqueue_job(test_video.id, "download")
    job.status = "failed"
    job.attempts = 1
    job.max_attempts = 3
    job.error_message = "Test error"
    db_session.commit()
    
    # Retry job
    retried = service.retry_job(job.id)
    
    assert retried.status == "queued"
    assert retried.error_message is None
    assert retried.attempts == 1  # Will be incremented on next execution


def test_queue_statistics_integration(db_session, test_video):
    """Test queue statistics with real database"""
    service = QueueService(db_session)
    
    # Create jobs in various states
    job1 = service.enqueue_job(test_video.id, "download")
    job1.status = "completed"
    job1.duration = 120
    job1.started_at = datetime.utcnow() - timedelta(seconds=120)
    job1.completed_at = datetime.utcnow()
    db_session.commit()
    
    job2 = service.enqueue_job(test_video.id, "transform")
    job2.status = "processing"
    job2.started_at = datetime.utcnow() - timedelta(seconds=30)
    job2.queued_at = datetime.utcnow() - timedelta(seconds=60)
    db_session.commit()
    
    job3 = service.enqueue_job(test_video.id, "download")
    # Still queued
    
    stats = service.get_statistics()
    
    assert stats["total_jobs"] == 3
    assert stats["queued"] == 1
    assert stats["processing"] == 1
    assert stats["completed"] == 1
    assert stats["success_rate"] == 100.0  # 1 completed, 0 failed
    assert stats["average_processing_time"] == 120.0
    assert stats["average_wait_time"] == 30.0  # 60s queued - 30s processing = 30s wait
