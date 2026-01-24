"""
Video filtering utilities for quality and viral content
"""

from typing import Dict, Any, Optional
import re


def filter_by_resolution(metadata: Dict[str, Any], min_resolution: str) -> bool:
    """
    Filter video by minimum resolution
    
    Args:
        metadata: Video metadata dictionary
        min_resolution: Minimum resolution (e.g., '720p', '1080p')
        
    Returns:
        True if video meets resolution requirement
    """
    resolution = metadata.get("resolution")
    if not resolution:
        return False
    
    resolution_order = ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
    try:
        res_idx = resolution_order.index(resolution)
        min_idx = resolution_order.index(min_resolution)
        return res_idx >= min_idx
    except ValueError:
        return False


def filter_by_views(metadata: Dict[str, Any], min_views: Optional[int]) -> bool:
    """
    Filter video by minimum view count
    
    Args:
        metadata: Video metadata dictionary
        min_views: Minimum view count (None to skip filter)
        
    Returns:
        True if video meets view count requirement
    """
    if min_views is None:
        return True
    
    view_count = metadata.get("view_count")
    if view_count is None:
        # If view count not available, assume it doesn't meet requirement
        return False
    
    return view_count >= min_views


def filter_by_duration(metadata: Dict[str, Any], max_duration: Optional[int]) -> bool:
    """
    Filter video by maximum duration
    
    Args:
        metadata: Video metadata dictionary
        max_duration: Maximum duration in seconds (None to skip filter)
        
    Returns:
        True if video meets duration requirement
    """
    if max_duration is None:
        return True
    
    duration = metadata.get("duration", 0)
    return duration > 0 and duration <= max_duration


def detect_watermark(metadata: Dict[str, Any]) -> bool:
    """
    Basic watermark detection (placeholder for future implementation)
    
    Currently checks title/description for common watermark patterns.
    Future: Could use OpenCV for visual watermark detection.
    
    Args:
        metadata: Video metadata dictionary
        
    Returns:
        True if watermark detected, False otherwise
    """
    # Common watermark patterns in titles/descriptions
    watermark_patterns = [
        r"@\w+",  # @username mentions
        r"watermark",
        r"subscribe.*channel",
        r"follow.*@",
    ]
    
    title = metadata.get("title", "").lower()
    description = metadata.get("description", "").lower()
    
    text = f"{title} {description}"
    
    for pattern in watermark_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def filter_watermarked(metadata: Dict[str, Any], exclude_watermarked: bool) -> bool:
    """
    Filter watermarked videos
    
    Args:
        metadata: Video metadata dictionary
        exclude_watermarked: Whether to exclude watermarked videos
        
    Returns:
        True if video should be included (not watermarked or watermark allowed)
    """
    if not exclude_watermarked:
        return True
    
    return not detect_watermark(metadata)


def apply_filters(
    metadata: Dict[str, Any],
    min_resolution: str = "720p",
    min_views: Optional[int] = None,
    max_duration: Optional[int] = None,
    exclude_watermarked: bool = True,
) -> bool:
    """
    Apply all filters to video metadata
    
    Args:
        metadata: Video metadata dictionary
        min_resolution: Minimum resolution requirement
        min_views: Minimum view count requirement
        max_duration: Maximum duration requirement
        exclude_watermarked: Whether to exclude watermarked videos
        
    Returns:
        True if video passes all filters
    """
    if not filter_by_resolution(metadata, min_resolution):
        return False
    
    if not filter_by_views(metadata, min_views):
        return False
    
    if not filter_by_duration(metadata, max_duration):
        return False
    
    if not filter_watermarked(metadata, exclude_watermarked):
        return False
    
    return True
