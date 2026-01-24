# Statistics & Analytics Documentation

## Overview

The Statistics & Analytics page provides comprehensive insights into channel performance, growth trends, and engagement metrics. Users can track performance across all channels, identify trends, detect anomalies, and export data for further analysis.

## Features

### Overview Statistics

Displays key metrics across all channels:

- **Total Subscribers**: Combined subscriber count across all active channels
- **Total Views**: Combined view count across all published videos
- **Total Videos**: Total number of videos published
- **Recent Activity**: Subscriber and view gains in recent period

### Per-Channel Breakdown

Table showing individual channel performance:

- Channel name
- Subscriber count with growth trend
- Total views with growth trend
- Video count
- Growth status indicator

### Growth Trends

Visual charts showing:

- **Subscriber Growth**: Line chart showing subscriber growth over time
- **View Growth**: Line chart showing view growth over time
- Interactive tooltips with exact values
- Date range on X-axis

### Engagement Metrics

Displays engagement data when available:

- Likes, comments, shares
- Engagement rate calculations
- Per-video engagement metrics

### Filters

Filter statistics by:

- **Channel**: Filter by specific channel or view all
- **Metric**: Focus on subscribers, views, videos, or engagement
- **Date Range**: Start and end dates for time period analysis

### Anomaly Detection

Automatically detects and highlights:

- **Spikes**: Significant increases (>50% growth)
- **Drops**: Significant decreases (>30% decline)
- Visual indicators with dates and percentages
- Alerts for notable changes

### Export Functionality

Export statistics data:

- **CSV Export**: Download data as CSV for spreadsheet analysis
- **JSON Export**: Download data as JSON for programmatic analysis
- Includes all filtered data

## Usage

### Viewing Statistics

1. Navigate to the Statistics page from the sidebar
2. View overview statistics at the top
3. Review per-channel breakdown in the table
4. Examine growth trends in charts
5. Check for anomalies and notable changes

### Filtering Data

1. Select filters from the filter bar
2. Choose channel, metric, and date range
3. Statistics automatically update based on filters
4. Click "Clear" to reset all filters

### Exporting Data

1. Apply desired filters
2. Click "CSV" or "JSON" export button
3. Data will be downloaded in the selected format

## Auto-Refresh

Statistics automatically refresh every 60 seconds to show the latest data. You can also manually refresh using the refresh button.

## Components

### StatisticsOverview

Overview cards showing:
- Total subscribers
- Total views
- Total videos
- Recent activity

### ChannelBreakdown

Table component showing:
- Per-channel metrics
- Growth trends
- Status indicators

### GrowthTrendsChart

Line chart visualization:
- Subscriber growth over time
- View growth over time
- Interactive data points

### StatisticsFilters

Filter controls:
- Channel dropdown
- Metric dropdown
- Date range inputs
- Export buttons
- Clear button

### AnomalyIndicator

Anomaly detection:
- Automatic spike/drop detection
- Visual alerts
- Detailed information

## API Endpoints

The statistics page uses the following endpoints:

- `GET /api/statistics/overview` - System-wide statistics
- `GET /api/channels/{channelId}/statistics` - Channel statistics with trends
- `GET /api/videos/{videoId}/statistics` - Video statistics

## Best Practices

1. **Monitor Regularly**: Check statistics regularly to track growth
2. **Review Trends**: Analyze growth trends to identify patterns
3. **Investigate Anomalies**: Review detected anomalies to understand causes
4. **Use Filters**: Use filters to focus on specific channels or time periods
5. **Export Data**: Export data for deeper analysis in external tools
6. **Compare Periods**: Use date filters to compare different time periods

## Related Documentation

- [Frontend README](../README.md)
- [Dashboard Documentation](./DASHBOARD.md)
- [Channel Detail Documentation](./CHANNEL-DETAIL.md)
