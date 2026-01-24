import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Today,
  ViewWeek,
  CalendarMonth,
  ArrowBack,
  ArrowForward,
} from '@mui/icons-material';
import { PublicationSchedule } from '../../services/schedules';
import ScheduleItem from './ScheduleItem';

interface CalendarViewProps {
  schedules: PublicationSchedule[];
  currentDate: Date;
  view: 'day' | 'week' | 'month';
  onDateChange: (date: Date) => void;
  onViewChange: (view: 'day' | 'week' | 'month') => void;
  onScheduleClick?: (schedule: PublicationSchedule) => void;
  onScheduleReschedule?: (scheduleId: string, newDate: Date) => void;
}

export default function CalendarView({
  schedules,
  currentDate,
  view,
  onDateChange,
  onViewChange,
  onScheduleClick,
  onScheduleReschedule,
}: CalendarViewProps) {
  const getDaysInView = () => {
    const days: Date[] = [];
    const start = new Date(currentDate);

    if (view === 'day') {
      days.push(new Date(start));
    } else if (view === 'week') {
      // Start of week (Monday)
      const dayOfWeek = start.getDay();
      const diff = start.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
      start.setDate(diff);
      
      for (let i = 0; i < 7; i++) {
        const day = new Date(start);
        day.setDate(start.getDate() + i);
        days.push(day);
      }
    } else {
      // Month view - first day of month
      start.setDate(1);
      const firstDay = start.getDay();
      const daysInMonth = new Date(start.getFullYear(), start.getMonth() + 1, 0).getDate();
      
      // Start from Monday of the week containing the first day
      const startDate = new Date(start);
      startDate.setDate(1 - (firstDay === 0 ? 6 : firstDay - 1));
      
      // Show 6 weeks (42 days) to fill calendar grid
      for (let i = 0; i < 42; i++) {
        const day = new Date(startDate);
        day.setDate(startDate.getDate() + i);
        days.push(day);
      }
    }

    return days;
  };

  const getSchedulesForDay = (date: Date) => {
    const dayStart = new Date(date);
    dayStart.setHours(0, 0, 0, 0);
    const dayEnd = new Date(date);
    dayEnd.setHours(23, 59, 59, 999);

    return schedules.filter((schedule) => {
      const scheduleDate = new Date(schedule.scheduledAt);
      return scheduleDate >= dayStart && scheduleDate <= dayEnd;
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (view === 'day') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
    } else if (view === 'week') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    } else {
      newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
    }
    onDateChange(newDate);
  };

  const days = getDaysInView();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return (
    <Box>
      {/* Header Controls */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigateDate('prev')} size="small">
            <ArrowBack />
          </IconButton>
          <Typography variant="h6">
            {view === 'day'
              ? currentDate.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
              : view === 'week'
              ? `Week of ${formatDate(days[0])}`
              : currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </Typography>
          <IconButton onClick={() => navigateDate('next')} size="small">
            <ArrowForward />
          </IconButton>
          <IconButton onClick={() => onDateChange(new Date())} size="small">
            <Today />
          </IconButton>
        </Box>

        <Box display="flex" gap={1}>
          <Tooltip title="Day View">
            <IconButton
              onClick={() => onViewChange('day')}
              color={view === 'day' ? 'primary' : 'default'}
              size="small"
            >
              <Today />
            </IconButton>
          </Tooltip>
          <Tooltip title="Week View">
            <IconButton
              onClick={() => onViewChange('week')}
              color={view === 'week' ? 'primary' : 'default'}
              size="small"
            >
              <ViewWeek />
            </IconButton>
          </Tooltip>
          <Tooltip title="Month View">
            <IconButton
              onClick={() => onViewChange('month')}
              color={view === 'month' ? 'primary' : 'default'}
              size="small"
            >
              <CalendarMonth />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Calendar Grid */}
      {view === 'day' ? (
        <Card>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              {formatDate(currentDate)}
            </Typography>
            <Box display="flex" flexDirection="column" gap={1} mt={2}>
              {getSchedulesForDay(currentDate).map((schedule) => (
                <ScheduleItem
                  key={schedule.id}
                  schedule={schedule}
                  onClick={() => onScheduleClick?.(schedule)}
                  onReschedule={(newDate) => onScheduleReschedule?.(schedule.id, newDate)}
                />
              ))}
              {getSchedulesForDay(currentDate).length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  No schedules for this day
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      ) : view === 'week' ? (
        <Grid container spacing={1}>
          {days.map((day, idx) => {
            const daySchedules = getSchedulesForDay(day);
            const isToday = day.toDateString() === today.toDateString();

            return (
              <Grid item xs key={idx}>
                <Card
                  sx={{
                    minHeight: 200,
                    border: isToday ? 2 : 0,
                    borderColor: 'primary.main',
                  }}
                >
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      {day.toLocaleDateString('en-US', { weekday: 'short' })}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(day)}
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={0.5} mt={1}>
                      {daySchedules.slice(0, 3).map((schedule) => (
                        <ScheduleItem
                          key={schedule.id}
                          schedule={schedule}
                          compact
                          onClick={() => onScheduleClick?.(schedule)}
                        />
                      ))}
                      {daySchedules.length > 3 && (
                        <Typography variant="caption" color="text.secondary">
                          +{daySchedules.length - 3} more
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      ) : (
        <Grid container spacing={0.5}>
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
            <Grid item xs key={day} sx={{ textAlign: 'center', p: 1 }}>
              <Typography variant="caption" fontWeight="bold">
                {day}
              </Typography>
            </Grid>
          ))}
          {days.map((day, idx) => {
            const daySchedules = getSchedulesForDay(day);
            const isToday = day.toDateString() === today.toDateString();
            const isCurrentMonth = day.getMonth() === currentDate.getMonth();

            return (
              <Grid item xs key={idx}>
                <Card
                  sx={{
                    minHeight: 100,
                    border: isToday ? 2 : 0,
                    borderColor: 'primary.main',
                    opacity: isCurrentMonth ? 1 : 0.5,
                  }}
                >
                  <CardContent sx={{ p: 1 }}>
                    <Typography variant="caption" color={isToday ? 'primary' : 'text.secondary'}>
                      {day.getDate()}
                    </Typography>
                    {daySchedules.length > 0 && (
                      <Box mt={0.5}>
                        <Chip
                          label={daySchedules.length}
                          size="small"
                          color="primary"
                          sx={{ height: 16, fontSize: '0.65rem' }}
                        />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Box>
  );
}
