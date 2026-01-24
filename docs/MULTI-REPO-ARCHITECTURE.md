# Multi-Repository Architecture Guide

This document explains the multi-repository architecture used by Project Echo and how to create and manage channel repositories.

## Overview

Project Echo uses a **multi-repository architecture** where:
- **Central Orchestration Repository** (this repo): Manages coordination, provides management interface, contains shared libraries
- **Channel Repositories** (one per YouTube channel): Independent repos with channel-specific workflows and secrets

## Why Multi-Repository?

**Benefits:**
- **Security:** Each channel has isolated GitHub Secrets (credentials can't leak between channels)
- **Independence:** Channels can be managed, updated, and scaled independently
- **Isolation:** Problems with one channel don't affect others
- **Flexibility:** Each channel can have custom workflows and configurations

**Trade-offs:**
- More repositories to manage
- Requires orchestration system to coordinate
- Shared code must be distributed (via Python packages or Git submodules)

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│  Central Orchestration Repository       │
│  - React Frontend (Management UI)      │
│  - FastAPI Backend (Orchestration)     │
│  - Shared Libraries                     │
│  - Channel Repo Template               │
└──────────────┬──────────────────────────┘
               │
               │ Coordinates
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Channel │ │Channel │ │Channel │
│ Repo 1 │ │ Repo 2 │ │ Repo N │
│        │ │        │ │        │
│ GitHub │ │ GitHub │ │ GitHub │
│Actions │ │Actions │ │Actions │
└────────┘ └────────┘ └────────┘
```

## Creating a New Channel Repository

### Method 1: Using the Setup Script (Recommended)

```bash
# From central orchestration repo root
./scripts/setup-channel-repo.sh channel-name

# This will:
# 1. Copy the template to project-echo-channel-{name}
# 2. Initialize Git repository
# 3. Set up basic configuration
# 4. Provide instructions for next steps
```

### Method 2: Manual Setup

1. **Copy the template:**
   ```bash
   cp -r templates/channel-repo-template project-echo-channel-{name}
   cd project-echo-channel-{name}
   ```

2. **Initialize Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Channel repository setup"
   ```

3. **Create GitHub repository:**
   - Create a new repository on GitHub: `project-echo-channel-{name}`
   - Link local repo to GitHub:
     ```bash
     git remote add origin https://github.com/your-username/project-echo-channel-{name}.git
     git push -u origin main
     ```

4. **Configure channel:**
   - Edit `config/channel.yaml` with channel-specific settings
   - See [Channel Configuration](#channel-configuration) below

5. **Set up GitHub Secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add required secrets (see [GitHub Secrets](#github-secrets) below)

6. **Register in central system:**
   - Channel must be registered in the central orchestration database
   - Use the management interface or API to register the channel

## Channel Configuration

Each channel repository has a `config/channel.yaml` file that defines:

- **Channel Identity:** Name, YouTube channel ID
- **Posting Schedule:** Frequency, times, days
- **Effect Presets:** Which transformation preset to use
- **Content Filters:** What types of videos to scrape
- **Metadata Templates:** Title, description, tags templates

Example configuration:
```yaml
channel:
  name: "Gaming Edits"
  youtube_channel_id: "UC1234567890"
  schedule:
    frequency: "daily"
    times: ["10:00", "18:00"]
  effect_preset_id: "gaming-style"
  enabled: true
```

## GitHub Secrets

Each channel repository requires the following GitHub Secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `YOUTUBE_CLIENT_ID` | YouTube API OAuth client ID | `123456789-abc.apps.googleusercontent.com` |
| `YOUTUBE_CLIENT_SECRET` | YouTube API OAuth client secret | `GOCSPX-xxxxxxxxxxxx` |
| `YOUTUBE_REFRESH_TOKEN` | OAuth refresh token for this channel | `1//xxx...` |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 storage | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `CHANNEL_ID` | UUID of channel (from central system) | `550e8400-e29b-41d4-a716-446655440000` |

**Setting Secrets:**
1. Go to channel repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with appropriate value

**Security Note:** Never commit secrets to the repository. Always use GitHub Secrets.

## GitHub Actions Workflow

Each channel repository has a workflow (`.github/workflows/process-video.yaml`) that:

- **Triggers:** Manual, scheduled (cron), or via repository dispatch
- **Executes:** Video processing pipeline (download → transform → upload)
- **Uses:** GitHub Secrets for credentials
- **Runs:** On ubuntu-latest runner

**Workflow Triggers:**
- `workflow_dispatch`: Manual trigger from GitHub Actions UI
- `schedule`: Cron-based automatic triggers
- `repository_dispatch`: Triggered by central orchestration system

## Shared Code Distribution

Channel repositories use shared libraries from the central repo. Two options:

### Option 1: Python Package (Recommended)

```bash
# In channel repo workflow or script
pip install git+https://github.com/user/project-echo-orchestration.git#subdirectory=shared
```

**Benefits:**
- Clean installation
- Version control via Git tags
- Easy updates

### Option 2: Git Submodule

```bash
# In channel repo
git submodule add https://github.com/user/project-echo-orchestration.git shared
git submodule update --init --recursive
```

**Benefits:**
- Version pinning
- Direct access to source

**Recommendation:** Use Python Package (Option 1) for simplicity.

## Central Orchestration Integration

The central orchestration system:

1. **Manages Channels:** Registers and tracks all channel repositories
2. **Coordinates Operations:** Schedules and distributes videos across channels
3. **Monitors Status:** Tracks channel health, processing status, errors
4. **Provides Interface:** Web UI for managing all channels

**Channel Registration:**
- Channel must be registered in central database
- Registration links channel repo to central system
- Central system can trigger channel workflows via GitHub API

## Workflow Example

1. **Central system scrapes video** → Stores in S3
2. **Central system schedules publication** → Assigns video to channels
3. **Central system triggers channel workflow** → Via GitHub API repository_dispatch
4. **Channel workflow runs** → Downloads, transforms, uploads to YouTube
5. **Channel workflow reports status** → Updates central system

## Troubleshooting

### Channel workflow not running
- Check GitHub Secrets are set correctly
- Verify workflow file syntax
- Check GitHub Actions logs for errors

### Shared libraries not found
- Ensure shared library is installed correctly
- Check Python path and imports
- Verify Git repository access

### Configuration not loading
- Check `config/channel.yaml` syntax (YAML)
- Verify file is in correct location
- Check for YAML parsing errors

## Best Practices

1. **One Channel Per Repo:** Never mix multiple channels in one repository
2. **Isolate Secrets:** Each channel has its own GitHub Secrets
3. **Version Control:** Keep channel repos in version control
4. **Documentation:** Document channel-specific customizations
5. **Testing:** Test channel workflows before production use

## Migration Guide

If you need to migrate a channel to a new repository:

1. Copy channel configuration from old repo
2. Create new repo from template
3. Update channel configuration
4. Set up GitHub Secrets in new repo
5. Update central system with new repo URL
6. Test workflow execution
7. Archive old repository

---

For more information, see:
- [Central Repository README](../README.md)
- [Architecture Document](../architecture.md)
- [Development Workflow](../architecture.md#development-workflow)
