"""Unit tests for pattern validation service."""

import pytest
import re
from url_filtering import PatternValidationService, PatternValidationResult


class TestPatternValidationService:
    """Test cases for PatternValidationService."""
    
    def test_validate_pattern_valid_pattern(self):
        """Test validation of valid regex patterns."""
        valid_patterns = [
            r".*/docs/.*",
            r".*/blog/.*",
            r".*/api/.*",
            r"https://example\.com/.*",
            r"^https://.*\.com$",
            r"[a-z]+/[0-9]+",
            r".*\.(html|pdf)$"
        ]
        
        for pattern in valid_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is True
            assert result.error_message is None
            assert result.compiled_pattern is not None
            assert isinstance(result.compiled_pattern, re.Pattern)
    
    def test_validate_pattern_empty_pattern(self):
        """Test validation of empty patterns."""
        empty_patterns = ["", "   ", "\t", "\n"]
        
        for pattern in empty_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is False
            assert "Pattern cannot be empty" in result.error_message
            assert result.compiled_pattern is None
    
    def test_validate_pattern_invalid_syntax(self):
        """Test validation of invalid regex syntax."""
        invalid_patterns = [
            "[invalid",  # Unmatched bracket
            "(unclosed",  # Unmatched parenthesis
            "*invalid",  # Nothing to repeat
            "[a-z",  # Unterminated character set
            "a{2,1}",  # Bad character range
        ]
        
        for pattern in invalid_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is False
            assert "Invalid regex pattern" in result.error_message
            assert pattern in result.error_message
            assert result.compiled_pattern is None
    
    def test_validate_pattern_none_input(self):
        """Test validation with None input."""
        result = PatternValidationService.validate_pattern(None)
        assert result.is_valid is False
        assert "Pattern cannot be empty" in result.error_message
    
    def test_validate_pattern_compilation_error(self):
        """Test validation with compilation errors."""
        # Pattern that compiles but might cause issues
        complex_pattern = r"(?P<name>.*?)(?P=name)"  # This should be valid
        result = PatternValidationService.validate_pattern(complex_pattern)
        assert result.is_valid is True
        
        # Pattern that definitely won't compile
        invalid_pattern = r"[a-z{2,3"  # Invalid quantifier in character class - missing closing bracket
        result = PatternValidationService.validate_pattern(invalid_pattern)
        assert result.is_valid is False
        assert "Invalid regex pattern" in result.error_message
    
    def test_validate_pattern_unicode(self):
        """Test validation with unicode patterns."""
        unicode_patterns = [
            r"[\u4e00-\u9fff]+",  # Chinese characters
            r"[\u3040-\u309f]+",  # Hiragana
            r"[\u30a0-\u30ff]+",  # Katakana
        ]
        
        for pattern in unicode_patterns:
            result = PatternValidationService.validate_pattern(pattern)
            assert result.is_valid is True
            assert result.compiled_pattern is not None
    
    def test_validate_pattern_special_characters(self):
        """Test validation with special regex characters."""
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

