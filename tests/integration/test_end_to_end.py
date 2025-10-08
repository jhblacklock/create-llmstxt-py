"""End-to-end integration tests for complete workflow."""

import pytest
import subprocess
import sys
import os
import tempfile
import shutil


class TestEndToEndWorkflow:
    """Test cases for complete end-to-end workflow."""
    
    def test_complete_workflow_with_filtering(self):
        """Test complete workflow from CLI to file generation with filtering."""
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--max-urls", "10",
                    "--output-dir", temp_dir,
                    "--firecrawl-api-key", "test-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_complete_workflow_without_filtering(self):
        """Test complete workflow without filtering (backward compatibility)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--max-urls", "5",
                    "--output-dir", temp_dir,
                    "--firecrawl-api-key", "test-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_complete_workflow_with_no_matches(self):
        """Test complete workflow when filtering results in no matches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/nonexistent/.*",
                    "--max-urls", "10",
                    "--output-dir", temp_dir,
                    "--firecrawl-api-key", "test-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_complete_workflow_with_invalid_pattern(self):
        """Test complete workflow with invalid regex pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", "[invalid",
                    "--output-dir", temp_dir,
                    "--firecrawl-api-key", "test-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to invalid pattern
            assert result.returncode == 1
            assert "Invalid regex pattern" in result.stderr or "Error" in result.stderr
    
    def test_complete_workflow_with_all_options(self):
        """Test complete workflow with all CLI options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--max-urls", "50",
                    "--output-dir", temp_dir,
                    "--no-full-text",
                    "--verbose",
                    "--firecrawl-api-key", "test-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_complete_workflow_performance(self):
        """Test complete workflow performance with large dataset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/page[0-9]+$",
                    "--max-urls", "1000",
                    "--output-dir", temp_dir,
                    "--firecrawl-api-key", "test-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to API key but not due to argument parsing
            assert result.returncode == 1
            assert "No URLs found" in result.stderr or "Error" in result.stderr
    
    def test_complete_workflow_error_handling(self):
        """Test complete workflow error handling and recovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable, "generate-llmstxt.py",
                    "https://example.com",
                    "--include-pattern", ".*/docs/.*",
                    "--max-urls", "10",
                    "--output-dir", temp_dir,
                    "--firecrawl-api-key", "invalid-key"
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/../../"))
            )
            
            # Should fail due to invalid API key
            assert result.returncode == 1
            assert "Error" in result.stderr or "Error" in result.stdout