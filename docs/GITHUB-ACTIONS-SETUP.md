# GitHub Actions Setup Guide

This guide explains how to set up and configure GitHub Actions workflows for Project Echo.

## Overview

Project Echo uses GitHub Actions for:
- **Central Repository:** CI/CD pipeline (testing, linting, deployment)
- **Channel Repositories:** Video processing and publication workflows

## Central Repository Workflows

### CI Pipeline (`.github/workflows/ci.yaml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
1. **Frontend Tests:** Linting, type checking, unit tests
2. **Backend Tests:** Linting, type checking, unit tests with coverage
3. **Build Frontend:** Production build (only on `main` branch)

**No Secrets Required:** This workflow runs tests only, no external service credentials needed.

### Deployment Workflow (`.github/workflows/deploy.yaml`)

**Triggers:**
- Push to `main` branch
- Manual trigger (workflow_dispatch)

**Jobs:**
1. **Deploy Frontend:** Builds and deploys to Vercel

**Required Secrets:**
- `VERCEL_TOKEN` - Vercel deployment token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID

**Setting Up Vercel Secrets:**
1. Go to repository Settings → Secrets and variables → Actions
2. Add each secret with values from your Vercel dashboard

## Channel Repository Workflows

### Process Video Workflow (`.github/workflows/process-video.yaml`)

**Triggers:**
- **Manual:** Via GitHub Actions UI (workflow_dispatch)
- **Scheduled:** Cron-based (configurable in workflow file)
- **API:** Repository dispatch from central orchestration system

**Workflow Steps:**
1. Checkout repository
2. Set up Python 3.11
3. Install system dependencies (FFmpeg)
4. Install Python dependencies
5. Configure AWS credentials
6. Process and publish video
7. Upload logs as artifacts

### Required GitHub Secrets (Per Channel)

Each channel repository requires the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `YOUTUBE_CLIENT_ID` | YouTube API OAuth client ID | `123456789-abc.apps.googleusercontent.com` |
| `YOUTUBE_CLIENT_SECRET` | YouTube API OAuth client secret | `GOCSPX-xxxxxxxxxxxx` |
| `YOUTUBE_REFRESH_TOKEN` | OAuth refresh token for this channel | `1//xxx...` |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 storage | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `CHANNEL_ID` | UUID of channel (from central system) | `550e8400-e29b-41d4-a716-446655440000` |

### Setting Up Channel Repository Secrets

1. **Navigate to Channel Repository:**
   - Go to your channel repository on GitHub
   - Example: `https://github.com/your-username/project-echo-channel-{name}`

2. **Access Secrets Settings:**
   - Click **Settings** → **Secrets and variables** → **Actions**

3. **Add Each Secret:**
   - Click **New repository secret**
   - Enter secret name (exactly as listed above)
   - Enter secret value
   - Click **Add secret**

4. **Verify Secrets:**
   - All 6 secrets should be listed
   - Secrets are encrypted and cannot be viewed after creation

### Configuring the Workflow

1. **Update Shared Library URL:**
   ```yaml
   # In .github/workflows/process-video.yaml
   pip install git+https://github.com/your-username/project-echo-orchestration.git#subdirectory=shared
   ```
   Replace `your-username` with your GitHub username.

2. **Customize Schedule:**
   ```yaml
   schedule:
     - cron: '0 */6 * * *'  # Every 6 hours
   ```
   Update the cron expression to match your channel's posting schedule.

3. **Update AWS Region (if needed):**
   ```yaml
   aws-region: us-east-1  # Change if using different region
   ```

## Testing the Workflow

### Manual Test

1. **Go to Channel Repository:**
   - Navigate to **Actions** tab
   - Select **Process and Publish Video** workflow
   - Click **Run workflow**
   - Optionally provide inputs (video_url, preset_id)
   - Click **Run workflow**

2. **Monitor Execution:**
   - Watch workflow steps execute in real-time
   - Check logs for each step
   - Verify all steps complete successfully

3. **Check Artifacts:**
   - After workflow completes, download logs artifact
   - Review `logs/workflow.log` for execution details

### Test Script

The workflow includes a test script (`scripts/test_workflow.py`) that validates:
- Environment variables are set
- Python environment is correct
- System dependencies (FFmpeg) are available
- Workflow arguments are passed correctly

**Run Test Script Locally:**
```bash
python scripts/test_workflow.py \
  --channel-id "test-channel-id" \
  --video-url "auto" \
  --preset "default"
```

