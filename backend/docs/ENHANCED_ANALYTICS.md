# Enhanced Analytics & Music Promotion Metrics Documentation

## Overview

The Enhanced Analytics system tracks music promotion effectiveness and provides insights into the "viral wave" strategy. It includes metrics for music promotion, wave effects, Phase 2 comparisons, ROI calculations, insights, and recommendations.

## Features

### Music Promotion Metrics

- **Total Music Videos**: Count of videos with music replacement
- **Total Views**: Aggregate views for all music videos
- **Unique Music Tracks**: Number of different music tracks used
- **Average Views per Video**: Performance metric for music videos

### Wave Effect Metrics

- **Total Waves**: Number of simultaneous publication waves detected
- **Largest Wave**: Biggest wave (videos and channels count)
- **Average Wave Size**: Average number of videos per wave
- **Total Reach**: Total number of unique channels reached
- **Average Reach per Wave**: Average channels per wave

### Phase 2 Comparison

- **Pre-Phase 2 Metrics**: Performance before music promotion
- **Post-Phase 2 Metrics**: Performance after music promotion
- **Improvement**: Percentage improvement in views per video

### ROI Metrics

- **Effort**: Number of videos processed with music replacement
- **Results**: Total views achieved
- **ROI**: Views per video processed (efficiency metric)

### Insights

Automatically detects and highlights:
- High performing music videos
- Large wave effects
- Phase 2 success indicators
- Growth spikes

### Recommendations

Provides actionable recommendations:
- Enable Phase 2 for channels
- Increase music video production
- Optimize timing and channel selection

## API Endpoints

### Get Music Promotion Metrics

```http
GET /api/analytics/music-promotion?channel_ids=uuid1,uuid2&start_date=2026-01-01&end_date=2026-01-31
```

**Response:**
```json
{
  "total_music_videos": 50,
  "total_views": 100000,
  "unique_music_tracks": 2,
  "average_views_per_video": 2000,
  "videos": [...]
}
```

### Get Wave Effect Metrics

```http
GET /api/analytics/wave-effect?start_date=2026-01-01&end_date=2026-01-31&time_window_hours=24
```

**Response:**
```json
{
  "total_waves": 10,
  "largest_wave": {
    "videos_count": 15,
    "channels_count": 5,
    "start_time": "2026-01-15T10:00:00Z"
  },
  "average_wave_size": 8.5,
  "total_reach": 25,
  "average_reach_per_wave": 2.5
}
```

### Get Phase 2 Comparison

```http
GET /api/analytics/phase2-comparison?channel_ids=uuid1&phase2_start_date=2026-01-01
```

**Response:**
```json
{
  "pre_phase2": {
    "total_videos": 100,
    "total_views": 50000,
    "average_views_per_video": 500
  },
  "post_phase2": {
    "total_videos": 50,
    "total_views": 100000,
    "average_views_per_video": 2000
  },
  "improvement": {
    "views_per_video": 300.0
  }
}
```

### Get ROI Metrics

```http
GET /api/analytics/roi?channel_ids=uuid1&start_date=2026-01-01&end_date=2026-01-31
```

**Response:**
```json
{
  "effort": 50,
  "results": 100000,
  "roi": 2000,
  "efficiency": {
    "views_per_video": 2000,
    "average_views": 2000
  }
}
```

### Get Insights

```http
GET /api/analytics/insights?channel_ids=uuid1&start_date=2026-01-01&end_date=2026-01-31
```

**Response:**
```json
{
  "insights": [
    {
      "type": "success",
      "title": "High Performing Music Videos",
      "message": "Music videos average 2000 views per video",
      "metric": "average_views",
      "value": 2000
    }
  ]
}
```

### Get Recommendations

```http
GET /api/analytics/recommendations?channel_ids=uuid1
```

**Response:**
```json
{
  "recommendations": [
    {
      "type": "action",
      "title": "Enable Phase 2",
      "message": "Consider enabling Phase 2 for 3 active channel(s)",
      "action": "enable_phase2",
      "channels": ["uuid1", "uuid2"]
    }
  ]
}
```

### Export Analytics

```http
GET /api/analytics/export?channel_ids=uuid1&start_date=2026-01-01&end_date=2026-01-31
```

**Response:**
```json
{
  "exported_at": "2026-01-23T00:00:00Z",
  "music_promotion": {...},
  "wave_effect": {...},
  "phase2_comparison": {...},
  "roi": {...},
  "insights": [...],
  "recommendations": [...]
}
```

## Usage

### Getting Music Promotion Metrics

```python
from src.services.enhanced_analytics.enhanced_analytics_service import EnhancedAnalyticsService

service = EnhancedAnalyticsService(db)

metrics = service.get_music_promotion_metrics(
    channel_ids=["channel-1"],
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
)
```

### Getting Wave Effect Metrics

```python
wave_metrics = service.get_wave_effect_metrics(
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    time_window_hours=24,
)
```

### Getting Phase 2 Comparison

```python
comparison = service.get_phase2_comparison(
    channel_ids=["channel-1"],
    phase2_start_date=datetime(2026, 1, 1),
)
```

## Best Practices

1. **Regular Monitoring**: Check analytics regularly to track promotion effectiveness
2. **Date Ranges**: Use appropriate date ranges for meaningful comparisons
3. **Channel Filtering**: Filter by specific channels for targeted analysis
4. **Export Data**: Export analytics for external analysis and reporting
5. **Follow Recommendations**: Act on recommendations to optimize performance
6. **Track Insights**: Monitor insights to identify successful strategies

## Related Documentation

- [Phase 2 Activation](./PHASE2.md)
- [Music File Management](./MUSIC.md)
- [Statistics](./STATISTICS.md)
- [Channel Management](./CHANNELS.md)
