"""
Channel configuration management service
Handles creation, update, validation, export/import of channel configurations
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.channel import Channel
from src.repositories.channel_repository import ChannelRepository
from src.repositories.preset_repository import PresetRepository
from src.services.youtube.auth_service import YouTubeAuthService
from src.utils.encryption import encrypt_dict, decrypt_dict
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError, AuthenticationError

logger = get_logger(__name__)

# Default configurations
DEFAULT_POSTING_SCHEDULE = {
    "frequency": "daily",
    "preferred_times": ["12:00"],
    "timezone": "UTC",
    "days_of_week": [0, 1, 2, 3, 4, 5, 6],  # All days
}

DEFAULT_CONTENT_FILTERS = {
    "min_resolution": "720p",
    "min_views": 0,
    "exclude_watermarked": True,
    "preferred_sources": [],
}

DEFAULT_METADATA_TEMPLATE = {
    "title": "{channel_name} - {source_title}",
    "description": "Video from {channel_name}\n\nOriginal: {source_title}",
    "tags": ["edit", "music", "viral"],
    "category": "entertainment",
    "privacy": "unlisted",
}


class ChannelConfigurationService:
    """Service for managing channel configurations"""

    def __init__(self, db: Session):
        self.db = db
        self.channel_repo = ChannelRepository(db)
        self.preset_repo = PresetRepository(db)
        self.auth_service = YouTubeAuthService(db)

    def create_channel(
        self,
        name: str,
        youtube_channel_id: str,
        youtube_channel_url: str,
        api_credentials: Dict[str, Any],
        posting_schedule: Optional[Dict[str, Any]] = None,
        content_filters: Optional[Dict[str, Any]] = None,
        metadata_template: Optional[Dict[str, Any]] = None,
        effect_preset_id: Optional[str] = None,
        is_active: bool = False,
    ) -> Channel:
        """
        Create a new channel with configuration
        
        Args:
            name: Channel name
            youtube_channel_id: YouTube channel ID
            youtube_channel_url: YouTube channel URL
            api_credentials: YouTube API credentials dictionary
            posting_schedule: Optional posting schedule (uses default if not provided)
            content_filters: Optional content filters (uses default if not provided)
            metadata_template: Optional metadata template (uses default if not provided)
            effect_preset_id: Optional transformation preset ID
            is_active: Whether channel is active (default: False)
            
        Returns:
            Created Channel object
        """
        # Validate YouTube channel ID is unique
        existing = self.channel_repo.get_by_youtube_channel_id(youtube_channel_id)
        if existing:
            raise ValidationError(f"YouTube channel ID {youtube_channel_id} already exists")
        
        # Use defaults if not provided
        posting_schedule = posting_schedule or DEFAULT_POSTING_SCHEDULE
        content_filters = content_filters or DEFAULT_CONTENT_FILTERS
        metadata_template = metadata_template or DEFAULT_METADATA_TEMPLATE
        
        # Validate configuration
        self._validate_posting_schedule(posting_schedule)
        self._validate_content_filters(content_filters)
        self._validate_metadata_template(metadata_template)
        
        if effect_preset_id:
            self._validate_preset_exists(effect_preset_id)
        
        # Encrypt credentials
        encrypted_credentials = encrypt_dict(api_credentials)
        
        # Create channel
        channel = Channel(
            name=name,
            youtube_channel_id=youtube_channel_id,
            youtube_channel_url=youtube_channel_url,
            is_active=is_active,
            api_credentials_encrypted=encrypted_credentials,
            posting_schedule=json.dumps(posting_schedule),
            content_filters=json.dumps(content_filters),
            metadata_template=json.dumps(metadata_template),
            effect_preset_id=effect_preset_id,
        )
        
        channel = self.channel_repo.create(channel)
        
        logger.info(f"Created channel {channel.id} ({name}) with configuration")
        
        return channel

    def update_channel_configuration(
        self,
        channel_id: str,
        posting_schedule: Optional[Dict[str, Any]] = None,
        content_filters: Optional[Dict[str, Any]] = None,
        metadata_template: Optional[Dict[str, Any]] = None,
        effect_preset_id: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Channel:
        """
        Update channel configuration
        
        Args:
            channel_id: Channel ID
            posting_schedule: Optional posting schedule to update
            content_filters: Optional content filters to update
            metadata_template: Optional metadata template to update
            effect_preset_id: Optional effect preset ID to update
            is_active: Optional active status to update
            
        Returns:
            Updated Channel object
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Update fields if provided
        if posting_schedule is not None:
            self._validate_posting_schedule(posting_schedule)
            channel.posting_schedule = json.dumps(posting_schedule)
            logger.info(f"Updated posting schedule for channel {channel_id}")
        
        if content_filters is not None:
            self._validate_content_filters(content_filters)
            channel.content_filters = json.dumps(content_filters)
            logger.info(f"Updated content filters for channel {channel_id}")
        
        if metadata_template is not None:
            self._validate_metadata_template(metadata_template)
            channel.metadata_template = json.dumps(metadata_template)
            logger.info(f"Updated metadata template for channel {channel_id}")
        
        if effect_preset_id is not None:
            if effect_preset_id:  # Not empty string
                self._validate_preset_exists(effect_preset_id)
            channel.effect_preset_id = effect_preset_id if effect_preset_id else None
            logger.info(f"Updated effect preset for channel {channel_id}")
        
        if is_active is not None:
            channel.is_active = is_active
            logger.info(f"Updated active status for channel {channel_id}: {is_active}")
        
        channel = self.channel_repo.update(channel)
        
        logger.info(f"Updated configuration for channel {channel_id}")
        
        return channel

    def update_api_credentials(
        self,
        channel_id: str,
        api_credentials: Dict[str, Any],
    ) -> Channel:
        """
        Update YouTube API credentials for a channel
        
        Args:
            channel_id: Channel ID
            api_credentials: New API credentials dictionary
            
        Returns:
            Updated Channel object
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Encrypt credentials
        encrypted_credentials = encrypt_dict(api_credentials)
        channel.api_credentials_encrypted = encrypted_credentials
        
        channel = self.channel_repo.update(channel)
        
        logger.info(f"Updated API credentials for channel {channel_id}")
        
        return channel

    def validate_channel_configuration(self, channel_id: str) -> Dict[str, Any]:
        """
        Validate channel configuration
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dictionary with validation results
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        results = {
            "channel_id": channel_id,
            "valid": True,
            "errors": [],
            "warnings": [],
        }
        
        # Validate posting schedule
        try:
            posting_schedule = json.loads(channel.posting_schedule)
            self._validate_posting_schedule(posting_schedule)
        except (json.JSONDecodeError, ValidationError) as e:
            results["valid"] = False
            results["errors"].append(f"Invalid posting schedule: {str(e)}")
        
        # Validate content filters
        try:
            content_filters = json.loads(channel.content_filters)
            self._validate_content_filters(content_filters)
        except (json.JSONDecodeError, ValidationError) as e:
            results["valid"] = False
            results["errors"].append(f"Invalid content filters: {str(e)}")
        
        # Validate metadata template
        try:
            metadata_template = json.loads(channel.metadata_template)
            self._validate_metadata_template(metadata_template)
        except (json.JSONDecodeError, ValidationError) as e:
            results["valid"] = False
            results["errors"].append(f"Invalid metadata template: {str(e)}")
        
        # Validate effect preset
        if channel.effect_preset_id:
            try:
                self._validate_preset_exists(channel.effect_preset_id)
            except NotFoundError:
                results["warnings"].append(f"Effect preset {channel.effect_preset_id} not found")
        
        # Validate API credentials
        try:
            is_valid = self.auth_service.validate_authentication(channel_id)
            if not is_valid:
                results["valid"] = False
                results["errors"].append("YouTube API credentials are invalid")
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Failed to validate API credentials: {str(e)}")
        
        return results

    def export_channel_configuration(self, channel_id: str, include_credentials: bool = False) -> Dict[str, Any]:
        """
        Export channel configuration to dictionary
        
        Args:
            channel_id: Channel ID
            include_credentials: Whether to include encrypted credentials (default: False)
            
        Returns:
            Dictionary with channel configuration
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        config = {
            "name": channel.name,
            "youtube_channel_id": channel.youtube_channel_id,
            "youtube_channel_url": channel.youtube_channel_url,
            "is_active": channel.is_active,
            "posting_schedule": json.loads(channel.posting_schedule),
            "content_filters": json.loads(channel.content_filters),
            "metadata_template": json.loads(channel.metadata_template),
            "effect_preset_id": channel.effect_preset_id,
            "phase2_enabled": channel.phase2_enabled,
            "github_repo_url": channel.github_repo_url,
        }
        
        if include_credentials:
            try:
                credentials = self.auth_service.get_credentials(channel_id)
                config["api_credentials"] = credentials
            except Exception as e:
                logger.warning(f"Failed to decrypt credentials for export: {e}")
                config["api_credentials"] = None
        
        return config

    def import_channel_configuration(
        self,
        config: Dict[str, Any],
        update_existing: bool = False,
    ) -> Channel:
        """
        Import channel configuration from dictionary
        
        Args:
            config: Configuration dictionary
            update_existing: If True, update existing channel; if False, create new
            
        Returns:
            Channel object (created or updated)
        """
        youtube_channel_id = config.get("youtube_channel_id")
        if not youtube_channel_id:
            raise ValidationError("youtube_channel_id is required")
        
        existing = self.channel_repo.get_by_youtube_channel_id(youtube_channel_id)
        
        if existing and not update_existing:
            raise ValidationError(f"Channel with YouTube ID {youtube_channel_id} already exists")
        
        if existing and update_existing:
            # Update existing channel
            return self.update_channel_configuration(
                channel_id=existing.id,
                posting_schedule=config.get("posting_schedule"),
                content_filters=config.get("content_filters"),
                metadata_template=config.get("metadata_template"),
                effect_preset_id=config.get("effect_preset_id"),
                is_active=config.get("is_active"),
            )
        else:
            # Create new channel
            api_credentials = config.get("api_credentials")
            if not api_credentials:
                raise ValidationError("api_credentials is required for new channels")
            
            return self.create_channel(
                name=config.get("name", f"Channel {youtube_channel_id}"),
                youtube_channel_id=youtube_channel_id,
                youtube_channel_url=config.get("youtube_channel_url", f"https://youtube.com/channel/{youtube_channel_id}"),
                api_credentials=api_credentials,
                posting_schedule=config.get("posting_schedule"),
                content_filters=config.get("content_filters"),
                metadata_template=config.get("metadata_template"),
                effect_preset_id=config.get("effect_preset_id"),
                is_active=config.get("is_active", False),
            )

    def get_default_configuration(self) -> Dict[str, Any]:
        """
        Get default channel configuration
        
        Returns:
            Dictionary with default configuration
        """
        return {
            "posting_schedule": DEFAULT_POSTING_SCHEDULE,
            "content_filters": DEFAULT_CONTENT_FILTERS,
            "metadata_template": DEFAULT_METADATA_TEMPLATE,
        }

    def _validate_posting_schedule(self, schedule: Dict[str, Any]) -> None:
        """Validate posting schedule configuration"""
        if not isinstance(schedule, dict):
            raise ValidationError("Posting schedule must be a dictionary")
        
        frequency = schedule.get("frequency")
        if frequency not in ["daily", "weekly", "custom"]:
            raise ValidationError(f"Invalid frequency: {frequency}. Must be 'daily', 'weekly', or 'custom'")
        
        preferred_times = schedule.get("preferred_times", [])
        if not isinstance(preferred_times, list):
            raise ValidationError("preferred_times must be a list")
        
        timezone = schedule.get("timezone")
        if not timezone:
            raise ValidationError("timezone is required")

    def _validate_content_filters(self, filters: Dict[str, Any]) -> None:
        """Validate content filters configuration"""
        if not isinstance(filters, dict):
            raise ValidationError("Content filters must be a dictionary")
        
        min_resolution = filters.get("min_resolution")
        if min_resolution and min_resolution not in ["720p", "1080p", "1440p", "2160p"]:
            raise ValidationError(f"Invalid min_resolution: {min_resolution}")

    def _validate_metadata_template(self, template: Dict[str, Any]) -> None:
        """Validate metadata template configuration"""
        if not isinstance(template, dict):
            raise ValidationError("Metadata template must be a dictionary")
        
        if "title" not in template:
            raise ValidationError("Metadata template must include 'title'")

    def _validate_preset_exists(self, preset_id: str) -> None:
        """Validate transformation preset exists"""
        preset = self.preset_repo.get_by_id(preset_id)
        if not preset:
            raise NotFoundError(f"Transformation preset {preset_id} not found", resource_type="preset")
