# YouTube API Authentication Documentation

## Overview

This guide explains how to set up and use YouTube Data API v3 authentication for Project Echo. The system uses OAuth 2.0 to authenticate with YouTube on behalf of each channel.

## Prerequisites

1. **Google Cloud Console Project**: You need a Google Cloud project with YouTube Data API v3 enabled
2. **OAuth 2.0 Credentials**: Client ID and Client Secret from Google Cloud Console
3. **Encryption Key**: `ENCRYPTION_KEY` environment variable (32+ characters) for encrypting stored credentials

## Setting Up YouTube API Credentials

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (for testing) or Internal (for Google Workspace)
   - App name: "Project Echo"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add the following:
     - `https://www.googleapis.com/auth/youtube.upload`
     - `https://www.googleapis.com/auth/youtube`
     - `https://www.googleapis.com/auth/youtubepartner`
   - Save and continue
4. Create OAuth client ID:
   - Application type: **Web application**
   - Name: "Project Echo Web Client"
   - Authorized redirect URIs: Add your callback URL (e.g., `http://localhost:8000/callback`)
   - Click "Create"
5. **Save the Client ID and Client Secret** - you'll need these for authentication

### Step 3: Configure Environment Variables

Set the following environment variables (or add to `.env` file):

```bash
# Encryption key (32+ characters, random string)
ENCRYPTION_KEY=your-32-character-or-longer-encryption-key-here

# Optional: Default YouTube API credentials (can also be set per-channel)
YOUTUBE_API_CLIENT_ID=your-client-id
YOUTUBE_API_CLIENT_SECRET=your-client-secret
```

**Important**: The `ENCRYPTION_KEY` is critical for security. Generate a strong random key:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## OAuth 2.0 Authentication Flow

### Step 1: Get Authorization URL

```python
from src.services.youtube.auth_service import YouTubeAuthService

service = YouTubeAuthService(db)

authorization_url = service.get_authorization_url(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8000/callback",
    state="optional-csrf-state",
)
```

### Step 2: User Authorization

1. Redirect user to `authorization_url`
2. User authorizes the application
3. Google redirects to `redirect_uri` with an authorization code

### Step 3: Exchange Code for Credentials

```python
credentials = service.exchange_code_for_credentials(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8000/callback",
    authorization_code=code_from_callback,
)
```

### Step 4: Store Credentials

```python
service.store_credentials(
    channel_id="channel-uuid",
    credentials=credentials,
)
```

Credentials are automatically encrypted before storage.

## Using Authenticated YouTube Client

### Get Authenticated Client

```python
from src.services.youtube.client import YouTubeClient

client = YouTubeClient(db, channel_id="channel-uuid")

# Validate connection
if client.validate_connection():
    print("Authentication valid")
else:
    print("Authentication invalid")

# Get channel info
channel_info = client.get_channel_info()
```

### Automatic Token Refresh

The `YouTubeClient` automatically refreshes access tokens when they expire. You don't need to manually handle token refresh.

## Per-Channel Credentials

Each channel has its own OAuth credentials stored encrypted in the database:

- **Storage**: `Channel.api_credentials_encrypted` (encrypted JSON)
- **Encryption**: Uses AES-256 encryption via `ENCRYPTION_KEY`
- **Isolation**: Each channel's credentials are completely separate

### Setting Credentials for a Channel

```python
from src.services.youtube.auth_service import YouTubeAuthService

service = YouTubeAuthService(db)

# After OAuth flow, store credentials
service.store_credentials(
    channel_id=channel.id,
    credentials={
        "client_id": "...",
        "client_secret": "...",
        "refresh_token": "...",
        # ... other fields
    },
)
```

### Retrieving Credentials

```python
credentials = service.get_credentials(channel_id)
```

## Authentication Validation

### Check Authentication Status

```python
is_valid = service.validate_authentication(channel_id)
```

This makes a test API call to verify:
- Credentials are valid
- Access token is not expired
- API permissions are correct

### Get Channel Information

```python
channel_info = service.get_channel_info(channel_id)
```

Returns channel information from YouTube API, validating authentication in the process.

## Error Handling

The authentication service handles various error scenarios:

### Invalid Credentials

```python
try:
    credentials = service.get_authenticated_credentials(channel_id)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Token Refresh Failure

If token refresh fails, the service raises `AuthenticationError` with details. Common causes:
- Refresh token revoked
- Invalid client credentials
- Network errors

### API Errors

The `YouTubeClient` handles API errors:
- **401 Unauthorized**: Credentials invalid, re-authenticate
- **403 Forbidden**: Quota exceeded or insufficient permissions
- **429 Rate Limit**: Too many requests, retry later

## Security Best Practices

1. **Encryption Key**: Use a strong, random `ENCRYPTION_KEY` (32+ characters)
2. **Environment Variables**: Never commit credentials to version control
3. **GitHub Secrets**: Use GitHub Secrets for credentials in CI/CD
4. **Per-Channel Isolation**: Each channel has separate credentials
5. **Token Refresh**: Tokens are automatically refreshed, but monitor for failures
6. **Error Logging**: Authentication errors are logged for monitoring

## GitHub Actions Integration

For GitHub Actions workflows, pass credentials as secrets:

```yaml
env:
  YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
  YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
  ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
```

Then use them in the OAuth flow:

```python
client_id = os.getenv("YOUTUBE_CLIENT_ID")
client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
```

## Troubleshooting

### "No credentials found for channel"

- Ensure credentials were stored using `store_credentials()`
- Check that `channel_id` is correct
- Verify encryption/decryption is working

### "Failed to refresh token"

- Check that refresh token is valid (not revoked)
- Verify client ID and secret are correct
- Check network connectivity to Google OAuth servers

### "Authentication invalid"

- Run `validate_authentication()` to get detailed error
- Check that OAuth scopes are correct
- Verify channel has valid credentials stored

### "Encryption failed"

- Ensure `ENCRYPTION_KEY` is set
- Verify key is 32+ characters
- Check that key hasn't changed (would break decryption)

## API Scopes

The following scopes are required:

- `https://www.googleapis.com/auth/youtube.upload` - Upload videos
- `https://www.googleapis.com/auth/youtube` - Manage YouTube account
- `https://www.googleapis.com/auth/youtubepartner` - Access YouTube Partner features

## Rate Limits

YouTube Data API v3 has rate limits:

- **Default Quota**: 10,000 units per day (free tier)
- **Video Upload**: 1,600 units per upload
- **Video List**: 1 unit per request
- **Channel List**: 1 unit per request

Monitor quota usage to avoid exhaustion.

## Related Documentation

- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Project Echo Architecture](../../docs/architecture.md)
