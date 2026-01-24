# Publication Calendar & Timeline Documentation

## Overview

The Publication Calendar page provides a visual timeline of all scheduled video publications across all channels. Users can view the "viral wave" effect, manage schedules, detect conflicts, and optimize publication timing.

## Features

### Calendar Views

The calendar supports three view modes:

- **Day View**: Detailed view of a single day with all scheduled publications
- **Week View**: Overview of a week with publications grouped by day
- **Month View**: Calendar grid showing publication counts per day

### Schedule Display

Each schedule item shows:

- **Time**: Scheduled publication time
- **Status**: Pending, Scheduled, Executing, Completed, Failed, Cancelled
- **Type**: Simultaneous, Staggered, or Independent
- **Channel**: Which channel will publish
- **Video**: Video ID (if assigned)
- **Wave ID**: For coordinated "viral wave" publications

### Conflict Detection

The calendar automatically detects conflicts:

- Same video scheduled multiple times on the same channel
- Visual warning indicators
- Detailed conflict information

### Schedule Management

Available actions:

- **View Details**: Click on a schedule to see full details
- **Reschedule**: Change publication time (for pending schedules)
- **Cancel**: Cancel a schedule (before execution)

### Filters

Filter schedules by:

- **Channel**: Filter by specific channel
- **Status**: Pending, Scheduled, Executing, Completed, Failed
- **Type**: Simultaneous, Staggered, Independent
- **Date Range**: Start and end dates
- **History**: Toggle to include past publications

### Navigation

- **Date Navigation**: Previous/Next buttons to navigate through time
- **Today Button**: Jump to current date
- **View Switcher**: Switch between day, week, and month views

## Usage

### Viewing the Calendar

1. Navigate to the Calendar page from the sidebar
2. Select your preferred view (day, week, or month)
3. Navigate to the desired date range
4. Use filters to focus on specific channels or schedules

### Managing Schedules

1. **View Details**: Click on any schedule item to see details
2. **Reschedule**: Click "Reschedule" in the detail dialog, select new time, and save
3. **Cancel**: Click "Cancel" in the detail dialog to cancel a schedule

### Detecting Conflicts

1. Conflicts are automatically highlighted with warning indicators
2. Review conflict alerts at the top of the calendar
3. Resolve conflicts by rescheduling or canceling duplicate schedules

## Auto-Refresh

The calendar automatically refreshes every 30 seconds to show the latest schedules. You can also manually refresh using the refresh button.

## Components

### CalendarView

Main calendar component:
- Day, week, and month views
- Date navigation
- View switcher
- Schedule items display

### ScheduleItem

Individual schedule item:
- Compact and full display modes
- Status indicators
- Action buttons
- Click to view details

### CalendarFilters

Filter controls:
- Channel dropdown
- Status dropdown
- Type dropdown
- Date range inputs
- History toggle
- Clear button

### ConflictIndicator

Conflict detection:
- Automatic conflict detection
- Warning alerts
- Conflict details

## API Endpoints

The calendar uses the following endpoints:

- `GET /api/orchestration/schedules` - List schedules with filters
- `GET /api/orchestration/schedules/{scheduleId}` - Get schedule details
- `PUT /api/orchestration/schedules/{scheduleId}` - Update schedule
- `POST /api/orchestration/schedules/{scheduleId}/cancel` - Cancel schedule
- `POST /api/orchestration/schedules/bulk` - Bulk schedule (future)

## Best Practices

1. **Monitor Regularly**: Check the calendar regularly to optimize timing
2. **Review Conflicts**: Resolve conflicts promptly to avoid issues
3. **Use Filters**: Use filters to focus on specific channels or time periods
4. **Plan Waves**: Use simultaneous scheduling for viral wave effects
5. **Check History**: Review past publications to learn from patterns

## Related Documentation

- [Frontend README](../README.md)
- [Dashboard Documentation](./DASHBOARD.md)
- [Scheduling System](../../backend/docs/SCHEDULING.md)
