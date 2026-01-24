"""
Schedule repository - data access layer for publication schedules
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.schedule import PublicationSchedule
from src.utils.exceptions import NotFoundError


class ScheduleRepository:
    """Repository for publication schedule data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, schedule: PublicationSchedule) -> PublicationSchedule:
        """Create a new publication schedule"""
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def get_by_id(self, schedule_id: str) -> Optional[PublicationSchedule]:
        """Get schedule by ID"""
        return self.db.query(PublicationSchedule).filter(PublicationSchedule.id == schedule_id).first()

    def get_by_channel(
        self,
        channel_id: str,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PublicationSchedule]:
        """Get schedules for a channel, optionally filtered by status and date range"""
        query = self.db.query(PublicationSchedule).filter(PublicationSchedule.channel_id == channel_id)
        
        if status:
            query = query.filter(PublicationSchedule.status == status)
        
        if start_date:
            query = query.filter(PublicationSchedule.scheduled_at >= start_date)
        
        if end_date:
            query = query.filter(PublicationSchedule.scheduled_at <= end_date)
        
        return query.order_by(PublicationSchedule.scheduled_at).all()

    def get_by_video(self, video_id: str) -> List[PublicationSchedule]:
        """Get schedules for a video"""
        return (
            self.db.query(PublicationSchedule)
            .filter(PublicationSchedule.video_id == video_id)
            .order_by(PublicationSchedule.scheduled_at)
            .all()
        )

    def get_by_coordination_group(self, coordination_group_id: str) -> List[PublicationSchedule]:
        """Get schedules in a coordination group (for simultaneous/staggered)"""
        return (
            self.db.query(PublicationSchedule)
            .filter(PublicationSchedule.coordination_group_id == coordination_group_id)
            .order_by(PublicationSchedule.scheduled_at)
            .all()
        )

    def get_by_wave_id(self, wave_id: str) -> List[PublicationSchedule]:
        """Get schedules for a viral wave"""
        return (
            self.db.query(PublicationSchedule)
            .filter(PublicationSchedule.wave_id == wave_id)
            .order_by(PublicationSchedule.scheduled_at)
            .all()
        )

    def get_pending_schedules(
        self,
        before: Optional[datetime] = None,
        channel_id: Optional[str] = None,
    ) -> List[PublicationSchedule]:
        """Get pending schedules ready to execute"""
        query = (
            self.db.query(PublicationSchedule)
            .filter(PublicationSchedule.status == "pending")
            .filter(PublicationSchedule.is_paused == False)
        )
        
        if before:
            query = query.filter(PublicationSchedule.scheduled_at <= before)
        
        if channel_id:
            query = query.filter(PublicationSchedule.channel_id == channel_id)
        
        return query.order_by(PublicationSchedule.scheduled_at).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        channel_id: Optional[str] = None,
    ) -> List[PublicationSchedule]:
        """Get schedules in a date range"""
        query = (
            self.db.query(PublicationSchedule)
            .filter(PublicationSchedule.scheduled_at >= start_date)
            .filter(PublicationSchedule.scheduled_at <= end_date)
        )
        
        if channel_id:
            query = query.filter(PublicationSchedule.channel_id == channel_id)
        
        return query.order_by(PublicationSchedule.scheduled_at).all()

    def check_conflict(
        self,
        channel_id: str,
        video_id: Optional[str],
        scheduled_at: datetime,
        exclude_schedule_id: Optional[str] = None,
    ) -> bool:
        """Check if a schedule conflicts with existing schedules"""
        query = (
            self.db.query(PublicationSchedule)
            .filter(PublicationSchedule.channel_id == channel_id)
            .filter(PublicationSchedule.status.in_(["pending", "scheduled", "executing"]))
        )
        
        # Check for same video on same channel
        if video_id:
            query = query.filter(PublicationSchedule.video_id == video_id)
        
        # Check for overlapping time windows (within 1 minute)
        time_window_start = scheduled_at.replace(second=0, microsecond=0)
        time_window_end = scheduled_at.replace(second=59, microsecond=999999)
        query = query.filter(
            and_(
                PublicationSchedule.scheduled_at >= time_window_start,
                PublicationSchedule.scheduled_at <= time_window_end,
            )
        )
        
        if exclude_schedule_id:
            query = query.filter(PublicationSchedule.id != exclude_schedule_id)
        
        return query.first() is not None

    def update(self, schedule: PublicationSchedule) -> PublicationSchedule:
        """Update an existing schedule"""
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        schedule = self.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundError(f"Schedule {schedule_id} not found", resource_type="schedule")
        self.db.delete(schedule)
        self.db.commit()
        return True

    def get_all(
        self,
        status: Optional[str] = None,
        schedule_type: Optional[str] = None,
    ) -> List[PublicationSchedule]:
        """Get all schedules, optionally filtered by status and type"""
        query = self.db.query(PublicationSchedule)
        
        if status:
            query = query.filter(PublicationSchedule.status == status)
        
        if schedule_type:
            query = query.filter(PublicationSchedule.schedule_type == schedule_type)
        
        return query.order_by(PublicationSchedule.scheduled_at).all()
