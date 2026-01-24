"""
Unit tests for video transformation functionality
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from shared.src.transformation import (
    VideoTransformer,
    get_preset,
    get_default_presets,
    TransformationError,
)


class TestVideoTransformer:
    """Tests for VideoTransformer"""

    def test_init(self):
        """Test transformer initialization"""
        transformer = VideoTransformer()
        assert transformer.output_dir is not None
        assert os.path.exists(transformer.output_dir)

    def test_build_color_grading_filter(self):
        """Test color grading filter building"""
        transformer = VideoTransformer()
        
        params = {
            "brightness": 0.1,
            "contrast": 1.1,
            "saturation": 1.2,
            "hue": 10.0,
        }
        filter_str = transformer._build_color_grading_filter(params)
        
        assert "eq=" in filter_str
        assert "brightness=0.1" in filter_str
        assert "contrast=1.1" in filter_str

    def test_build_flip_filter(self):
        """Test flip filter building"""
        transformer = VideoTransformer()
        
        # Horizontal flip
        filters = transformer._build_flip_filter({"horizontal": True, "vertical": False})
        assert "hflip" in filters
        assert len(filters) == 1
        
        # Vertical flip
        filters = transformer._build_flip_filter({"horizontal": False, "vertical": True})
        assert "vflip" in filters
        
        # Both
        filters = transformer._build_flip_filter({"horizontal": True, "vertical": True})
        assert len(filters) == 2

    def test_build_blur_filter(self):
        """Test blur filter building"""
        transformer = VideoTransformer()
        
        # No blur
        assert transformer._build_blur_filter(0.0) is None
        
        # With blur
        filter_str = transformer._build_blur_filter(2.0)
        assert filter_str is not None
        assert "boxblur=" in filter_str

    def test_build_sharpen_filter(self):
        """Test sharpen filter building"""
        transformer = VideoTransformer()
        
        # No sharpen
        assert transformer._build_sharpen_filter(0.0) is None
        
        # With sharpen
        filter_str = transformer._build_sharpen_filter(0.5)
        assert filter_str is not None
        assert "unsharp=" in filter_str

    @patch("shared.src.transformation.video_transformer.ffmpeg")
    def test_transform_success(self, mock_ffmpeg):
        """Test successful video transformation"""
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_video = MagicMock()
        mock_audio = MagicMock()
        mock_output = MagicMock()
        
        mock_ffmpeg.input.return_value = mock_input
        mock_input.video = mock_video
        mock_input.audio = mock_audio
        mock_ffmpeg.output.return_value = mock_output
        
        transformer = VideoTransformer()
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(b"fake video content")
            temp_file_path = temp_file.name
        
        try:
            params = {
                "color_grading": {
                    "brightness": 0.1,
                    "contrast": 1.1,
                    "saturation": 1.2,
                    "hue": 0.0,
                },
            }
            
            with patch("os.path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    result = transformer.transform(temp_file_path, params=params)
                    
                    assert result["file_size"] == 1024
                    assert "params" in result
        finally:
            os.unlink(temp_file_path)

    def test_transform_file_not_found(self):
        """Test transformation with non-existent file"""
        transformer = VideoTransformer()
        
        with pytest.raises(TransformationError):
            transformer.transform("/nonexistent/file.mp4")


class TestPresets:
    """Tests for transformation presets"""

    def test_get_default_presets(self):
        """Test getting default presets"""
        presets = get_default_presets()
        
        assert "subtle" in presets
        assert "moderate" in presets
        assert "strong" in presets
        assert "color_only" in presets
        assert "flip_only" in presets

    def test_get_preset(self):
        """Test getting specific preset"""
        preset = get_preset("moderate")
        
        assert "color_grading" in preset
        assert "flip" in preset
        assert "filters" in preset

    def test_get_preset_not_found(self):
        """Test getting non-existent preset"""
        with pytest.raises(KeyError):
            get_preset("nonexistent")
