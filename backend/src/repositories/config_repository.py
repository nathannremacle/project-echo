"""
Configuration repository - data access layer for system configuration
"""

from typing import Any, Dict, List, Optional
import json

from sqlalchemy.orm import Session

from src.models.config import SystemConfiguration
from src.utils.exceptions import NotFoundError, ConfigurationError


class ConfigRepository:
    """Repository for system configuration data access"""

    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[Any]:
        """Get configuration value by key"""
        config = (
            self.db.query(SystemConfiguration)
            .filter(SystemConfiguration.key == key)
            .first()
        )
        if not config:
            return None
        
        # Parse JSON value
        try:
            return json.loads(config.value)
        except json.JSONDecodeError:
            # If not JSON, return as string
            return config.value

    def set(self, key: str, value: Any, description: Optional[str] = None, encrypted: bool = False) -> SystemConfiguration:
        """Set configuration value"""
        # Serialize as JSON for dict/list/bool so get() returns proper types
        if isinstance(value, (dict, list, bool)) or value is None:
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        config = (
            self.db.query(SystemConfiguration)
            .filter(SystemConfiguration.key == key)
            .first()
        )

        if config:
            # Update existing
            config.value = value_str
            config.encrypted = encrypted
            if description:
                config.description = description
        else:
            # Create new
            config = SystemConfiguration(
                key=key,
                value=value_str,
                description=description,
                encrypted=encrypted,
            )
            self.db.add(config)

        self.db.commit()
        self.db.refresh(config)
        return config

    def delete(self, key: str) -> bool:
        """Delete configuration key"""
        config = (
            self.db.query(SystemConfiguration)
            .filter(SystemConfiguration.key == key)
            .first()
        )
        if not config:
            raise NotFoundError(f"Configuration key {key} not found", resource_type="configuration")
        self.db.delete(config)
        self.db.commit()
        return True

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        configs = self.db.query(SystemConfiguration).all()
        result = {}
        for config in configs:
            try:
                result[config.key] = json.loads(config.value)
            except json.JSONDecodeError:
                result[config.key] = config.value
        return result

    def get_all_entries(self) -> List[SystemConfiguration]:
        """Get all configuration entries as list"""
        return self.db.query(SystemConfiguration).all()

    def exists(self, key: str) -> bool:
        """Check if configuration key exists"""
        return (
            self.db.query(SystemConfiguration)
            .filter(SystemConfiguration.key == key)
            .first() is not None
        )
