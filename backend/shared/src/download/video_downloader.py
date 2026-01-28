"""
Video downloader using yt-dlp
Downloads videos from URLs to local storage
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from shared.src.download.exceptions import DownloadError as CustomDownloadError, VideoUnavailableError


class VideoDownloader:
    """Video downloader using yt-dlp"""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Initialize video downloader
        
        Args:
            output_dir: Directory to save downloaded videos (default: temp directory)
            progress_callback: Callback function for download progress updates
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        self.progress_callback = progress_callback
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_ydl_opts(self, output_path: str, format_preference: Optional[str] = None) -> Dict[str, Any]:
        """
        Get yt-dlp options for download
        
        Args:
            output_path: Output file path
            format_preference: Preferred format (e.g., 'bestvideo[height<=1080]+bestaudio/best[height<=1080]')
            
        Returns:
            yt-dlp options dictionary
        """
        opts = {
            "outtmpl": output_path,
            "format": format_preference or "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "merge_output_format": "mp4",
            "quiet": False,
            "no_warnings": False,
        }
        
        # Add progress hook if callback provided
        if self.progress_callback:
            opts["progress_hooks"] = [self.progress_callback]
        
        return opts

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL for naming"""
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(url)
        if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
            if "v=" in parsed.query:
                return parse_qs(parsed.query)["v"][0]
            elif parsed.path.startswith("/watch/"):
                return parsed.path.split("/")[-1]
            elif "youtu.be" in parsed.netloc:
                return parsed.path.lstrip("/")
        return None

    def download(
        self,
        url: str,
        video_id: Optional[str] = None,
        format_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Download video from URL
        
        Args:
            url: Video URL
            video_id: Optional video ID for naming (extracted from URL if not provided)
            format_preference: Preferred format
            
        Returns:
            Dictionary with download information:
            - file_path: Path to downloaded file
            - file_size: File size in bytes
            - duration: Video duration in seconds
            - resolution: Video resolution (e.g., "1080p")
            - format: Video format/codec
            - width: Video width in pixels
            - height: Video height in pixels
            
        Raises:
            CustomDownloadError: If download fails
            VideoUnavailableError: If video is unavailable
        """
        # Extract video ID if not provided
        if not video_id:
            video_id = self._extract_video_id(url) or "video"
        
        # Generate output path (yt-dlp format string)
        output_filename = f"{video_id}.%(ext)s"
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            with yt_dlp.YoutubeDL(self._get_ydl_opts(output_path, format_preference)) as ydl:
                # Extract info first to get metadata
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise CustomDownloadError(f"Failed to extract info from {url}")
                
                # Download video
                ydl.download([url])
                
                # Find downloaded file (yt-dlp uses format string, so we need to find actual file)
                # yt-dlp replaces %(ext)s with actual extension
                downloaded_file = None
                
                # Try common extensions
                for ext in ["mp4", "webm", "mkv", "avi", "m4a"]:
                    potential_file = os.path.join(self.output_dir, f"{video_id}.{ext}")
                    if os.path.exists(potential_file):
                        downloaded_file = potential_file
                        break
                
                if not downloaded_file:
                    # Try to find file with video_id in name (fallback)
                    for file in os.listdir(self.output_dir):
                        if video_id in file and os.path.isfile(os.path.join(self.output_dir, file)):
                            downloaded_file = os.path.join(self.output_dir, file)
                            break
                
                if not downloaded_file:
                    raise CustomDownloadError(f"Downloaded file not found for {url}")
                
                # Get file size
                file_size = os.path.getsize(downloaded_file)
                
                # Extract metadata from info
                duration = info.get("duration", 0)
                width = info.get("width")
                height = info.get("height")
                
                # Determine resolution
                resolution = None
                if height:
                    if height >= 2160:
                        resolution = "2160p"
                    elif height >= 1440:
                        resolution = "1440p"
                    elif height >= 1080:
                        resolution = "1080p"
                    elif height >= 720:
                        resolution = "720p"
                    elif height >= 480:
                        resolution = "480p"
                    else:
                        resolution = "360p"
                
                # Get format info
                format_id = info.get("format_id", "")
                format_note = info.get("format_note", "")
                video_format = format_note or format_id
                
                return {
                    "file_path": downloaded_file,
                    "file_size": file_size,
                    "duration": duration,
                    "resolution": resolution,
                    "format": video_format,
                    "width": width,
                    "height": height,
                    "ext": os.path.splitext(downloaded_file)[1],
                }
                
        except DownloadError as e:
            if "Private video" in str(e) or "Video unavailable" in str(e):
                raise VideoUnavailableError(f"Video unavailable: {url}") from e
            raise CustomDownloadError(f"Download error for {url}: {str(e)}") from e
        except ExtractorError as e:
            raise CustomDownloadError(f"Extraction error for {url}: {str(e)}") from e
        except Exception as e:
            raise CustomDownloadError(f"Unexpected error downloading {url}: {str(e)}") from e
