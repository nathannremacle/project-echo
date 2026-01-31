"""
System configuration API endpoints
"""

import json
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.repositories.config_repository import ConfigRepository

router = APIRouter(prefix="/config", tags=["Configuration"])


class ConfigUpdate(BaseModel):
    key: str
    value: Optional[Any] = None
    category: Optional[str] = None


def _parse_config_value(value_str: str):
    """Parse config value from JSON string"""
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        return value_str


def _config_to_dict(config) -> dict:
    """Convert config ORM to camelCase dict for frontend"""
    return {
        "id": config.key,
        "key": config.key,
        "value": _parse_config_value(config.value),
        "description": config.description,
        "category": "system",
        "isEncrypted": config.encrypted,
        "updatedAt": config.updated_at.isoformat() if config.updated_at else None,
    }


@router.get("")
async def get_configuration(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """Get system configuration"""
    config_repo = ConfigRepository(db)
    configs = config_repo.get_all_entries()
    result = [_config_to_dict(c) for c in configs]
    if category:
        result = [c for c in result if c.get("category") == category]
    return {"config": result}


@router.put("")
async def update_configuration(
    update: ConfigUpdate,
    db: Session = Depends(get_db),
):
    """Update system configuration"""
    config_repo = ConfigRepository(db)
    config = config_repo.set(
        key=update.key,
        value=update.value,
        description=update.category or f"Updated {update.key}",
    )
    return _config_to_dict(config)
