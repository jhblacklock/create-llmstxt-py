"""Unit tests for edge cases and additional scenarios."""

import pytest
from url_filtering import PatternValidationService, URLFilteringService, ErrorHandlingService


class TestEdgeCases:
    """Test cases for edge cases and additional scenarios."""
    
    def test_very_long_pattern(self):
        """Test pattern validation with very long regex pattern."""
        long_pattern = "a" * 1000 + ".*" + "b" * 1000
        
        result = PatternValidationService.validate_pattern(long_pattern)
        assert result.is_valid is True
        assert result.compiled_pattern is not None
    
    def test_unicode_pattern(self):
        """Test pattern validation with unicode characters."""
        unicode_patterns = [
            r"[\u4e00-\u9fff]+",  # Chinese characters
            r"[\u3040-\u309f]+",  # Hiragana
            r"[\u30a0-\u30ff]+",  # Katakana
            r"[\u0400-\u04ff]+",  # Cyrillic
        ]
        
        for pattern in unicode_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is True
            assert result.compiled_pattern is not None
    
    def test_very_large_url_list(self):
        """Test URL filtering with very large URL list."""
        large_url_list = [f"https://example.com/page{i}" for i in range(10000)]
        large_url_list.extend([f"https://example.com/docs/page{i}" for i in range(1000)])
        
        result = URLFilteringService.filter_urls(large_url_list, ".*/docs/.*")
        
        assert result.filter_count == 1000
        assert len(result.original_urls) == 11000
        assert result.filter_ratio == 1000/11000
        assert len(result.filtered_urls) == 1000
    
    def test_empty_url_list(self):
        """Test URL filtering with empty URL list."""
        result = URLFilteringService.filter_urls([], ".*")
        
        assert result.filter_count == 0
        assert len(result.original_urls) == 0
        assert result.filter_ratio == 0.0
        assert result.filtered_urls == []
    
    def test_single_url(self):
        """Test URL filtering with single URL."""
        single_url = ["https://example.com/page1"]
        
        result = URLFilteringService.filter_urls(single_url, ".*")
        assert result.filter_count == 1
        assert result.filtered_urls == single_url
        
        result = URLFilteringService.filter_urls(single_url, ".*/nonexistent/.*")
        assert result.filter_count == 0
        assert result.filtered_urls == []
    
    def test_pattern_with_special_regex_characters(self):
        """Test patterns with special regex characters."""
        special_patterns = [
            r"\.",  # Escaped dot
            r"\*",  # Escaped asterisk
            r"\+",  # Escaped plus
            r"\?",  # Escaped question mark
            r"\[",  # Escaped bracket
            r"\]",  # Escaped bracket
            r"\(",  # Escaped parenthesis
            r"\)",  # Escaped parenthesis
            r"\{",  # Escaped brace
            r"\}",  # Escaped brace
            r"\|",  # Escaped pipe
            r"\^",  # Escaped caret
            r"\$",  # Escaped dollar
        ]
        
        for pattern in special_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is True
            assert result.compiled_pattern is not None
    
    def test_complex_regex_patterns(self):
        """Test complex regex patterns."""
        complex_patterns = [
            r"^https://.*\.com$",  # Exact domain match
            r".*\.(html|pdf|doc)$",  # File extension match
            r".*/(\d{4})/(\d{2})/.*",  # Date pattern
            r".*[?&]id=(\d+).*",  # Query parameter match
            r".*#section-\d+$",  # Fragment match
            r".*[A-Z]{2,}.*",  # Uppercase letters
            r".*\d{3,}.*",  # Multiple digits
        ]
        
        for pattern in complex_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is True
            assert result.compiled_pattern is not None
    
    def test_error_handling_with_very_long_pattern(self):
        """Test error handling with very long invalid pattern."""
        long_invalid_pattern = "[" + "a" * 1000  # Very long invalid pattern
        
        result = PatternValidationService.validate_pattern(long_invalid_pattern)
        assert result.is_valid is False
        assert "Invalid regex pattern" in result.error_message
        assert long_invalid_pattern in result.error_message
    
    def test_error_handling_with_unicode_pattern(self):
        """Test error handling with unicode in pattern."""
        unicode_invalid_pattern = "[\u4e00-\u9fff"  # Invalid unicode range
        
        result = PatternValidationService.validate_pattern(unicode_invalid_pattern)
        assert result.is_valid is False
        assert "Invalid regex pattern" in result.error_message
    
    def test_url_filtering_with_unicode_urls(self):
        """Test URL filtering with unicode in URLs."""
        unicode_urls = [
            "https://example.com/中文页面",
            "https://example.com/ページ",
            "https://example.com/страница",
            "https://example.com/page1",
        ]
        
        # Test with unicode pattern
        result = URLFilteringService.filter_urls(unicode_urls, r".*[\u4e00-\u9fff].*")
        assert result.filter_count == 1
        assert "中文页面" in result.filtered_urls[0]
        
        # Test with regular pattern
        result = URLFilteringService.filter_urls(unicode_urls, r".*page.*")
        assert result.filter_count == 1  # Only page1 contains "page" in ASCII
    
    def test_url_filtering_with_special_characters_in_urls(self):
        """Test URL filtering with special characters in URLs."""
        special_urls = [
            "https://example.com/page+with+plus",
            "https://example.com/page?query=value",
            "https://example.com/page#fragment",
            "https://example.com/page with spaces",
            "https://example.com/page%20encoded",
            "https://example.com/page&param=value",
        ]
        
        # Test with plus sign pattern
        result = URLFilteringService.filter_urls(special_urls, r".*\+.*")
        assert result.filter_count == 1
        assert "page+with+plus" in result.filtered_urls[0]
        
        # Test with query parameter pattern
        result = URLFilteringService.filter_urls(special_urls, r".*\?.*")
        assert result.filter_count == 1
        assert "query=value" in result.filtered_urls[0]
        
        # Test with fragment pattern
        result = URLFilteringService.filter_urls(special_urls, r".*#.*")
        assert result.filter_count == 1
        assert "fragment" in result.filtered_urls[0]
    
    def test_performance_with_repeated_patterns(self):
        """Test performance with repeated pattern compilation."""
        import time
        
        pattern = ".*/docs/.*"
        url_list = [f"https://example.com/page{i}" for i in range(1000)]
        
        # Test repeated pattern validation
        start_time = time.time()
        for _ in range(100):
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is True
        validation_time = time.time() - start_time
        
        # Should be fast (under 1 second for 100 validations)
        assert validation_time < 1.0
        
        # Test repeated URL filtering
        start_time = time.time()
        for _ in range(10):
            result = URLFilteringService.filter_urls(url_list, pattern)
            assert result.filter_count == 0  # No docs URLs
        filtering_time = time.time() - start_time
        
        # Should be fast (under 1 second for 10 filterings)
        assert filtering_time < 1.0
    
    def test_memory_usage_with_large_datasets(self):
        """Test memory usage with large datasets."""
        import sys
        
        # Create large URL list
        large_url_list = [f"https://example.com/page{i}" for i in range(10000)]
        
        # Measure memory before filtering
        initial_memory = sys.getsizeof(large_url_list)
        
        # Apply filtering
        result = URLFilteringService.filter_urls(large_url_list, ".*/page[0-9]+$")
        
        # Measure memory after filtering
        filtered_memory = sys.getsizeof(result.original_urls) + sys.getsizeof(result.filtered_urls)
        
        # Memory usage should be reasonable (not more than 2.5x original)
        assert filtered_memory < initial_memory * 2.5
        
        # Results should be correct
        assert result.filter_count == 10000
        assert len(result.original_urls) == 10000
        assert result.filter_ratio == 1.0
    
    def test_edge_case_patterns(self):
        """Test edge case patterns that might cause issues."""
        edge_patterns = [
            "",  # Empty pattern
            ".*",  # Match everything
            "^$",  # Match empty string
            "a*",  # Zero or more
            "a+",  # One or more
            "a?",  # Zero or one
            "a{0,}",  # Zero or more (same as *)
            "a{1,}",  # One or more (same as +)
            "a{0,1}",  # Zero or one (same as ?)
            "a{5}",  # Exactly 5
            "a{5,10}",  # Between 5 and 10
            "a{5,}",  # 5 or more
        ]
        
        for pattern in edge_patterns:
            if pattern == "":
                # Empty pattern should be invalid
                result = PatternValidationService.validate_pattern(pattern)
                assert result.is_valid is False
            else:
                # Other patterns should be valid
                result = PatternValidationService.validate_pattern(pattern)
                assert result.is_valid is True
                assert result.compiled_pattern is not None

