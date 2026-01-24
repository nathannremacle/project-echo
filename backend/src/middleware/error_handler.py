"""
Error handling middleware for FastAPI
Provides standardized error responses
"""

import uuid
from datetime import datetime
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from src.utils.exceptions import ProjectEchoException
from src.utils.logging import get_logger

logger = get_logger(__name__)


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Create standardized error response"""
    if request_id is None:
        request_id = str(uuid.uuid4())

    error_response = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "requestId": request_id,
        }
    }

    return JSONResponse(
        status_code=status_code,
        content=error_response,
    )


async def project_echo_exception_handler(request: Request, exc: ProjectEchoException) -> JSONResponse:
    """Handle ProjectEchoException"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log error
    logger.error(
        f"ProjectEchoException: {exc.message}",
        extra={
            "context": {
                "code": exc.code,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )

    # Map exception codes to HTTP status codes
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
        "FORBIDDEN": status.HTTP_403_FORBIDDEN,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "EXTERNAL_API_ERROR": status.HTTP_502_BAD_GATEWAY,
        "PROCESSING_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "CONFIGURATION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    http_status = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=http_status,
        details=exc.details,
        request_id=request_id,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log validation error
    logger.warning(
        "Request validation failed",
        extra={
            "context": {
                "errors": exc.errors(),
                "request_id": request_id,
            }
        },
    )

    return create_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"validation_errors": exc.errors()},
        request_id=request_id,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log unexpected error
    logger.exception(
        f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        extra={
            "context": {
                "exception_type": type(exc).__name__,
                "request_id": request_id,
            }
        },
    )

    return create_error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


def setup_error_handlers(app) -> None:
    """Setup error handlers for FastAPI app"""
    app.add_exception_handler(ProjectEchoException, project_echo_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
