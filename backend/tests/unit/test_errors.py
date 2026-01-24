"""
Unit tests for custom exceptions
"""

import pytest

from src.utils.exceptions import (
    ProjectEchoException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    ExternalAPIError,
    ProcessingError,
    DatabaseError,
    ConfigurationError,
)


def test_project_echo_exception():
    """Test base ProjectEchoException"""
    exc = ProjectEchoException("Test message", code="TEST_CODE")
    assert str(exc) == "Test message"
    assert exc.code == "TEST_CODE"
    assert exc.details == {}


def test_validation_error():
    """Test ValidationError"""
    exc = ValidationError("Invalid input", details={"field": "name"})
    assert exc.code == "VALIDATION_ERROR"
    assert exc.details == {"field": "name"}


def test_not_found_error():
    """Test NotFoundError"""
    exc = NotFoundError("Resource not found", resource_type="channel")
    assert exc.code == "NOT_FOUND"
    assert exc.details == {"resource_type": "channel"}


def test_unauthorized_error():
    """Test UnauthorizedError"""
    exc = UnauthorizedError()
    assert exc.code == "UNAUTHORIZED"
    assert exc.message == "Authentication required"


def test_forbidden_error():
    """Test ForbiddenError"""
    exc = ForbiddenError()
    assert exc.code == "FORBIDDEN"
    assert exc.message == "Insufficient permissions"


def test_rate_limit_error():
    """Test RateLimitError"""
    exc = RateLimitError(retry_after=60)
    assert exc.code == "RATE_LIMIT_EXCEEDED"
    assert exc.details == {"retry_after": 60}


def test_external_api_error():
    """Test ExternalAPIError"""
    exc = ExternalAPIError("API error", service="youtube")
    assert exc.code == "EXTERNAL_API_ERROR"
    assert exc.details == {"service": "youtube"}


def test_processing_error():
    """Test ProcessingError"""
    exc = ProcessingError("Processing failed", job_id="job-123")
    assert exc.code == "PROCESSING_ERROR"
    assert exc.details == {"job_id": "job-123"}


def test_database_error():
    """Test DatabaseError"""
    exc = DatabaseError("DB error", operation="select")
    assert exc.code == "DATABASE_ERROR"
    assert exc.details == {"operation": "select"}


def test_configuration_error():
    """Test ConfigurationError"""
    exc = ConfigurationError("Config error", config_key="DATABASE_URL")
    assert exc.code == "CONFIGURATION_ERROR"
    assert exc.details == {"config_key": "DATABASE_URL"}
