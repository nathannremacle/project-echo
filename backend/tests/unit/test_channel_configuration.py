"""
Unit tests for channel configuration service
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from src.services.orchestration.channel_configuration_service import (
    ChannelConfigurationService,
    DEFAULT_POSTING_SCHEDULE,
    DEFAULT_CONTENT_FILTERS,
    DEFAULT_METADATA_TEMPLATE,
)
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
def test_api_credentials():
    """Test API credentials"""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    }


@patch("src.services.orchestration.channel_configuration_service.encrypt_dict")
def test_create_channel_with_defaults(db_session, test_api_credentials, mock_encrypt):
    """Test creating channel with default configurations"""
    mock_encrypt.return_value = "encrypted_creds"
    
    service = ChannelConfigurationService(db_session)
    
    channel = service.create_channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        api_credentials=test_api_credentials,
    )
    
    assert channel.id is not None
    assert channel.name == "Test Channel"
    assert channel.youtube_channel_id == "UC123"
    
    # Verify defaults were applied
    posting_schedule = json.loads(channel.posting_schedule)
    assert posting_schedule["frequency"] == "daily"
    
    content_filters = json.loads(channel.content_filters)
    assert content_filters["min_resolution"] == "720p"
    
    metadata_template = json.loads(channel.metadata_template)
    assert "title" in metadata_template


def test_create_channel_duplicate_youtube_id(db_session, test_api_credentials):
    """Test creating channel with duplicate YouTube channel ID"""
    service = ChannelConfigurationService(db_session)
    
    # Create first channel
    service.create_channel(
        name="Channel 1",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        api_credentials=test_api_credentials,
    )
    
    # Try to create duplicate
    with pytest.raises(ValidationError) as exc_info:
        service.create_channel(
            name="Channel 2",
            youtube_channel_id="UC123",  # Duplicate
            youtube_channel_url="https://youtube.com/channel/UC123",
            api_credentials=test_api_credentials,
        )
    
    assert "already exists" in str(exc_info.value)


def test_update_channel_configuration(db_session, test_api_credentials):
    """Test updating channel configuration"""
    service = ChannelConfigurationService(db_session)
    
    # Create channel
    channel = service.create_channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        api_credentials=test_api_credentials,
    )
    
    # Update configuration
    new_schedule = {
        "frequency": "weekly",
        "preferred_times": ["18:00"],
        "timezone": "UTC",
        "days_of_week": [0, 6],  # Weekend only
    }
    
    updated = service.update_channel_configuration(
        channel_id=channel.id,
        posting_schedule=new_schedule,
        is_active=True,
    )
    
    assert updated.is_active is True
    schedule = json.loads(updated.posting_schedule)
    assert schedule["frequency"] == "weekly"


def test_validate_channel_configuration(db_session, test_api_credentials):
    """Test validating channel configuration"""
    service = ChannelConfigurationService(db_session)
    
    # Create channel
    channel = service.create_channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        api_credentials=test_api_credentials,
    )
    
    # Validate configuration
    with patch("src.services.orchestration.channel_configuration_service.YouTubeAuthService.validate_authentication") as mock_validate:
        mock_validate.return_value = True
        
        results = service.validate_channel_configuration(channel.id)
        
        assert results["valid"] is True
        assert len(results["errors"]) == 0


def test_export_channel_configuration(db_session, test_api_credentials):
    """Test exporting channel configuration"""
    service = ChannelConfigurationService(db_session)
    
    # Create channel
    channel = service.create_channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        api_credentials=test_api_credentials,
    )
    
    # Export configuration
    with patch("src.services.orchestration.channel_configuration_service.YouTubeAuthService.get_credentials") as mock_get_creds:
        mock_get_creds.return_value = test_api_credentials
        
        config = service.export_channel_configuration(channel.id, include_credentials=True)
        
        assert config["name"] == "Test Channel"
        assert config["youtube_channel_id"] == "UC123"
        assert config["api_credentials"] == test_api_credentials
        assert "posting_schedule" in config


def test_import_channel_configuration(db_session, test_api_credentials):
    """Test importing channel configuration"""
    service = ChannelConfigurationService(db_session)
    
    config = {
        "name": "Imported Channel",
        "youtube_channel_id": "UC456",
        "youtube_channel_url": "https://youtube.com/channel/UC456",
        "api_credentials": test_api_credentials,
        "posting_schedule": DEFAULT_POSTING_SCHEDULE,
        "content_filters": DEFAULT_CONTENT_FILTERS,
        "metadata_template": DEFAULT_METADATA_TEMPLATE,
        "is_active": False,
    }
    
    with patch("src.services.orchestration.channel_configuration_service.encrypt_dict") as mock_encrypt:
        mock_encrypt.return_value = "encrypted_creds"
        
        channel = service.import_channel_configuration(config)
        
        assert channel.name == "Imported Channel"
        assert channel.youtube_channel_id == "UC456"


def test_get_default_configuration(db_session):
    """Test getting default configuration"""
    service = ChannelConfigurationService(db_session)
    
    defaults = service.get_default_configuration()
    
    assert "posting_schedule" in defaults
    assert "content_filters" in defaults
    assert "metadata_template" in defaults
    assert defaults["posting_schedule"]["frequency"] == "daily"


def test_validate_posting_schedule_invalid(db_session):
    """Test validating invalid posting schedule"""
    service = ChannelConfigurationService(db_session)
    
    with pytest.raises(ValidationError):
        service._validate_posting_schedule({"frequency": "invalid"})


def test_validate_content_filters_invalid(db_session):
    """Test validating invalid content filters"""
    service = ChannelConfigurationService(db_session)
    
    with pytest.raises(ValidationError):
        service._validate_content_filters({"min_resolution": "480p"})


def test_validate_metadata_template_invalid(db_session):
    """Test validating invalid metadata template"""
    service = ChannelConfigurationService(db_session)
    
    with pytest.raises(ValidationError):
        service._validate_metadata_template({})  # Missing title
