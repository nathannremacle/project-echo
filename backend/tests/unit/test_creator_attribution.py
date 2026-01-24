"""
Unit tests for Creator Attribution service
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.creator_attribution.creator_attribution_service import CreatorAttributionService
from src.models.video import Video
from src.utils.exceptions import NotFoundError


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
def creator_attribution_service(mock_db, mock_video_repo):
    """Create Creator Attribution service with mocked dependencies"""
    with patch("src.services.creator_attribution.creator_attribution_service.VideoRepository", return_value=mock_video_repo):
        service = CreatorAttributionService(mock_db)
        service.video_repo = mock_video_repo
        return service


def test_get_all_creators(creator_attribution_service, mock_db):
    """Test getting all creators"""
    # Mock query result
    mock_result = [("Creator 1", 5), ("Creator 2", 3)]
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = mock_result
    
    mock_db.query.return_value = mock_query
    
    creators = creator_attribution_service.get_all_creators()
    
    assert len(creators) == 2
    assert creators[0]["name"] == "Creator 1"
    assert creators[0]["video_count"] == 5


def test_get_videos_by_creator(creator_attribution_service, mock_db):
    """Test getting videos by creator"""
    videos = [
        Video(id="1", source_creator="Creator 1", source_title="Video 1"),
        Video(id="2", source_creator="Creator 1", source_title="Video 2"),
    ]
    
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = videos
    
    mock_count_query = Mock()
    mock_count_query.filter.return_value = mock_count_query
    mock_count_query.scalar.return_value = 2
    
    mock_db.query.side_effect = [mock_query, mock_count_query]
    
    result = creator_attribution_service.get_videos_by_creator("Creator 1", limit=10, offset=0)
    
    assert result["creator"] == "Creator 1"
    assert len(result["videos"]) == 2
    assert result["total"] == 2


def test_search_creators(creator_attribution_service, mock_db):
    """Test searching creators"""
    mock_result = [("Creator 1", 5)]
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_result
    
    mock_db.query.return_value = mock_query
    
    creators = creator_attribution_service.search_creators("Creator", limit=50)
    
    assert len(creators) == 1
    assert creators[0]["name"] == "Creator 1"


def test_attribute_video(creator_attribution_service, mock_video_repo):
    """Test attributing a video"""
    video = Video(id="1", source_creator=None, source_title="Video 1")
    mock_video_repo.get_by_id.return_value = video
    mock_video_repo.update.return_value = video
    
    result = creator_attribution_service.attribute_video("1", "Creator 1")
    
    assert result.source_creator == "Creator 1"
    mock_video_repo.update.assert_called_once()


def test_attribute_video_not_found(creator_attribution_service, mock_video_repo):
    """Test attributing a non-existent video"""
    mock_video_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundError):
        creator_attribution_service.attribute_video("1", "Creator 1")


def test_bulk_attribute_videos(creator_attribution_service, mock_video_repo):
    """Test bulk attributing videos"""
    videos = [
        Video(id="1", source_creator=None, source_title="Video 1"),
        Video(id="2", source_creator=None, source_title="Video 2"),
    ]
    
    mock_video_repo.get_by_id.side_effect = videos
    mock_video_repo.update.side_effect = videos
    
    result = creator_attribution_service.bulk_attribute_videos(["1", "2"], "Creator 1")
    
    assert len(result["updated"]) == 2
    assert len(result["failed"]) == 0
    assert result["total"] == 2


def test_get_attribution_template_variable(creator_attribution_service, mock_video_repo):
    """Test getting attribution template variable"""
    video = Video(id="1", source_creator="Creator 1", source_title="Video 1")
    mock_video_repo.get_by_id.return_value = video
    
    attribution = creator_attribution_service.get_attribution_template_variable("1")
    
    assert attribution == "Original video by: Creator 1"


def test_get_attribution_template_variable_no_creator(creator_attribution_service, mock_video_repo):
    """Test getting attribution template variable when no creator"""
    video = Video(id="1", source_creator=None, source_title="Video 1")
    mock_video_repo.get_by_id.return_value = video
    
    attribution = creator_attribution_service.get_attribution_template_variable("1")
    
    assert attribution == ""
