"""
Unit tests for advanced video transformation functionality
"""

import pytest
from unittest.mock import patch, MagicMock

from shared.src.transformation import (
    randomize_params,
    randomize_preset_params,
    get_default_randomization_ranges,
    QualityValidator,
)


class TestRandomization:
    """Tests for parameter randomization"""

    def test_randomize_params(self):
        """Test parameter randomization"""
        base_params = {
            "color_grading": {
                "brightness": 0.1,
                "contrast": 1.1,
                "saturation": 1.2,
            }
        }
        
        ranges = {
            "color_grading.brightness": (-0.05, 0.05),
            "color_grading.contrast": (-0.05, 0.05),
        }
        
        randomized = randomize_params(base_params, ranges)
        
        # Check structure preserved
        assert "color_grading" in randomized
        assert "brightness" in randomized["color_grading"]
        assert "contrast" in randomized["color_grading"]
        
        # Check values are within range
        brightness = randomized["color_grading"]["brightness"]
        assert 0.05 <= brightness <= 0.15  # 0.1 ± 0.05
        
        contrast = randomized["color_grading"]["contrast"]
        assert 1.05 <= contrast <= 1.15  # 1.1 ± 0.05

    def test_randomize_preset_params_enabled(self):
        """Test preset parameter randomization when enabled"""
        preset_params = {
            "color_grading": {
                "brightness": 0.1,
                "contrast": 1.1,
            }
        }
        
        config = {
            "enabled": True,
            "ranges": {
                "color_grading.brightness": (-0.05, 0.05),
            }
        }
        
        randomized = randomize_preset_params(preset_params, config)
        
        # Should be randomized
        assert randomized["color_grading"]["brightness"] != 0.1

    def test_randomize_preset_params_disabled(self):
        """Test preset parameter randomization when disabled"""
        preset_params = {
            "color_grading": {
                "brightness": 0.1,
            }
        }
        
        config = {
            "enabled": False,
        }
        
        randomized = randomize_preset_params(preset_params, config)
        
        # Should be unchanged
        assert randomized["color_grading"]["brightness"] == 0.1

    def test_get_default_randomization_ranges(self):
        """Test getting default randomization ranges"""
        ranges = get_default_randomization_ranges()
        
        assert "color_grading.brightness" in ranges
        assert "color_grading.contrast" in ranges
        assert "color_grading.saturation" in ranges
        assert "color_grading.hue" in ranges


class TestQualityValidator:
    """Tests for quality validation"""

    def test_init(self):
        """Test validator initialization"""
        validator = QualityValidator()
        assert validator is not None

    @patch("shared.src.transformation.quality_validator.ffmpeg.probe")
    def test_validate_video_success(self, mock_probe):
        """Test successful video validation"""
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                }
            ],
            "format": {
                "duration": "120.0",
            }
        }
        
        validator = QualityValidator()
        
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=1024000):
                result = validator.validate_video("/test/video.mp4")
                
                assert result["valid"] is True
                assert result["resolution"] == (1920, 1080)
                assert result["duration"] == 120.0
                assert result["file_size"] == 1024000

    def test_validate_video_not_found(self):
        """Test validation of non-existent file"""
        validator = QualityValidator()
        
        with patch("os.path.exists", return_value=False):
            result = validator.validate_video("/nonexistent/video.mp4")
            
            assert result["valid"] is False
            assert len(result["errors"]) > 0

    @patch("shared.src.transformation.quality_validator.ffmpeg.probe")
    def test_validate_video_low_resolution(self, mock_probe):
        """Test validation with low resolution"""
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 640,
                    "height": 480,
                }
            ],
            "format": {
                "duration": "120.0",
            }
        }
        
        validator = QualityValidator()
        
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=1024000):
                result = validator.validate_video("/test/video.mp4")
                
                assert result["valid"] is False
                assert any("Resolution too low" in error for error in result["errors"])
