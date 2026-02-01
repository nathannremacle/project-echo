"""
Central orchestration service - coordinates all multi-channel operations
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.config import settings
from src.repositories.channel_repository import ChannelRepository
from src.repositories.video_repository import VideoRepository
from src.repositories.config_repository import ConfigRepository
from src.repositories.distribution_repository import DistributionRepository
from src.repositories.schedule_repository import ScheduleRepository
from src.services.orchestration.queue_service import QueueService
from src.services.orchestration.pipeline_service import PipelineService
from src.services.orchestration.channel_configuration_service import ChannelConfigurationService
from src.services.orchestration.github_repository_service import GitHubRepositoryService
from src.services.orchestration.scheduling_service import SchedulingService
from src.services.orchestration.video_distribution_service import VideoDistributionService
from src.services.youtube.statistics_service import YouTubeStatisticsService
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

logger = get_logger(__name__)


class CentralOrchestrationService:
    """Central service for coordinating all multi-channel operations"""

    def __init__(self, db: Session):
        self.db = db
        self.channel_repo = ChannelRepository(db)
        self.video_repo = VideoRepository(db)
        self.config_repo = ConfigRepository(db)
        self.distribution_repo = DistributionRepository(db)
        self.schedule_repo = ScheduleRepository(db)
        
        # Initialize all orchestration services
        self.queue_service = QueueService(db)
        self.pipeline_service = PipelineService(db)
        self.config_service = ChannelConfigurationService(db)
        # GitHub service only when GITHUB_TOKEN is set (avoids crash at startup)
        try:
            self.github_service = GitHubRepositoryService(db) if settings.GITHUB_TOKEN else None
        except Exception:
            self.github_service = None
        self.scheduling_service = SchedulingService(db)
        self.distribution_service = VideoDistributionService(db)
        self.stats_service = YouTubeStatisticsService(db)
        
        # Orchestration state
        self._is_running = False
        self._is_paused = False

    def start(self) -> Dict[str, Any]:
        """Start the orchestration system"""
        if self._is_running:
            raise ValidationError("Orchestration system is already running")
        
        self._is_running = True
        self._is_paused = False
        
        # Set system config
        self.config_repo.set("orchestration_running", True, "Orchestration system running status")
        self.config_repo.set("orchestration_started_at", datetime.utcnow().isoformat(), "Orchestration start time")
        
        logger.info("Central orchestration system started")
        
        return {
            "status": "started",
            "started_at": datetime.utcnow().isoformat(),
        }

    def stop(self) -> Dict[str, Any]:
        """Stop the orchestration system"""
        if not self._is_running:
            raise ValidationError("Orchestration system is not running")
        
        self._is_running = False
        self._is_paused = False
        
        # Set system config
        self.config_repo.set("orchestration_running", False, "Orchestration system running status")
        self.config_repo.set("orchestration_stopped_at", datetime.utcnow().isoformat(), "Orchestration stop time")
        
        logger.info("Central orchestration system stopped")
        
        return {
            "status": "stopped",
            "stopped_at": datetime.utcnow().isoformat(),
        }

    def pause(self) -> Dict[str, Any]:
        """Pause the orchestration system"""
        if not self._is_running:
            raise ValidationError("Orchestration system is not running")
        
        self._is_paused = True
        self.config_repo.set("orchestration_paused", True, "Orchestration system paused status")
        
        logger.info("Central orchestration system paused")
        
        return {"status": "paused"}

    def resume(self) -> Dict[str, Any]:
        """Resume the orchestration system"""
        if not self._is_running:
            raise ValidationError("Orchestration system is not running")
        
        self._is_paused = False
        self.config_repo.set("orchestration_paused", False, "Orchestration system paused status")
        
        logger.info("Central orchestration system resumed")
        
        return {"status": "resumed"}

    def get_status(self) -> Dict[str, Any]:
        """Get orchestration system status"""
        is_running = self.config_repo.get("orchestration_running") or False
        is_paused = self.config_repo.get("orchestration_paused") or False
        
        return {
            "running": is_running,
            "paused": is_paused,
            "started_at": self.config_repo.get("orchestration_started_at"),
            "stopped_at": self.config_repo.get("orchestration_stopped_at"),
        }

    def coordinate_publication(
        self,
        video_id: str,
        channel_ids: List[str],
        timing: str = "simultaneous",
        scheduled_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Coordinate publication across multiple channels
        
        Args:
            video_id: Video ID to publish
            channel_ids: List of channel IDs
            timing: Publication timing (simultaneous, staggered, independent)
            scheduled_at: Optional scheduled time (default: now + 1 hour)
            
        Returns:
            Dictionary with coordination results
        """
        if not self._is_running or self._is_paused:
            raise ValidationError("Orchestration system is not running or is paused")
        
        if scheduled_at is None:
            scheduled_at = datetime.utcnow() + timedelta(hours=1)
        
        logger.info(f"Coordinating publication of video {video_id} to {len(channel_ids)} channels ({timing})")
        
        if timing == "simultaneous":
            schedules = self.scheduling_service.create_simultaneous_schedule(
                video_id=video_id,
                channel_ids=channel_ids,
                scheduled_at=scheduled_at,
            )
        elif timing == "staggered":
            schedules = self.scheduling_service.create_staggered_schedule(
                video_id=video_id,
                channel_ids=channel_ids,
                start_time=scheduled_at,
                delay_seconds=3600,  # 1 hour between channels
            )
        else:
            # Independent - create separate schedules
            schedules = []
            for channel_id in channel_ids:
                schedule = self.scheduling_service.create_independent_schedule(
                    channel_id=channel_id,
                    scheduled_at=scheduled_at,
                    video_id=video_id,
                )
                schedules.append(schedule)
        
        logger.info(f"Created {len(schedules)} schedules for coordinated publication")
        
        return {
            "video_id": video_id,
            "channel_ids": channel_ids,
            "timing": timing,
            "scheduled_at": scheduled_at.isoformat(),
            "schedules_created": len(schedules),
            "schedule_ids": [s.id for s in schedules],
        }

    def trigger_pipeline(
        self,
        channel_id: str,
        video_id: Optional[str] = None,
        source_url: Optional[str] = None,
        skip_upload: bool = False,
    ) -> Dict[str, Any]:
        """
        Trigger pipeline for a channel (via GitHub Actions or direct execution)
        
        In central mode (no github_repo_url): runs pipeline directly in this process.
        In multi-repo mode: triggers GitHub Actions workflow.
        
        Args:
            channel_id: Channel ID
            video_id: Optional video ID (if None, will scrape new video)
            source_url: Optional source URL to scrape (YouTube, etc.)
            
        Returns:
            Dictionary with trigger results
        """
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        
        logger.info(f"Triggering pipeline for channel {channel_id}")
        
        # Check if channel has GitHub repository
        if channel.github_repo_url:
            if not self.github_service:
                raise ValidationError("GITHUB_TOKEN not configured - required for GitHub Actions")
            # Trigger via GitHub Actions
            result = self.github_service.trigger_workflow(
                channel_id=channel_id,
                workflow_type="process-video",
                client_payload={"video_id": video_id} if video_id else {},
            )
            return {
                "channel_id": channel_id,
                "method": "github_actions",
                "triggered": True,
                "workflow_type": "process-video",
            }
        else:
            # Central mode: run pipeline directly (no GitHub repo needed)
            result = self.pipeline_service.execute_pipeline(
                channel_id=channel_id,
                source_url=source_url,
                video_id=video_id,
                skip_upload=skip_upload,
            )
            return {
                "channel_id": channel_id,
                "method": "direct",
                "result": result,
            }

    def schedule_wave_publication(
        self,
        video_ids: List[str],
        channel_ids: List[str],
        wave_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Schedule viral wave publication
        
        Args:
            video_ids: List of video IDs
            channel_ids: List of channel IDs
            wave_config: Wave configuration (timing, delays, etc.)
            
        Returns:
            Dictionary with wave schedule results
        """
        if not self._is_running or self._is_paused:
            raise ValidationError("Orchestration system is not running or is paused")
        
        wave_id = wave_config.get("wave_id") or f"wave-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        timing = wave_config.get("timing", "simultaneous")
        scheduled_at = wave_config.get("scheduled_at")
        if scheduled_at:
            scheduled_at = datetime.fromisoformat(scheduled_at) if isinstance(scheduled_at, str) else scheduled_at
        else:
            scheduled_at = datetime.utcnow() + timedelta(hours=1)
        
        logger.info(f"Scheduling wave publication: {len(video_ids)} videos to {len(channel_ids)} channels")
        
        all_schedules = []
        
        # Distribute videos to channels
        for video_id in video_ids:
            if timing == "simultaneous":
                schedules = self.scheduling_service.create_simultaneous_schedule(
                    video_id=video_id,
                    channel_ids=channel_ids,
                    scheduled_at=scheduled_at,
                    wave_id=wave_id,
                )
            elif timing == "staggered":
                delay_seconds = wave_config.get("delay_seconds", 3600)
                schedules = self.scheduling_service.create_staggered_schedule(
                    video_id=video_id,
                    channel_ids=channel_ids,
                    start_time=scheduled_at,
                    delay_seconds=delay_seconds,
                    wave_id=wave_id,
                )
            else:
                # Independent - one video per channel
                schedules = []
                for channel_id in channel_ids:
                    schedule = self.scheduling_service.create_independent_schedule(
                        channel_id=channel_id,
                        scheduled_at=scheduled_at,
                        video_id=video_id,
                        metadata={"wave_id": wave_id},
                    )
                    schedules.append(schedule)
            
            all_schedules.extend(schedules)
        
        logger.info(f"Created {len(all_schedules)} schedules for wave {wave_id}")
        
        return {
            "wave_id": wave_id,
            "video_ids": video_ids,
            "channel_ids": channel_ids,
            "timing": timing,
            "scheduled_at": scheduled_at.isoformat(),
            "schedules_created": len(all_schedules),
        }

    def monitor_channels(self) -> List[Dict[str, Any]]:
        """
        Monitor health and status of all channels
        
        Returns:
            List of channel status dictionaries
        """
        channels = self.channel_repo.get_all()
        channel_statuses = []
        
        for channel in channels:
            status = {
                "channel_id": channel.id,
                "name": channel.name,
                "is_active": channel.is_active,
                "health": "unknown",
                "status": "unknown",
                "errors": [],
                "last_publication_at": channel.last_publication_at.isoformat() if channel.last_publication_at else None,
                "statistics": {},
            }
            
            # Check health
            try:
                # Two modes: central (no GitHub repo) vs multi-repo (with GitHub)
                if channel.github_repo_url:
                    # Multi-repo mode: channel has its own GitHub repo
                    if self.github_service:
                        repo_info = self.github_service.get_repository_info(channel.id)
                        if repo_info.get("exists"):
                            status["health"] = "healthy"
                        else:
                            status["health"] = "warning"
                            status["errors"].append("GitHub repository not found")
                    else:
                        status["health"] = "warning"
                        status["errors"].append("GITHUB_TOKEN not configured")
                else:
                    # Central mode: pipeline runs directly in this app - no GitHub repo needed
                    status["health"] = "healthy"
                    # Don't add to errors - central mode is valid and expected
                
                # Check channel status
                if channel.is_active:
                    status["status"] = "active"
                else:
                    status["status"] = "inactive"
                
                # Get recent statistics
                dist_stats = self.distribution_repo.get_statistics(
                    channel_id=channel.id,
                    start_date=datetime.utcnow() - timedelta(days=7),
                )
                status["statistics"] = {
                    "distributions_7d": dist_stats.get("total", 0),
                    "published_7d": dist_stats.get("published_count", 0),
                    "success_rate": dist_stats.get("success_rate", 0),
                }
                
            except Exception as e:
                status["health"] = "error"
                status["errors"].append(str(e))
                logger.error(f"Error monitoring channel {channel.id}: {e}")
            
            channel_statuses.append(status)
        
        return channel_statuses

    def distribute_videos(self) -> Dict[str, Any]:
        """
        Automatically assign videos to channels based on configuration
        
        Returns:
            Dictionary with distribution results
        """
        if not self._is_running or self._is_paused:
            raise ValidationError("Orchestration system is not running or is paused")
        
        logger.info("Running automatic video distribution")
        
        # Auto-distribute by filters
        filter_distributions = self.distribution_service.auto_distribute_by_filters()
        
        # Auto-distribute by schedule
        schedule_distributions = self.distribution_service.auto_distribute_by_schedule()
        
        total = len(filter_distributions) + len(schedule_distributions)
        
        logger.info(f"Distributed {total} videos ({len(filter_distributions)} by filters, {len(schedule_distributions)} by schedule)")
        
        return {
            "total_distributed": total,
            "by_filters": len(filter_distributions),
            "by_schedule": len(schedule_distributions),
            "distributions": [
                {"id": d.id, "video_id": d.video_id, "channel_id": d.channel_id, "method": d.distribution_method}
                for d in filter_distributions + schedule_distributions
            ],
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get status dashboard data (all channels, system health)
        
        Returns:
            Dictionary with dashboard data
        """
        # System status
        system_status = self.get_status()
        
        # Channel monitoring
        channel_statuses = self.monitor_channels()
        
        # Overall statistics
        overall_stats = self.distribution_repo.get_statistics(
            start_date=datetime.utcnow() - timedelta(days=30),
        )
        
        # Recent schedules
        recent_schedules = self.schedule_repo.get_pending_schedules(
            before=datetime.utcnow() + timedelta(days=7),
        )
        
        # Queue status
        queue_paused = self.queue_service.is_paused()
        
        return {
            "system": {
                "status": system_status,
                "queue_paused": queue_paused,
            },
            "channels": {
                "total": len(channel_statuses),
                "active": sum(1 for c in channel_statuses if c["is_active"]),
                "statuses": channel_statuses,
            },
            "statistics": {
                "overall": overall_stats,
                "period": "30_days",
            },
            "schedules": {
                "pending": len(recent_schedules),
                "upcoming_7d": len(recent_schedules),
            },
        }

    def sync_channel_configs(self) -> Dict[str, Any]:
        """
        Sync configurations across channel repositories
        
        Returns:
            Dictionary with sync results
        """
        if not self._is_running or self._is_paused:
            raise ValidationError("Orchestration system is not running or is paused")
        
        channels = self.channel_repo.get_all(active_only=True)
        synced = 0
        errors = []
        
        for channel in channels:
            try:
                if channel.github_repo_url and self.github_service:
                    # Sync secrets
                    secrets_info = self.github_service.sync_secrets_from_channel(channel.id)
                    logger.info(f"Synced secrets for channel {channel.id}")
                    synced += 1
            except Exception as e:
                error_msg = f"Channel {channel.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            "synced": synced,
            "total": len(channels),
            "errors": errors,
        }
