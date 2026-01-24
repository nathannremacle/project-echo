"""
Unit tests for utility functions
"""

import pytest

from src.utils.common.helpers import (
    generate_uuid,
    generate_request_id,
    hash_string,
    get_current_timestamp,
    truncate_string,
    sanitize_filename,
    format_file_size,
    validate_youtube_channel_id,
    validate_youtube_video_id,
)


def test_generate_uuid():
    """Test UUID generation"""
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()
    
    assert uuid1 != uuid2
    assert len(uuid1) == 36  # Standard UUID length
    assert uuid1.count("-") == 4


def test_generate_request_id():
    """Test request ID generation"""
    request_id = generate_request_id()
    assert len(request_id) == 36
    assert isinstance(request_id, str)


def test_hash_string():
    """Test string hashing"""
    result = hash_string("test")
    assert isinstance(result, str)
    assert len(result) == 64  # SHA256 hex digest length


def test_get_current_timestamp():
    """Test timestamp generation"""
    timestamp = get_current_timestamp()
    assert "T" in timestamp
    assert "Z" in timestamp or "+" in timestamp


def test_truncate_string():
    """Test string truncation"""
    long_string = "a" * 100
    truncated = truncate_string(long_string, 50)
    assert len(truncated) == 50
    assert truncated.endswith("...")
    
    short_string = "short"
    not_truncated = truncate_string(short_string, 50)
    assert not_truncated == short_string


def test_sanitize_filename():
    """Test filename sanitization"""
    invalid = "test<>file:name.txt"
    sanitized = sanitize_filename(invalid)
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert ":" not in sanitized


def test_format_file_size():
    """Test file size formatting"""
    assert format_file_size(1024) == "1.00 KB"
    assert format_file_size(1024 * 1024) == "1.00 MB"
    assert format_file_size(500) == "500.00 B"


def test_validate_youtube_channel_id():
    """Test YouTube channel ID validation"""
    assert validate_youtube_channel_id("UC1234567890123456789012") is True
    assert validate_youtube_channel_id("UC123") is False
    assert validate_youtube_channel_id("") is False
    assert validate_youtube_channel_id("not_a_channel_id") is False


def test_validate_youtube_video_id():
    """Test YouTube video ID validation"""
    assert validate_youtube_video_id("dQw4w9WgXcQ") is True
    assert validate_youtube_video_id("short") is False
    assert validate_youtube_video_id("") is False
    assert validate_youtube_video_id("too_long_video_id") is False
