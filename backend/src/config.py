"""
Configuration management for Project Echo backend
Loads configuration from environment variables and config files
"""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Project Echo API"
    APP_ENV: str = Field(default="development", description="Environment: development, staging, production")
    APP_DEBUG: bool = Field(default=True, description="Debug mode")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./data/project_echo.db",
        description="Database connection URL",
    )

    # YouTube API (for validation, not per-channel)
    YOUTUBE_API_CLIENT_ID: str = Field(default="", description="YouTube API OAuth client ID")
    YOUTUBE_API_CLIENT_SECRET: str = Field(default="", description="YouTube API OAuth client secret")

    # Cloud Storage (AWS S3 or DigitalOcean Spaces - S3-compatible)
    AWS_ACCESS_KEY_ID: str = Field(default="", description="S3/Spaces access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="S3/Spaces secret access key")
    AWS_REGION: str = Field(default="us-east-1", description="S3/Spaces region")
    AWS_S3_BUCKET: str = Field(default="project-echo-videos-dev", description="S3/Spaces bucket name")
    S3_ENDPOINT_URL: str = Field(default="", description="S3 endpoint URL (for DigitalOcean Spaces: region.digitaloceanspaces.com)")

    # GitHub API (for orchestration)
    GITHUB_TOKEN: str = Field(default="", description="GitHub personal access token")

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(default="", description="JWT secret key for token signing")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="JWT token expiration in hours")

    # Encryption
    ENCRYPTION_KEY: str = Field(default="", description="Encryption key for credential storage (32 bytes)")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = Field(default="json", description="Log format: json, text")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, v):
        """Validate APP_ENV value"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate LOG_LEVEL value"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV == "development"

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV == "production"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
