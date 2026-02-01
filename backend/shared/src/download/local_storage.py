"""
Local file storage for video files (development fallback when S3 is not configured)
Stores files in a local directory and returns file:// URLs
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from shared.src.download.exceptions import StorageError


class LocalStorageClient:
    """Local file storage client for development (when S3 credentials are not configured)"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize local storage client

        Args:
            base_dir: Base directory for storing files (default: ./data/videos)
        """
        self.base_dir = Path(base_dir or os.path.join(os.getcwd(), "data", "videos"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_local_path(self, channel_id: str, video_id: str, filename: str) -> Path:
        """Generate local file path for video"""
        channel_id = channel_id.replace("/", "_")
        video_id = video_id.replace("/", "_")
        filename = os.path.basename(filename)
        dir_path = self.base_dir / channel_id / video_id
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / filename

    def upload_file(
        self,
        local_file_path: str,
        channel_id: str,
        video_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Copy file to local storage (simulates upload)

        Args:
            local_file_path: Path to local file
            channel_id: Channel ID
            video_id: Video ID
            metadata: Optional metadata (ignored for local storage)

        Returns:
            file:// URL of stored file
        """
        if not os.path.exists(local_file_path):
            raise StorageError(f"Local file not found: {local_file_path}")

        filename = os.path.basename(local_file_path)
        dest_path = self._generate_local_path(channel_id, video_id, filename)

        try:
            shutil.copy2(local_file_path, dest_path)
            # Return file:// URL (use Path.as_uri() for cross-platform)
            file_url = Path(dest_path).resolve().as_uri()
            return file_url
        except Exception as e:
            raise StorageError(f"Failed to copy file to local storage: {str(e)}") from e

    @staticmethod
    def get_local_path(file_url: str) -> str:
        """
        Extract local file path from file:// URL (cross-platform)

        Args:
            file_url: file:// URL

        Returns:
            Local file path
        """
        from urllib.parse import urlparse
        from urllib.request import url2pathname

        if not file_url.startswith("file://"):
            raise StorageError(f"Invalid file URL (expected file://): {file_url}")
        parsed = urlparse(file_url)
        return url2pathname(parsed.path)
