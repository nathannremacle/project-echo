#!/usr/bin/env python3
"""
Test script for GitHub Actions workflow validation
This script verifies that the workflow environment is set up correctly
"""

import argparse
import os
import sys
from datetime import datetime


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test GitHub Actions workflow setup")
    parser.add_argument("--channel-id", required=True, help="Channel ID")
    parser.add_argument("--video-url", default="auto", help="Video URL (or 'auto' for auto-discovery)")
    parser.add_argument("--preset", default="default", help="Transformation preset ID")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GitHub Actions Workflow Test Script")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print()
    
    # Test 1: Environment variables
    print("Test 1: Environment Variables")
    print("-" * 60)
    required_vars = [
        "YOUTUBE_CLIENT_ID",
        "YOUTUBE_CLIENT_SECRET",
        "YOUTUBE_REFRESH_TOKEN",
        "CHANNEL_ID",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_present = False
    
    print()
    
    # Test 2: Python environment
    print("Test 2: Python Environment")
    print("-" * 60)
    print(f"  Python version: {sys.version}")
    print(f"  Python executable: {sys.executable}")
    print()
    
    # Test 3: Arguments
    print("Test 3: Workflow Arguments")
    print("-" * 60)
    print(f"  Channel ID: {args.channel_id}")
    print(f"  Video URL: {args.video_url}")
    print(f"  Preset ID: {args.preset}")
    print()
    
    # Test 4: System dependencies
    print("Test 4: System Dependencies")
    print("-" * 60)
    import subprocess
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            print(f"  ✅ FFmpeg: {version_line}")
        else:
            print(f"  ❌ FFmpeg: Not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"  ❌ FFmpeg: Not found or timeout")
    
    print()
    
    # Test 5: Python packages (if available)
    print("Test 5: Python Packages")
    print("-" * 60)
    try:
        import fastapi
        print(f"  ✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print(f"  ⚠️  FastAPI: Not installed (expected if shared libs not installed)")
    
    try:
        import sqlalchemy
        print(f"  ✅ SQLAlchemy: {sqlalchemy.__version__}")
    except ImportError:
        print(f"  ⚠️  SQLAlchemy: Not installed")
    
    print()
    
    # Summary
    print("=" * 60)
    if all_present:
        print("✅ All required environment variables are set")
        print("✅ Workflow environment is ready")
        return 0
    else:
        print("❌ Some required environment variables are missing")
        print("Please configure GitHub Secrets for this repository")
        return 1


if __name__ == "__main__":
    sys.exit(main())
