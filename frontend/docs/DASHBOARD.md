# Dashboard Overview Documentation

## Overview

The Dashboard is the main landing page of the Project Echo management interface. It provides an at-a-glance view of all channels, system status, statistics, and recent activity.

## Features

### System Statistics

The dashboard displays key system-wide metrics:

- **System Status**: Running, Stopped, or Paused
- **Published Videos**: Total videos published across all channels
- **Success Rate**: Percentage of successful publications
- **Pending Schedules**: Number of scheduled publications

### Channel Cards

Each channel is displayed in a card showing:

- **Channel Name**: Display name
- **Health Indicator**: Color-coded status (green/yellow/red)
  - Green: Healthy
  - Yellow: Warning
  - Red: Error
- **Metrics**:
  - Distributions (7 days)
  - Published videos (7 days)
  - Success rate
- **Last Publication**: Date of last successful publication
- **Errors**: Any error messages or warnings

Clicking on a channel card navigates to the channel detail page.

### Quick Actions

Quick action buttons for common tasks:

- **Add New Channel**: Navigate to channel creation
- **Trigger Phase 2**: Enable music replacement for all channels
- **View Logs**: Navigate to system logs

### Activity Feed

Recent activity feed showing:

- Latest publications
- System events
- Errors and warnings
- Timestamps

## Auto-Refresh

The dashboard automatically refreshes every 30 seconds to show the latest data. You can also manually refresh using the refresh button in the top-right corner.

## Layout

The dashboard uses a responsive grid layout:

- **Desktop**: 2-column layout (channels on left, sidebar on right)
- **Tablet**: Stacked layout
- **Mobile**: Single column

## Data Sources

The dashboard fetches data from:

- `/api/orchestration/dashboard` - Comprehensive dashboard data
- `/api/orchestration/monitor-channels` - Channel statuses
- `/api/orchestration/status` - System status

## Components

### SystemStats

Displays system-wide statistics in a grid of cards:
- System status
- Published videos count
- Success rate
- Pending schedules

### ChannelCard

Individual channel card component:
- Channel information
- Health indicators
- Key metrics
- Error display

### QuickActions

Quick action buttons:
- Add channel
- Trigger phase 2
- View logs

### ActivityFeed

Recent activity list:
- Publication events
- System events
- Error notifications

## Usage

The dashboard is the default landing page (`/`) and loads automatically when you access the application.

### Manual Refresh

Click the refresh icon in the top-right corner to manually refresh the dashboard data.

### Navigation

- Click on a channel card to view channel details
- Use quick action buttons for common tasks
- Use the sidebar navigation for other pages

## Best Practices

1. **Monitor Regularly**: Check the dashboard regularly to monitor system health
2. **Review Errors**: Pay attention to error indicators and messages
3. **Use Quick Actions**: Use quick actions for common tasks
4. **Check Activity Feed**: Review recent activity to stay informed

## Related Documentation

- [Frontend README](../README.md)
- [Orchestration API](../../backend/docs/ORCHESTRATION.md)
- [Channel Configuration](../../backend/docs/CHANNEL-CONFIGURATION.md)
