"""
Integration tests for complete pipeline execution
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from src.services.orchestration.pipeline_service import PipelineService
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
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        is_active=True,
        api_credentials_encrypted="encrypted_creds",
        posting_schedule=json.dumps({}),
        content_filters=json.dumps({}),
        metadata_template=json.dumps({
            "title": "Test Video",
            "description": "Test Description",
            "tags": ["test"],
            "category": "entertainment",
            "privacy": "unlisted",
        }),
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@patch("src.services.orchestration.pipeline_service.ScrapingService")
@patch("src.services.orchestration.pipeline_service.DownloadService")
@patch("src.services.orchestration.pipeline_service.TransformationService")
@patch("src.services.orchestration.pipeline_service.YouTubeUploadService")
def test_execute_pipeline_complete(
    db_session, test_channel,
    mock_upload, mock_transform, mock_download, mock_scrape
):
    """Test complete pipeline execution"""
    # Mock services
    mock_scrape_instance = MagicMock()
    mock_scrape_instance.scrape_video_url.return_value = {
        "videos": [MagicMock(id="video-123")]
    }
    mock_scrape.return_value = mock_scrape_instance
    
    mock_download_instance = MagicMock()
    mock_download.return_value = mock_download_instance
    
    mock_transform_instance = MagicMock()
    mock_transform.return_value = mock_transform_instance
    
    mock_upload_instance = MagicMock()
    mock_upload_instance.upload_video.return_value = {
        "video_id": "youtube_video_id_123",
        "video_url": "https://www.youtube.com/watch?v=youtube_video_id_123",
    }
    mock_upload.return_value = mock_upload_instance
    
    # Create test video
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        download_status="downloaded",
        download_url="s3://bucket/video.mp4",
        transformation_status="transformed",
        transformed_url="s3://bucket/transformed.mp4",
    )
    db_session.add(video)
    db_session.commit()
    
    # Mock video repository to return our test video
    with patch("src.services.orchestration.pipeline_service.VideoRepository") as mock_video_repo:
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = video
        mock_video_repo.return_value = mock_repo_instance
        
        service = PipelineService(db_session)
        
        results = service.execute_pipeline(
            channel_id=test_channel.id,
            source_url="https://youtube.com/watch?v=test123",
            skip_upload=False,
        )
        
        assert results["status"] == "completed"
        assert results["video_id"] == "video-123"
        assert results["youtube_video_id"] == "youtube_video_id_123"
        assert "scrape" in results["steps"]
        assert "download" in results["steps"]
        assert "transform" in results["steps"]
        assert "upload" in results["steps"]


@patch("src.services.orchestration.pipeline_service.ScrapingService")
def test_execute_pipeline_scrape_failure(db_session, test_channel, mock_scrape):
    """Test pipeline failure at scrape step"""
    mock_scrape_instance = MagicMock()
    mock_scrape_instance.scrape_video_url.side_effect = ProcessingError("Scrape failed")
    mock_scrape.return_value = mock_scrape_instance
    
    service = PipelineService(db_session)
    
    results = service.execute_pipeline(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
    )
    
    assert results["status"] == "failed"
    assert results["steps"]["scrape"]["status"] == "failed"
    assert len(results["errors"]) > 0


def test_execute_pipeline_channel_not_found(db_session):
    """Test pipeline execution with non-existent channel"""
    service = PipelineService(db_session)
    
    with pytest.raises(NotFoundError):
        service.execute_pipeline(channel_id="non-existent-id")


@patch("src.services.orchestration.pipeline_service.DownloadService")
def test_execute_pipeline_with_existing_video(
    db_session, test_channel, mock_download
):
    """Test pipeline execution with existing video (skip scrape)"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        download_status="downloaded",
        download_url="s3://bucket/video.mp4",
        transformation_status="transformed",
        transformed_url="s3://bucket/transformed.mp4",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    
    mock_download_instance = MagicMock()
    mock_download.return_value = mock_download_instance
    
    service = PipelineService(db_session)
    
    results = service.execute_pipeline(
        channel_id=test_channel.id,
        video_id=video.id,
        skip_upload=True,
    )
    
    assert results["status"] == "completed"
    assert results["video_id"] == video.id
    assert "scrape" not in results["steps"]  # Scrape skipped
    assert results["steps"]["upload"]["status"] == "skipped"
