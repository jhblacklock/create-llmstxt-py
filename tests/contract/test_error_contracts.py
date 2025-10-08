"""Contract tests for error message formats."""

import pytest
import re
from url_filtering import ErrorHandlingService, PatternValidationService, URLFilteringService


class TestErrorContracts:
    """Test cases for error message contract compliance."""
    
    def test_pattern_validation_error_contract(self):
        """Test that pattern validation errors follow the contract."""
        invalid_patterns = [
            "[invalid",
            "(unclosed", 
            "*bad",
            "[z-a]",
            "a{2,1}",
            ""
        ]
        
        for pattern in invalid_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            
            # Contract: Invalid patterns should have is_valid=False
            assert result.is_valid is False
            
            # Contract: Error message should be present
            assert result.error_message is not None
            assert isinstance(result.error_message, str)
            assert len(result.error_message) > 0
            
            # Contract: Compiled pattern should be None
            assert result.compiled_pattern is None
    
    def test_user_friendly_error_contract(self):
        """Test that user-friendly error messages follow the contract."""
        error_cases = [
            (re.error("unexpected end of regular expression"), "[invalid"),
            (re.error("unbalanced parenthesis"), "(unclosed"),
            (re.error("nothing to repeat"), "*bad"),
            (re.error("bad character range"), "[z-a]"),
            (re.error("unterminated character set"), "[a-z"),
        ]
        
        for error, pattern in error_cases:
            error_msg = ErrorHandlingService.generate_user_friendly_error(error, pattern)
            
            # Contract: Error message should be a non-empty string
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0
            
            # Contract: Should contain pattern information
            assert "Invalid regex pattern" in error_msg
            assert pattern in error_msg
            
            # Contract: Should contain error details
            assert "Error:" in error_msg
            assert str(error) in error_msg
            
            # Contract: Should contain suggestion for common errors
            if "unexpected end" in str(error) or "unbalanced" in str(error):
                assert "Suggestion:" in error_msg
    
    def test_no_matches_message_contract(self):
        """Test that no matches messages follow the contract."""
        test_cases = [
            (".*/docs/.*", 10),
            (".*/blog/.*", 100),
            (r"https://.*\.com$", 1000),
            (".*/nonexistent/.*", 0),
        ]
        
        for pattern, total_urls in test_cases:
            message = ErrorHandlingService.generate_no_matches_message(pattern, total_urls)
            
            # Contract: Message should be a non-empty string
            assert isinstance(message, str)
            assert len(message) > 0
            
            # Contract: Should contain pattern information
            assert "No URLs matched" in message
            assert pattern in message
            
            # Contract: Should contain URL count information
            assert str(total_urls) in message
            assert "discovered URLs" in message
            
            # Contract: Should indicate no files will be generated
            assert "No llms.txt files will be generated" in message
    
    def test_url_filtering_error_contract(self):
        """Test that URL filtering errors follow the contract."""
        sample_urls = ["https://example.com/page1", "https://example.com/page2"]
        
        # Test empty pattern error
        with pytest.raises(ValueError) as exc_info:
            URLFilteringService.filter_urls(sample_urls, "")
        
        error_msg = str(exc_info.value)
        assert "Pattern cannot be empty" in error_msg
        
        # Test invalid pattern error
        with pytest.raises(re.error) as exc_info:
            URLFilteringService.filter_urls(sample_urls, "[invalid")
        
        error_msg = str(exc_info.value)
        assert "Invalid regex pattern" in error_msg
        assert "[invalid" in error_msg
    
    def test_error_message_consistency_contract(self):
        """Test that error messages are consistent across similar error types."""
        # Test pattern validation consistency
        empty_patterns = ["", "   ", "\t", "\n"]
        for pattern in empty_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert "Pattern cannot be empty" in result.error_message
        
        # Test regex syntax error consistency
        syntax_error_patterns = ["[invalid", "(unclosed", "*bad"]
        for pattern in syntax_error_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert "Invalid regex pattern" in result.error_message
            assert pattern in result.error_message
    
    def test_error_message_format_contract(self):
        """Test that error messages follow the expected format contract."""
        # Test user-friendly error format
        error = re.error("unexpected end of regular expression")
        pattern = "[invalid"
        error_msg = ErrorHandlingService.generate_user_friendly_error(error, pattern)
        
        # Format: "Invalid regex pattern: '{pattern}'. Error: {error}. Suggestion: {hint}"
        parts = error_msg.split(". ")
        assert len(parts) >= 3  # At least 3 parts separated by ". "
        assert parts[0].startswith("Invalid regex pattern:")
        assert f"'{pattern}'" in parts[0]
        assert parts[1].startswith("Error:")
        assert "unexpected end of regular expression" in parts[1]
        assert parts[2].startswith("Suggestion:")
    
    def test_no_matches_message_format_contract(self):
        """Test that no matches messages follow the expected format contract."""
        pattern = ".*/docs/.*"
        total_urls = 50
        message = ErrorHandlingService.generate_no_matches_message(pattern, total_urls)
        
        # Format: "No URLs matched the pattern '{pattern}' out of {count} discovered URLs. No llms.txt files will be generated."
        assert message.startswith("No URLs matched")
        assert f"'{pattern}'" in message
        assert f"out of {total_urls} discovered URLs" in message
        assert message.endswith("No llms.txt files will be generated.")
    
    def test_error_handling_performance_contract(self):
        """Test that error handling meets performance requirements."""
        import time
        
        # Test error message generation performance
        error = re.error("unexpected end of regular expression")
        pattern = "[invalid"
        
        start_time = time.time()
        for _ in range(1000):
            ErrorHandlingService.generate_user_friendly_error(error, pattern)
        generation_time = time.time() - start_time
        
        # Should be fast (under 1 second for 1000 generations)
        assert generation_time < 1.0
        
        # Test no matches message generation performance
        start_time = time.time()
        for _ in range(1000):
            ErrorHandlingService.generate_no_matches_message(pattern, 100)
        generation_time = time.time() - start_time
        
        # Should be fast (under 1 second for 1000 generations)
        assert generation_time < 1.0
    
    def test_error_message_memory_contract(self):
        """Test that error messages don't use excessive memory."""
        import sys
        
        # Test memory usage for error message generation
        error = re.error("unexpected end of regular expression")
        pattern = "[invalid"
        
        # Generate many error messages
        messages = []
        for _ in range(1000):
            msg = ErrorHandlingService.generate_user_friendly_error(error, pattern)
            messages.append(msg)
        
        # Check that memory usage is reasonable
        total_memory = sum(sys.getsizeof(msg) for msg in messages)
        assert total_memory < 1000000  # Should be under 1MB for 1000 messages
    
    def test_error_contract_edge_cases(self):
        """Test error handling contract for edge cases."""
        # Test with very long pattern
        long_pattern = "a" * 1000
        result = PatternValidationService.validate_pattern(long_pattern)
        assert result.is_valid is True  # Should be valid
        
        # Test with very long error message
        long_error = re.error("x" * 1000)
        error_msg = ErrorHandlingService.generate_user_friendly_error(long_error, "test")
        assert isinstance(error_msg, str)
        assert len(error_msg) > 0
        
        # Test with zero URLs
        message = ErrorHandlingService.generate_no_matches_message(".*", 0)
        assert "0" in message
        assert "discovered URLs" in message
        
        # Test with very large URL count
        message = ErrorHandlingService.generate_no_matches_message(".*", 1000000)
        assert "1000000" in message
        assert "discovered URLs" in message

