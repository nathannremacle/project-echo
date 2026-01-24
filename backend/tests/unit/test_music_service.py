"""
Unit tests for music service
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from src.services.music.music_service import MusicService, SUPPORTED_FORMATS, MAX_FILE_SIZE
from src.models.music import Music
from src.utils.exceptions import ValidationError, ProcessingError


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_music_repo():
    """Mock music repository"""
    repo = Mock()
    return repo


@pytest.fixture
def mock_storage():
    """Mock S3 storage client"""
    storage = Mock()
    storage.bucket_name = "test-bucket"
    storage._generate_s3_key = lambda channel_id, video_id, filename: f"{channel_id}/{video_id}/{filename}"
    return storage


@pytest.fixture
def music_service(mock_db, mock_music_repo, mock_storage):
    """Create music service with mocked dependencies"""
    with patch("src.services.music.music_service.MusicRepository", return_value=mock_music_repo), \
         patch("src.services.music.music_service.S3StorageClient", return_value=mock_storage):
        service = MusicService(mock_db)
        service.music_repo = mock_music_repo
        service.storage = mock_storage
        return service


def test_validate_file_supported_format(music_service):
    """Test file validation with supported format"""
    file = BytesIO(b"fake mp3 content")
    file.name = "test.mp3"
    
    with patch.object(music_service, "_extract_duration", return_value=60):
        result = music_service._validate_file(file, "test.mp3")
        assert result["format"] == ".mp3"
        assert result["size"] > 0


def test_validate_file_unsupported_format(music_service):
    """Test file validation with unsupported format"""
    file = BytesIO(b"fake content")
    file.name = "test.txt"
    
    with pytest.raises(ValidationError, match="Unsupported file format"):
        music_service._validate_file(file, "test.txt")


def test_validate_file_too_large(music_service):
    """Test file validation with file too large"""
    # Create a file larger than MAX_FILE_SIZE
    large_content = b"x" * (MAX_FILE_SIZE + 1)
    file = BytesIO(large_content)
    file.name = "test.mp3"
    
    with pytest.raises(ValidationError, match="exceeds maximum"):
        music_service._validate_file(file, "test.mp3")


def test_upload_music_success(music_service, mock_music_repo, mock_storage):
    """Test successful music upload"""
    file = BytesIO(b"fake mp3 content")
    file.name = "test.mp3"
    
    # Mock music creation
    music = Music(
        id="test-id",
        name="Test Track",
        artist="Test Artist",
        file_size=1000,
        duration=60,
    )
    mock_music_repo.create.return_value = music
    mock_music_repo.update.return_value = music
    
    # Mock storage upload
    mock_storage.upload_file.return_value = "s3://bucket/music/test-id/test.mp3"
    
    with patch.object(music_service, "_validate_file", return_value={"format": ".mp3", "size": 1000, "duration": 60}), \
         patch("tempfile.NamedTemporaryFile") as mock_temp:
        # Mock temporary file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test.mp3"
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp.return_value = mock_temp_file
        
        result = music_service.upload_music(
            file=file,
            filename="test.mp3",
            name="Test Track",
            artist="Test Artist",
        )
        
        assert result.id == "test-id"
        assert result.name == "Test Track"
        mock_music_repo.create.assert_called_once()
        mock_storage.upload_file.assert_called_once()


def test_delete_music_success(music_service, mock_music_repo, mock_storage):
    """Test successful music deletion"""
    music = Music(
        id="test-id",
        name="Test Track",
        file_path="s3://bucket/music/test-id/test.mp3",
    )
    mock_music_repo.get_by_id.return_value = music
    mock_music_repo.delete.return_value = True
    mock_storage.delete_file.return_value = True
    
    result = music_service.delete_music("test-id")
    
    assert result is True
    mock_music_repo.delete.assert_called_once_with("test-id")


def test_get_preview_url_success(music_service, mock_music_repo):
    """Test successful preview URL generation"""
    music = Music(
        id="test-id",
        name="Test Track",
        file_path="s3://bucket/music/test-id/test.mp3",
    )
    mock_music_repo.get_by_id.return_value = music
    
    with patch("boto3.client") as mock_boto3:
        mock_s3_client = Mock()
        mock_s3_client.generate_presigned_url.return_value = "https://presigned-url.com"
        mock_boto3.return_value = mock_s3_client
        
        url = music_service.get_preview_url("test-id")
        
        assert url == "https://presigned-url.com"
        mock_s3_client.generate_presigned_url.assert_called_once()


def test_list_music(music_service, mock_music_repo):
    """Test listing music tracks"""
    tracks = [
        Music(id="1", name="Track 1", is_active=True),
        Music(id="2", name="Track 2", is_active=False),
    ]
    mock_music_repo.get_all.return_value = tracks
    
    result = music_service.list_music(active_only=True)
    
    assert len(result) == 2
    mock_music_repo.get_all.assert_called_once_with(active_only=True)
