"""
YouTube API client wrapper
Provides authenticated access to YouTube Data API v3
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.services.youtube.auth_service import YouTubeAuthService
from src.utils.logging import get_logger
from src.utils.exceptions import AuthenticationError

logger = get_logger(__name__)


class YouTubeClient:
    """Authenticated YouTube API client wrapper"""

    def __init__(self, db: Session, channel_id: str):
        """
        Initialize YouTube client for a channel
        
        Args:
            db: Database session
            channel_id: Channel ID (database ID)
        """
        self.db = db
        self.channel_id = channel_id
        self.auth_service = YouTubeAuthService(db)
        self._youtube = None

    @property
    def youtube(self):
        """
        Get authenticated YouTube API service object
        Lazily initializes and refreshes credentials as needed
        """
        if self._youtube is None:
            credentials = self.auth_service.get_authenticated_credentials(self.channel_id)
            self._youtube = build("youtube", "v3", credentials=credentials)
        return self._youtube

    def validate_connection(self) -> bool:
        """
        Validate API connection by making a test call
        
        Returns:
            True if connection is valid, False otherwise
        """
        return self.auth_service.validate_authentication(self.channel_id)

    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """
        Get authenticated channel information
        
        Returns:
            Channel information dictionary or None
        """
        return self.auth_service.get_channel_info(self.channel_id)

    def _handle_api_error(self, error: HttpError, operation: str) -> None:
        """
        Handle YouTube API errors with appropriate error messages
        
        Args:
            error: HttpError from API call
            operation: Description of the operation that failed
        """
        status = error.resp.status
        error_details = error.error_details if hasattr(error, "error_details") else str(error)
        
        if status == 401:
            raise AuthenticationError(f"Authentication failed for {operation}: Unauthorized. Please re-authenticate.")
        elif status == 403:
            if "quotaExceeded" in str(error_details):
                raise AuthenticationError(f"YouTube API quota exceeded for {operation}. Please wait or request quota increase.")
            else:
                raise AuthenticationError(f"Access forbidden for {operation}: {error_details}. Check API permissions and scopes.")
        elif status == 404:
            raise NotFoundError(f"Resource not found for {operation}: {error_details}", resource_type="youtube_resource")
        elif status == 429:
            raise AuthenticationError(f"Rate limit exceeded for {operation}. Please retry after rate limit resets.")
        else:
            raise AuthenticationError(f"YouTube API error for {operation}: {error_details} (Status: {status})")
