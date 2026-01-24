"""
Integration tests for preset management
"""

import json
import pytest

from src.database import Base, SessionLocal
from src.models.preset import TransformationPreset
from src.services.transformation.preset_service import PresetService
from src.utils.exceptions import NotFoundError, ValidationError


@pytest.fixture
def db_session():
    """Create test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_create_preset(db_session):
    """Test creating a preset"""
    service = PresetService(db_session)
    
    params = {
        "color_grading": {
            "brightness": 0.1,
            "contrast": 1.1,
        },
        "flip": {
            "horizontal": True,
        }
    }
    
    preset = service.create_preset(
        name="Test Preset",
        description="Test description",
        parameters=params,
    )
    
    assert preset.id is not None
    assert preset.name == "Test Preset"
    assert preset.description == "Test description"
    assert preset.is_active is True
    
    # Verify parameters stored correctly
    stored_params = json.loads(preset.parameters)
    assert stored_params["color_grading"]["brightness"] == 0.1


def test_update_preset(db_session):
    """Test updating a preset"""
    service = PresetService(db_session)
    
    # Create preset
    preset = service.create_preset(
        name="Original Name",
        parameters={"color_grading": {"brightness": 0.1}},
    )
    
    # Update preset
    updated = service.update_preset(
        preset.id,
        name="Updated Name",
        parameters={"color_grading": {"brightness": 0.2}},
    )
    
    assert updated.name == "Updated Name"
    stored_params = json.loads(updated.parameters)
    assert stored_params["color_grading"]["brightness"] == 0.2


def test_delete_preset(db_session):
    """Test deleting a preset"""
    service = PresetService(db_session)
    
    # Create preset
    preset = service.create_preset(
        name="To Delete",
        parameters={},
    )
    
    # Delete preset
    result = service.delete_preset(preset.id)
    assert result is True
    
    # Verify deleted
    with pytest.raises(NotFoundError):
        service.get_preset(preset.id)


def test_delete_default_preset_fails(db_session):
    """Test that deleting default preset fails"""
    service = PresetService(db_session)
    
    # Create default preset
    preset = service.create_preset(
        name="Default Preset",
        parameters={},
        is_default=True,
    )
    
    # Try to delete (should fail)
    with pytest.raises(ValidationError):
        service.delete_preset(preset.id)


def test_list_presets(db_session):
    """Test listing presets"""
    service = PresetService(db_session)
    
    # Create multiple presets
    service.create_preset("Preset 1", parameters={}, is_active=True)
    service.create_preset("Preset 2", parameters={}, is_active=True)
    service.create_preset("Preset 3", parameters={}, is_active=False)
    
    # List all
    all_presets = service.list_presets(active_only=False)
    assert len(all_presets) == 3
    
    # List active only
    active_presets = service.list_presets(active_only=True)
    assert len(active_presets) == 2


def test_set_default_preset(db_session):
    """Test setting default preset"""
    service = PresetService(db_session)
    
    # Create first preset
    preset1 = service.create_preset("Preset 1", parameters={}, is_default=True)
    
    # Create second preset and set as default
    preset2 = service.create_preset("Preset 2", parameters={}, is_default=False)
    
    # Update preset2 to be default
    updated = service.update_preset(preset2.id, is_default=True)
    
    assert updated.is_default is True
    
    # Verify preset1 is no longer default
    preset1_updated = service.get_preset(preset1.id)
    assert preset1_updated.is_default is False
