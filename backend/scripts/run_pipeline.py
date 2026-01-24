#!/usr/bin/env python3
"""
CLI script for executing complete video processing pipeline
Usage: python scripts/run_pipeline.py --channel-id <channel_id> [options]
"""

import argparse
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.database import SessionLocal
from src.services.orchestration.pipeline_service import PipelineService
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Execute complete video processing pipeline (scrape → download → transform → upload)"
    )
    
    parser.add_argument(
        "--channel-id",
        required=True,
        help="Channel ID (database ID) to process",
    )
    
    parser.add_argument(
        "--source-url",
        help="Optional source URL to scrape (if not provided, scrapes channel)",
    )
    
    parser.add_argument(
        "--video-id",
        help="Optional existing video ID to process (skip scraping)",
    )
    
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip upload step (for testing)",
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Initialize pipeline service
        pipeline_service = PipelineService(db)
        
        # Execute pipeline
        print(f"Starting pipeline execution for channel {args.channel_id}...")
        print("-" * 60)
        
        results = pipeline_service.execute_pipeline(
            channel_id=args.channel_id,
            source_url=args.source_url,
            video_id=args.video_id,
            skip_upload=args.skip_upload,
        )
        
        # Print results
        print("\n" + "=" * 60)
        print("PIPELINE EXECUTION RESULTS")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Total Duration: {results.get('total_duration', 0)}s")
        print(f"Video ID: {results.get('video_id', 'N/A')}")
        
        if results.get('youtube_video_id'):
            print(f"YouTube Video ID: {results['youtube_video_id']}")
            print(f"YouTube URL: {results['youtube_video_url']}")
        
        print("\nStep Details:")
        for step_name, step_result in results.get("steps", {}).items():
            print(f"  {step_name.upper()}:")
            print(f"    Status: {step_result.get('status', 'unknown')}")
            print(f"    Duration: {step_result.get('duration', 0)}s")
            if step_result.get('status') == 'failed':
                print(f"    Error: {step_result.get('error', 'Unknown error')}")
        
        if results.get("errors"):
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  {error.get('step', 'unknown')}: {error.get('error', 'Unknown error')}")
        
        print("=" * 60)
        
        # Exit with appropriate code
        if results["status"] == "completed":
            print("\n✓ Pipeline completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Pipeline failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        print(f"\n✗ Pipeline execution error: {e}")
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
