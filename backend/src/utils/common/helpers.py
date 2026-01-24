"""
Common helper functions
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


def generate_request_id() -> str:
    """Generate a unique request ID"""
    return generate_uuid()


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """Hash a string using the specified algorithm"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(value.encode("utf-8"))
    return hash_obj.hexdigest()


def generate_random_string(length: int = 32) -> str:
    """Generate a random string of specified length"""
    return secrets.token_urlsafe(length)


def get_current_timestamp() -> str:
    """Get current UTC timestamp as ISO 8601 string"""
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO 8601 timestamp string to datetime"""
    return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))


def safe_get(dictionary: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values"""
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result


def truncate_string(value: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length with suffix"""
    if len(value) <= max_length:
        return value
    return value[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    sanitized = "".join(c if c not in invalid_chars else "_" for c in filename)
    return sanitized.strip()


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable string"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def validate_youtube_channel_id(channel_id: str) -> bool:
    """Validate YouTube channel ID format"""
    if not channel_id:
        return False
    # YouTube channel IDs start with UC and are 24 characters
    return channel_id.startswith("UC") and len(channel_id) == 24


def validate_youtube_video_id(video_id: str) -> bool:
    """Validate YouTube video ID format"""
    if not video_id:
        return False
    # YouTube video IDs are 11 characters
    return len(video_id) == 11
