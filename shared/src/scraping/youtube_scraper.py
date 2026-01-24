"""
YouTube video scraper using yt-dlp
Discovers and extracts metadata from YouTube videos
"""

import json
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from shared.src.scraping.exceptions import ScrapingError, RateLimitError, VideoUnavailableError


class YouTubeScraper:
    """YouTube video scraper using yt-dlp"""

    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize YouTube scraper
        
        Args:
            rate_limit_delay: Delay in seconds between requests to respect rate limits
        """
        self.rate_limit_delay = rate_limit_delay
        self._ydl_opts_base = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,  # Extract full metadata
            "skip_download": True,  # Don't download, just get metadata
        }

    def _get_ydl_opts(self, **kwargs) -> Dict[str, Any]:
        """Get yt-dlp options with custom overrides"""
        opts = self._ydl_opts_base.copy()
        opts.update(kwargs)
        return opts

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com\/v\/([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _parse_resolution(self, width: Optional[int], height: Optional[int]) -> Optional[str]:
        """Parse resolution from width and height"""
        if not width or not height:
            return None
        
        # Common resolutions
        if height >= 2160:
            return "2160p"
        elif height >= 1440:
            return "1440p"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
        elif height >= 360:
            return "360p"
        else:
            return "240p"

    def _check_min_resolution(self, resolution: Optional[str], min_resolution: str) -> bool:
        """Check if resolution meets minimum requirement"""
        if not resolution:
            return False
        
        resolution_order = ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        try:
            res_idx = resolution_order.index(resolution)
            min_idx = resolution_order.index(min_resolution)
            return res_idx >= min_idx
        except ValueError:
            # Unknown resolution, assume it doesn't meet requirement
            return False

    def scrape_video(self, url: str) -> Dict[str, Any]:
        """
        Scrape metadata for a single video
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video metadata
            
        Raises:
            ScrapingError: If scraping fails
            VideoUnavailableError: If video is unavailable
            RateLimitError: If rate limited
        """
        try:
            with yt_dlp.YoutubeDL(self._get_ydl_opts()) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ScrapingError(f"Failed to extract info from {url}")
                
                # Extract metadata
                video_id = info.get("id") or self._extract_video_id(url)
                width = info.get("width")
                height = info.get("height")
                resolution = self._parse_resolution(width, height)
                
                metadata = {
                    "url": url,
                    "video_id": video_id,
                    "title": info.get("title", ""),
                    "description": info.get("description", ""),
                    "duration": info.get("duration", 0),
                    "creator": info.get("uploader", info.get("channel", "")),
                    "creator_id": info.get("channel_id") or info.get("uploader_id"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "resolution": resolution,
                    "width": width,
                    "height": height,
                    "thumbnail_url": info.get("thumbnail"),
                    "upload_date": info.get("upload_date"),
                    "platform": "youtube",
                }
                
                return metadata
                
        except DownloadError as e:
            if "Private video" in str(e) or "Video unavailable" in str(e):
                raise VideoUnavailableError(f"Video unavailable: {url}") from e
            raise ScrapingError(f"Download error for {url}: {str(e)}") from e
        except ExtractorError as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                raise RateLimitError(f"Rate limited: {url}") from e
            raise ScrapingError(f"Extraction error for {url}: {str(e)}") from e
        except Exception as e:
            raise ScrapingError(f"Unexpected error scraping {url}: {str(e)}") from e

    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of video metadata dictionaries
        """
        search_url = f"ytsearch{max_results}:{query}"
        
        try:
            with yt_dlp.YoutubeDL(self._get_ydl_opts()) as ydl:
                results = ydl.extract_info(search_url, download=False)
                
                if not results or "entries" not in results:
                    return []
                
                videos = []
                entries = results.get("entries", [])
                if not entries:
                    return []
                
                for entry in entries:
                    if not entry:
                        continue
                    
                    video_url = entry.get("url") or entry.get("webpage_url")
                    if not video_url:
                        continue
                    
                    # Extract metadata from entry
                    width = entry.get("width")
                    height = entry.get("height")
                    resolution = self._parse_resolution(width, height)
                    
                    metadata = {
                        "url": video_url,
                        "video_id": entry.get("id"),
                        "title": entry.get("title", ""),
                        "description": entry.get("description", ""),
                        "duration": entry.get("duration", 0),
                        "creator": entry.get("uploader", entry.get("channel", "")),
                        "creator_id": entry.get("channel_id") or entry.get("uploader_id"),
                        "view_count": entry.get("view_count"),
                        "like_count": entry.get("like_count"),
                        "resolution": resolution,
                        "width": width,
                        "height": height,
                        "thumbnail_url": entry.get("thumbnail"),
                        "upload_date": entry.get("upload_date"),
                        "platform": "youtube",
                    }
                    
                    videos.append(metadata)
                
                return videos
                
        except Exception as e:
            raise ScrapingError(f"Search error for query '{query}': {str(e)}") from e

    def scrape_playlist(self, playlist_url: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape videos from a playlist
        
        Args:
            playlist_url: YouTube playlist URL
            max_results: Maximum number of videos to scrape (None for all)
            
        Returns:
            List of video metadata dictionaries
        """
        try:
            opts = self._get_ydl_opts()
            if max_results:
                opts["playlistend"] = max_results
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info or "entries" not in info:
                    return []
                
                videos = []
                entries = info.get("entries", [])
                if not entries:
                    return []
                
                for entry in entries:
                    if not entry:
                        continue
                    
                    video_url = entry.get("url") or entry.get("webpage_url")
                    if not video_url:
                        continue
                    
                    width = entry.get("width")
                    height = entry.get("height")
                    resolution = self._parse_resolution(width, height)
                    
                    metadata = {
                        "url": video_url,
                        "video_id": entry.get("id"),
                        "title": entry.get("title", ""),
                        "description": entry.get("description", ""),
                        "duration": entry.get("duration", 0),
                        "creator": entry.get("uploader", entry.get("channel", "")),
                        "creator_id": entry.get("channel_id") or entry.get("uploader_id"),
                        "view_count": entry.get("view_count"),
                        "like_count": entry.get("like_count"),
                        "resolution": resolution,
                        "width": width,
                        "height": height,
                        "thumbnail_url": entry.get("thumbnail"),
                        "upload_date": entry.get("upload_date"),
                        "platform": "youtube",
                    }
                    
                    videos.append(metadata)
                
                return videos
                
        except Exception as e:
            raise ScrapingError(f"Playlist scraping error for {playlist_url}: {str(e)}") from e

    def scrape_channel(self, channel_url: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape videos from a channel
        
        Args:
            channel_url: YouTube channel URL
            max_results: Maximum number of videos to scrape (None for all)
            
        Returns:
            List of video metadata dictionaries
        """
        # yt-dlp can handle channel URLs directly
        return self.scrape_playlist(channel_url, max_results)
