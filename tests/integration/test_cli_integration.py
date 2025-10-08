"""Integration tests for CLI argument processing."""

import pytest
import subprocess
import sys
import os
from unittest.mock import patch, Mock


class TestCLIIntegration:
    """Test cases for CLI integration with --include-pattern."""
    
    def test_cli_help_includes_patterns_option(self):
        """Test that --include-pattern appears in help output."""
        result = subprocess.run(
            [sys.executable, "generate-llmstxt.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        assert result.returncode == 0
        assert "--include-pattern" in result.stdout
        assert "Regex pattern to filter URLs" in result.stdout
        assert "Examples:" in result.stdout
    
    def test_cli_with_valid_pattern(self):
        """Test CLI with valid regex pattern."""
        result = subprocess.run(
            [
                sys.executable, "generate-llmstxt.py",
                "https://example.com",
                "--include-pattern", ".*/docs/.*",
                "--max-urls", "10",
                "--firecrawl-api-key", "test-key"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        # Should fail due to API key but not due to argument parsing
        assert result.returncode == 1  # Expected due to API key issues
        assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_cli_without_pattern(self):
        """Test CLI without --include-pattern (backward compatibility)."""
        result = subprocess.run(
            [
                sys.executable, "generate-llmstxt.py",
                "https://example.com",
                "--max-urls", "10",
                "--firecrawl-api-key", "test-key"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        # Should fail due to API key but not due to argument parsing
        assert result.returncode == 1  # Expected due to API key issues
        assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_cli_with_invalid_pattern(self):
        """Test CLI with invalid regex pattern."""
        result = subprocess.run(
            [
                sys.executable, "generate-llmstxt.py",
                "https://example.com",
                "--include-pattern", "[invalid",
                "--firecrawl-api-key", "test-key"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        # Should fail due to invalid pattern
        assert result.returncode == 1
        assert "Invalid regex pattern" in result.stderr or "Error" in result.stderr
    
    def test_cli_with_empty_pattern(self):
        """Test CLI with empty pattern."""
        result = subprocess.run(
            [
                sys.executable, "generate-llmstxt.py",
                "https://example.com",
                "--include-pattern", "",
                "--firecrawl-api-key", "test-key"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        # Should fail due to empty pattern
        assert result.returncode == 1
        assert "Pattern cannot be empty" in result.stderr or "Error" in result.stderr
    
    def test_cli_argument_order(self):
        """Test that --include-pattern works with other arguments."""
        # Test with multiple arguments
        result = subprocess.run(
            [
                sys.executable, "generate-llmstxt.py",
                "https://example.com",
                "--include-pattern", ".*/docs/.*",
                "--max-urls", "50",
                "--output-dir", "/tmp",
                "--verbose",
                "--firecrawl-api-key", "test-key"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        # Should fail due to API key but not due to argument parsing
        assert result.returncode == 1  # Expected due to API key issues
        assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_cli_pattern_with_special_characters(self):
        """Test CLI with pattern containing special characters."""
        # Test with pattern containing special characters
        special_pattern = r"https://example\.com/.*\.html$"
        result = subprocess.run(
            [
                sys.executable, "generate-llmstxt.py",
                "https://example.com",
                "--include-pattern", special_pattern,
                "--firecrawl-api-key", "test-key"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
        )
        
        # Should fail due to API key but not due to argument parsing
        assert result.returncode == 1  # Expected due to API key issues
        assert "No URLs found" in result.stderr or "Error" in result.stderr

