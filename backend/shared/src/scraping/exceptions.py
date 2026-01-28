"""
Scraping-specific exceptions
"""


class ScrapingError(Exception):
    """Base exception for scraping errors"""
    pass


class RateLimitError(ScrapingError):
    """Raised when rate limited by source platform"""
    pass


class VideoUnavailableError(ScrapingError):
    """Raised when video is unavailable (deleted, private, etc.)"""
    pass


class ConfigurationError(ScrapingError):
    """Raised when scraping configuration is invalid"""
    pass
