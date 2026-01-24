"""
Unit tests for scraping functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from shared.src.scraping import (
    YouTubeScraper,
    apply_filters,
    filter_by_resolution,
    filter_by_views,
    filter_by_duration,
    detect_watermark,
    ScrapingError,
    RateLimitError,
    VideoUnavailableError,
)


class TestYouTubeScraper:
    """Tests for YouTubeScraper"""

    def test_parse_resolution(self):
        """Test resolution parsing"""
        scraper = YouTubeScraper()
        
        assert scraper._parse_resolution(1920, 1080) == "1080p"
        assert scraper._parse_resolution(1280, 720) == "720p"
        assert scraper._parse_resolution(640, 480) == "480p"
        assert scraper._parse_resolution(None, None) is None

    def test_check_min_resolution(self):
        """Test minimum resolution check"""
        scraper = YouTubeScraper()
        
        assert scraper._check_min_resolution("1080p", "720p") is True
        assert scraper._check_min_resolution("720p", "720p") is True
        assert scraper._check_min_resolution("480p", "720p") is False
        assert scraper._check_min_resolution(None, "720p") is False

    @patch("shared.src.scraping.youtube_scraper.yt_dlp.YoutubeDL")
    def test_scrape_video_success(self, mock_ydl_class):
        """Test successful video scraping"""
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        mock_info = {
            "id": "test123",
            "title": "Test Video",
            "description": "Test description",
            "duration": 120,
            "uploader": "Test Creator",
            "channel_id": "UC123",
            "view_count": 1000,
            "like_count": 50,
            "width": 1920,
            "height": 1080,
            "thumbnail": "https://example.com/thumb.jpg",
            "upload_date": "20230101",
        }
        mock_ydl.extract_info.return_value = mock_info
        
        scraper = YouTubeScraper()
        result = scraper.scrape_video("https://youtube.com/watch?v=test123")
        
        assert result["title"] == "Test Video"
        assert result["duration"] == 120
        assert result["resolution"] == "1080p"
        assert result["platform"] == "youtube"

    @patch("shared.src.scraping.youtube_scraper.yt_dlp.YoutubeDL")
    def test_scrape_video_unavailable(self, mock_ydl_class):
        """Test scraping unavailable video"""
        from yt_dlp.utils import DownloadError
        
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = DownloadError("Video unavailable")
        
        scraper = YouTubeScraper()
        
        with pytest.raises(VideoUnavailableError):
            scraper.scrape_video("https://youtube.com/watch?v=test123")


class TestFilters:
    """Tests for video filters"""

    def test_filter_by_resolution(self):
        """Test resolution filtering"""
        metadata = {"resolution": "1080p"}
        assert filter_by_resolution(metadata, "720p") is True
        
        metadata = {"resolution": "480p"}
        assert filter_by_resolution(metadata, "720p") is False
        
        metadata = {"resolution": None}
        assert filter_by_resolution(metadata, "720p") is False

    def test_filter_by_views(self):
        """Test view count filtering"""
        metadata = {"view_count": 5000}
        assert filter_by_views(metadata, 1000) is True
        
        metadata = {"view_count": 500}
        assert filter_by_views(metadata, 1000) is False
        
        metadata = {"view_count": None}
        assert filter_by_views(metadata, 1000) is False
        
        # No filter
        assert filter_by_views(metadata, None) is True

    def test_filter_by_duration(self):
        """Test duration filtering"""
        metadata = {"duration": 60}
        assert filter_by_duration(metadata, 120) is True
        
        metadata = {"duration": 180}
        assert filter_by_duration(metadata, 120) is False
        
        # No filter
        assert filter_by_duration(metadata, None) is True

    def test_detect_watermark(self):
        """Test watermark detection"""
        # Watermarked
        metadata = {"title": "Check out @creator", "description": ""}
        assert detect_watermark(metadata) is True
        
        metadata = {"title": "Video with watermark", "description": ""}
        assert detect_watermark(metadata) is True
        
        # Not watermarked
        metadata = {"title": "Regular video title", "description": "Normal description"}
        assert detect_watermark(metadata) is False

    def test_apply_filters(self):
        """Test applying all filters"""
        # Passes all filters
        metadata = {
            "resolution": "1080p",
            "view_count": 5000,
            "duration": 60,
            "title": "Clean video",
            "description": "No watermark",
        }
        assert apply_filters(metadata, min_resolution="720p", min_views=1000, max_duration=120) is True
        
        # Fails resolution
        metadata["resolution"] = "480p"
        assert apply_filters(metadata, min_resolution="720p") is False
        
        # Fails views
        metadata["resolution"] = "1080p"
        metadata["view_count"] = 500
        assert apply_filters(metadata, min_resolution="720p", min_views=1000) is False
        
        # Fails duration
        metadata["view_count"] = 5000
        metadata["duration"] = 180
        assert apply_filters(metadata, min_resolution="720p", max_duration=120) is False
        
        # Fails watermark
        metadata["duration"] = 60
        metadata["title"] = "Check @creator"
        assert apply_filters(metadata, min_resolution="720p", exclude_watermarked=True) is False
