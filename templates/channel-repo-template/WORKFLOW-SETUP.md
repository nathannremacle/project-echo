# Channel Repository Workflow Setup

This guide explains how to set up and use the GitHub Actions workflow for video processing in your channel repository.

## Quick Start

1. **Copy workflow to your channel repo:**
   - The workflow file is already in `.github/workflows/process-video.yaml`
   - No changes needed if using the template

2. **Configure GitHub Secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add all 6 required secrets (see below)

3. **Update shared library URL:**
   - Edit `.github/workflows/process-video.yaml`
   - Replace `your-username` with your GitHub username

4. **Test the workflow:**
   - Go to Actions tab
   - Click "Process and Publish Video"
   - Click "Run workflow"

## Required GitHub Secrets

Add these secrets in your channel repository:

| Secret | Description | Where to Get It |
|--------|-------------|-----------------|
| `YOUTUBE_CLIENT_ID` | YouTube API OAuth client ID | Google Cloud Console |
| `YOUTUBE_CLIENT_SECRET` | YouTube API OAuth client secret | Google Cloud Console |
| `YOUTUBE_REFRESH_TOKEN` | OAuth refresh token | Generated via OAuth flow |
| `AWS_ACCESS_KEY_ID` | AWS access key | AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | AWS IAM Console |
| `CHANNEL_ID` | Channel UUID | Central orchestration system |

**Setting Secrets:**
1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"

## Workflow Triggers

### Manual Trigger

1. Go to **Actions** tab
2. Select **Process and Publish Video**
3. Click **Run workflow**
4. Optionally provide:
   - Video URL (or leave empty for auto-discovery)
   - Preset ID (default: "default")
5. Click **Run workflow**

### Scheduled Trigger

The workflow runs automatically on a schedule defined in the workflow file:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

**Customize Schedule:**
- Edit `.github/workflows/process-video.yaml`
- Update the cron expression
- See [GitHub Actions documentation](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) for cron syntax

### API Trigger (Repository Dispatch)

Trigger from central orchestration system:

```python
from github import Github

github = Github(token=GITHUB_TOKEN)
repo = github.get_repo("username/project-echo-channel-name")
repo.create_repository_dispatch(
    event_type="process-video",
    client_payload={
        "video_url": "https://example.com/video.mp4",
        "preset_id": "default"
    }
)
```

## Workflow Steps

The workflow executes these steps:

1. **Checkout repository** - Gets the latest code
2. **Set up Python** - Installs Python 3.11 with caching
3. **Install system dependencies** - Installs FFmpeg
4. **Install Python dependencies** - Installs shared libraries and requirements
5. **Verify Python environment** - Confirms setup is correct
6. **Configure AWS credentials** - Sets up S3 access
7. **Create logs directory** - Prepares for logging
8. **Process video** - Executes video processing (or test script)
9. **Upload logs** - Saves logs as artifacts
10. **Report workflow status** - Final status check

## Testing the Workflow

### First Test

1. **Set up secrets** (use dummy values for testing if needed)
2. **Run workflow manually:**
   - Actions → Process and Publish Video → Run workflow
3. **Check execution:**
   - Watch steps execute in real-time
   - Review logs for each step
4. **Verify test script:**
   - The workflow runs `scripts/test_workflow.py`
   - This validates environment setup

### Test Script Output

The test script checks:
- ✅ All environment variables are set
- ✅ Python version is correct
- ✅ FFmpeg is installed
- ✅ Python packages are available
- ✅ Workflow arguments are passed

### Common Issues

**Secrets not found:**
- Verify secret names match exactly (case-sensitive)
- Check secrets are in correct repository
- Ensure secrets are under "Actions" (not "Dependencies")

**FFmpeg not found:**
- Check "Install system dependencies" step
- Verify `sudo apt-get install -y ffmpeg` succeeded

**Python import errors:**
- Check shared library URL is correct
- Verify `requirements.txt` exists (can be empty)
- Check Python version is 3.11+

## Monitoring

### View Workflow Runs

1. Go to **Actions** tab
2. Click on workflow name
3. View run history
4. Click on a run to see details

### Download Logs

1. After workflow completes, find **Artifacts** section
2. Download `processing-logs-{run-id}`
3. Extract and review `logs/workflow.log`

### Check Usage

1. Repository → Settings → Actions → Usage
2. View minutes used this month
3. Monitor remaining quota

## Customization

### Update Schedule

Edit `.github/workflows/process-video.yaml`:

```yaml
schedule:
  - cron: '0 10,18 * * *'  # 10:00 and 18:00 daily
```

### Change Shared Library URL

```yaml
pip install git+https://github.com/YOUR-USERNAME/project-echo-orchestration.git#subdirectory=shared
```

### Add Channel-Specific Dependencies

Create `requirements.txt` in channel repo root:

```txt
custom-package==1.0.0
another-package==2.0.0
```

### Customize AWS Region

```yaml
aws-region: us-west-2  # Change from us-east-1
```

## Troubleshooting

See [GitHub Actions Setup Guide](../../docs/GITHUB-ACTIONS-SETUP.md) for detailed troubleshooting.

## Next Steps

After workflow is set up and tested:
1. Register channel in central orchestration system
2. Configure channel settings (posting schedule, presets)
3. Enable scheduled triggers (if desired)
4. Monitor workflow executions

---

For more information, see:
- [GitHub Actions Setup Guide](../../docs/GITHUB-ACTIONS-SETUP.md)
- [Multi-Repository Architecture Guide](../../docs/MULTI-REPO-ARCHITECTURE.md)
