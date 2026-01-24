# Video Transformation Documentation

## Overview

The video transformation system applies various effects to downloaded videos to make them unique and avoid YouTube detection. The system supports basic transformations (color grading, flips, filters) and advanced transformations (frame rate adjustment, aspect ratio modifications).

## Transformation Effects

### Color Grading

Adjusts video color properties:

- **Brightness**: -1.0 to 1.0 (default: 0.0)
- **Contrast**: 0.0 to 3.0 (default: 1.0)
- **Saturation**: 0.0 to 3.0 (default: 1.0)
- **Hue**: -180.0 to 180.0 degrees (default: 0.0)

**Example:**
```json
{
  "color_grading": {
    "brightness": 0.1,
    "contrast": 1.1,
    "saturation": 1.2,
    "hue": 5.0
  }
}
```

### Flip/Mirror Effects

Flips video horizontally or vertically:

- **Horizontal**: true/false
- **Vertical**: true/false

**Example:**
```json
{
  "flip": {
    "horizontal": true,
    "vertical": false
  }
}
```

### Basic Filters

Applies visual filters:

- **Blur**: 0.0 to 10.0 (radius in pixels)
- **Sharpen**: 0.0 to 2.0 (strength multiplier)
- **Noise Reduction**: 0.0 to 1.0 (strength)

**Example:**
```json
{
  "filters": {
    "blur": 0.0,
    "sharpen": 0.2,
    "noise_reduction": 0.1
  }
}
```

### Advanced Effects

#### Frame Rate Adjustment

Changes video frame rate:

- **target_fps**: Target frames per second (e.g., 24, 30, 60)
- **method**: "drop", "duplicate", or "interpolate" (future)

**Example:**
```json
{
  "frame_rate": {
    "target_fps": 30
  }
}
```

#### Aspect Ratio Modifications

Modifies video aspect ratio:

- **action**: "crop" or "pad"
- **target_ratio**: "16:9", "4:3", "1:1", etc.
- **position**: "center", "top", "bottom", "left", "right" (for crop/pad)

**Example:**
```json
{
  "aspect_ratio": {
    "action": "crop",
    "target_ratio": "16:9",
    "position": "center"
  }
}
```

## Transformation Presets

### Default Presets

The system includes 5 default presets:

1. **subtle**: Light color grading, no flips, no filters
2. **moderate**: Moderate color grading, horizontal flip, light sharpen
3. **strong**: Strong color grading, horizontal flip, moderate sharpen
4. **color_only**: Color grading only, no other effects
5. **flip_only**: Horizontal flip only, no color changes

### Creating Custom Presets

Use the `PresetService` to create custom presets:

```python
from src.services.transformation.preset_service import PresetService

preset_service = PresetService(db)

preset = preset_service.create_preset(
    name="My Custom Preset",
    description="Custom transformation for my channel",
    parameters={
        "color_grading": {
            "brightness": 0.15,
            "contrast": 1.15,
            "saturation": 1.3,
            "hue": 10.0
        },
        "flip": {
            "horizontal": True,
            "vertical": False
        },
        "filters": {
            "sharpen": 0.3,
            "noise_reduction": 0.2
        }
    }
)
```

### Preset Management

- **Create**: `preset_service.create_preset(...)`
- **Update**: `preset_service.update_preset(preset_id, ...)`
- **Delete**: `preset_service.delete_preset(preset_id)`
- **List**: `preset_service.list_presets(active_only=True)`
- **Get**: `preset_service.get_preset(preset_id)`

## Parameter Randomization

To ensure uniqueness, parameters can be randomized within ranges:

```json
{
  "randomization": {
    "enabled": true,
    "ranges": {
      "color_grading.brightness": [-0.05, 0.05],
      "color_grading.contrast": [-0.05, 0.05],
      "color_grading.saturation": [-0.1, 0.1],
      "color_grading.hue": [-5.0, 5.0]
    }
  }
}
```

Randomization adds small variations to base parameters, ensuring each video is slightly different even with the same preset.

## Quality Validation

The system validates transformed videos to ensure quality:

- **Resolution check**: Minimum 720p
- **File size check**: Non-zero file
- **Duration check**: Valid video duration
- **Playback check**: Video can be probed by FFmpeg

Quality validation runs automatically after transformation and logs warnings if issues are detected.

## Error Handling & Fallbacks

The transformation system includes graceful error handling:

1. **Try advanced transformation first** (with frame rate, aspect ratio, etc.)
2. **On failure, fallback to basic effects** (color grading, flip, filters only)
3. **Log fallback decisions** for monitoring
4. **Continue processing** with simpler effects if advanced fails

This ensures videos are still transformed even if advanced effects fail.

## Usage Examples

### Transform with Preset

```python
from src.services.transformation.transformation_service import TransformationService

service = TransformationService(db)

# Transform with default preset
video = service.transform_video(video_id)

# Transform with specific preset
video = service.transform_video(video_id, preset_id="preset-123")

# Transform with custom parameters
video = service.transform_video(
    video_id,
    custom_params={
        "color_grading": {"brightness": 0.1, "contrast": 1.1},
        "flip": {"horizontal": True}
    }
)
```

### Transform with Randomization

```python
# Load preset
params = service._load_preset_params(preset_id)

# Add randomization
params["randomization"] = {
    "enabled": True,
    "ranges": {
        "color_grading.brightness": [-0.05, 0.05],
        "color_grading.contrast": [-0.05, 0.05]
    }
}

# Transform
video = service.transform_video(video_id, custom_params=params)
```

## Processing Time

Typical processing times for HD videos (1080p):

- **Basic transformation**: 1-3 minutes
- **Advanced transformation**: 2-5 minutes
- **With quality validation**: +5-10 seconds

Processing time depends on:
- Video duration
- Video resolution
- Number of effects applied
- System resources

## Best Practices

1. **Use presets** for consistent transformations across videos
2. **Enable randomization** to ensure uniqueness
3. **Test presets** with sample videos before production use
4. **Monitor quality validation** warnings
5. **Review fallback logs** to identify problematic effects
6. **Create channel-specific presets** for different styles

## Troubleshooting

### Transformation Fails

1. Check video is downloaded first (`download_status == "downloaded"`)
2. Verify S3 credentials are correct
3. Check FFmpeg is installed and accessible
4. Review error logs for specific FFmpeg errors

### Quality Validation Warnings

1. Check input video quality
2. Verify transformation parameters are reasonable
3. Review validation errors in logs
4. Consider adjusting preset parameters

### Slow Processing

1. Reduce number of effects
2. Use simpler filters (avoid heavy blur/sharpen)
3. Consider processing in parallel (future feature)
4. Check system resources (CPU, disk I/O)

## Related Documentation

- [Video Download & Storage](../docs/stories/2.2.video-download-storage.md)
- [Database Models](../../src/models/preset.py)
- [Transformation Presets](../../shared/src/transformation/presets.py)
