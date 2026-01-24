"""
Integration tests for download service
"""

import json
import pytest
import os
from unittest.mock import patch, MagicMock

from src.database import Base, SessionLocal
from src.models.channel import Channel
from src.models.video import Video
from src.services.download.download_service import DownloadService
from src.repositories.video_repository import VideoRepository


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


@patch("src.services.download.download_service.S3StorageClient")
@patch("src.services.download.download_service.VideoDownloader")
@patch.dict(os.environ, {
    "AWS_ACCESS_KEY_ID": "test_key",
    "AWS_SECRET_ACCESS_KEY": "test_secret",
    "AWS_S3_BUCKET": "test-bucket",
})
def test_download_video_success(mock_downloader_class, mock_storage_class, db_session, test_video):
    """Test successful video download"""
    # Mock downloader
    mock_downloader = MagicMock()
    mock_downloader_class.return_value = mock_downloader
    
    download_info = {
        "file_path": "/tmp/test123.mp4",
        "file_size": 1024000,
        "duration": 120,
        "resolution": "1080p",
        "format": "mp4",
        "width": 1920,
        "height": 1080,
        "ext": ".mp4",
    }
    mock_downloader.download.return_value = download_info
    
    # Mock storage
    mock_storage = MagicMock()
    mock_storage_class.return_value = mock_storage
    mock_storage.upload_file.return_value = "s3://test-bucket/channel123/test123/video.mp4"
    
    # Mock file operations
    with patch("os.path.exists", return_value=True):
        with patch("os.remove"):
            service = DownloadService(db_session)
            result = service.download_video(test_video.id)
            
            assert result.download_status == "downloaded"
            assert result.download_url is not None
            assert result.download_size == 1024000
            assert result.download_duration == 120
            assert result.download_resolution == "1080p"


@patch("src.services.download.download_service.S3StorageClient")
@patch("src.services.download.download_service.VideoDownloader")
@patch.dict(os.environ, {
    "AWS_ACCESS_KEY_ID": "test_key",
    "AWS_SECRET_ACCESS_KEY": "test_secret",
    "AWS_S3_BUCKET": "test-bucket",
})
def test_download_video_already_downloaded(mock_downloader_class, mock_storage_class, db_session, test_video):
    """Test download of already downloaded video"""
    # Mark video as already downloaded
    test_video.download_status = "downloaded"
    test_video.download_url = "s3://test-bucket/existing.mp4"
    db_session.commit()
    
    service = DownloadService(db_session)
    result = service.download_video(test_video.id)
    
    # Should return without downloading
    assert result.download_status == "downloaded"
    # Downloader should not be called
    mock_downloader_class.return_value.download.assert_not_called()


def test_get_storage_usage(db_session, test_channel):
    """Test storage usage calculation"""
    # Create videos with different download statuses
    video1 = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test1",
        source_title="Video 1",
        source_platform="youtube",
        download_status="downloaded",
        download_size=1024000,
    )
    video2 = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test2",
        source_title="Video 2",
        source_platform="youtube",
        download_status="downloaded",
        download_size=2048000,
    )
    video3 = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test3",
        source_title="Video 3",
        source_platform="youtube",
        download_status="pending",
        download_size=None,
    )
    
    db_session.add_all([video1, video2, video3])
    db_session.commit()
    
    with patch("src.services.download.download_service.S3StorageClient"):
        with patch("src.services.download.download_service.VideoDownloader"):
            service = DownloadService(db_session)
            usage = service.get_storage_usage(channel_id=test_channel.id)
            
            assert usage["total_size_bytes"] == 3072000  # 1MB + 2MB
            assert usage["video_count"] == 2  # Only downloaded videos
            assert usage["average_size_bytes"] == 1536000  # Average of 2 videos
