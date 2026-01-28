"""
Configuration service - manages configuration loading from multiple sources
Priority: environment variables > database > config files > defaults
"""

import json
from typing import Any, Dict, Optional
from pathlib import Path

from sqlalchemy.orm import Session

from src.repositories.config_repository import ConfigRepository
from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigService:
    """Service for managing configuration from multiple sources"""

    def __init__(self, db: Session):
        self.db = db
        self.config_repo = ConfigRepository(db)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with priority:
        1. Environment variables (via settings)
        2. Database
        3. Config files
        4. Default value
        """
        # Try environment variables first (handled by settings)
        # This is done at the settings level, so we skip here

        # Try database
        db_value = self.config_repo.get(key)
        if db_value is not None:
            logger.debug(f"Configuration {key} loaded from database")
            return db_value

        # Try config files (future implementation)
        # file_value = self._load_from_file(key)
        # if file_value is not None:
        #     return file_value

        # Return default
        if default is not None:
            logger.debug(f"Configuration {key} using default value")
            return default

        return None

    def set(self, key: str, value: Any, description: Optional[str] = None, encrypted: bool = False) -> None:
        """Set configuration value in database"""
        self.config_repo.set(key, value, description, encrypted)
        logger.info(f"Configuration {key} updated in database")

    def get_channel_config(self, channel_id: str) -> Dict[str, Any]:
        """Get channel-specific configuration"""
        # This will be implemented when channel service is created
        # For now, return empty dict
        return {}

    def set_default_configs(self) -> None:
        """Set default system configurations"""
        defaults = {
            "default_posting_frequency": {
                "value": "daily",
                "description": "Default posting frequency for new channels",
            },
            "default_min_resolution": {
                "value": "720p",
                "description": "Default minimum video resolution",
            },
            "max_concurrent_jobs": {
                "value": 5,
                "description": "Maximum concurrent video processing jobs",
            },
            "default_retry_attempts": {
                "value": 3,
                "description": "Default number of retry attempts for failed jobs",
            },
            "orchestration_running": {
                "value": False,
                "description": "Orchestration system running status",
            },
            "orchestration_paused": {
                "value": False,
                "description": "Orchestration system paused status",
            },
            "queue_paused": {
                "value": False,
                "description": "Queue processing paused status",
            },
        }

        for key, config in defaults.items():
            if not self.config_repo.exists(key):
                self.config_repo.set(
                    key,
                    config["value"],
                    description=config.get("description"),
                )
                logger.info(f"Default configuration {key} set")
