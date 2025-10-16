"""Unit tests for CSV reading functionality."""

import pytest
import tempfile
import os
from unittest.mock import patch
import sys
import os
import importlib.util

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module with hyphen in filename
spec = importlib.util.spec_from_file_location("generate_llmstxt", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "generate-llmstxt.py"))
generate_llmstxt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_llmstxt)
SimpleLLMsTextGenerator = generate_llmstxt.SimpleLLMsTextGenerator


class TestCSVReading:
    """Test cases for CSV URL reading functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SimpleLLMsTextGenerator()
    
    def test_read_valid_csv_file(self):
        """Test reading a valid CSV file with URLs."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            for url in urls:
                f.write(f"{url}\n")
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_read_empty_csv_file(self):
        """Test reading an empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert result == []
        finally:
            os.unlink(temp_file)
    
    def test_read_csv_with_comments(self):
        """Test reading CSV file with comment lines."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("# This is a comment\n")
            f.write(f"{urls[0]}\n")
            f.write("# Another comment\n")
            f.write(f"{urls[1]}\n")
            f.write("# Final comment\n")
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_read_csv_with_empty_lines(self):
        """Test reading CSV file with empty lines."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(f"{urls[0]}\n")
            f.write("\n")  # Empty line
            f.write(f"{urls[1]}\n")
            f.write("\n")  # Empty line
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_read_csv_with_whitespace(self):
        """Test reading CSV file with URLs that have leading/trailing whitespace."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(f"  {urls[0]}  \n")  # Leading and trailing spaces
            f.write(f"\t{urls[1]}\t\n")  # Leading and trailing tabs
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_read_nonexistent_file(self):
        """Test reading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.generator.read_urls_from_file("nonexistent_file.csv")
    
    def test_read_file_with_encoding_error(self):
        """Test reading a file with encoding issues."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as f:
            # Write some invalid UTF-8 bytes
            f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8
            temp_file = f.name
        
        try:
            with pytest.raises(UnicodeDecodeError):
                self.generator.read_urls_from_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_read_file_with_permission_error(self):
        """Test reading a file with permission issues."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("https://example.com/page1\n")
            temp_file = f.name
        
        try:
            # Make file read-only
            os.chmod(temp_file, 0o000)
            
            with pytest.raises(PermissionError):
                self.generator.read_urls_from_file(temp_file)
        finally:
            # Restore permissions and clean up
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)
    
    def test_read_large_csv_file(self):
        """Test reading a large CSV file with many URLs."""
        urls = [f"https://example.com/page{i}" for i in range(1000)]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            for url in urls:
                f.write(f"{url}\n")
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert len(result) == 1000
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_read_csv_with_mixed_content(self):
        """Test reading CSV file with mixed content (URLs, comments, empty lines)."""
        expected_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("# Header comment\n")
            f.write(f"{expected_urls[0]}\n")
            f.write("\n")  # Empty line
            f.write("# Section comment\n")
            f.write(f"{expected_urls[1]}\n")
            f.write("  \n")  # Whitespace-only line
            f.write(f"{expected_urls[2]}\n")
            f.write("# Footer comment\n")
            temp_file = f.name
        
        try:
            result = self.generator.read_urls_from_file(temp_file)
            assert result == expected_urls
        finally:
            os.unlink(temp_file)
