"""
Custom exception classes for Project Echo
Domain-specific exceptions for better error handling
"""


class ProjectEchoException(Exception):
    """Base exception for Project Echo"""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ProjectEchoException):
    """Validation error"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(ProjectEchoException):
    """Resource not found error"""

    def __init__(self, message: str, resource_type: str | None = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(message, code="NOT_FOUND", details=details)


class UnauthorizedError(ProjectEchoException):
    """Unauthorized access error"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="UNAUTHORIZED")


class AuthenticationError(ProjectEchoException):
    """Authentication error (OAuth, token refresh, etc.)"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class ForbiddenError(ProjectEchoException):
    """Forbidden access error"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, code="FORBIDDEN")


class RateLimitError(ProjectEchoException):
    """Rate limit exceeded error"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", details=details)


class ExternalAPIError(ProjectEchoException):
    """External API error"""

    def __init__(self, message: str, service: str | None = None, details: dict | None = None):
        error_details = details or {}
        if service:
            error_details["service"] = service
        super().__init__(message, code="EXTERNAL_API_ERROR", details=error_details)


class ProcessingError(ProjectEchoException):
    """Video processing error"""

    def __init__(self, message: str, job_id: str | None = None, details: dict | None = None):
        error_details = details or {}
        if job_id:
            error_details["job_id"] = job_id
        super().__init__(message, code="PROCESSING_ERROR", details=error_details)


class DatabaseError(ProjectEchoException):
    """Database operation error"""

    def __init__(self, message: str, operation: str | None = None, details: dict | None = None):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        super().__init__(message, code="DATABASE_ERROR", details=error_details)


class ConfigurationError(ProjectEchoException):
    """Configuration error"""

    def __init__(self, message: str, config_key: str | None = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)