## Workflow Optimization

### Free Tier Limits

GitHub Actions free tier includes:
- **2,000 minutes/month** for private repositories
- **500 minutes/month** for public repositories
- **6-hour maximum** job duration
- **20 concurrent jobs** maximum

### Optimization Tips

1. **Cache Dependencies:**
   - Python dependencies are cached automatically
   - pnpm cache is configured for frontend

2. **Conditional Steps:**
   - Use `if:` conditions to skip unnecessary steps
   - Only build on `main` branch

3. **Timeout Settings:**
   - Video processing: 360 minutes (6 hours max)
   - CI tests: Default timeout (usually sufficient)

4. **Parallel Jobs:**
   - Frontend and backend tests run in parallel
   - Reduces total workflow time

## Troubleshooting

### Workflow Fails to Start

**Problem:** Workflow doesn't trigger
- **Solution:** Check workflow file syntax (YAML)
- **Solution:** Verify trigger conditions (branch names, event types)

### Secrets Not Found

**Problem:** `Error: Secret not found`
- **Solution:** Verify secret name matches exactly (case-sensitive)
- **Solution:** Check that secrets are set in correct repository
- **Solution:** Ensure secrets are added under "Actions" (not "Dependencies")

### Python Dependencies Fail

**Problem:** `ModuleNotFoundError` or import errors
- **Solution:** Check `requirements.txt` exists and is valid
- **Solution:** Verify shared library URL is correct
- **Solution:** Check Python version (must be 3.11+)

### FFmpeg Not Found

**Problem:** `ffmpeg: command not found`
- **Solution:** Workflow should install FFmpeg automatically
- **Solution:** Check "Install system dependencies" step logs
- **Solution:** Verify `sudo apt-get install -y ffmpeg` step succeeded

### AWS Credentials Error

**Problem:** `Invalid credentials` or AWS access denied
- **Solution:** Verify AWS secrets are correct
- **Solution:** Check AWS IAM permissions for S3 access
- **Solution:** Verify AWS region matches your bucket region

### Workflow Times Out

**Problem:** Workflow exceeds 6-hour limit
- **Solution:** Optimize video processing (reduce quality, duration)
- **Solution:** Split processing into multiple workflows
- **Solution:** Consider upgrading GitHub Actions plan

### Logs Not Uploaded

**Problem:** Artifacts missing or empty
- **Solution:** Check `logs/` directory exists
- **Solution:** Verify `if: always()` condition on upload step
- **Solution:** Check artifact retention settings

## Monitoring Workflow Usage

### Check Usage

1. Go to repository **Settings** → **Actions** → **Usage**
2. View:
   - Minutes used this month
   - Remaining minutes
   - Job execution history

### Set Usage Limits

1. Go to repository **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Configure:
   - Workflow permissions
   - Actions and reusable workflows
   - Artifact and log retention

## Best Practices

1. **Never Commit Secrets:**
   - Always use GitHub Secrets
   - Never hardcode credentials in workflow files
   - Use environment variables for secrets

2. **Test Workflows Locally:**
   - Use `act` tool to test workflows locally
   - Validate YAML syntax before committing

3. **Monitor Usage:**
   - Check usage regularly to avoid exceeding limits
   - Optimize workflows to reduce execution time

4. **Use Workflow Templates:**
   - Start from template in `templates/channel-repo-template/`
   - Customize only what's necessary

5. **Document Customizations:**
   - Add comments in workflow files
   - Document any channel-specific changes

## Advanced Configuration

### Repository Dispatch (API Trigger)

Trigger workflows from central orchestration system:

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

### Custom Schedule Expressions

Cron syntax: `minute hour day month day-of-week`

Examples:
- `0 */6 * * *` - Every 6 hours
- `0 10,18 * * *` - At 10:00 and 18:00 daily
- `0 0 * * 1` - Every Monday at midnight
- `0 0 1 * *` - First day of every month

### Matrix Strategy (Multiple Channels)

Process multiple videos in parallel:

```yaml
strategy:
  matrix:
    channel: [channel1, channel2, channel3]
```

## Support

For issues or questions:
1. Check workflow logs for error messages
2. Review this documentation
3. Check GitHub Actions documentation: https://docs.github.com/en/actions
4. Review Project Echo architecture documentation

---

**Last Updated:** 2026-01-23
