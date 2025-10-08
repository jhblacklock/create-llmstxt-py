"""URL filtering functionality for include-patterns feature."""

import re
from typing import List, Optional, NamedTuple
from dataclasses import dataclass


class PatternValidationResult(NamedTuple):
    """Result of regex pattern validation."""
    is_valid: bool
    error_message: Optional[str] = None
    compiled_pattern: Optional[re.Pattern] = None


@dataclass
class FilteredURLSet:
    """Collection of URLs that match a regex pattern."""
    original_urls: List[str]
    filtered_urls: List[str]
    filter_count: int
    filter_ratio: float
    
    def __post_init__(self) -> None:
        """Validate the filtered URL set after initialization."""
        if not isinstance(self.original_urls, list):
            raise ValueError("original_urls must be a list")
        if not isinstance(self.filtered_urls, list):
            raise ValueError("filtered_urls must be a list")
        if not all(url in self.original_urls for url in self.filtered_urls):
            raise ValueError("filtered_urls must be a subset of original_urls")
        if self.filter_count != len(self.filtered_urls):
            raise ValueError("filter_count must match length of filtered_urls")
        if not (0.0 <= self.filter_ratio <= 1.0):
            raise ValueError("filter_ratio must be between 0.0 and 1.0")


class PatternValidationService:
    """Service for validating regex patterns."""
    
    @staticmethod
    def validate_pattern(pattern: str) -> PatternValidationResult:
        """
        Validate a regex pattern.
        
        Args:
            pattern: Regex pattern string to validate
            
        Returns:
            PatternValidationResult with validation status and details
        """
        if not pattern or not pattern.strip():
            return PatternValidationResult(
                is_valid=False,
                error_message="Pattern cannot be empty. Use a valid regex pattern."
            )
        
        try:
            compiled_pattern = re.compile(pattern)
            return PatternValidationResult(
                is_valid=True,
                compiled_pattern=compiled_pattern
            )
        except re.error as e:
            return PatternValidationResult(
                is_valid=False,
                error_message=f"Invalid regex pattern: {pattern}. Error: {str(e)}"
            )


class URLFilteringService:
    """Service for filtering URLs using regex patterns."""
    
    @staticmethod
    def filter_urls(urls: List[str], pattern: str) -> FilteredURLSet:
        """
        Filter URLs using a regex pattern.
        
        Args:
            urls: List of URLs to filter
            pattern: Regex pattern string
            
        Returns:
            FilteredURLSet containing filtered URLs and statistics
            
        Raises:
            ValueError: If pattern is empty or invalid
            re.error: If pattern is not valid regex syntax
        """
        if not urls:
            return FilteredURLSet(
                original_urls=[],
                filtered_urls=[],
                filter_count=0,
                filter_ratio=0.0
            )
        
        if not pattern or not pattern.strip():
            raise ValueError("Pattern cannot be empty. Use a valid regex pattern.")
        
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise re.error(f"Invalid regex pattern: {pattern}. Error: {str(e)}")
        
        filtered_urls = [url for url in urls if compiled_pattern.search(url)]
        
        return FilteredURLSet(
            original_urls=urls,
            filtered_urls=filtered_urls,
            filter_count=len(filtered_urls),
            filter_ratio=len(filtered_urls) / len(urls) if urls else 0.0
        )
    
    @staticmethod
    def filter_urls_multiple_patterns(urls: List[str], patterns: List[str]) -> FilteredURLSet:
        """
        Filter URLs using multiple regex patterns (OR logic - URL matches if it matches any pattern).
        
        Args:
            urls: List of URLs to filter
            patterns: List of regex pattern strings
            
        Returns:
            FilteredURLSet containing filtered URLs and statistics
            
        Raises:
            ValueError: If patterns list is empty or any pattern is empty
            re.error: If any pattern is not valid regex syntax
        """
        if not urls:
            return FilteredURLSet(
                original_urls=[],
                filtered_urls=[],
                filter_count=0,
                filter_ratio=0.0
            )
        
        if not patterns:
            raise ValueError("At least one pattern must be provided.")
        
        # Validate all patterns first
        compiled_patterns = []
        for pattern in patterns:
            if not pattern or not pattern.strip():
                raise ValueError("Pattern cannot be empty. Use a valid regex pattern.")
            try:
                compiled_patterns.append(re.compile(pattern))
            except re.error as e:
                raise re.error(f"Invalid regex pattern: {pattern}. Error: {str(e)}")
        
        # Filter URLs - URL matches if it matches ANY pattern
        filtered_urls = []
        for url in urls:
            for compiled_pattern in compiled_patterns:
                if compiled_pattern.search(url):
                    filtered_urls.append(url)
                    break  # URL already matched, no need to check other patterns
        
        return FilteredURLSet(
            original_urls=urls,
            filtered_urls=filtered_urls,
            filter_count=len(filtered_urls),
            filter_ratio=len(filtered_urls) / len(urls) if urls else 0.0
        )


class ErrorHandlingService:
    """Service for handling regex validation errors."""
    
    @staticmethod
    def generate_user_friendly_error(error: re.error, pattern: str) -> str:
        """
        Generate user-friendly error messages for regex validation failures.
        
        Args:
            error: The re.error exception
            pattern: The pattern that caused the error
            
        Returns:
            User-friendly error message with suggestions
        """
        error_msg = str(error)
        
        # Common error patterns and suggestions
        suggestions = {
            "unexpected end of regular expression": "Check for unmatched brackets, parentheses, or braces",
            "unbalanced parenthesis": "Check for unmatched opening or closing parentheses",
            "unterminated character set": "Check for unmatched square brackets",
            "bad character range": "Check character ranges in square brackets (e.g., [a-z])",
            "nothing to repeat": "Check for quantifiers (*, +, ?, {}) without preceding characters",
            "multiple repeat": "Check for multiple quantifiers on the same character"
        }
        
        suggestion = ""
        for error_type, hint in suggestions.items():
            if error_type in error_msg.lower():
                suggestion = f" Suggestion: {hint}"
                break
        
        return f"Invalid regex pattern: '{pattern}'. Error: {error_msg}.{suggestion}"
    
    @staticmethod
    def generate_no_matches_message(pattern: str, total_urls: int) -> str:
        """
        Generate message when no URLs match the pattern.
        
        Args:
            pattern: The regex pattern used
            total_urls: Total number of URLs that were checked
            
        Returns:
            Informative message about no matches
        """
        return f"No URLs matched the pattern '{pattern}' out of {total_urls} discovered URLs. No llms.txt files will be generated."

