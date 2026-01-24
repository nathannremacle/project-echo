#!/usr/bin/env python3
"""
Health check CLI script
Can be run standalone to check system health
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.health_check import perform_health_check
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Run health check and print results"""
    try:
        health = perform_health_check()
        
        # Print JSON output
        output = health.model_dump()
        print(json.dumps(output, indent=2, default=str))
        
        # Exit with appropriate code
        if health.status == "healthy":
            return 0
        elif health.status == "degraded":
            return 1  # Warning
        else:
            return 2  # Error
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        print(json.dumps({
            "status": "unhealthy",
            "error": str(e),
        }, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
