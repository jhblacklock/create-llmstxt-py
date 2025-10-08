"""Unit tests for URL filtering service."""

import pytest
import re
from url_filtering import URLFilteringService, FilteredURLSet


class TestURLFilteringService:
    """Test cases for URLFilteringService."""
    
    def test_filter_urls_basic_patterns(self, sample_urls):
        """Test filtering with basic regex patterns."""
        # Test docs pattern
        result = URLFilteringService.filter_urls(sample_urls, r".*/docs/.*")
        assert isinstance(result, FilteredURLSet)
        assert len(result.original_urls) == len(sample_urls)
        assert result.filter_count == 2
        assert result.filter_ratio == 2/8
        assert "https://example.com/docs/page1" in result.filtered_urls
        assert "https://example.com/docs/page2" in result.filtered_urls
        
        # Test blog pattern
        result = URLFilteringService.filter_urls(sample_urls, r".*/blog/.*")
        assert result.filter_count == 2
        assert "https://example.com/blog/post1" in result.filtered_urls
        assert "https://example.com/blog/post2" in result.filtered_urls
        
        # Test api pattern
        result = URLFilteringService.filter_urls(sample_urls, r".*/api/.*")
        assert result.filter_count == 2
        assert "https://example.com/api/endpoint1" in result.filtered_urls
        assert "https://example.com/api/endpoint2" in result.filtered_urls
    
    def test_filter_urls_no_matches(self, sample_urls):
        """Test filtering when no URLs match the pattern."""
        result = URLFilteringService.filter_urls(sample_urls, r".*/nonexistent/.*")
        assert result.filter_count == 0
        assert result.filter_ratio == 0.0
        assert result.filtered_urls == []
    
    def test_filter_urls_all_matches(self, sample_urls):
        """Test filtering when all URLs match the pattern."""
        result = URLFilteringService.filter_urls(sample_urls, r".*")
        assert result.filter_count == len(sample_urls)
        assert result.filter_ratio == 1.0
        assert result.filtered_urls == sample_urls
    
    def test_filter_urls_empty_url_list(self):
        """Test filtering with empty URL list."""
        result = URLFilteringService.filter_urls([], r".*")
        assert result.filter_count == 0
        assert result.filter_ratio == 0.0
        assert result.filtered_urls == []
        assert len(result.original_urls) == 0
    
    def test_filter_urls_complex_patterns(self, sample_urls):
        """Test filtering with complex regex patterns."""
        # Test case-insensitive pattern
        result = URLFilteringService.filter_urls(sample_urls, r"(?i).*DOCS.*")
        assert result.filter_count == 2
        
        # Test exact match pattern
        result = URLFilteringService.filter_urls(sample_urls, r"^https://example\.com/docs/page1$")
        assert result.filter_count == 1
        assert result.filtered_urls == ["https://example.com/docs/page1"]
        
        # Test multiple alternatives
        result = URLFilteringService.filter_urls(sample_urls, r".*/(docs|blog)/.*")
        assert result.filter_count == 4
    
    def test_filter_urls_invalid_pattern(self, sample_urls):
        """Test filtering with invalid regex pattern."""
        with pytest.raises(re.error):
            URLFilteringService.filter_urls(sample_urls, "[invalid")
    
    def test_filter_urls_empty_pattern(self, sample_urls):
        """Test filtering with empty pattern."""
        with pytest.raises(ValueError, match="Pattern cannot be empty"):
            URLFilteringService.filter_urls(sample_urls, "")
    
    def test_filter_urls_none_pattern(self, sample_urls):
        """Test filtering with None pattern."""
        with pytest.raises(ValueError, match="Pattern cannot be empty"):
            URLFilteringService.filter_urls(sample_urls, None)
    
    def test_filter_urls_whitespace_pattern(self, sample_urls):
        """Test filtering with whitespace-only pattern."""
        with pytest.raises(ValueError, match="Pattern cannot be empty"):
            URLFilteringService.filter_urls(sample_urls, "   ")
    
    def test_filter_urls_performance(self):
        """Test filtering performance with large URL list."""
        # Generate a large list of URLs
        large_url_list = [
            f"https://example.com/page{i}" for i in range(1000)
        ] + [
            f"https://example.com/docs/page{i}" for i in range(100)
        ]
        
        result = URLFilteringService.filter_urls(large_url_list, r".*/docs/.*")
        assert result.filter_count == 100
        assert len(result.original_urls) == 1100
        assert result.filter_ratio == 100/1100
    
    def test_filter_urls_special_characters(self):
        """Test filtering with URLs containing special characters."""
        special_urls = [
            "https://example.com/page+with+plus",
            "https://example.com/page?query=value",
            "https://example.com/page#fragment",
            "https://example.com/page with spaces",
            "https://example.com/page%20encoded",
        ]
        
        # Test pattern that matches special characters
        result = URLFilteringService.filter_urls(special_urls, r".*\+.*")
        assert result.filter_count == 1
        assert "https://example.com/page+with+plus" in result.filtered_urls
        
        # Test pattern that matches query parameters
        result = URLFilteringService.filter_urls(special_urls, r".*\?.*")
        assert result.filter_count == 1
        assert "https://example.com/page?query=value" in result.filtered_urls


class TestFilteredURLSet:
    """Test cases for FilteredURLSet data class."""
    
    def test_filtered_url_set_valid_creation(self):
        """Test creating a valid FilteredURLSet."""
        original_urls = ["url1", "url2", "url3"]
        filtered_urls = ["url1", "url3"]
        
        result = FilteredURLSet(
            original_urls=original_urls,
            filtered_urls=filtered_urls,
            filter_count=2,
            filter_ratio=2/3
        )
        
        assert result.original_urls == original_urls
        assert result.filtered_urls == filtered_urls
        assert result.filter_count == 2
        assert result.filter_ratio == 2/3
    
    def test_filtered_url_set_invalid_subset(self):
        """Test FilteredURLSet validation with invalid subset."""
        original_urls = ["url1", "url2", "url3"]
        filtered_urls = ["url1", "url4"]  # url4 not in original_urls
        
        with pytest.raises(ValueError, match="filtered_urls must be a subset"):
            FilteredURLSet(
                original_urls=original_urls,
                filtered_urls=filtered_urls,
                filter_count=2,
                filter_ratio=2/3
            )
    
    def test_filtered_url_set_count_mismatch(self):
        """Test FilteredURLSet validation with count mismatch."""
        original_urls = ["url1", "url2", "url3"]
        filtered_urls = ["url1", "url2"]
        
        with pytest.raises(ValueError, match="filter_count must match length"):
            FilteredURLSet(
                original_urls=original_urls,
                filtered_urls=filtered_urls,
                filter_count=3,  # Wrong count
                filter_ratio=2/3
            )
    
    def test_filtered_url_set_invalid_ratio(self):
        """Test FilteredURLSet validation with invalid ratio."""
        original_urls = ["url1", "url2", "url3"]
        filtered_urls = ["url1", "url2"]
        
        with pytest.raises(ValueError, match="filter_ratio must be between"):
            FilteredURLSet(
                original_urls=original_urls,
                filtered_urls=filtered_urls,
                filter_count=2,
                filter_ratio=1.5  # Invalid ratio > 1.0
            )
    
    def test_filtered_url_set_empty_original(self):
        """Test FilteredURLSet with empty original URLs."""
        result = FilteredURLSet(
            original_urls=[],
            filtered_urls=[],
            filter_count=0,
            filter_ratio=0.0
        )
        
        assert result.original_urls == []
        assert result.filtered_urls == []
        assert result.filter_count == 0
        assert result.filter_ratio == 0.0

