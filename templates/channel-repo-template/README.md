# Project Echo Channel Repository Template

This is a template for creating new YouTube channel repositories. Each channel operates in its own isolated repository with independent GitHub Actions workflows and secrets.

## Quick Start

1. **Create new repository from this template:**
   ```bash
   # Copy this template to create a new channel repo
   cp -r templates/channel-repo-template project-echo-channel-{name}
   cd project-echo-channel-{name}
   ```

2. **Configure channel settings:**
   - Edit `config/channel.yaml` with channel-specific configuration
   - Set channel name, posting schedule, effect presets, etc.

3. **Set up GitHub Secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `YOUTUBE_CLIENT_ID` - YouTube API client ID for this channel
     - `YOUTUBE_CLIENT_SECRET` - YouTube API client secret
     - `YOUTUBE_REFRESH_TOKEN` - OAuth refresh token
     - `AWS_ACCESS_KEY_ID` - AWS credentials for storage
     - `AWS_SECRET_ACCESS_KEY` - AWS secret key
     - `CHANNEL_ID` - UUID of channel (from central orchestration system)

4. **Update workflow configuration:**
   - Edit `.github/workflows/process-video.yaml`
   - Replace `your-username` with your GitHub username in shared library URL
   - Customize schedule cron expression if needed

5. **Test the workflow:**
   - Go to Actions tab → Process and Publish Video
   - Click "Run workflow" to test
   - Verify all steps complete successfully

6. **Register channel in central system:**
   - Channel must be registered in the central orchestration repository
   - Central system will coordinate this channel's operations

## Repository Structure

```
project-echo-channel-{name}/
├── .github/
│   └── workflows/
│       └── process-video.yaml    # Channel-specific workflow
├── config/
│   ├── channel.yaml              # Channel configuration
│   └── .gitignore                # Ignore sensitive configs
├── scripts/                       # Channel-specific scripts
│   ├── test_workflow.py          # Workflow test script
│   └── README.md
├── logs/                          # Workflow logs (gitignored)
│   └── .gitkeep
├── requirements.txt               # Channel-specific dependencies
├── .gitignore
├── README.md
└── WORKFLOW-SETUP.md             # Workflow setup guide
```

## Configuration

Edit `config/channel.yaml` to configure:
- Channel name and YouTube channel ID
- Posting schedule (frequency, timing)
- Effect presets (transformation preferences)
- Content filters (what types of edits to scrape)
- Metadata templates (title, description, tags)

## GitHub Actions Workflow

The workflow (`process-video.yaml`) can be triggered:
- **Manually:** Via GitHub Actions UI (workflow_dispatch)
- **On Schedule:** Cron-based triggers (configure in workflow file)
- **Via API:** Repository dispatch events from central orchestration

**Workflow Features:**
- Automatic Python 3.11 setup with caching
- FFmpeg installation for video processing
- Shared library installation from central repo
- AWS credentials configuration
- Comprehensive logging and error reporting
- Artifact uploads for debugging

## Testing

The workflow includes a test script (`scripts/test_workflow.py`) that validates:
- Environment variables are set correctly
- Python environment is configured
- System dependencies (FFmpeg) are available
- Workflow arguments are passed correctly

**Run test manually:**
```bash
python scripts/test_workflow.py \
  --channel-id "test-id" \
  --video-url "auto" \
  --preset "default"
```

## Integration with Central System

This channel repository is coordinated by the central orchestration system:
- Central system manages video scraping and processing
- Central system schedules publications across all channels
- This repo executes the actual video processing and upload via GitHub Actions

## Documentation

For more information, see:
- [Workflow Setup Guide](WORKFLOW-SETUP.md) - Detailed workflow configuration
- [GitHub Actions Setup Guide](../../docs/GITHUB-ACTIONS-SETUP.md) - Complete setup guide
- [Multi-Repository Architecture Guide](../../docs/MULTI-REPO-ARCHITECTURE.md) - Architecture overview
- [Central Orchestration Repository README](../../README.md) - Main repository docs
