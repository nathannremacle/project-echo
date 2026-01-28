"""
Shared scraping utilities
"""

from shared.src.scraping.youtube_scraper import YouTubeScraper
from shared.src.scraping.filters import (
    filter_by_resolution,
    filter_by_views,
    filter_by_duration,
    detect_watermark,
    filter_watermarked,
    apply_filters,
)
from shared.src.scraping.exceptions import (
    ScrapingError,
    RateLimitError,
    VideoUnavailableError,
    ConfigurationError,
)

__all__ = [
    "YouTubeScraper",
    "filter_by_resolution",
    "filter_by_views",
    "filter_by_duration",
    "detect_watermark",
    "filter_watermarked",
    "apply_filters",
    "ScrapingError",
    "RateLimitError",
    "VideoUnavailableError",
    "ConfigurationError",
]
