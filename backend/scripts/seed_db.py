#!/usr/bin/env python3
"""
Seed database with default system configurations.

Run this after migrations (alembic upgrade head) when the database is empty
or when adding new default keys. Inserts orchestration_running=False,
orchestration_paused=False, queue_paused=False, and other defaults.

Usage (run from backend/):
  python scripts/seed_db.py
  python -m scripts.seed_db

Usage from repo root:
  python backend/scripts/seed_db.py
"""

import sys
from pathlib import Path

# Add backend root to path (same as init_default_configs)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import SessionLocal
from src.services.config_service import ConfigService
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main() -> int:
    """Seed default configurations. Idempotent: skips keys that already exist."""
    db = SessionLocal()
    try:
        logger.info("Seeding default system configurations...")
        ConfigService(db).set_default_configs()
        logger.info("Default configurations seeded successfully.")
        return 0
    except Exception as e:
        logger.exception("Seed failed: %s", e)
        print(f"Seed failed: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
