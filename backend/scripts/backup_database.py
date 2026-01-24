#!/usr/bin/env python3
"""
Database backup script for Project Echo
Backs up SQLite database to a timestamped file
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import settings
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def backup_sqlite_database(output_dir: Optional[str] = None) -> str:
    """
    Backup SQLite database to a timestamped file
    
    Args:
        output_dir: Directory to save backup (default: ./backups)
    
    Returns:
        Path to backup file
    """
    # Parse database URL to get file path
    db_url = settings.DATABASE_URL
    if not db_url.startswith("sqlite:///"):
        raise ValueError("Backup script only supports SQLite databases")

    # Extract file path from SQLite URL
    db_path = db_url.replace("sqlite:///", "")
    db_file = Path(db_path)

    if not db_file.exists():
        raise FileNotFoundError(f"Database file not found: {db_file}")

    # Create backup directory
    if output_dir:
        backup_dir = Path(output_dir)
    else:
        backup_dir = Path("backups")
    
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"project_echo_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename

    # Copy database file
    logger.info(f"Backing up database from {db_file} to {backup_path}")
    shutil.copy2(db_file, backup_path)

    logger.info(f"Backup completed: {backup_path}")
    return str(backup_path)


def restore_sqlite_database(backup_path: str, confirm: bool = False) -> None:
    """
    Restore SQLite database from backup file
    
    Args:
        backup_path: Path to backup file
        confirm: Require confirmation before restoring
    """
    backup_file = Path(backup_path)
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    # Parse database URL to get file path
    db_url = settings.DATABASE_URL
    if not db_url.startswith("sqlite:///"):
        raise ValueError("Restore script only supports SQLite databases")

    db_path = db_url.replace("sqlite:///", "")
    db_file = Path(db_path)

    if not confirm:
        response = input(f"Restore database from {backup_path}? This will overwrite {db_file}. (yes/no): ")
        if response.lower() != "yes":
            logger.info("Restore cancelled")
            return

    # Backup current database first
    if db_file.exists():
        current_backup = f"{db_file}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Backing up current database to {current_backup}")
        shutil.copy2(db_file, current_backup)

    # Restore from backup
    logger.info(f"Restoring database from {backup_path} to {db_file}")
    shutil.copy2(backup_file, db_file)

    logger.info(f"Database restored successfully from {backup_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database backup and restore utility")
    parser.add_argument(
        "action",
        choices=["backup", "restore"],
        help="Action to perform",
    )
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory for backup files (default: ./backups)",
    )
    parser.add_argument(
        "--backup-file",
        help="Path to backup file for restore",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation for restore",
    )

    args = parser.parse_args()

    try:
        if args.action == "backup":
            backup_path = backup_sqlite_database(args.output_dir)
            print(f"✅ Backup created: {backup_path}")
        elif args.action == "restore":
            if not args.backup_file:
                print("❌ Error: --backup-file required for restore")
                return 1
            restore_sqlite_database(args.backup_file, confirm=args.yes)
            print(f"✅ Database restored from {args.backup_file}")
        return 0
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    from typing import Optional

    sys.exit(main())
