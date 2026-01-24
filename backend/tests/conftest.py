"""
Pytest configuration and fixtures
"""

import pytest
from unittest.mock import Mock, patch

from src.config import Settings


@pytest.fixture
def test_settings():
    """Create test settings instance"""
    return Settings(
        APP_ENV="development",
        APP_DEBUG=True,
        DATABASE_URL="sqlite:///./test.db",
        LOG_LEVEL="DEBUG",
        LOG_FORMAT="text",
    )


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return Mock()


@pytest.fixture
def sample_request_id():
    """Sample request ID for testing"""
    return "test-request-id-123"
