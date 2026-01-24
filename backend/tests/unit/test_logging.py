"""
Unit tests for logging configuration
"""

import logging
import sys
from unittest.mock import patch

import pytest

from src.utils.logging import setup_logging, get_logger, TextFormatter


def test_setup_logging():
    """Test that logging setup works"""
    # This should not raise any exceptions
    setup_logging()
    
    # Verify root logger is configured
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0


def test_get_logger():
    """Test that get_logger returns a logger instance"""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_text_formatter():
    """Test TextFormatter formats log records correctly"""
    formatter = TextFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    
    formatted = formatter.format(record)
    assert "Test message" in formatted
    assert "INFO" in formatted
