"""
Cloud storage client for video files
Supports AWS S3 (primary) and Google Cloud Storage (future)
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from shared.src.download.exceptions import StorageError


class S3StorageClient:
    """AWS S3 storage client for video files"""

    def __init__(
        self,
        bucket_name: str,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region: str = "us-east-1",
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize S3 storage client (supports AWS S3 and S3-compatible services like DigitalOcean Spaces)
        
        Args:
            bucket_name: S3 bucket name
            access_key_id: AWS/S3 access key ID (from env if not provided)
            secret_access_key: AWS/S3 secret access key (from env if not provided)
            region: AWS/S3 region
            endpoint_url: Optional endpoint URL for S3-compatible services (e.g., DigitalOcean Spaces)
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # Get credentials from parameters or environment
        access_key_id = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_access_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        
        if not access_key_id or not secret_access_key:
            raise StorageError("S3 credentials not provided (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        
        # Build client config
        client_config = {
            "aws_access_key_id": access_key_id,
            "aws_secret_access_key": secret_access_key,
            "region_name": region,
        }
        
        # Add endpoint URL if provided (for S3-compatible services like DigitalOcean Spaces)
        if endpoint_url:
            # Ensure endpoint URL has protocol
            if not endpoint_url.startswith("http"):
                endpoint_url = f"https://{endpoint_url}"
            client_config["endpoint_url"] = endpoint_url
        
        # Create S3 client
        self.s3_client = boto3.client("s3", **client_config)

    def _generate_s3_key(self, channel_id: str, video_id: str, filename: str) -> str:
        """
        Generate S3 key (path) for video file
        
        Args:
            channel_id: Channel ID
            video_id: Video ID
            filename: Filename with extension
            
        Returns:
            S3 key (e.g., "channel_id/video_id/video.mp4")
        """
        # Clean IDs and filename
        channel_id = channel_id.replace("/", "_")
        video_id = video_id.replace("/", "_")
        filename = os.path.basename(filename)  # Remove any path components
        
        return f"{channel_id}/{video_id}/{filename}"

    def upload_file(
        self,
        local_file_path: str,
        channel_id: str,
        video_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Upload file to S3
        
        Args:
            local_file_path: Path to local file
            channel_id: Channel ID
            video_id: Video ID
            metadata: Optional metadata to attach to S3 object
            
        Returns:
            S3 URL of uploaded file
            
        Raises:
            StorageError: If upload fails
        """
        if not os.path.exists(local_file_path):
            raise StorageError(f"Local file not found: {local_file_path}")
        
        # Generate S3 key
        filename = os.path.basename(local_file_path)
        s3_key = self._generate_s3_key(channel_id, video_id, filename)
        
        try:
            # Prepare metadata
            extra_args = {}
            if metadata:
                # S3 metadata keys must be lowercase and can't contain underscores
                s3_metadata = {}
                for key, value in metadata.items():
                    s3_key_clean = key.lower().replace("_", "-")
                    s3_metadata[s3_key_clean] = str(value)
                extra_args["Metadata"] = s3_metadata
            
            # Upload file
            self.s3_client.upload_file(
                local_file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
            )
            
            # Generate URL
            s3_url = f"s3://{self.bucket_name}/{s3_key}"
            
            return s3_url
            
        except ClientError as e:
            raise StorageError(f"S3 upload failed: {str(e)}") from e
        except BotoCoreError as e:
            raise StorageError(f"AWS error: {str(e)}") from e
        except Exception as e:
            raise StorageError(f"Unexpected error uploading to S3: {str(e)}") from e

    def delete_file(self, channel_id: str, video_id: str, filename: str) -> bool:
        """
        Delete file from S3
        
        Args:
            channel_id: Channel ID
            video_id: Video ID
            filename: Filename to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            StorageError: If deletion fails
        """
        s3_key = self._generate_s3_key(channel_id, video_id, filename)
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            raise StorageError(f"S3 delete failed: {str(e)}") from e
        except Exception as e:
            raise StorageError(f"Unexpected error deleting from S3: {str(e)}") from e

    def get_file_size(self, channel_id: str, video_id: str, filename: str) -> Optional[int]:
        """
        Get file size from S3
        
        Args:
            channel_id: Channel ID
            video_id: Video ID
            filename: Filename
            
        Returns:
            File size in bytes, or None if file doesn't exist
        """
        s3_key = self._generate_s3_key(channel_id, video_id, filename)
        
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return response.get("ContentLength")
        except ClientError:
            return None
        except Exception:
            return None

    def file_exists(self, channel_id: str, video_id: str, filename: str) -> bool:
        """
        Check if file exists in S3
        
        Args:
            channel_id: Channel ID
            video_id: Video ID
            filename: Filename
            
        Returns:
            True if file exists
        """
        return self.get_file_size(channel_id, video_id, filename) is not None
