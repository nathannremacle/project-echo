#!/usr/bin/env python3
"""
Seed database with default system configurations and optional test channel.

Run this after migrations (alembic upgrade head) when the database is empty
or when adding new default keys. Inserts orchestration_running=False,
orchestration_paused=False, queue_paused=False, and other defaults.

If the channels table is empty and ENCRYPTION_KEY is set, creates a test channel
so the dashboard displays something immediately.

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
from src.repositories.channel_repository import ChannelRepository
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

TEST_CHANNEL = {
    "name": "Chaîne de test",
    "youtube_channel_id": "UC_test_channel_default",
    "youtube_channel_url": "https://www.youtube.com/channel/UC_test_channel_default",
    "api_credentials": {
        "type": "placeholder",
        "test": True,
        "client_id": "placeholder",
        "client_secret": "placeholder",
    },
    "is_active": True,
}


def seed_test_channel(db) -> bool:
    """Create a test channel if channels table is empty. Returns True if created."""
    channel_repo = ChannelRepository(db)
    if channel_repo.get_all():
        return False
    try:
        from src.services.orchestration.channel_configuration_service import ChannelConfigurationService

        service = ChannelConfigurationService(db)
        service.create_channel(
            name=TEST_CHANNEL["name"],
            youtube_channel_id=TEST_CHANNEL["youtube_channel_id"],
            youtube_channel_url=TEST_CHANNEL["youtube_channel_url"],
            api_credentials=TEST_CHANNEL["api_credentials"],
            is_active=TEST_CHANNEL["is_active"],
        )
        logger.info("Test channel created for dashboard display")
        return True
    except ValueError as e:
        if "ENCRYPTION_KEY" in str(e):
            logger.warning("Skipping test channel: ENCRYPTION_KEY not set (add to .env for channel creation)")
        else:
            logger.warning("Skipping test channel: %s", e)
        return False
    except Exception as e:
        logger.warning("Skipping test channel: %s", e)
        return False


def main() -> int:
    """Seed default configurations and optional test channel. Idempotent."""
    db = SessionLocal()
    try:
        logger.info("Seeding default system configurations...")
        ConfigService(db).set_default_configs()
        logger.info("Default configurations seeded successfully.")

        seed_test_channel(db)

        return 0
    except Exception as e:
        logger.exception("Seed failed: %s", e)
        print(f"Seed failed: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
