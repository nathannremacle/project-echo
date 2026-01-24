"""
TransformationPreset repository - data access layer for presets
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.preset import TransformationPreset
from src.utils.exceptions import NotFoundError


class PresetRepository:
    """Repository for transformation preset data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, preset: TransformationPreset) -> TransformationPreset:
        """Create a new preset"""
        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        return preset

    def get_by_id(self, preset_id: str) -> Optional[TransformationPreset]:
        """Get preset by ID"""
        return self.db.query(TransformationPreset).filter(TransformationPreset.id == preset_id).first()

    def get_all(self, active_only: bool = False) -> List[TransformationPreset]:
        """Get all presets, optionally filtered by active status"""
        query = self.db.query(TransformationPreset)
        if active_only:
            query = query.filter(TransformationPreset.is_active == True)
        return query.all()

    def get_default(self) -> Optional[TransformationPreset]:
        """Get default preset"""
        return (
            self.db.query(TransformationPreset)
            .filter(TransformationPreset.is_default == True)
            .first()
        )

    def update(self, preset: TransformationPreset) -> TransformationPreset:
        """Update an existing preset"""
        self.db.commit()
        self.db.refresh(preset)
        return preset

    def delete(self, preset_id: str) -> bool:
        """Delete a preset"""
        preset = self.get_by_id(preset_id)
        if not preset:
            raise NotFoundError(f"Preset {preset_id} not found", resource_type="preset")
        self.db.delete(preset)
        self.db.commit()
        return True
