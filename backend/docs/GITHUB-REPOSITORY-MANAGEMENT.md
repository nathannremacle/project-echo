# GitHub Repository Management Documentation

## Overview

This guide explains how to create and manage GitHub repositories for YouTube channels. Each channel has its own repository with independent GitHub Actions workflows and secrets.

## Prerequisites

1. **GitHub Token**: `GITHUB_TOKEN` environment variable with GitHub personal access token
2. **Permissions**: Token must have `repo` scope (full control of private repositories)
3. **Channel Configuration**: Channel must exist in database

## Creating a Channel Repository

### Create Repository via API

```python
from src.database import SessionLocal
from src.services.orchestration.github_repository_service import GitHubRepositoryService

db = SessionLocal()
service = GitHubRepositoryService(db)

# Create GitHub repository for channel
result = service.create_channel_repository(
    channel_id="channel-uuid",
    repo_name="project-echo-channel-my-channel",  # Optional
    description="Project Echo channel repository",  # Optional
    private=True,  # Default: True
)

print(f"Repository created: {result['repository_url']}")
```

### Setup from Template

```python
# Get setup instructions from template
result = service.setup_repository_from_template(
    channel_id="channel-uuid",
    workflow_schedule="0 */6 * * *",  # Every 6 hours
)

# Follow instructions to complete setup
for instruction in result["instructions"]:
    print(instruction)
```

## Workflow Configuration

### Configure Workflow Schedule

```python
# Update workflow schedule
service.configure_workflow(
    channel_id="channel-uuid",
    schedule="0 */6 * * *",  # Every 6 hours
)
```

### Workflow Triggers

Workflows support multiple triggers:

- **workflow_dispatch**: Manual trigger from GitHub UI
- **schedule**: Scheduled trigger (cron)
- **repository_dispatch**: Triggered by central system via API

## GitHub Secrets Management

### Sync Secrets from Channel

```python
# Get secrets that should be set
secrets_info = service.sync_secrets_from_channel("channel-uuid")

print("Secrets to set:")
for name, value in secrets_info["secrets"].items():
    print(f"  {name}: {value[:10]}...")  # Don't print full value
```

### Required Secrets

Each channel repository needs these secrets:

- `CHANNEL_ID`: Channel UUID from central system
- `YOUTUBE_CLIENT_ID`: YouTube API client ID
- `YOUTUBE_CLIENT_SECRET`: YouTube API client secret
- `YOUTUBE_REFRESH_TOKEN`: OAuth refresh token
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `ENCRYPTION_KEY`: Encryption key for credentials

**Note**: GitHub Secrets must be set manually via GitHub UI or GitHub CLI. The service provides the values but cannot set them directly (requires repository public key encryption).

## Triggering Workflows

### Trigger Workflow via API

```python
# Trigger workflow with payload
result = service.trigger_workflow(
    channel_id="channel-uuid",
    workflow_type="process-video",
    client_payload={
        "video_id": "video-uuid",
        "preset_id": "preset-uuid",
    },
)

print(f"Workflow triggered: {result['triggered']}")
```

### Workflow Payload

The `client_payload` is passed to the workflow and accessible via:

```yaml
# In workflow
${{ github.event.client_payload.video_id }}
${{ github.event.client_payload.preset_id }}
```

## Repository Information

### Get Repository Info

```python
info = service.get_repository_info("channel-uuid")

if info["exists"]:
    print(f"Repository: {info['repository_url']}")
    print(f"Private: {info['private']}")
    print(f"Default branch: {info['default_branch']}")
else:
    print("Repository does not exist")
```

## Repository Management

### Update Workflow

Workflows can be updated programmatically:

```python
service.configure_workflow(
    channel_id="channel-uuid",
    schedule="0 12 * * *",  # Daily at 12:00 UTC
)
```

### Link Repository to Channel

After creating a repository, it's automatically linked:

```python
# Repository URL is stored in channel.github_repo_url
channel = channel_repo.get_by_id("channel-uuid")
print(f"Repository: {channel.github_repo_url}")
```

## Manual Setup Process

If you prefer manual setup:

1. **Copy Template:**
   ```bash
   cp -r templates/channel-repo-template project-echo-channel-{name}
   cd project-echo-channel-{name}
   ```

2. **Initialize Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Create GitHub Repository:**
   - Create repository on GitHub
   - Link and push:
     ```bash
     git remote add origin https://github.com/user/repo.git
     git push -u origin main
     ```

4. **Set GitHub Secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add all required secrets

5. **Link in Database:**
   ```python
   channel.github_repo_url = "https://github.com/user/repo"
   channel_repo.update(channel)
   ```

## Workflow Templates

### Default Workflow Schedule

Default schedule: Every 6 hours (`0 */6 * * *`)

### Custom Schedules

Examples:
- Daily at 12:00 UTC: `0 12 * * *`
- Every 4 hours: `0 */4 * * *`
- Weekdays at 18:00: `0 18 * * 1-5`
- Twice daily: `0 8,20 * * *`

## Error Handling

### Common Errors

#### Repository Already Exists

```python
ValidationError: GitHub repository project-echo-channel-name already exists
```

**Solution**: Use different repository name or delete existing repository.

#### No GitHub Token

```python
ValidationError: GITHUB_TOKEN not configured in environment variables
```

**Solution**: Set `GITHUB_TOKEN` environment variable.

#### Repository Not Found

```python
ProcessingError: Failed to get repository info: 404
```

**Solution**: Verify repository URL is correct and repository exists.

#### Insufficient Permissions

```python
ProcessingError: Failed to create GitHub repository: 403
```

**Solution**: Check GitHub token has `repo` scope.

## Best Practices

1. **Private Repositories**: Use private repositories for security
2. **Unique Names**: Ensure repository names are unique
3. **Secrets Security**: Never commit secrets to repository
4. **Workflow Testing**: Test workflows before enabling schedules
5. **Repository Linking**: Always link repository URL in database
6. **Token Security**: Store GitHub token securely (environment variable, not in code)

## Automation

### Automated Repository Creation

For bulk channel setup:

```python
channels = channel_repo.get_all()

for channel in channels:
    if not channel.github_repo_url:
        try:
            result = service.create_channel_repository(channel.id)
            print(f"Created repository for {channel.name}: {result['repository_url']}")
        except Exception as e:
            print(f"Failed to create repository for {channel.name}: {e}")
```

## Related Documentation

- [Multi-Repository Architecture](../../docs/MULTI-REPO-ARCHITECTURE.md)
- [GitHub Actions Setup](../../docs/GITHUB-ACTIONS-SETUP.md)
- [Channel Configuration](./CHANNEL-CONFIGURATION.md)
