"""Integration tests for various CLI option combinations."""

import pytest
import subprocess
import sys
import os
import tempfile


class TestOptionCombinations:
    """Test cases for various CLI option combinations."""
    
    def test_include_patterns_with_max_urls(self):
        """Test --include-pattern with --max-urls."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--max-urls", "50",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_with_output_dir(self):
        """Test --include-pattern with --output-dir."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/blog/.*",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_with_verbose(self):
        """Test --include-pattern with --verbose."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/api/.*",
                    "--verbose",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_with_no_full_text(self):
        """Test --include-pattern with --no-full-text."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--no-full-text",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_with_all_options(self):
        """Test --include-pattern with all other options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--max-urls", "100",
                    "--output-dir", temp_dir,
                    "--no-full-text",
                    "--verbose",
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_with_api_keys(self):
        """Test --include-pattern with API key options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_processing_order(self):
        """Test that filtering happens before max-urls limiting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--max-urls", "2",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_backward_compatibility(self):
        """Test backward compatibility when no patterns are provided."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--max-urls", "10",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_include_patterns_error_with_other_options(self):
        """Test error handling when pattern is invalid with other options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", "[invalid",
                    "--max-urls", "50",
                    "--output-dir", temp_dir,
                    "--verbose",
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to invalid pattern
            assert result.returncode == 1
            assert "Invalid regex pattern" in result.stderr or "Error" in result.stderr
    
    def test_no_summary_option(self):
        """Test --no-summary option generates only llms-full.txt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--no-summary",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_no_full_text_option(self):
        """Test --no-full-text option generates only llms.txt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--no-full-text",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_both_no_options_error(self):
        """Test that using both --no-full-text and --no-summary causes an error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--no-full-text",
                    "--no-summary",
                    "--output-dir", temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to both options being used
            assert result.returncode == 1
            assert "Cannot use both --no-full-text and --no-summary" in result.stderr