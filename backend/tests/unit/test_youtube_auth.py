"""
Unit tests for YouTube authentication service
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

from src.services.youtube.auth_service import YouTubeAuthService, YOUTUBE_SCOPES
from src.models.channel import Channel
from src.utils.exceptions import AuthenticationError, NotFoundError


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
        api_credentials_encrypted="",  # Will be set in tests
        posting_schedule=json.dumps({}),
        content_filters=json.dumps({}),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


def test_get_oauth_flow(db_session):
    """Test creating OAuth flow"""
    service = YouTubeAuthService(db_session)
    
    flow = service.get_oauth_flow(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/callback",
    )
    
    assert flow is not None
    assert flow.redirect_uri == "http://localhost:8000/callback"


def test_get_authorization_url(db_session):
    """Test getting authorization URL"""
    service = YouTubeAuthService(db_session)
    
    url = service.get_authorization_url(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/callback",
        state="test_state",
    )
    
    assert url is not None
    assert "accounts.google.com" in url
    assert "test_state" in url or "state=" in url


@patch("src.services.youtube.auth_service.Flow")
def test_exchange_code_for_credentials(db_session, mock_flow_class):
    """Test exchanging authorization code for credentials"""
    # Mock flow and credentials
    mock_credentials = MagicMock()
    mock_credentials.refresh_token = "test_refresh_token"
    mock_credentials.token = "test_access_token"
    mock_credentials.token_uri = "https://oauth2.googleapis.com/token"
    mock_credentials.client_id = "test_client_id"
    mock_credentials.client_secret = "test_client_secret"
    mock_credentials.scopes = YOUTUBE_SCOPES
    mock_credentials.expiry = None
    
    mock_flow = MagicMock()
    mock_flow.credentials = mock_credentials
    mock_flow_class.from_client_config.return_value = mock_flow
    
    service = YouTubeAuthService(db_session)
    
    creds = service.exchange_code_for_credentials(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/callback",
        authorization_code="test_code",
    )
    
    assert creds is not None
    assert creds["refresh_token"] == "test_refresh_token"
    assert creds["token"] == "test_access_token"
    assert creds["client_id"] == "test_client_id"
    mock_flow.fetch_token.assert_called_once_with(code="test_code")


@patch("src.services.youtube.auth_service.encrypt_dict")
def test_store_credentials(db_session, test_channel, mock_encrypt):
    """Test storing credentials"""
    mock_encrypt.return_value = "encrypted_creds"
    
    service = YouTubeAuthService(db_session)
    
    credentials = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    }
    
    service.store_credentials(test_channel.id, credentials)
    
    mock_encrypt.assert_called_once_with(credentials)
    db_session.refresh(test_channel)
    assert test_channel.api_credentials_encrypted == "encrypted_creds"


@patch("src.services.youtube.auth_service.decrypt_dict")
def test_get_credentials(db_session, test_channel, mock_decrypt):
    """Test getting credentials"""
    test_channel.api_credentials_encrypted = "encrypted_creds"
    db_session.commit()
    
    mock_decrypt.return_value = {
        "client_id": "test_client_id",
        "refresh_token": "test_refresh_token",
    }
    
    service = YouTubeAuthService(db_session)
    
    creds = service.get_credentials(test_channel.id)
    
    assert creds is not None
    assert creds["client_id"] == "test_client_id"
    mock_decrypt.assert_called_once_with("encrypted_creds")


def test_get_credentials_not_found(db_session, test_channel):
    """Test getting credentials when channel has none"""
    service = YouTubeAuthService(db_session)
    
    creds = service.get_credentials(test_channel.id)
    
    assert creds is None


@patch("src.services.youtube.auth_service.decrypt_dict")
@patch("src.services.youtube.auth_service.Credentials")
@patch("src.services.youtube.auth_service.Request")
def test_get_authenticated_credentials_not_expired(
    db_session, test_channel, mock_request, mock_credentials_class, mock_decrypt
):
    """Test getting authenticated credentials when token is not expired"""
    mock_decrypt.return_value = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "token": "test_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": YOUTUBE_SCOPES,
        "expiry": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
    }
    
    mock_creds = MagicMock()
    mock_creds.expired = False
    mock_creds.expiry = datetime.utcnow() + timedelta(hours=2)
    mock_credentials_class.return_value = mock_creds
    
    test_channel.api_credentials_encrypted = "encrypted"
    db_session.commit()
    
    service = YouTubeAuthService(db_session)
    
    creds = service.get_authenticated_credentials(test_channel.id)
    
    assert creds is not None
    assert creds == mock_creds
    mock_creds.refresh.assert_not_called()  # Should not refresh if not expired


@patch("src.services.youtube.auth_service.decrypt_dict")
@patch("src.services.youtube.auth_service.Credentials")
@patch("src.services.youtube.auth_service.Request")
@patch("src.services.youtube.auth_service.encrypt_dict")
def test_get_authenticated_credentials_refresh(
    db_session, test_channel, mock_encrypt, mock_request, mock_credentials_class, mock_decrypt
):
    """Test getting authenticated credentials when token is expired and needs refresh"""
    expiry = datetime.utcnow() - timedelta(hours=1)
    mock_decrypt.return_value = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "token": "old_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": YOUTUBE_SCOPES,
        "expiry": expiry.isoformat(),
    }
    
    mock_creds = MagicMock()
    mock_creds.expired = True
    mock_creds.expiry = expiry
    mock_creds.token = "new_token"
    mock_creds.expiry = datetime.utcnow() + timedelta(hours=1)
    mock_credentials_class.return_value = mock_creds
    
    test_channel.api_credentials_encrypted = "encrypted"
    db_session.commit()
    
    service = YouTubeAuthService(db_session)
    
    creds = service.get_authenticated_credentials(test_channel.id)
    
    assert creds is not None
    mock_creds.refresh.assert_called_once()  # Should refresh if expired
    mock_encrypt.assert_called_once()  # Should update stored credentials


@patch("src.services.youtube.auth_service.build")
@patch("src.services.youtube.auth_service.YouTubeAuthService.get_authenticated_credentials")
def test_validate_authentication_success(db_session, test_channel, mock_get_creds, mock_build):
    """Test validating authentication successfully"""
    mock_creds = MagicMock()
    mock_get_creds.return_value = mock_creds
    
    mock_youtube = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = {"items": [{"id": "test"}]}
    mock_youtube.channels.return_value.list.return_value = mock_request
    mock_build.return_value = mock_youtube
    
    service = YouTubeAuthService(db_session)
    
    result = service.validate_authentication(test_channel.id)
    
    assert result is True


@patch("src.services.youtube.auth_service.build")
@patch("src.services.youtube.auth_service.YouTubeAuthService.get_authenticated_credentials")
def test_validate_authentication_failed(db_session, test_channel, mock_get_creds, mock_build):
    """Test validating authentication when it fails"""
    from googleapiclient.errors import HttpError
    
    mock_creds = MagicMock()
    mock_get_creds.return_value = mock_creds
    
    mock_youtube = MagicMock()
    mock_request = MagicMock()
    error_resp = MagicMock()
    error_resp.status = 401
    mock_request.execute.side_effect = HttpError(error_resp, b"Unauthorized")
    mock_youtube.channels.return_value.list.return_value = mock_request
    mock_build.return_value = mock_youtube
    
    service = YouTubeAuthService(db_session)
    
    result = service.validate_authentication(test_channel.id)
    
    assert result is False
