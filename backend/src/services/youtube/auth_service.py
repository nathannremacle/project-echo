"""
YouTube authentication service
Handles OAuth 2.0 authentication and token management for YouTube Data API v3
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models.channel import Channel
from src.repositories.channel_repository import ChannelRepository
from src.utils.encryption import encrypt_dict, decrypt_dict
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, AuthenticationError

logger = get_logger(__name__)

# OAuth 2.0 scopes required for YouTube Data API v3
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtubepartner",
]


class YouTubeAuthService:
    """Service for YouTube API authentication and credential management"""

    def __init__(self, db: Session):
        self.db = db
        self.channel_repo = ChannelRepository(db)

    def get_oauth_flow(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> Flow:
        """
        Create OAuth 2.0 flow for user authorization
        
        Args:
            client_id: OAuth client ID from Google Cloud Console
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            
        Returns:
            OAuth flow object
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=YOUTUBE_SCOPES,
        )
        flow.redirect_uri = redirect_uri
        return flow

    def get_authorization_url(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        state: Optional[str] = None,
    ) -> str:
        """
        Get authorization URL for OAuth flow
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        flow = self.get_oauth_flow(client_id, client_secret, redirect_uri)
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes=True,
            prompt="consent",  # Force consent to get refresh token
            state=state,
        )
        return authorization_url

    def exchange_code_for_credentials(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        authorization_code: str,
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for credentials (including refresh token)
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Dictionary with credentials (client_id, client_secret, refresh_token, etc.)
        """
        try:
            flow = self.get_oauth_flow(client_id, client_secret, redirect_uri)
            flow.fetch_token(code=authorization_code)
            
            credentials = flow.credentials
            
            # Extract credentials
            creds_dict = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": credentials.refresh_token,
                "token": credentials.token,
                "token_uri": credentials.token_uri,
                "client_id_from_creds": credentials.client_id,
                "client_secret_from_creds": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            }
            
            logger.info("Successfully exchanged authorization code for credentials")
            return creds_dict
            
        except Exception as e:
            logger.error(f"Failed to exchange authorization code: {e}")
            raise AuthenticationError(f"Failed to exchange authorization code: {str(e)}")

    def store_credentials(self, channel_id: str, credentials: Dict[str, Any]) -> None:
        """
        Store encrypted credentials for a channel
        
        Args:
            channel_id: Channel ID
            credentials: Credentials dictionary to store
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Encrypt credentials
        encrypted = encrypt_dict(credentials)
        channel.api_credentials_encrypted = encrypted
        self.channel_repo.update(channel)
        
        logger.info(f"Stored credentials for channel {channel_id}")

    def get_credentials(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get decrypted credentials for a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Decrypted credentials dictionary or None if not found
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        if not channel.api_credentials_encrypted:
            return None
        
        try:
            return decrypt_dict(channel.api_credentials_encrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt credentials for channel {channel_id}: {e}")
            raise AuthenticationError(f"Failed to decrypt credentials: {str(e)}")

    def get_authenticated_credentials(self, channel_id: str) -> Credentials:
        """
        Get authenticated Google Credentials object for a channel
        Automatically refreshes token if expired
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Google Credentials object ready for API calls
        """
        creds_dict = self.get_credentials(channel_id)
        if not creds_dict:
            raise AuthenticationError(f"No credentials found for channel {channel_id}")
        
        # Create Credentials object
        credentials = Credentials(
            token=creds_dict.get("token"),
            refresh_token=creds_dict.get("refresh_token"),
            token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=creds_dict.get("client_id") or creds_dict.get("client_id_from_creds"),
            client_secret=creds_dict.get("client_secret") or creds_dict.get("client_secret_from_creds"),
            scopes=creds_dict.get("scopes", YOUTUBE_SCOPES),
        )
        
        # Set expiry if available
        if creds_dict.get("expiry"):
            credentials.expiry = datetime.fromisoformat(creds_dict["expiry"])
        
        # Refresh token if expired or about to expire (within 5 minutes)
        if credentials.expired or (credentials.expiry and credentials.expiry <= datetime.utcnow() + timedelta(minutes=5)):
            try:
                credentials.refresh(Request())
                
                # Update stored credentials with new token
                creds_dict["token"] = credentials.token
                creds_dict["expiry"] = credentials.expiry.isoformat() if credentials.expiry else None
                self.store_credentials(channel_id, creds_dict)
                
                logger.info(f"Refreshed token for channel {channel_id}")
            except Exception as e:
                logger.error(f"Failed to refresh token for channel {channel_id}: {e}")
                raise AuthenticationError(f"Failed to refresh token: {str(e)}")
        
        return credentials

    def validate_authentication(self, channel_id: str) -> bool:
        """
        Validate authentication for a channel by making a test API call
        
        Args:
            channel_id: Channel ID
            
        Returns:
            True if authentication is valid, False otherwise
        """
        try:
            credentials = self.get_authenticated_credentials(channel_id)
            
            # Make a test API call to verify authentication
            youtube = build("youtube", "v3", credentials=credentials)
            request = youtube.channels().list(part="snippet", mine=True, maxResults=1)
            response = request.execute()
            
            # If we get a response, authentication is valid
            return True
            
        except HttpError as e:
            if e.resp.status == 401:
                logger.warning(f"Authentication invalid for channel {channel_id}: Unauthorized")
                return False
            elif e.resp.status == 403:
                logger.warning(f"Authentication invalid for channel {channel_id}: Forbidden (check scopes)")
                return False
            else:
                logger.error(f"API error validating authentication for channel {channel_id}: {e}")
                return False
        except Exception as e:
            logger.error(f"Error validating authentication for channel {channel_id}: {e}")
            return False

    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel information from YouTube API
        
        Args:
            channel_id: Channel ID (database ID, not YouTube channel ID)
            
        Returns:
            Channel information dictionary or None if not found
        """
        try:
            credentials = self.get_authenticated_credentials(channel_id)
            youtube = build("youtube", "v3", credentials=credentials)
            
            request = youtube.channels().list(part="snippet,statistics", mine=True, maxResults=1)
            response = request.execute()
            
            if response.get("items"):
                return response["items"][0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting channel info for channel {channel_id}: {e}")
            raise AuthenticationError(f"Failed to get channel info: {str(e)}")
