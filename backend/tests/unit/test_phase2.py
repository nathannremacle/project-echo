"""
Unit tests for Phase 2 service
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.phase2.phase2_service import Phase2Service
from src.models.channel import Channel
from src.models.music import Music
from src.models.video import Video
from src.utils.exceptions import NotFoundError, ValidationError


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_channel_repo():
    """Mock channel repository"""
    repo = Mock()
    return repo


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
def mock_audio_service():
    """Mock audio replacement service"""
    service = Mock()
    return service


@pytest.fixture
def phase2_service(mock_db, mock_channel_repo, mock_video_repo, mock_music_repo, mock_audio_service):
    """Create Phase 2 service with mocked dependencies"""
    with patch("src.services.phase2.phase2_service.ChannelRepository", return_value=mock_channel_repo), \
         patch("src.services.phase2.phase2_service.VideoRepository", return_value=mock_video_repo), \
         patch("src.services.phase2.phase2_service.MusicRepository", return_value=mock_music_repo), \
         patch("src.services.phase2.phase2_service.AudioReplacementService", return_value=mock_audio_service):
        service = Phase2Service(mock_db)
        service.channel_repo = mock_channel_repo
        service.video_repo = mock_video_repo
        service.music_repo = mock_music_repo
        service.audio_replacement_service = mock_audio_service
        return service


def test_activate_phase2_success(phase2_service, mock_channel_repo, mock_music_repo, mock_video_repo, mock_audio_service):
    """Test successful Phase 2 activation"""
    # Setup mocks
    channel = Channel(id="channel-1", name="Test Channel", phase2_enabled=False)
    music = Music(id="music-1", name="Test Music")
    videos = [
        Video(id="video-1", channel_id="channel-1", music_replaced=False, transformation_status="transformed"),
        Video(id="video-2", channel_id="channel-1", music_replaced=False, transformation_status="transformed"),
    ]
    
    mock_channel_repo.get_by_id.return_value = channel
    mock_channel_repo.update.return_value = channel
    mock_music_repo.get_by_id.return_value = music
    mock_video_repo.get_by_channel_id.return_value = videos
    mock_audio_service.replace_audio_batch.return_value = {
        "success": [{"video_id": "video-1"}, {"video_id": "video-2"}],
        "failed": [],
    }
    
    result = phase2_service.activate_phase2(
        channel_ids=["channel-1"],
        music_id="music-1",
    )
    
    assert len(result["activated"]) == 1
    assert result["activated"][0]["channel_id"] == "channel-1"
    assert channel.phase2_enabled is True


def test_activate_phase2_music_not_found(phase2_service, mock_music_repo):
    """Test Phase 2 activation with non-existent music"""
    mock_music_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundError):
        phase2_service.activate_phase2(
            channel_ids=["channel-1"],
            music_id="nonexistent",
        )


def test_deactivate_phase2_success(phase2_service, mock_channel_repo):
    """Test successful Phase 2 deactivation"""
    channel = Channel(id="channel-1", name="Test Channel", phase2_enabled=True)
    mock_channel_repo.get_all.return_value = [channel]
    mock_channel_repo.update.return_value = channel
    
    result = phase2_service.deactivate_phase2()
    
    assert len(result["deactivated"]) == 1
    assert channel.phase2_enabled is False


def test_get_phase2_status(phase2_service, mock_channel_repo, mock_music_repo):
    """Test getting Phase 2 status"""
    channels = [
        Channel(id="1", name="Channel 1", phase2_enabled=True, is_active=True),
        Channel(id="2", name="Channel 2", phase2_enabled=False, is_active=True),
    ]
    music_tracks = [Music(id="1"), Music(id="2")]
    
    mock_channel_repo.get_all.return_value = channels
    mock_music_repo.get_all.return_value = music_tracks
    
    status = phase2_service.get_phase2_status()
    
    assert status["phase2_enabled"] is True
    assert status["phase2_channels_count"] == 1
    assert status["total_channels"] == 2
    assert status["available_music_tracks"] == 2


def test_check_channel_readiness(phase2_service, mock_channel_repo):
    """Test channel readiness check"""
    channel = Channel(id="channel-1", name="Test Channel", is_active=True)
    mock_channel_repo.get_by_id.return_value = channel
    
    result = phase2_service.check_channel_readiness(
        channel_id="channel-1",
        min_subscribers=1000,
        min_views=10000,
    )
    
    assert result["channel_id"] == "channel-1"
    assert "ready" in result
    assert "checks" in result
