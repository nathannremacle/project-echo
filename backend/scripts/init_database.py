#!/usr/bin/env python3
"""
Initialize database - create tables and set default configurations
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, SessionLocal
from src.services.config_service import ConfigService
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Initialize database"""
    logger.info("Initializing database...")
    
    # Create all tables
    logger.info("Creating database tables...")
    init_db()
    logger.info("✅ Database tables created")
    
    # Set default configurations
    logger.info("Setting default configurations...")
    db = SessionLocal()
    try:
        config_service = ConfigService(db)
        config_service.set_default_configs()
        logger.info("✅ Default configurations set")
    except Exception as e:
        logger.error(f"Failed to set default configurations: {e}")
        return 1
    finally:
        db.close()
    
    logger.info("✅ Database initialization complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
