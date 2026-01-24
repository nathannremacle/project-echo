"""
Preset management service
Handles creation, update, and deletion of transformation presets
"""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.preset import TransformationPreset
from src.repositories.preset_repository import PresetRepository
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError

logger = get_logger(__name__)


class PresetService:
    """Service for transformation preset management"""

    def __init__(self, db: Session):
        self.db = db
        self.preset_repo = PresetRepository(db)

    def create_preset(
        self,
        name: str,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        is_default: bool = False,
        is_active: bool = True,
    ) -> TransformationPreset:
        """
        Create a new transformation preset
        
        Args:
            name: Preset name
            description: Optional description
            parameters: Transformation parameters dictionary
            is_default: Whether this is the default preset
            is_active: Whether preset is active
            
        Returns:
            Created TransformationPreset object
        """
        if not name:
            raise ValidationError("Preset name is required")
        
        # Validate parameters
        if parameters:
            self._validate_parameters(parameters)
        
        # If setting as default, unset other defaults
        if is_default:
            existing_default = self.preset_repo.get_default()
            if existing_default:
                existing_default.is_default = False
                self.preset_repo.update(existing_default)
        
        preset = TransformationPreset(
            name=name,
            description=description,
            parameters=json.dumps(parameters or {}),
            is_default=is_default,
            is_active=is_active,
        )
        
        preset = self.preset_repo.create(preset)
        logger.info(f"Created transformation preset: {name} (ID: {preset.id})")
        
        return preset

    def update_preset(
        self,
        preset_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        is_default: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> TransformationPreset:
        """
        Update an existing preset
        
        Args:
            preset_id: Preset ID
            name: New name (optional)
            description: New description (optional)
            parameters: New parameters (optional)
            is_default: New default flag (optional)
            is_active: New active flag (optional)
            
        Returns:
            Updated TransformationPreset object
        """
        preset = self.preset_repo.get_by_id(preset_id)
        if not preset:
            raise NotFoundError(f"Preset {preset_id} not found", resource_type="preset")
        
        if name is not None:
            preset.name = name
        if description is not None:
            preset.description = description
        if parameters is not None:
            self._validate_parameters(parameters)
            preset.parameters = json.dumps(parameters)
        if is_default is not None:
            # If setting as default, unset other defaults
            if is_default:
                existing_default = self.preset_repo.get_default()
                if existing_default and existing_default.id != preset_id:
                    existing_default.is_default = False
                    self.preset_repo.update(existing_default)
            preset.is_default = is_default
        if is_active is not None:
            preset.is_active = is_active
        
        preset = self.preset_repo.update(preset)
        logger.info(f"Updated transformation preset: {preset_id}")
        
        return preset

    def delete_preset(self, preset_id: str) -> bool:
        """
        Delete a preset
        
        Args:
            preset_id: Preset ID
            
        Returns:
            True if deleted successfully
        """
        preset = self.preset_repo.get_by_id(preset_id)
        if not preset:
            raise NotFoundError(f"Preset {preset_id} not found", resource_type="preset")
        
        # Don't allow deleting default preset
        if preset.is_default:
            raise ValidationError("Cannot delete default preset")
        
        self.preset_repo.delete(preset_id)
        logger.info(f"Deleted transformation preset: {preset_id}")
        
        return True

    def get_preset(self, preset_id: str) -> TransformationPreset:
        """
        Get preset by ID
        
        Args:
            preset_id: Preset ID
            
        Returns:
            TransformationPreset object
        """
        preset = self.preset_repo.get_by_id(preset_id)
        if not preset:
            raise NotFoundError(f"Preset {preset_id} not found", resource_type="preset")
        return preset

    def list_presets(self, active_only: bool = False) -> List[TransformationPreset]:
        """
        List all presets
        
        Args:
            active_only: Only return active presets
            
        Returns:
            List of TransformationPreset objects
        """
        return self.preset_repo.get_all(active_only=active_only)

    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate transformation parameters
        
        Args:
            parameters: Parameters dictionary
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Basic structure validation
        if not isinstance(parameters, dict):
            raise ValidationError("Parameters must be a dictionary")
        
        # Validate color grading if present
        if "color_grading" in parameters:
            color = parameters["color_grading"]
            if not isinstance(color, dict):
                raise ValidationError("color_grading must be a dictionary")
            
            # Validate ranges
            if "brightness" in color and not -1.0 <= color["brightness"] <= 1.0:
                raise ValidationError("brightness must be between -1.0 and 1.0")
            if "contrast" in color and not 0.0 <= color["contrast"] <= 3.0:
                raise ValidationError("contrast must be between 0.0 and 3.0")
            if "saturation" in color and not 0.0 <= color["saturation"] <= 3.0:
                raise ValidationError("saturation must be between 0.0 and 3.0")
        
        # Validate flip if present
        if "flip" in parameters:
            flip = parameters["flip"]
            if not isinstance(flip, dict):
                raise ValidationError("flip must be a dictionary")
        
        # Validate filters if present
        if "filters" in parameters:
            filters = parameters["filters"]
            if not isinstance(filters, dict):
                raise ValidationError("filters must be a dictionary")
