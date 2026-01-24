"""
Unit tests for configuration management
"""

import pytest
from src.config import Settings, get_settings


def test_settings_defaults():
    """Test that settings have default values"""
    settings = Settings()
    assert settings.APP_NAME == "Project Echo API"
    assert settings.APP_ENV == "development"
    assert settings.APP_DEBUG is True


def test_settings_environment_validation():
    """Test that invalid APP_ENV raises error"""
    with pytest.raises(ValueError, match="APP_ENV must be one of"):
        Settings(APP_ENV="invalid")


def test_settings_log_level_validation():
    """Test that invalid LOG_LEVEL raises error"""
    with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
        Settings(LOG_LEVEL="invalid")


def test_settings_cors_origins_parsing():
    """Test that CORS_ORIGINS can be parsed from string"""
    settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:5173")
    assert len(settings.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert "http://localhost:5173" in settings.CORS_ORIGINS


def test_settings_is_development():
    """Test is_development method"""
    settings = Settings(APP_ENV="development")
    assert settings.is_development() is True
    assert settings.is_production() is False


def test_settings_is_production():
    """Test is_production method"""
    settings = Settings(APP_ENV="production")
    assert settings.is_development() is False
    assert settings.is_production() is True


def test_get_settings():
    """Test get_settings function returns Settings instance"""
    settings = get_settings()
    assert isinstance(settings, Settings)
