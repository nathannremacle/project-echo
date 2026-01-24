"""
Unit tests for video download functionality
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

from shared.src.download import (
    VideoDownloader,
    S3StorageClient,
    DownloadError,
    VideoUnavailableError,
    StorageError,
)


class TestVideoDownloader:
    """Tests for VideoDownloader"""

    def test_init(self):
        """Test downloader initialization"""
        downloader = VideoDownloader()
        assert downloader.output_dir is not None
        assert os.path.exists(downloader.output_dir)

    def test_init_with_custom_dir(self):
        """Test downloader with custom output directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = VideoDownloader(output_dir=temp_dir)
            assert downloader.output_dir == temp_dir

    @patch("shared.src.download.video_downloader.yt_dlp.YoutubeDL")
    def test_download_success(self, mock_ydl_class):
        """Test successful video download"""
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        mock_info = {
            "duration": 120,
            "width": 1920,
            "height": 1080,
            "format_id": "best",
            "format_note": "1080p",
        }
        mock_ydl.extract_info.return_value = mock_info
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = VideoDownloader(output_dir=temp_dir)
            
            # Create a mock downloaded file
            test_file = os.path.join(temp_dir, "test123.mp4")
            with open(test_file, "w") as f:
                f.write("test")
            
            # Mock the file finding logic
            with patch("os.path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    result = downloader.download("https://youtube.com/watch?v=test123", video_id="test123")
                    
                    assert result["file_size"] == 1024
                    assert result["duration"] == 120
                    assert result["resolution"] == "1080p"

    @patch("shared.src.download.video_downloader.yt_dlp.YoutubeDL")
    def test_download_unavailable(self, mock_ydl_class):
        """Test download of unavailable video"""
        from yt_dlp.utils import DownloadError
        
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = DownloadError("Video unavailable")
        
        downloader = VideoDownloader()
        
        with pytest.raises(VideoUnavailableError):
            downloader.download("https://youtube.com/watch?v=test123")


class TestS3StorageClient:
    """Tests for S3StorageClient"""

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
    })
    @patch("shared.src.download.storage_client.boto3.client")
    def test_init(self, mock_boto_client):
        """Test S3 client initialization"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        client = S3StorageClient(bucket_name="test-bucket")
        
        assert client.bucket_name == "test-bucket"
        mock_boto_client.assert_called_once()

    @patch.dict(os.environ, {})
    def test_init_missing_credentials(self):
        """Test initialization without credentials"""
        with pytest.raises(StorageError):
            S3StorageClient(bucket_name="test-bucket")

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
    })
    @patch("shared.src.download.storage_client.boto3.client")
    def test_generate_s3_key(self, mock_boto_client):
        """Test S3 key generation"""
        client = S3StorageClient(bucket_name="test-bucket")
        
        key = client._generate_s3_key("channel123", "video456", "video.mp4")
        assert key == "channel123/video456/video.mp4"
        
        # Test with special characters
        key = client._generate_s3_key("channel/123", "video/456", "video.mp4")
        assert "/" not in key.split("/")[0]  # Channel ID cleaned
        assert "/" not in key.split("/")[1]  # Video ID cleaned

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
    })
    @patch("shared.src.download.storage_client.boto3.client")
    def test_upload_file(self, mock_boto_client):
        """Test file upload to S3"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        client = S3StorageClient(bucket_name="test-bucket")
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file_path = temp_file.name
        
        try:
            url = client.upload_file(temp_file_path, "channel123", "video456")
            
            assert url.startswith("s3://test-bucket/")
            assert "channel123" in url
            assert "video456" in url
            mock_s3.upload_file.assert_called_once()
        finally:
            os.unlink(temp_file_path)

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
    })
    @patch("shared.src.download.storage_client.boto3.client")
    def test_upload_file_not_found(self, mock_boto_client):
        """Test upload with non-existent file"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        client = S3StorageClient(bucket_name="test-bucket")
        
        with pytest.raises(StorageError):
            client.upload_file("/nonexistent/file.mp4", "channel123", "video456")
