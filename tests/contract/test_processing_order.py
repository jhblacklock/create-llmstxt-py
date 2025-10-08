"""Contract tests for processing order validation."""

import pytest
from unittest.mock import Mock, patch
from url_filtering import URLFilteringService


class TestProcessingOrderContract:
    """Test cases for processing order contract compliance."""
    
    def test_filtering_before_max_urls_contract(self):
        """Test that filtering happens before max-urls limiting."""
        # Simulate the processing order as implemented in generate_llmstxt.py
        original_urls = [
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
            "https://example.com/blog/post1",
            "https://example.com/blog/post2",
            "https://example.com/api/endpoint1",
            "https://example.com/api/endpoint2",
            "https://example.com/about",
            "https://example.com/contact"
        ]
        
        # Step 1: Apply filtering (as done in generate_llmstxt.py)
        filtered_set = URLFilteringService.filter_urls(original_urls, ".*/docs/.*")
        filtered_urls = filtered_set.filtered_urls
        
        # Contract: Filtering should reduce the number of URLs
        assert len(filtered_urls) < len(original_urls)
        assert len(filtered_urls) == 2  # Only docs pages
        
        # Step 2: Apply max-urls limiting (as done in generate_llmstxt.py)
        max_urls = 1
        final_urls = filtered_urls[:max_urls]
        
        # Contract: Final URLs should be limited by max_urls
        assert len(final_urls) <= max_urls
        assert len(final_urls) == 1  # Limited to 1 URL
        
        # Contract: Final URLs should all be from the filtered set
        assert all(url in filtered_urls for url in final_urls)
        assert all(url in original_urls for url in final_urls)
    
    def test_processing_order_with_no_filtering(self):
        """Test processing order when no filtering is applied."""
        original_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
            "https://example.com/page4",
            "https://example.com/page5"
        ]
        
        # Step 1: No filtering applied (include_patterns is None)
        filtered_urls = original_urls  # No filtering
        
        # Step 2: Apply max-urls limiting
        max_urls = 3
        final_urls = filtered_urls[:max_urls]
        
        # Contract: Should respect max_urls limit
        assert len(final_urls) == max_urls
        assert final_urls == original_urls[:max_urls]
    
    def test_processing_order_with_high_filtering_ratio(self):
        """Test processing order when filtering removes most URLs."""
        original_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
            "https://example.com/page4",
            "https://example.com/page5"
        ]
        
        # Step 1: Apply strict filtering
        filtered_set = URLFilteringService.filter_urls(original_urls, ".*page1$")
        filtered_urls = filtered_set.filtered_urls
        
        # Contract: Filtering should significantly reduce URLs
        assert len(filtered_urls) == 1
        assert filtered_urls == ["https://example.com/page1"]
        
        # Step 2: Apply max-urls limiting
        max_urls = 10  # Higher than filtered count
        final_urls = filtered_urls[:max_urls]
        
        # Contract: Should not exceed available filtered URLs
        assert len(final_urls) == 1  # Only 1 URL available
        assert final_urls == filtered_urls
    
    def test_processing_order_with_zero_matches(self):
        """Test processing order when filtering results in zero matches."""
        original_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        # Step 1: Apply filtering that matches nothing
        filtered_set = URLFilteringService.filter_urls(original_urls, ".*/nonexistent/.*")
        filtered_urls = filtered_set.filtered_urls
        
        # Contract: Filtering should result in empty list
        assert len(filtered_urls) == 0
        assert filtered_urls == []
        
        # Step 2: Apply max-urls limiting
        max_urls = 5
        final_urls = filtered_urls[:max_urls]
        
        # Contract: Should remain empty
        assert len(final_urls) == 0
        assert final_urls == []
    
    def test_processing_order_performance_contract(self):
        """Test that processing order meets performance requirements."""
        import time
        
        # Create a large URL list
        large_url_list = [f"https://example.com/page{i}" for i in range(1000)]
        large_url_list.extend([f"https://example.com/docs/page{i}" for i in range(100)])
        
        # Test filtering performance
        start_time = time.time()
        filtered_set = URLFilteringService.filter_urls(large_url_list, ".*/docs/.*")
        filtering_time = time.time() - start_time
        
        # Contract: Filtering should be fast
        assert filtering_time < 1.0  # Under 1 second
        
        # Test max-urls limiting performance
        start_time = time.time()
        final_urls = filtered_set.filtered_urls[:50]
        limiting_time = time.time() - start_time
        
        # Contract: Limiting should be very fast
        assert limiting_time < 0.1  # Under 100ms
        
        # Contract: Results should be correct
        assert len(final_urls) == 50
        assert all("docs" in url for url in final_urls)
    
    def test_processing_order_memory_contract(self):
        """Test that processing order doesn't use excessive memory."""
        import sys
        
        # Create a moderately large URL list
        url_list = [f"https://example.com/page{i}" for i in range(1000)]
        
        # Measure memory usage
        initial_memory = sys.getsizeof(url_list)
        
        # Apply filtering
        filtered_set = URLFilteringService.filter_urls(url_list, ".*/page[0-9]+$")
        
        # Measure memory after filtering
        filtered_memory = sys.getsizeof(filtered_set.original_urls) + sys.getsizeof(filtered_set.filtered_urls)
        
        # Contract: Memory usage should be reasonable
        assert filtered_memory < initial_memory * 2.5  # Should not significantly increase memory usage
        
        # Apply max-urls limiting
        final_urls = filtered_set.filtered_urls[:100]
        final_memory = sys.getsizeof(final_urls)
        
        # Contract: Final memory usage should be smaller
        assert final_memory < filtered_memory
    
    def test_processing_order_consistency_contract(self):
        """Test that processing order is consistent across multiple runs."""
        original_urls = [
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
            "https://example.com/blog/post1",
            "https://example.com/blog/post2"
        ]
        
        # Run processing multiple times
        results = []
        for _ in range(10):
            filtered_set = URLFilteringService.filter_urls(original_urls, ".*/docs/.*")
            final_urls = filtered_set.filtered_urls[:2]  # Limit to 2 URLs
            results.append(final_urls)
        
        # Contract: Results should be consistent
        for result in results:
            assert result == results[0]  # All results should be identical
            assert len(result) == 2
            assert all("docs" in url for url in result)
    
    def test_processing_order_edge_cases_contract(self):
        """Test processing order with edge cases."""
        # Test with empty URL list
        empty_urls = []
        filtered_set = URLFilteringService.filter_urls(empty_urls, ".*")
        final_urls = filtered_set.filtered_urls[:10]
        assert final_urls == []
        
        # Test with single URL
        single_url = ["https://example.com/page1"]
        filtered_set = URLFilteringService.filter_urls(single_url, ".*")
        final_urls = filtered_set.filtered_urls[:1]
        assert final_urls == single_url
        
        # Test with very large max_urls
        url_list = ["https://example.com/page1", "https://example.com/page2"]
        filtered_set = URLFilteringService.filter_urls(url_list, ".*")
        final_urls = filtered_set.filtered_urls[:1000]  # Much larger than available
        assert final_urls == url_list  # Should return all available URLs
        
        # Test with zero max_urls
        final_urls = filtered_set.filtered_urls[:0]
        assert final_urls == []
    
    def test_processing_order_data_integrity_contract(self):
        """Test that processing order maintains data integrity."""
        original_urls = [
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
            "https://example.com/blog/post1",
            "https://example.com/blog/post2"
        ]
        
        # Apply filtering
        filtered_set = URLFilteringService.filter_urls(original_urls, ".*/docs/.*")
        
        # Contract: Filtered URLs should be a subset of original URLs
        assert all(url in original_urls for url in filtered_set.filtered_urls)
        
        # Contract: Original URLs should not be modified
        assert len(original_urls) == 4
        assert "https://example.com/docs/page1" in original_urls
        
        # Apply max-urls limiting
        final_urls = filtered_set.filtered_urls[:1]
        
        # Contract: Final URLs should be a subset of filtered URLs
        assert all(url in filtered_set.filtered_urls for url in final_urls)
        
        # Contract: Final URLs should be a subset of original URLs
        assert all(url in original_urls for url in final_urls)

