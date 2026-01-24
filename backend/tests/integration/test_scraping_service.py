"""
Integration tests for scraping service
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.database import Base, SessionLocal
from src.models.channel import Channel
from src.models.video import Video
from src.services.scraping.scraping_service import ScrapingService
from src.repositories.channel_repository import ChannelRepository


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
        content_filters=json.dumps({
            "sources": ["https://youtube.com/watch?v=test1"],
            "keywords": ["edit video"],
            "min_resolution": "720p",
            "min_views": 1000,
            "max_duration": 300,
            "exclude_watermarked": True,
        }),
        metadata_template=json.dumps({}),
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@patch("src.services.scraping.scraping_service.YouTubeScraper")
def test_scrape_single_video(mock_scraper_class, db_session, test_channel):
    """Test scraping a single video"""
    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    
    mock_metadata = {
        "url": "https://youtube.com/watch?v=test1",
        "title": "Test Video",
        "description": "Test description",
        "duration": 120,
        "creator": "Test Creator",
        "creator_id": "UC123",
        "view_count": 5000,
        "like_count": 100,
        "resolution": "1080p",
        "width": 1920,
        "height": 1080,
        "thumbnail_url": "https://example.com/thumb.jpg",
        "upload_date": "20230101",
        "platform": "youtube",
    }
    mock_scraper.scrape_video.return_value = mock_metadata
    
    service = ScrapingService(db_session)
    video = service.scrape_single_video("https://youtube.com/watch?v=test1", test_channel.id)
    
    assert video is not None
    assert video.source_url == "https://youtube.com/watch?v=test1"
    assert video.source_title == "Test Video"
    assert video.source_creator == "Test Creator"
    assert video.download_status == "pending"


@patch("src.services.scraping.scraping_service.YouTubeScraper")
@patch("src.services.scraping.scraping_service.apply_filters")
def test_scrape_for_channel(mock_apply_filters, mock_scraper_class, db_session, test_channel):
    """Test scraping for a channel"""
    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    mock_scraper.rate_limit_delay = 1.0
    
    mock_metadata = {
        "url": "https://youtube.com/watch?v=test1",
        "title": "Test Video",
        "description": "Test description",
        "duration": 120,
        "creator": "Test Creator",
        "resolution": "1080p",
        "view_count": 5000,
        "platform": "youtube",
    }
    
    mock_scraper.scrape_video.return_value = mock_metadata
    mock_apply_filters.return_value = True
    
    service = ScrapingService(db_session)
    result = service.scrape_for_channel(test_channel.id)
    
    assert result.success is True
    assert result.videos_found > 0
    assert result.videos_stored > 0


def test_duplicate_detection(db_session, test_channel):
    """Test duplicate video detection"""
    # Create existing video
    existing_video = Video(
        channel_id=test_channel.id,
        source_url="https://youtube.com/watch?v=test1",
        source_title="Existing Video",
        source_platform="youtube",
    )
    db_session.add(existing_video)
    db_session.commit()
    
    service = ScrapingService(db_session)
    is_duplicate = service._is_duplicate("https://youtube.com/watch?v=test1", test_channel.id)
    
    assert is_duplicate is True
    
    is_duplicate = service._is_duplicate("https://youtube.com/watch?v=test2", test_channel.id)
    assert is_duplicate is False
