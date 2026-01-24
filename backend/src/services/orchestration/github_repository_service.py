"""
GitHub repository management service
Handles creation, configuration, and management of channel repositories
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from github import Github
from github.GithubException import GithubException

from src.repositories.channel_repository import ChannelRepository
from src.services.youtube.auth_service import YouTubeAuthService
from src.utils.encryption import decrypt_dict
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError
from src.config import settings

logger = get_logger(__name__)


class GitHubRepositoryService:
    """Service for managing GitHub repositories for channels"""

    def __init__(self, db: Session):
        self.db = db
        self.channel_repo = ChannelRepository(db)
        self.auth_service = YouTubeAuthService(db)
        
        # Initialize GitHub client
        github_token = settings.GITHUB_TOKEN
        if not github_token:
            raise ValidationError("GITHUB_TOKEN not configured in environment variables")
        self.github = Github(github_token)
        self.user = self.github.get_user()

    def create_channel_repository(
        self,
        channel_id: str,
        repo_name: Optional[str] = None,
        description: Optional[str] = None,
        private: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new GitHub repository for a channel
        
        Args:
            channel_id: Channel ID (database ID)
            repo_name: Optional repository name (default: project-echo-channel-{channel_name})
            description: Optional repository description
            private: Whether repository is private (default: True)
            
        Returns:
            Dictionary with repository information
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Generate repository name if not provided
        if not repo_name:
            # Sanitize channel name for repository name
            safe_name = channel.name.lower().replace(" ", "-").replace("_", "-")
            safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
            repo_name = f"project-echo-channel-{safe_name}"
        
        try:
            # Check if repository already exists
            try:
                existing_repo = self.user.get_repo(repo_name)
                if existing_repo:
                    raise ValidationError(f"GitHub repository {repo_name} already exists")
            except GithubException as e:
                if e.status != 404:
                    raise
            
            # Create repository
            repo = self.user.create_repo(
                name=repo_name,
                description=description or f"Project Echo channel repository for {channel.name}",
                private=private,
                auto_init=False,  # We'll push files manually
            )
            
            logger.info(f"Created GitHub repository {repo_name} for channel {channel_id}")
            
            # Update channel with repository URL
            channel.github_repo_url = repo.html_url
            self.channel_repo.update(channel)
            
            return {
                "repository_name": repo_name,
                "repository_url": repo.html_url,
                "repository_id": repo.id,
                "clone_url": repo.clone_url,
            }
            
        except GithubException as e:
            logger.error(f"Failed to create GitHub repository: {e}")
            raise ProcessingError(f"Failed to create GitHub repository: {str(e)}")

    def setup_repository_from_template(
        self,
        channel_id: str,
        repo_name: Optional[str] = None,
        workflow_schedule: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set up channel repository from template (local file system)
        
        Args:
            channel_id: Channel ID
            repo_name: Optional repository name
            workflow_schedule: Optional cron schedule for workflow (e.g., "0 */6 * * *")
            
        Returns:
            Dictionary with setup results
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        # Get template directory
        template_dir = Path(__file__).parent.parent.parent.parent.parent / "templates" / "channel-repo-template"
        if not template_dir.exists():
            raise ProcessingError(f"Template directory not found: {template_dir}")
        
        # Generate repository name if not provided
        if not repo_name:
            safe_name = channel.name.lower().replace(" ", "-").replace("_", "-")
            safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
            repo_name = f"project-echo-channel-{safe_name}"
        
        # Create local directory (outside workspace for now, as template suggests)
        # In production, this would be handled differently
        logger.info(f"Repository setup from template would create: {repo_name}")
        logger.info("Note: Actual file system operations should be done via script or separate process")
        
        # Return repository information
        return {
            "repository_name": repo_name,
            "template_location": str(template_dir),
            "instructions": [
                f"1. Copy template: cp -r {template_dir} ../{repo_name}",
                f"2. Create GitHub repository: {repo_name}",
                f"3. Link and push: git remote add origin <repo-url> && git push",
                f"4. Configure GitHub Secrets",
                f"5. Update channel.github_repo_url in database",
            ],
        }

    def configure_workflow(
        self,
        channel_id: str,
        schedule: Optional[str] = None,
        triggers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Configure GitHub Actions workflow for a channel
        
        Args:
            channel_id: Channel ID
            schedule: Optional cron schedule (e.g., "0 */6 * * *")
            triggers: Optional list of trigger types (workflow_dispatch, schedule, repository_dispatch)
            
        Returns:
            Dictionary with workflow configuration
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        if not channel.github_repo_url:
            raise ValidationError(f"Channel {channel_id} has no GitHub repository URL")
        
        # Extract repository name from URL
        repo_name = channel.github_repo_url.split("/")[-1]
        
        try:
            repo = self.user.get_repo(repo_name)
            
            # Get workflow file
            workflow_path = ".github/workflows/process-video.yaml"
            try:
                workflow_file = repo.get_contents(workflow_path)
                workflow_content = workflow_file.decoded_content.decode("utf-8")
            except GithubException:
                # Workflow doesn't exist yet, use template
                template_path = Path(__file__).parent.parent.parent.parent.parent / "templates" / "channel-repo-template" / ".github" / "workflows" / "process-video.yaml"
                if template_path.exists():
                    workflow_content = template_path.read_text()
                else:
                    raise ProcessingError(f"Workflow template not found: {template_path}")
            
            # Update workflow schedule if provided
            if schedule:
                # Update cron schedule in workflow content
                pattern = r"schedule:\s*\n\s*-\s*cron:\s*['\"](.*?)['\"]"
                if re.search(pattern, workflow_content):
                    workflow_content = re.sub(
                        pattern,
                        f"schedule:\n    - cron: '{schedule}'",
                        workflow_content,
                    )
                else:
                    # Add schedule if not present
                    schedule_section = f"  schedule:\n    - cron: '{schedule}'\n"
                    workflow_content = workflow_content.replace(
                        "  repository_dispatch:",
                        schedule_section + "  repository_dispatch:",
                    )
            
            # Update workflow file
            repo.update_file(
                path=workflow_path,
                message=f"Update workflow schedule for channel {channel.name}",
                content=workflow_content,
                sha=workflow_file.sha if 'workflow_file' in locals() else None,
            )
            
            logger.info(f"Updated workflow configuration for repository {repo_name}")
            
            return {
                "repository_name": repo_name,
                "workflow_path": workflow_path,
                "schedule": schedule,
                "updated": True,
            }
            
        except GithubException as e:
            logger.error(f"Failed to configure workflow: {e}")
            raise ProcessingError(f"Failed to configure workflow: {str(e)}")

    def create_or_update_secret(
        self,
        channel_id: str,
        secret_name: str,
        secret_value: str,
    ) -> None:
        """
        Create or update a GitHub Secret for a channel repository
        
        Args:
            channel_id: Channel ID
            secret_name: Secret name (e.g., YOUTUBE_CLIENT_ID)
            secret_value: Secret value
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        if not channel.github_repo_url:
            raise ValidationError(f"Channel {channel_id} has no GitHub repository URL")
        
        repo_name = channel.github_repo_url.split("/")[-1]
        
        try:
            repo = self.user.get_repo(repo_name)
            
            # Note: PyGithub doesn't directly support creating secrets
            # This would require using GitHub API directly or a library that supports it
            # For now, we log the instruction
            logger.info(f"Secret {secret_name} should be set for repository {repo_name}")
            logger.info("Note: GitHub Secrets must be set manually via GitHub UI or GitHub CLI")
            logger.info(f"Repository: {repo.html_url}/settings/secrets/actions")
            
            # In a full implementation, this would use GitHub API directly:
            # POST /repos/{owner}/{repo}/actions/secrets/{secret_name}
            # With encrypted value using repository's public key
            
        except GithubException as e:
            logger.error(f"Failed to manage secret: {e}")
            raise ProcessingError(f"Failed to manage secret: {str(e)}")

    def sync_secrets_from_channel(
        self,
        channel_id: str,
    ) -> Dict[str, Any]:
        """
        Sync GitHub Secrets from channel configuration
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dictionary with secrets that should be set
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        if not channel.github_repo_url:
            raise ValidationError(f"Channel {channel_id} has no GitHub repository URL")
        
        # Get channel credentials
        try:
            credentials = self.auth_service.get_credentials(channel_id)
        except Exception as e:
            logger.warning(f"Could not decrypt credentials for channel {channel_id}: {e}")
            credentials = None
        
        # Prepare secrets
        secrets = {
            "CHANNEL_ID": channel_id,
        }
        
        if credentials:
            secrets["YOUTUBE_CLIENT_ID"] = credentials.get("client_id", "")
            secrets["YOUTUBE_CLIENT_SECRET"] = credentials.get("client_secret", "")
            secrets["YOUTUBE_REFRESH_TOKEN"] = credentials.get("refresh_token", "")
        
        # Note: Actual secret creation requires GitHub API with encryption
        # For now, return the secrets that should be set
        logger.info(f"Secrets to set for channel {channel_id}: {list(secrets.keys())}")
        
        return {
            "repository_url": channel.github_repo_url,
            "secrets": secrets,
            "instructions": "Set these secrets in GitHub repository settings",
        }

    def trigger_workflow(
        self,
        channel_id: str,
        workflow_type: str = "process-video",
        client_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Trigger a workflow in a channel repository
        
        Args:
            channel_id: Channel ID
            workflow_type: Workflow dispatch type (default: "process-video")
            client_payload: Optional payload to pass to workflow
            
        Returns:
            Dictionary with trigger result
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        if not channel.github_repo_url:
            raise ValidationError(f"Channel {channel_id} has no GitHub repository URL")
        
        repo_name = channel.github_repo_url.split("/")[-1]
        
        try:
            repo = self.user.get_repo(repo_name)
            
            # Trigger repository_dispatch event
            repo.create_repository_dispatch(
                event_type=workflow_type,
                client_payload=client_payload or {},
            )
            
            logger.info(f"Triggered workflow {workflow_type} for repository {repo_name}")
            
            return {
                "repository_name": repo_name,
                "workflow_type": workflow_type,
                "triggered": True,
            }
            
        except GithubException as e:
            logger.error(f"Failed to trigger workflow: {e}")
            raise ProcessingError(f"Failed to trigger workflow: {str(e)}")

    def get_repository_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get information about channel's GitHub repository
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dictionary with repository information
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        if not channel.github_repo_url:
            return {"repository_url": None, "exists": False}
        
        repo_name = channel.github_repo_url.split("/")[-1]
        
        try:
            repo = self.user.get_repo(repo_name)
            
            return {
                "repository_name": repo_name,
                "repository_url": repo.html_url,
                "repository_id": repo.id,
                "private": repo.private,
                "exists": True,
                "default_branch": repo.default_branch,
            }
            
        except GithubException as e:
            if e.status == 404:
                return {"repository_url": channel.github_repo_url, "exists": False}
            raise ProcessingError(f"Failed to get repository info: {str(e)}")
