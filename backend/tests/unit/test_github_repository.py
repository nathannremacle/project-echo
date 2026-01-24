"""
Unit tests for GitHub repository service
"""

import pytest
from unittest.mock import patch, MagicMock

from src.services.orchestration.github_repository_service import GitHubRepositoryService
from src.models.channel import Channel
from src.utils.exceptions import NotFoundError, ValidationError


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
    import json
    
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        is_active=True,
        api_credentials_encrypted="encrypted_creds",
        posting_schedule=json.dumps({}),
        content_filters=json.dumps({}),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@patch("src.services.orchestration.github_repository_service.Github")
@patch("src.services.orchestration.github_repository_service.settings")
def test_create_channel_repository(db_session, test_channel, mock_settings, mock_github_class):
    """Test creating GitHub repository for channel"""
    mock_settings.GITHUB_TOKEN = "test_token"
    
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_repo.html_url = "https://github.com/user/project-echo-channel-test-channel"
    mock_repo.id = 12345
    mock_repo.clone_url = "https://github.com/user/project-echo-channel-test-channel.git"
    
    # Mock get_repo to raise 404 (repo doesn't exist)
    def get_repo_side_effect(name):
        from github.GithubException import GithubException
        exc = GithubException(404, {"message": "Not Found"}, None)
        raise exc
    
    mock_user.get_repo.side_effect = get_repo_side_effect
    mock_user.create_repo.return_value = mock_repo
    
    mock_github = MagicMock()
    mock_github.get_user.return_value = mock_user
    mock_github_class.return_value = mock_github
    
    service = GitHubRepositoryService(db_session)
    
    result = service.create_channel_repository(test_channel.id)
    
    assert result["repository_name"] == "project-echo-channel-test-channel"
    assert "repository_url" in result
    mock_user.create_repo.assert_called_once()


@patch("src.services.orchestration.github_repository_service.Github")
@patch("src.services.orchestration.github_repository_service.settings")
def test_create_channel_repository_duplicate(db_session, test_channel, mock_settings, mock_github_class):
    """Test creating repository that already exists"""
    mock_settings.GITHUB_TOKEN = "test_token"
    
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_user.get_repo.return_value = mock_repo  # Repo exists
    
    mock_github = MagicMock()
    mock_github.get_user.return_value = mock_user
    mock_github_class.return_value = mock_github
    
    service = GitHubRepositoryService(db_session)
    
    with pytest.raises(ValidationError) as exc_info:
        service.create_channel_repository(test_channel.id)
    
    assert "already exists" in str(exc_info.value)


@patch("src.services.orchestration.github_repository_service.Github")
@patch("src.services.orchestration.github_repository_service.settings")
def test_trigger_workflow(db_session, test_channel, mock_settings, mock_github_class):
    """Test triggering workflow in channel repository"""
    mock_settings.GITHUB_TOKEN = "test_token"
    
    test_channel.github_repo_url = "https://github.com/user/project-echo-channel-test"
    db_session.commit()
    
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_user.get_repo.return_value = mock_repo
    
    mock_github = MagicMock()
    mock_github.get_user.return_value = mock_user
    mock_github_class.return_value = mock_github
    
    service = GitHubRepositoryService(db_session)
    
    result = service.trigger_workflow(
        test_channel.id,
        workflow_type="process-video",
        client_payload={"video_id": "video-123"},
    )
    
    assert result["triggered"] is True
    mock_repo.create_repository_dispatch.assert_called_once_with(
        event_type="process-video",
        client_payload={"video_id": "video-123"},
    )


@patch("src.services.orchestration.github_repository_service.Github")
@patch("src.services.orchestration.github_repository_service.settings")
def test_get_repository_info(db_session, test_channel, mock_settings, mock_github_class):
    """Test getting repository information"""
    mock_settings.GITHUB_TOKEN = "test_token"
    
    test_channel.github_repo_url = "https://github.com/user/project-echo-channel-test"
    db_session.commit()
    
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_repo.html_url = "https://github.com/user/project-echo-channel-test"
    mock_repo.id = 12345
    mock_repo.private = True
    mock_repo.default_branch = "main"
    mock_user.get_repo.return_value = mock_repo
    
    mock_github = MagicMock()
    mock_github.get_user.return_value = mock_user
    mock_github_class.return_value = mock_github
    
    service = GitHubRepositoryService(db_session)
    
    info = service.get_repository_info(test_channel.id)
    
    assert info["exists"] is True
    assert info["repository_name"] == "project-echo-channel-test"
    assert info["private"] is True


def test_get_repository_info_no_repo(db_session, test_channel):
    """Test getting repository info when channel has no repo"""
    with patch("src.services.orchestration.github_repository_service.Github"), \
         patch("src.services.orchestration.github_repository_service.settings") as mock_settings:
        mock_settings.GITHUB_TOKEN = "test_token"
        
        service = GitHubRepositoryService(db_session)
        
        info = service.get_repository_info(test_channel.id)
        
        assert info["repository_url"] is None
        assert info["exists"] is False
