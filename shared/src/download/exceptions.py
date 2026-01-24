"""
Download-specific exceptions
"""


class DownloadError(Exception):
    """Base exception for download errors"""
    pass


class VideoUnavailableError(DownloadError):
    """Raised when video is unavailable (deleted, private, etc.)"""
    pass


class StorageError(DownloadError):
    """Raised when storage operation fails"""
    pass
