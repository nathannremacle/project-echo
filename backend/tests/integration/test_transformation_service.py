"""
Integration tests for transformation service
"""

import json
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from src.database import Base, SessionLocal
from src.models.channel import Channel
from src.models.video import Video
from src.models.preset import TransformationPreset
from src.services.transformation.transformation_service import TransformationService


@pytest.fixture
def db_session():
    """Create test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def test_channel(db_session):
    """Create test channel"""
    channel = Channel(
        name="Test Channel",
        youtube_channel_id="UC123",
        youtube_channel_url="https://youtube.com/channel/UC123",
        is_active=True,
        content_filters=json.dumps({}),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@pytest.fixture
def test_video(db_session, test_channel):
    """Create test video with downloaded status"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        download_status="downloaded",
        download_url="s3://test-bucket/channel123/test123/video.mp4",
        download_size=1024000,
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


@pytest.fixture
def test_preset(db_session):
    """Create test transformation preset"""
    preset = TransformationPreset(
        name="Test Preset",
        description="Test transformation preset",
        parameters=json.dumps({
            "color_grading": {
                "brightness": 0.1,
                "contrast": 1.1,
                "saturation": 1.2,
                "hue": 0.0,
            },
            "flip": {
                "horizontal": True,
                "vertical": False,
            },
            "filters": {
                "blur": 0.0,
                "sharpen": 0.2,
                "noise_reduction": 0.1,
            },
        }),
        is_default=False,
        is_active=True,
    )
    db_session.add(preset)
    db_session.commit()
    db_session.refresh(preset)
    return preset


@patch("src.services.transformation.transformation_service.S3StorageClient")
@patch("src.services.transformation.transformation_service.VideoTransformer")
@patch("src.services.transformation.transformation_service.boto3.client")
@patch.dict(os.environ, {
    "AWS_ACCESS_KEY_ID": "test_key",
    "AWS_SECRET_ACCESS_KEY": "test_secret",
    "AWS_S3_BUCKET": "test-bucket",
})
def test_transform_video_success(
    mock_boto3,
    mock_transformer_class,
    mock_storage_class,
    db_session,
    test_video,
    test_preset,
):
    """Test successful video transformation"""
    # Mock S3 download
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3
    
    # Create temp file for downloaded video
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file.write(b"fake video content")
        temp_file_path = temp_file.name
    
    # Mock transformer
    mock_transformer = MagicMock()
    mock_transformer_class.return_value = mock_transformer
    
    transform_result = {
        "output_file": temp_file_path.replace(".mp4", "_transformed.mp4"),
        "file_size": 2048000,
        "params": {},
    }
    mock_transformer.transform.return_value = transform_result
    
    # Mock storage
    mock_storage = MagicMock()
    mock_storage_class.return_value = mock_storage
    mock_storage.upload_file.return_value = "s3://test-bucket/channel123/test123/transformed_video.mp4"
    
    # Mock file operations
    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            with patch("os.rename"):
                with patch("os.remove"):
                    service = TransformationService(db_session)
                    result = service.transform_video(test_video.id, preset_id=test_preset.id)
                    
                    assert result.transformation_status == "transformed"
                    assert result.transformed_url is not None
                    assert result.transformed_size == 2048000
                    assert result.transformation_preset_id == test_preset.id
    
    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@patch.dict(os.environ, {
    "AWS_ACCESS_KEY_ID": "test_key",
    "AWS_SECRET_ACCESS_KEY": "test_secret",
    "AWS_S3_BUCKET": "test-bucket",
})
def test_transform_video_not_downloaded(db_session, test_channel):
    """Test transformation of non-downloaded video"""
    video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test123",
        source_title="Test Video",
        source_platform="youtube",
        download_status="pending",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    
    with patch("src.services.transformation.transformation_service.S3StorageClient"):
        with patch("src.services.transformation.transformation_service.VideoTransformer"):
            service = TransformationService(db_session)
            
            with pytest.raises(Exception):  # TransformationError
                service.transform_video(video.id)
