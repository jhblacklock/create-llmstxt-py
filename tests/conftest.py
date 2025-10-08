"""Test configuration and fixtures for create-llmstxt-py tests."""

import pytest
import logging
from unittest.mock import Mock


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def sample_urls():
    """Provide sample URLs for testing filtering."""
    return [
        "https://example.com/docs/page1",
        "https://example.com/docs/page2", 
        "https://example.com/blog/post1",
        "https://example.com/blog/post2",
        "https://example.com/api/endpoint1",
        "https://example.com/api/endpoint2",
        "https://example.com/about",
        "https://example.com/contact"
    ]


@pytest.fixture
def sample_patterns():
    """Provide sample regex patterns for testing."""
    return {
        "docs": r".*/docs/.*",
        "blog": r".*/blog/.*", 
        "api": r".*/api/.*",
        "invalid": r"[invalid",
        "empty": "",
        "complex": r"https://example\.com/(docs|blog)/.*\.html$"
    }

