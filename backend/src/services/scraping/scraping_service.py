"""
Scraping service - orchestrates video discovery and storage
"""

import json
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from shared.src.scraping import (
    YouTubeScraper,
    apply_filters,
    ScrapingError,
    RateLimitError,
    VideoUnavailableError,
)
from src.models.video import Video
from src.models.channel import Channel
from src.repositories.video_repository import VideoRepository
from src.repositories.channel_repository import ChannelRepository
from src.schemas.scraping import ScrapingConfig, ScrapedVideoMetadata, ScrapingResult
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError

logger = get_logger(__name__)


class ScrapingService:
    """Service for video scraping operations"""

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)
        self.scraper = YouTubeScraper(rate_limit_delay=1.0)

    def _load_channel_config(self, channel_id: str) -> ScrapingConfig:
        """
        Load scraping configuration from channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            ScrapingConfig object
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Parse content_filters JSON
        try:
            filters = json.loads(channel.content_filters) if channel.content_filters else {}
        except json.JSONDecodeError:
            logger.warning(f"Invalid content_filters JSON for channel {channel_id}, using defaults")
            filters = {}
        
        # Build config from channel filters
        config = ScrapingConfig(
            sources=filters.get("sources", []),
            keywords=filters.get("keywords", []),
            min_resolution=filters.get("min_resolution", "720p"),
            min_views=filters.get("min_views"),
            max_duration=filters.get("max_duration"),
            max_results=filters.get("max_results", 10),
            exclude_watermarked=filters.get("exclude_watermarked", True),
        )
        
        return config

    def _is_duplicate(self, source_url: str, channel_id: str) -> bool:
        """
        Check if video already exists in database
        
        Args:
            source_url: Source video URL
            channel_id: Channel ID
            
        Returns:
            True if video already exists
        """
        existing = self.video_repo.get_by_channel_id(channel_id)
        for video in existing:
            if video.source_url == source_url:
                return True
        return False

    def _store_video(self, metadata: Dict[str, Any], channel_id: str) -> Video:
        """
        Store scraped video in database
        
        Args:
            metadata: Video metadata dictionary
            channel_id: Channel ID
            
        Returns:
            Created Video object
        """
        video = Video(
            channel_id=channel_id,
            source_url=metadata["url"],
            source_title=metadata["title"],
            source_creator=metadata.get("creator"),
            source_platform=metadata.get("platform", "youtube"),
            download_status="pending",
        )
        
        return self.video_repo.create(video)

    def _scrape_source(self, source: str, config: ScrapingConfig) -> List[Dict[str, Any]]:
        """
        Scrape videos from a source (URL, search query, etc.)
        
        Args:
            source: Source URL or search query
            config: Scraping configuration
            
        Returns:
            List of video metadata dictionaries
        """
        videos = []
        
        try:
            # Determine source type
            if "youtube.com/watch" in source or "youtu.be" in source:
                # Single video URL
                logger.info(f"Scraping single video: {source}")
                metadata = self.scraper.scrape_video(source)
                videos.append(metadata)
                
            elif "youtube.com/playlist" in source or "list=" in source:
                # Playlist URL
                logger.info(f"Scraping playlist: {source}")
                playlist_videos = self.scraper.scrape_playlist(source, max_results=config.max_results)
                videos.extend(playlist_videos)
                
            elif "youtube.com/channel" in source or "youtube.com/c/" in source or "youtube.com/@/" in source:
                # Channel URL
                logger.info(f"Scraping channel: {source}")
                channel_videos = self.scraper.scrape_channel(source, max_results=config.max_results)
                videos.extend(channel_videos)
                
            else:
                # Treat as search query
                logger.info(f"Searching YouTube: {source}")
                search_videos = self.scraper.search_videos(source, max_results=config.max_results)
                videos.extend(search_videos)
            
            # Rate limiting delay
            time.sleep(self.scraper.rate_limit_delay)
            
        except VideoUnavailableError as e:
            logger.warning(f"Video unavailable: {source} - {str(e)}")
        except RateLimitError as e:
            logger.warning(f"Rate limited: {source} - {str(e)}")
            # Wait longer on rate limit
            time.sleep(5.0)
        except ScrapingError as e:
            logger.error(f"Scraping error for {source}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error scraping {source}: {str(e)}")
        
        return videos

    def scrape_for_channel(self, channel_id: str) -> ScrapingResult:
        """
        Scrape videos for a specific channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            ScrapingResult with statistics
        """
        logger.info(f"Starting scraping for channel {channel_id}")
        
        # Load channel configuration
        config = self._load_channel_config(channel_id)
        
        all_videos = []
        errors = []
        
        # Scrape from configured sources
        for source in config.sources:
            try:
                videos = self._scrape_source(source, config)
                all_videos.extend(videos)
            except Exception as e:
                error_msg = f"Error scraping source {source}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Scrape from keywords (search queries)
        for keyword in config.keywords:
            try:
                videos = self.scraper.search_videos(keyword, max_results=config.max_results)
                all_videos.extend(videos)
                time.sleep(self.scraper.rate_limit_delay)
            except Exception as e:
                error_msg = f"Error searching keyword '{keyword}': {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Found {len(all_videos)} videos before filtering")
        
        # Apply filters
        filtered_videos = []
        for video in all_videos:
            if apply_filters(
                video,
                min_resolution=config.min_resolution,
                min_views=config.min_views,
                max_duration=config.max_duration,
                exclude_watermarked=config.exclude_watermarked,
            ):
                filtered_videos.append(video)
            else:
                logger.debug(f"Video filtered out: {video.get('title', 'Unknown')}")
        
        logger.info(f"Filtered to {len(filtered_videos)} videos")
        
        # Store in database (skip duplicates)
        stored_count = 0
        for video_metadata in filtered_videos:
            try:
                # Check for duplicates
                if self._is_duplicate(video_metadata["url"], channel_id):
                    logger.debug(f"Skipping duplicate video: {video_metadata['url']}")
                    continue
                
                # Store video
                self._store_video(video_metadata, channel_id)
                stored_count += 1
                
            except Exception as e:
                error_msg = f"Error storing video {video_metadata.get('url', 'Unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Convert to ScrapedVideoMetadata objects
        metadata_list = [ScrapedVideoMetadata(**video) for video in filtered_videos]
        
        result = ScrapingResult(
            success=len(errors) == 0 or stored_count > 0,
            videos_found=len(all_videos),
            videos_filtered=len(filtered_videos),
            videos_stored=stored_count,
            errors=errors,
            metadata=metadata_list,
        )
        
        logger.info(
            f"Scraping completed for channel {channel_id}: "
            f"{stored_count} videos stored, {len(errors)} errors"
        )
        
        return result

    def scrape_single_video(self, url: str, channel_id: str) -> Optional[Video]:
        """
        Scrape a single video and store it
        
        Args:
            url: Video URL
            channel_id: Channel ID
            
        Returns:
            Created Video object or None if failed
        """
        try:
            # Scrape metadata
            metadata = self.scraper.scrape_video(url)
            
            # Check for duplicates
            if self._is_duplicate(url, channel_id):
                logger.info(f"Video already exists: {url}")
                return None
            
            # Store video
            video = self._store_video(metadata, channel_id)
            
            logger.info(f"Scraped and stored video: {url}")
            return video
            
        except VideoUnavailableError as e:
            logger.warning(f"Video unavailable: {url} - {str(e)}")
            return None
        except ScrapingError as e:
            logger.error(f"Scraping error for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None

    def scrape_video_url(self, url: str, channel_id: str) -> Dict[str, Any]:
        """
        Scrape a single video URL and return format compatible with pipeline.
        
        Args:
            url: Video URL (YouTube, etc.)
            channel_id: Channel ID
            
        Returns:
            Dict with "videos" key containing list of Video objects (empty if failed)
        """
        video = self.scrape_single_video(url, channel_id)
        return {"videos": [video] if video else []}

    def scrape_channel_for_pipeline(self, channel_id: str) -> Dict[str, Any]:
        """
        Scrape channel sources and return format compatible with pipeline.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dict with "videos" key containing list of stored Video objects
        """
        result = self.scrape_for_channel(channel_id)
        if result.videos_stored == 0:
            return {"videos": []}
        videos = self.video_repo.get_by_channel_id(channel_id, limit=result.videos_stored)
        return {"videos": videos}
