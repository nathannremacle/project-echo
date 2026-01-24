"""
Unit tests for YouTube upload service
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import json
import tempfile
import os

from src.services.youtube.upload_service import YouTubeUploadService, YOUTUBE_CATEGORIES
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
            "title": "{channel_name} - {source_title}",
            "description": "Video from {channel_name}",
            "tags": ["test", "video"],
            "category": "entertainment",
            "privacy": "unlisted",
        }),
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
        transformation_status="transformed",
        transformed_url="s3://bucket/video.mp4",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


def test_process_metadata_template(db_session):
    """Test metadata template processing"""
    service = YouTubeUploadService(db_session)
    
    template = {
        "title": "{channel_name} - {source_title} - {date}",
        "description": "Video from {channel_name}",
        "tags": ["tag1", "tag2"],
        "category": "entertainment",
        "privacy": "public",
    }
    
    metadata = service._process_metadata_template(
        template=template,
        channel_name="My Channel",
        source_title="Source Video",
        video_number=5,
    )
    
    assert "My Channel" in metadata["title"]
    assert "Source Video" in metadata["title"]
    assert metadata["category_id"] == YOUTUBE_CATEGORIES["entertainment"]
    assert metadata["privacy_status"] == "public"
    assert len(metadata["tags"]) == 2


def test_process_metadata_template_defaults(db_session):
    """Test metadata template with defaults"""
    service = YouTubeUploadService(db_session)
    
    template = {}
    
    metadata = service._process_metadata_template(
        template=template,
        channel_name="Channel",
        source_title="Video",
    )
    
    assert metadata["title"] == "Video"  # Uses source_title as default
    assert metadata["category_id"] == 24  # Default: Entertainment
    assert metadata["privacy_status"] == "unlisted"  # Default


@patch("src.services.youtube.upload_service.boto3.client")
def test_download_video_from_s3(db_session, mock_boto3):
    """Test downloading video from S3"""
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3
    
    service = YouTubeUploadService(db_session)
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        service._download_video_from_s3("s3://bucket/video.mp4", temp_path)
        
        mock_s3.download_file.assert_called_once_with("bucket", "video.mp4", temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@patch("src.services.youtube.upload_service.YouTubeClient")
@patch("src.services.youtube.upload_service.YouTubeUploadService._download_video_from_s3")
@patch("src.services.youtube.upload_service.YouTubeUploadService._upload_video_with_progress")
def test_upload_video_success(
    db_session, test_video, test_channel,
    mock_upload, mock_download, mock_youtube_client
):
    """Test successful video upload"""
    # Mock YouTube client
    mock_client = MagicMock()
    mock_youtube_client.return_value = mock_client
    
    # Mock upload result
    mock_upload.return_value = {
        "video_id": "youtube_video_id_123",
        "video_url": "https://www.youtube.com/watch?v=youtube_video_id_123",
        "published_at": "2026-01-23T12:00:00Z",
    }
    
    service = YouTubeUploadService(db_session)
    
    result = service.upload_video(test_video.id)
    
    assert result["video_id"] == "youtube_video_id_123"
    assert "youtube.com" in result["video_url"]
    
    # Verify video was updated
    db_session.refresh(test_video)
    assert test_video.publication_status == "published"
    assert test_video.youtube_video_id == "youtube_video_id_123"
    assert test_video.published_at is not None


def test_upload_video_not_found(db_session):
    """Test uploading non-existent video"""
    service = YouTubeUploadService(db_session)
    
    with pytest.raises(NotFoundError):
        service.upload_video("non-existent-id")


def test_upload_video_not_transformed(db_session, test_channel):
    """Test uploading video that is not transformed"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        transformation_status="pending",  # Not transformed
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    
    service = YouTubeUploadService(db_session)
    
    with pytest.raises(ProcessingError) as exc_info:
        service.upload_video(video.id)
    
    assert "not transformed" in str(exc_info.value).lower()


@patch("src.services.youtube.upload_service.YouTubeClient")
@patch("src.services.youtube.upload_service.YouTubeUploadService._download_video_from_s3")
@patch("src.services.youtube.upload_service.YouTubeUploadService._upload_video_with_progress")
def test_upload_video_with_metadata_override(
    db_session, test_video, test_channel,
    mock_upload, mock_download, mock_youtube_client
):
    """Test uploading video with metadata override"""
    mock_client = MagicMock()
    mock_youtube_client.return_value = mock_client
    
    mock_upload.return_value = {
        "video_id": "youtube_video_id_123",
        "video_url": "https://www.youtube.com/watch?v=youtube_video_id_123",
        "published_at": "2026-01-23T12:00:00Z",
    }
    
    service = YouTubeUploadService(db_session)
    
    metadata_override = {
        "title": "Custom Title",
        "privacy": "public",
    }
    
    result = service.upload_video(test_video.id, metadata_override=metadata_override)
    
    # Verify metadata was overridden
    call_args = mock_upload.call_args
    uploaded_metadata = call_args[1]["metadata"]
    assert uploaded_metadata["title"] == "Custom Title"
    assert uploaded_metadata["privacy_status"] == "public"


@patch("src.services.youtube.upload_service.YouTubeClient")
@patch("src.services.youtube.upload_service.YouTubeUploadService._download_video_from_s3")
@patch("src.services.youtube.upload_service.YouTubeUploadService._upload_video_with_progress")
def test_upload_video_failure(
    db_session, test_video, test_channel,
    mock_upload, mock_download, mock_youtube_client
):
    """Test video upload failure"""
    mock_client = MagicMock()
    mock_youtube_client.return_value = mock_client
    
    # Mock upload failure
    from src.utils.exceptions import AuthenticationError
    mock_upload.side_effect = AuthenticationError("Upload failed")
    
    service = YouTubeUploadService(db_session)
    
    with pytest.raises(ProcessingError):
        service.upload_video(test_video.id)
    
    # Verify video status is set to failed
    db_session.refresh(test_video)
    assert test_video.publication_status == "failed"
