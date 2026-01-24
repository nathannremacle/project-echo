#!/usr/bin/env python3
"""
Initialize default system configurations
Run this script after database setup to populate default values
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_db
from src.services.config_service import ConfigService
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Initialize default configurations"""
    db = SessionLocal()
    try:
        # Initialize database if needed
        init_db()
        
        # Create config service
        config_service = ConfigService(db)
        
        # Set default configurations
        logger.info("Setting default system configurations...")
        config_service.set_default_configs()
        
        logger.info("✅ Default configurations initialized successfully")
        return 0
    except Exception as e:
        logger.exception(f"Error initializing default configs: {e}")
        print(f"❌ Error: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
