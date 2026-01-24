"""
Unit tests for configuration loading
"""

import pytest
import json

from src.database import Base, SessionLocal
from src.models import SystemConfiguration
from src.repositories import ConfigRepository
from src.services.config_service import ConfigService


@pytest.fixture
def db_session():
    """Create test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_config_service_get_from_database(db_session):
    """Test ConfigService.get loads from database"""
    # Set value in database
    config_repo = ConfigRepository(db_session)
    config_repo.set("test_key", "test_value", description="Test")
    
    # Get via service
    config_service = ConfigService(db_session)
    value = config_service.get("test_key")
    
    assert value == "test_value"


def test_config_service_get_with_default(db_session):
    """Test ConfigService.get returns default when key not found"""
    config_service = ConfigService(db_session)
    value = config_service.get("non_existent_key", default="default_value")
    
    assert value == "default_value"


def test_config_service_set_default_configs(db_session):
    """Test ConfigService.set_default_configs"""
    config_service = ConfigService(db_session)
    config_service.set_default_configs()
    
    # Verify defaults are set
    assert config_service.get("default_posting_frequency") == "daily"
    assert config_service.get("default_min_resolution") == "720p"
    assert config_service.get("max_concurrent_jobs") == 5
    assert config_service.get("default_retry_attempts") == 3


def test_config_repository_json_value(db_session):
    """Test ConfigRepository with JSON values"""
    repo = ConfigRepository(db_session)
    
    # Set complex JSON value
    complex_value = {
        "nested": {
            "array": [1, 2, 3],
            "string": "test"
        }
    }
    repo.set("complex_key", complex_value)
    
    # Get and verify
    retrieved = repo.get("complex_key")
    assert retrieved == complex_value


def test_config_repository_update_existing(db_session):
    """Test ConfigRepository updates existing key"""
    repo = ConfigRepository(db_session)
    
    # Set initial value
    repo.set("update_key", "initial_value")
    
    # Update value
    repo.set("update_key", "updated_value")
    
    # Verify update
    value = repo.get("update_key")
    assert value == "updated_value"
