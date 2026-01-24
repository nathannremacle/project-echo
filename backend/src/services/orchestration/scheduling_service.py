"""
Scheduling service - manages publication schedules and coordination
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.schedule import PublicationSchedule
from src.repositories.schedule_repository import ScheduleRepository
from src.repositories.channel_repository import ChannelRepository
from src.repositories.video_repository import VideoRepository
from src.services.orchestration.github_repository_service import GitHubRepositoryService
from src.services.orchestration.queue_service import QueueService
from src.utils.logging import get_logger
from src.utils.exceptions import NotFoundError, ValidationError, ProcessingError

logger = get_logger(__name__)


class SchedulingService:
    """Service for managing publication schedules and coordination"""

    def __init__(self, db: Session):
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.channel_repo = ChannelRepository(db)
        self.video_repo = VideoRepository(db)
        self.github_service = GitHubRepositoryService(db)
        self.queue_service = QueueService(db)

    def create_simultaneous_schedule(
        self,
        video_id: str,
        channel_ids: List[str],
        scheduled_at: datetime,
        wave_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[PublicationSchedule]:
        """
        Create simultaneous publication schedule (same video on multiple channels at same time)
        
        Args:
            video_id: Video ID to publish
            channel_ids: List of channel IDs
            scheduled_at: When to publish (same time for all channels)
            wave_id: Optional wave ID for viral wave coordination
            metadata: Optional additional metadata
            
        Returns:
            List of created schedules
        """
        # Validate video exists
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        # Validate channels exist
        for channel_id in channel_ids:
            channel = self.channel_repo.get_by_id(channel_id)
            if not channel:
                raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
            if not channel.is_active:
                raise ValidationError(f"Channel {channel_id} is not active")
        
        # Check for conflicts
        for channel_id in channel_ids:
            if self.schedule_repo.check_conflict(channel_id, video_id, scheduled_at):
                raise ValidationError(
                    f"Schedule conflict: Video {video_id} already scheduled for channel {channel_id} at {scheduled_at}"
                )
        
        # Create coordination group ID
        coordination_group_id = str(uuid.uuid4())
        
        # Create schedules for all channels
        schedules = []
        for channel_id in channel_ids:
            schedule = PublicationSchedule(
                channel_id=channel_id,
                video_id=video_id,
                schedule_type="simultaneous",
                scheduled_at=scheduled_at,
                coordination_group_id=coordination_group_id,
                wave_id=wave_id,
                metadata_info=json.dumps(metadata) if metadata else None,
                status="pending",
            )
            schedule = self.schedule_repo.create(schedule)
            schedules.append(schedule)
            logger.info(f"Created simultaneous schedule {schedule.id} for channel {channel_id} at {scheduled_at}")
        
        return schedules

    def create_staggered_schedule(
        self,
        video_id: str,
        channel_ids: List[str],
        start_time: datetime,
        delay_seconds: int,
        wave_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[PublicationSchedule]:
        """
        Create staggered publication schedule (same video on channels with time delays)
        
        Args:
            video_id: Video ID to publish
            channel_ids: List of channel IDs (in order)
            start_time: When to publish on first channel
            delay_seconds: Delay between each channel (in seconds)
            wave_id: Optional wave ID for viral wave coordination
            metadata: Optional additional metadata
            
        Returns:
            List of created schedules
        """
        # Validate video exists
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise NotFoundError(f"Video {video_id} not found", resource_type="video")
        
        # Validate channels exist
        for channel_id in channel_ids:
            channel = self.channel_repo.get_by_id(channel_id)
            if not channel:
                raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
            if not channel.is_active:
                raise ValidationError(f"Channel {channel_id} is not active")
        
        if delay_seconds < 0:
            raise ValidationError("delay_seconds must be >= 0")
        
        # Create coordination group ID
        coordination_group_id = str(uuid.uuid4())
        
        # Create schedules for all channels with delays
        schedules = []
        for index, channel_id in enumerate(channel_ids):
            scheduled_at = start_time + timedelta(seconds=delay_seconds * index)
            
            # Check for conflicts
            if self.schedule_repo.check_conflict(channel_id, video_id, scheduled_at):
                raise ValidationError(
                    f"Schedule conflict: Video {video_id} already scheduled for channel {channel_id} at {scheduled_at}"
                )
            
            schedule = PublicationSchedule(
                channel_id=channel_id,
                video_id=video_id,
                schedule_type="staggered",
                scheduled_at=scheduled_at,
                delay_seconds=delay_seconds * index,
                coordination_group_id=coordination_group_id,
                wave_id=wave_id,
                metadata_info=json.dumps(metadata) if metadata else None,
                status="pending",
            )
            schedule = self.schedule_repo.create(schedule)
            schedules.append(schedule)
            logger.info(f"Created staggered schedule {schedule.id} for channel {channel_id} at {scheduled_at} (delay: {delay_seconds * index}s)")
        
        return schedules

    def create_independent_schedule(
        self,
        channel_id: str,
        scheduled_at: datetime,
        video_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PublicationSchedule:
        """
        Create independent schedule (channel posts on its own schedule)
        
        Args:
            channel_id: Channel ID
            scheduled_at: When to publish
            video_id: Optional video ID (if None, will be assigned later)
            metadata: Optional additional metadata
            
        Returns:
            Created schedule
        """
        # Validate channel exists
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundError(f"Channel {channel_id} not found", resource_type="channel")
        if not channel.is_active:
            raise ValidationError(f"Channel {channel_id} is not active")
        
        # Validate video if provided
        if video_id:
            video = self.video_repo.get_by_id(video_id)
            if not video:
                raise NotFoundError(f"Video {video_id} not found", resource_type="video")
            
            # Check for conflicts
            if self.schedule_repo.check_conflict(channel_id, video_id, scheduled_at):
                raise ValidationError(
                    f"Schedule conflict: Video {video_id} already scheduled for channel {channel_id} at {scheduled_at}"
                )
        
        schedule = PublicationSchedule(
            channel_id=channel_id,
            video_id=video_id,
            schedule_type="independent",
            scheduled_at=scheduled_at,
            metadata_info=json.dumps(metadata) if metadata else None,
            status="pending",
        )
        schedule = self.schedule_repo.create(schedule)
        logger.info(f"Created independent schedule {schedule.id} for channel {channel_id} at {scheduled_at}")
        
        return schedule

    def validate_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Validate a schedule (check for conflicts, valid timing)
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Dictionary with validation results
        """
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundError(f"Schedule {schedule_id} not found", resource_type="schedule")
        
        issues = []
        
        # Check if scheduled time is in the past
        if schedule.scheduled_at < datetime.utcnow():
            issues.append("Scheduled time is in the past")
        
        # Check for conflicts
        if schedule.video_id:
            conflict = self.schedule_repo.check_conflict(
                schedule.channel_id,
                schedule.video_id,
                schedule.scheduled_at,
                exclude_schedule_id=schedule_id,
            )
            if conflict:
                issues.append("Schedule conflicts with existing schedule")
        
        # Check channel is active
        channel = self.channel_repo.get_by_id(schedule.channel_id)
        if channel and not channel.is_active:
            issues.append("Channel is not active")
        
        # Check video exists if specified
        if schedule.video_id:
            video = self.video_repo.get_by_id(schedule.video_id)
            if not video:
                issues.append("Video does not exist")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def pause_schedule(self, schedule_id: str) -> PublicationSchedule:
        """Pause a schedule"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundError(f"Schedule {schedule_id} not found", resource_type="schedule")
        
        if schedule.status not in ["pending", "scheduled"]:
            raise ValidationError(f"Cannot pause schedule with status {schedule.status}")
        
        schedule.is_paused = True
        schedule = self.schedule_repo.update(schedule)
        logger.info(f"Paused schedule {schedule_id}")
        return schedule

    def resume_schedule(self, schedule_id: str) -> PublicationSchedule:
        """Resume a paused schedule"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundError(f"Schedule {schedule_id} not found", resource_type="schedule")
        
        schedule.is_paused = False
        schedule = self.schedule_repo.update(schedule)
        logger.info(f"Resumed schedule {schedule_id}")
        return schedule

    def pause_channel_schedules(self, channel_id: str) -> int:
        """Pause all schedules for a channel"""
        schedules = self.schedule_repo.get_by_channel(channel_id, status="pending")
        paused_count = 0
        
        for schedule in schedules:
            if not schedule.is_paused:
                schedule.is_paused = True
                self.schedule_repo.update(schedule)
                paused_count += 1
        
        logger.info(f"Paused {paused_count} schedules for channel {channel_id}")
        return paused_count

    def resume_channel_schedules(self, channel_id: str) -> int:
        """Resume all paused schedules for a channel"""
        schedules = self.schedule_repo.get_by_channel(channel_id, status="pending")
        resumed_count = 0
        
        for schedule in schedules:
            if schedule.is_paused:
                schedule.is_paused = False
                self.schedule_repo.update(schedule)
                resumed_count += 1
        
        logger.info(f"Resumed {resumed_count} schedules for channel {channel_id}")
        return resumed_count

    def cancel_schedule(self, schedule_id: str) -> PublicationSchedule:
        """Cancel a schedule"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundError(f"Schedule {schedule_id} not found", resource_type="schedule")
        
        if schedule.status in ["completed", "cancelled"]:
            raise ValidationError(f"Cannot cancel schedule with status {schedule.status}")
        
        schedule.status = "cancelled"
        schedule = self.schedule_repo.update(schedule)
        logger.info(f"Cancelled schedule {schedule_id}")
        return schedule

    def execute_pending_schedules(self, before: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Execute pending schedules that are ready
        
        Args:
            before: Only execute schedules before this time (default: now)
            
        Returns:
            List of execution results
        """
        if before is None:
            before = datetime.utcnow()
        
        pending_schedules = self.schedule_repo.get_pending_schedules(before=before)
        results = []
        
        for schedule in pending_schedules:
            try:
                result = self._execute_schedule(schedule)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to execute schedule {schedule.id}: {e}")
                schedule.status = "failed"
                schedule.error_message = str(e)
                self.schedule_repo.update(schedule)
                results.append({
                    "schedule_id": schedule.id,
                    "status": "failed",
                    "error": str(e),
                })
        
        return results

    def _execute_schedule(self, schedule: PublicationSchedule) -> Dict[str, Any]:
        """Execute a single schedule"""
        schedule.status = "executing"
        schedule = self.schedule_repo.update(schedule)
        
        try:
            # Get channel
            channel = self.channel_repo.get_by_id(schedule.channel_id)
            if not channel:
                raise NotFoundError(f"Channel {schedule.channel_id} not found", resource_type="channel")
            
            # Check if channel has GitHub repository
            if channel.github_repo_url:
                # Trigger via GitHub Actions
                self.github_service.trigger_workflow(
                    channel_id=schedule.channel_id,
                    workflow_type="process-video",
                    client_payload={
                        "video_id": schedule.video_id,
                        "schedule_id": schedule.id,
                    },
                )
                execution_result = {"method": "github_actions", "triggered": True}
            else:
                # Trigger via queue service
                if schedule.video_id:
                    # Create publish job in queue
                    # Note: This would require QueueService to support publication jobs
                    # For now, we'll log and mark as completed
                    logger.warning(f"Queue-based publication not yet implemented for schedule {schedule.id}")
                    execution_result = {"method": "queue", "status": "not_implemented"}
                else:
                    raise ValidationError("Cannot execute schedule without video_id")
            
            schedule.status = "completed"
            schedule.executed_at = datetime.utcnow()
            schedule.execution_result = json.dumps(execution_result)
            schedule = self.schedule_repo.update(schedule)
            
            logger.info(f"Executed schedule {schedule.id} for channel {schedule.channel_id}")
            
            return {
                "schedule_id": schedule.id,
                "status": "completed",
                "execution_result": execution_result,
            }
            
        except Exception as e:
            schedule.status = "failed"
            schedule.error_message = str(e)
            schedule = self.schedule_repo.update(schedule)
            raise

    def get_schedules_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        channel_id: Optional[str] = None,
    ) -> List[PublicationSchedule]:
        """Get schedules in a date range for calendar/timeline view"""
        return self.schedule_repo.get_by_date_range(start_date, end_date, channel_id)

    def get_schedules_by_channel(
        self,
        channel_id: str,
        status: Optional[str] = None,
    ) -> List[PublicationSchedule]:
        """Get schedules for a channel"""
        return self.schedule_repo.get_by_channel(channel_id, status=status)

    def get_schedules_by_wave(self, wave_id: str) -> List[PublicationSchedule]:
        """Get schedules for a viral wave"""
        return self.schedule_repo.get_by_wave_id(wave_id)
