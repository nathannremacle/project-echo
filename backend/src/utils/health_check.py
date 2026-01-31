"""
Health check utilities - verify system components
"""

import os
from datetime import datetime
from typing import Dict, Tuple

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.database import SessionLocal
from src.schemas.health import ComponentCheck, HealthCheckResponse
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Required Python dependencies to check
REQUIRED_DEPENDENCIES = [
    "fastapi",
    "sqlalchemy",
    "pydantic",
    "uvicorn",
    "alembic",
    "googleapiclient",
    "boto3",
    "yt_dlp",
    "cv2",  # opencv-python
    "github",
    "httpx",
    "requests",
    "jose",  # python-jose
    "cryptography",
]


def check_database() -> Tuple[str, str]:
    """
    Check database connectivity
    
    Returns:
        Tuple of (status, message)
    """
    try:
        # Try to execute a simple query
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            db.commit()
        return "ok", "Database connection successful"
    except SQLAlchemyError as e:
        logger.error(f"Database check failed: {e}")
        return "error", f"Database connection failed: {str(e)}"
    except Exception as e:
        logger.error(f"Database check failed with unexpected error: {e}")
        return "error", f"Database check error: {str(e)}"


def check_github_actions() -> Tuple[str, str]:
    """
    Check if running in GitHub Actions environment
    
    Returns:
        Tuple of (status, message)
    """
    # Check for GitHub Actions environment variables
    is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
    github_workflow = os.getenv("GITHUB_WORKFLOW")
    github_repo = os.getenv("GITHUB_REPOSITORY")
    
    if is_github_actions:
        message = f"GitHub Actions environment detected (workflow: {github_workflow}, repo: {github_repo})"
        return "ok", message
    else:
        # Not an error, just informational
        return "ok", "Not running in GitHub Actions (local development mode)"


def check_dependencies() -> Tuple[str, str]:
    """
    Check if required Python dependencies are available
    
    Returns:
        Tuple of (status, message)
    """
    missing_deps = []
    
    for dep in REQUIRED_DEPENDENCIES:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        return "error", f"Missing dependencies: {', '.join(missing_deps)}"
    else:
        return "ok", f"All {len(REQUIRED_DEPENDENCIES)} required dependencies available"


def check_configuration() -> Tuple[str, str]:
    """
    Check if configuration is loaded correctly
    
    Returns:
        Tuple of (status, message)
    """
    try:
        # Critical: DATABASE_URL must be set
        if not settings.DATABASE_URL:
            return "error", "DATABASE_URL not set"
        
        # In production, JWT/ENCRYPTION are recommended but not blocking for health check
        # (returning "error" would cause 503 and container restarts on DigitalOcean)
        if settings.is_production():
            warnings = []
            if not settings.JWT_SECRET_KEY:
                warnings.append("JWT_SECRET_KEY not set")
            if not settings.ENCRYPTION_KEY:
                warnings.append("ENCRYPTION_KEY not set")
            if warnings:
                return "ok", f"Configuration loaded (warnings: {', '.join(warnings)})"
        
        return "ok", "Configuration loaded successfully"
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        return "error", f"Configuration check error: {str(e)}"


def perform_health_check() -> HealthCheckResponse:
    """
    Perform comprehensive health check
    
    Returns:
        HealthCheckResponse with status of all components
    """
    checks: Dict[str, ComponentCheck] = {}
    
    # Check database
    db_status, db_message = check_database()
    checks["database"] = ComponentCheck(status=db_status, message=db_message)
    
    # Check GitHub Actions
    gh_status, gh_message = check_github_actions()
    checks["github_actions"] = ComponentCheck(status=gh_status, message=gh_message)
    
    # Check dependencies
    deps_status, deps_message = check_dependencies()
    checks["dependencies"] = ComponentCheck(status=deps_status, message=deps_message)
    
    # Check configuration
    config_status, config_message = check_configuration()
    checks["configuration"] = ComponentCheck(status=config_status, message=config_message)
    
    # Determine overall status
    error_count = sum(1 for check in checks.values() if check.status == "error")
    if error_count == 0:
        overall_status = "healthy"
    elif error_count < len(checks):
        overall_status = "degraded"  # Some checks failed, but not all
    else:
        overall_status = "unhealthy"  # All checks failed
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        checks=checks,
    )
