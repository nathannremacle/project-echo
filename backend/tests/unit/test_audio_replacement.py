"""
Unit tests for audio replacement service
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from src.services.audio_replacement.audio_replacement_service import AudioReplacementService
from src.models.video import Video
from src.models.music import Music
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_video_repo():
    """Mock video repository"""
    repo = Mock()
    return repo


@pytest.fixture
def mock_music_repo():
    """Mock music repository"""
    repo = Mock()
    return repo


@pytest.fixture
def mock_job_repo():
    """Mock job repository"""
    repo = Mock()
    return repo


@pytest.fixture
def mock_storage():
    """Mock S3 storage client"""
    storage = Mock()
    storage.bucket_name = "test-bucket"
    return storage


@pytest.fixture
def mock_transformer():
    """Mock video transformer"""
    transformer = Mock()
    transformer.replace_audio.return_value = {
        "output_file": "/tmp/output.mp4",
        "file_size": 1000000,
        "audio_duration": 180,
        "video_duration": 200,
    }
    return transformer


@pytest.fixture
def audio_replacement_service(mock_db, mock_video_repo, mock_music_repo, mock_job_repo, mock_storage, mock_transformer):
    """Create audio replacement service with mocked dependencies"""
    with patch("src.services.audio_replacement.audio_replacement_service.VideoRepository", return_value=mock_video_repo), \
         patch("src.services.audio_replacement.audio_replacement_service.MusicRepository", return_value=mock_music_repo), \
         patch("src.services.audio_replacement.audio_replacement_service.JobRepository", return_value=mock_job_repo), \
         patch("src.services.audio_replacement.audio_replacement_service.S3StorageClient", return_value=mock_storage), \
         patch("src.services.audio_replacement.audio_replacement_service.VideoTransformer", return_value=mock_transformer):
        service = AudioReplacementService(mock_db)
        service.video_repo = mock_video_repo
        service.music_repo = mock_music_repo
        service.job_repo = mock_job_repo
        service.storage = mock_storage
        service.transformer = mock_transformer
        return service


def test_replace_audio_for_video_success(audio_replacement_service, mock_video_repo, mock_music_repo, mock_job_repo, mock_storage, mock_transformer):
    """Test successful audio replacement for single video"""
    # Setup mocks
    video = Video(
        id="video-1",
        channel_id="channel-1",
        download_url="s3://bucket/video.mp4",
        music_replaced=False,
    )
    music = Music(
        id="music-1",
        file_path="s3://bucket/music.mp3",
    )
    job = Mock()
    job.id = "job-1"
    
    mock_video_repo.get_by_id.return_value = video
    mock_music_repo.get_by_id.return_value = music
    mock_job_repo.create.return_value = job
    mock_storage.upload_file.return_value = "s3://bucket/output.mp4"
    
    with patch.object(audio_replacement_service, "_download_file_from_s3"), \
         patch("tempfile.NamedTemporaryFile") as mock_temp:
        # Mock temporary files
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test.mp4"
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp.return_value = mock_temp_file
        
        result = audio_replacement_service.replace_audio_for_video(
            video_id="video-1",
            music_id="music-1",
        )
        
        assert result["video_id"] == "video-1"
        assert result["music_id"] == "music-1"
        assert video.music_replaced is True
        assert video.music_track_id == "music-1"


def test_replace_audio_video_not_found(audio_replacement_service, mock_video_repo):
    """Test audio replacement with non-existent video"""
    mock_video_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundError):
        audio_replacement_service.replace_audio_for_video(
            video_id="nonexistent",
            music_id="music-1",
        )


def test_replace_audio_music_not_found(audio_replacement_service, mock_video_repo, mock_music_repo):
    """Test audio replacement with non-existent music"""
    video = Video(id="video-1", channel_id="channel-1", download_url="s3://bucket/video.mp4")
    mock_video_repo.get_by_id.return_value = video
    mock_music_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundError):
        audio_replacement_service.replace_audio_for_video(
            video_id="video-1",
            music_id="nonexistent",
        )


def test_replace_audio_batch(audio_replacement_service):
    """Test batch audio replacement"""
    with patch.object(audio_replacement_service, "replace_audio_for_video") as mock_replace:
        mock_replace.side_effect = [
            {"video_id": "video-1", "music_id": "music-1"},
            ProcessingError("Failed"),
            {"video_id": "video-3", "music_id": "music-1"},
        ]
        
        result = audio_replacement_service.replace_audio_batch(
            video_ids=["video-1", "video-2", "video-3"],
            music_id="music-1",
        )
        
        assert result["total"] == 3
        assert len(result["success"]) == 2
        assert len(result["failed"]) == 1


def test_replace_audio_for_channel(audio_replacement_service, mock_video_repo):
    """Test audio replacement for channel"""
    videos = [
        Video(id="video-1", channel_id="channel-1", download_url="s3://bucket/v1.mp4", music_replaced=False),
        Video(id="video-2", channel_id="channel-1", download_url="s3://bucket/v2.mp4", music_replaced=False),
        Video(id="video-3", channel_id="channel-1", download_url=None, music_replaced=False),  # No file
    ]
    mock_video_repo.get_by_channel_id.return_value = videos
    
    with patch.object(audio_replacement_service, "replace_audio_batch") as mock_batch:
        mock_batch.return_value = {"success": [], "failed": [], "total": 2}
        
        result = audio_replacement_service.replace_audio_for_channel(
            channel_id="channel-1",
            music_id="music-1",
        )
        
        assert result["total"] == 2
        mock_batch.assert_called_once_with(["video-1", "video-2"], "music-1", normalize=True, match_volume=False, audio_bitrate=None, audio_sample_rate=None, loop_audio=True)
