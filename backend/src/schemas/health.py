"""
Health check response schemas
"""

from datetime import datetime
from typing import Dict, Literal

from pydantic import BaseModel, Field


class ComponentCheck(BaseModel):
    """Individual component health check result"""

    status: Literal["ok", "error"] = Field(..., description="Component status")
    message: str = Field(..., description="Status message")


class HealthCheckResponse(BaseModel):
    """Health check response schema"""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., description="Overall health status"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(default="1.0.0", description="API version")
    checks: Dict[str, ComponentCheck] = Field(..., description="Individual component checks")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-01-23T10:00:00Z",
                "version": "1.0.0",
                "checks": {
                    "database": {"status": "ok", "message": "Database connection successful"},
                    "github_actions": {"status": "ok", "message": "GitHub Actions environment detected"},
                    "dependencies": {"status": "ok", "message": "All required dependencies available"},
                    "configuration": {"status": "ok", "message": "Configuration loaded successfully"},
                },
            }
        }
