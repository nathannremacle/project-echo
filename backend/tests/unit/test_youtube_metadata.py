"""
Unit tests for YouTube metadata service
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from src.services.youtube.metadata_service import YouTubeMetadataService
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
        publication_status="published",
        youtube_video_id="youtube_video_id_123",
        youtube_video_url="https://www.youtube.com/watch?v=youtube_video_id_123",
        final_title="Current Title",
        final_description="Current Description",
        final_tags=json.dumps(["tag1", "tag2"]),
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


@patch("src.services.youtube.metadata_service.YouTubeClient")
def test_update_video_metadata_success(
    db_session, test_video, test_channel, mock_youtube_client
):
    """Test successful metadata update"""
    # Mock YouTube client
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_update = MagicMock()
    mock_update.execute.return_value = {
        "id": "youtube_video_id_123",
        "snippet": {
            "title": "Updated Title",
            "description": "Updated Description",
        },
    }
    mock_youtube.videos.return_value.update.return_value = mock_update
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    service = YouTubeMetadataService(db_session)
    
    metadata = {
        "title": "New Title",
        "description": "New Description",
        "tags": ["new", "tags"],
        "category": "gaming",
    }
    
    result = service.update_video_metadata(
        video_id=test_video.id,
        metadata=metadata,
        use_template=False,
    )
    
    assert result["video_id"] == test_video.id
    assert result["youtube_video_id"] == "youtube_video_id_123"
    
    # Verify video was updated
    db_session.refresh(test_video)
    assert test_video.final_title == "New Title"
    assert test_video.final_description == "New Description"


@patch("src.services.youtube.metadata_service.YouTubeClient")
def test_update_video_metadata_with_template(
    db_session, test_video, test_channel, mock_youtube_client
):
    """Test metadata update using channel template"""
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_update = MagicMock()
    mock_update.execute.return_value = {"id": "youtube_video_id_123"}
    mock_youtube.videos.return_value.update.return_value = mock_update
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    service = YouTubeMetadataService(db_session)
    
    result = service.update_video_metadata(
        video_id=test_video.id,
        use_template=True,
    )
    
    # Verify template was processed
    call_args = mock_update.execute.call_args
    assert call_args is not None
    
    # Verify video was updated
    db_session.refresh(test_video)
    assert test_video.final_title is not None


def test_update_video_metadata_not_found(db_session):
    """Test updating non-existent video"""
    service = YouTubeMetadataService(db_session)
    
    with pytest.raises(NotFoundError):
        service.update_video_metadata("non-existent-id")


def test_update_video_metadata_not_published(db_session, test_channel):
    """Test updating video that is not published"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        publication_status="pending",  # Not published
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    
    service = YouTubeMetadataService(db_session)
    
    with pytest.raises(ProcessingError) as exc_info:
        service.update_video_metadata(video.id)
    
    assert "not published" in str(exc_info.value).lower()


@patch("src.services.youtube.metadata_service.YouTubeClient")
def test_bulk_update_metadata(
    db_session, test_video, test_channel, mock_youtube_client
):
    """Test bulk metadata update"""
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_update = MagicMock()
    mock_update.execute.return_value = {"id": "youtube_video_id_123"}
    mock_youtube.videos.return_value.update.return_value = mock_update
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    # Create second video
    video2 = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test456",
        source_title="Test Video 2",
        source_platform="youtube",
        publication_status="published",
        youtube_video_id="youtube_video_id_456",
        youtube_video_url="https://www.youtube.com/watch?v=youtube_video_id_456",
    )
    db_session.add(video2)
    db_session.commit()
    
    service = YouTubeMetadataService(db_session)
    
    metadata = {
        "title": "Bulk Update Title",
        "description": "Bulk Update Description",
        "tags": ["bulk", "update"],
    }
    
    result = service.bulk_update_metadata(
        video_ids=[test_video.id, video2.id],
        metadata=metadata,
        use_template=False,
    )
    
    assert result["total"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0
    assert len(result["successful_ids"]) == 2


@patch("src.services.youtube.metadata_service.YouTubeClient")
def test_get_current_metadata(db_session, test_video, test_channel, mock_youtube_client):
    """Test getting current metadata from YouTube"""
    mock_client = MagicMock()
    mock_youtube = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [{
            "snippet": {
                "title": "Current Title",
                "description": "Current Description",
                "tags": ["tag1", "tag2"],
                "categoryId": "24",
                "thumbnails": {
                    "high": {"url": "https://thumbnail.url"}
                },
            }
        }]
    }
    mock_youtube.videos.return_value.list.return_value = mock_list
    mock_client.youtube = mock_youtube
    mock_youtube_client.return_value = mock_client
    
    service = YouTubeMetadataService(db_session)
    
    metadata = service.get_current_metadata(test_video.id)
    
    assert metadata["title"] == "Current Title"
    assert metadata["description"] == "Current Description"
    assert len(metadata["tags"]) == 2
    assert metadata["category_id"] == "24"
