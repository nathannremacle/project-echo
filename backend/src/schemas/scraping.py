"""
Scraping request/response schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ScrapedVideoMetadata(BaseModel):
    """Metadata for a scraped video"""

    url: str = Field(..., description="Video URL")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    duration: int = Field(..., description="Duration in seconds")
    creator: Optional[str] = Field(None, description="Creator/channel name")
    creator_id: Optional[str] = Field(None, description="Creator/channel ID")
    view_count: Optional[int] = Field(None, description="View count")
    like_count: Optional[int] = Field(None, description="Like count")
    resolution: Optional[str] = Field(None, description="Video resolution (e.g., '720p', '1080p')")
    width: Optional[int] = Field(None, description="Video width in pixels")
    height: Optional[int] = Field(None, description="Video height in pixels")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    upload_date: Optional[str] = Field(None, description="Upload date")
    platform: str = Field(default="youtube", description="Source platform")


class ScrapingConfig(BaseModel):
    """Configuration for scraping operation"""

    sources: List[str] = Field(default_factory=list, description="List of URLs (search, playlists, channels)")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    min_resolution: str = Field(default="720p", description="Minimum resolution (e.g., '720p', '1080p')")
    min_views: Optional[int] = Field(None, description="Minimum view count for viral filtering")
    max_duration: Optional[int] = Field(None, description="Maximum duration in seconds")
    max_results: int = Field(default=10, description="Maximum number of videos to scrape")
    exclude_watermarked: bool = Field(default=True, description="Prefer non-watermarked videos")


class ScrapingResult(BaseModel):
    """Result of a scraping operation"""

    success: bool = Field(..., description="Whether scraping was successful")
    videos_found: int = Field(..., description="Number of videos found")
    videos_filtered: int = Field(..., description="Number of videos after filtering")
    videos_stored: int = Field(..., description="Number of videos stored in database")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    metadata: List[ScrapedVideoMetadata] = Field(default_factory=list, description="Scraped video metadata")
