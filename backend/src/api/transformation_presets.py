"""
Transformation presets API endpoints
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.transformation.preset_service import PresetService
from src.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/transformation-presets", tags=["Transformation Presets"])


class PresetEffects(BaseModel):
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    saturation: Optional[float] = None
    hue: Optional[float] = None
    blur: Optional[float] = None
    sharpen: Optional[float] = None
    noise: Optional[float] = None


class PresetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    effects: Optional[PresetEffects] = None


class PresetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    effects: Optional[PresetEffects] = None


def _effects_to_parameters(effects: Optional[PresetEffects]) -> dict:
    """Convert frontend effects to backend parameters format"""
    if not effects:
        return {}
    params = {}
    if effects.brightness is not None:
        params.setdefault("color_grading", {})["brightness"] = effects.brightness
    if effects.contrast is not None:
        params.setdefault("color_grading", {})["contrast"] = effects.contrast
    if effects.saturation is not None:
        params.setdefault("color_grading", {})["saturation"] = effects.saturation
    if effects.hue is not None:
        params.setdefault("color_grading", {})["hue"] = effects.hue
    if effects.blur is not None:
        params.setdefault("filters", {})["blur"] = effects.blur
    if effects.sharpen is not None:
        params.setdefault("filters", {})["sharpen"] = effects.sharpen
    if effects.noise is not None:
        params.setdefault("filters", {})["noise"] = effects.noise
    return params


def _parameters_to_effects(parameters: str) -> dict:
    """Convert backend parameters to frontend effects format"""
    try:
        params = json.loads(parameters) if parameters else {}
    except json.JSONDecodeError:
        return {}
    effects = {}
    if "color_grading" in params:
        cg = params["color_grading"]
        if "brightness" in cg:
            effects["brightness"] = cg["brightness"]
        if "contrast" in cg:
            effects["contrast"] = cg["contrast"]
        if "saturation" in cg:
            effects["saturation"] = cg["saturation"]
        if "hue" in cg:
            effects["hue"] = cg["hue"]
    if "filters" in params:
        f = params["filters"]
        if "blur" in f:
            effects["blur"] = f["blur"]
        if "sharpen" in f:
            effects["sharpen"] = f["sharpen"]
        if "noise" in f:
            effects["noise"] = f["noise"]
    return effects


def _preset_to_dict(preset) -> dict:
    """Convert preset ORM to camelCase dict for frontend"""
    return {
        "id": preset.id,
        "name": preset.name,
        "description": preset.description,
        "effects": _parameters_to_effects(preset.parameters),
        "createdAt": preset.created_at.isoformat() if preset.created_at else None,
        "updatedAt": preset.updated_at.isoformat() if preset.updated_at else None,
    }


@router.get("")
async def list_presets(
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """List transformation presets"""
    service = PresetService(db)
    presets = service.list_presets(active_only=active_only)
    return {"presets": [_preset_to_dict(p) for p in presets]}


@router.post("")
async def create_preset(
    preset: PresetCreate,
    db: Session = Depends(get_db),
):
    """Create transformation preset"""
    service = PresetService(db)
    try:
        params = _effects_to_parameters(preset.effects)
        created = service.create_preset(
            name=preset.name,
            description=preset.description,
            parameters=params if params else None,
        )
        return _preset_to_dict(created)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{preset_id}")
async def update_preset(
    preset_id: str,
    preset: PresetUpdate,
    db: Session = Depends(get_db),
):
    """Update transformation preset"""
    service = PresetService(db)
    try:
        params = _effects_to_parameters(preset.effects) if preset.effects else None
        updated = service.update_preset(
            preset_id=preset_id,
            name=preset.name,
            description=preset.description,
            parameters=params,
        )
        return _preset_to_dict(updated)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{preset_id}")
async def delete_preset(
    preset_id: str,
    db: Session = Depends(get_db),
):
    """Delete transformation preset"""
    service = PresetService(db)
    try:
        service.delete_preset(preset_id)
        return {"message": "Preset deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
