"""Unit tests for resume_llmstxt.py functionality."""

import pytest
import tempfile
import os
import sys
import importlib.util
from unittest.mock import patch, mock_open

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the resume_llmstxt module
spec = importlib.util.spec_from_file_location("resume_llmstxt", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resume_llmstxt.py"))
resume_llmstxt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resume_llmstxt)


class TestResumeLLMsTxt:
    """Test cases for resume_llmstxt.py functionality."""
    
    def test_extract_processed_urls_empty_file(self):
        """Test extracting URLs from an empty llms.txt file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
        
        try:
            result = resume_llmstxt.extract_processed_urls(temp_file)
            assert result == set()
        finally:
            os.unlink(temp_file)
    
    def test_extract_processed_urls_nonexistent_file(self):
        """Test extracting URLs from a non-existent file."""
        result = resume_llmstxt.extract_processed_urls("nonexistent_file.txt")
        assert result == set()
    
    def test_extract_processed_urls_valid_content(self):
        """Test extracting URLs from a valid llms.txt file."""
        content = """# LLMs.txt for example.com

## Documentation
- [Getting Started](https://example.com/docs/getting-started)
- [API Reference](https://example.com/docs/api)
- [Tutorial](https://example.com/docs/tutorial)

## Blog Posts
- [Welcome Post](https://example.com/blog/welcome)
- [Update Notes](https://example.com/blog/update-notes)
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_file = f.name
        
        try:
            result = resume_llmstxt.extract_processed_urls(temp_file)
            expected = {
                "https://example.com/docs/getting-started",
                "https://example.com/docs/api",
                "https://example.com/docs/tutorial",
                "https://example.com/blog/welcome",
                "https://example.com/blog/update-notes"
            }
            assert result == expected
        finally:
            os.unlink(temp_file)
    
    def test_extract_processed_urls_no_urls(self):
        """Test extracting URLs from a file with no markdown links."""
        content = """# LLMs.txt for example.com

This file has no URLs in markdown format.
Just plain text content.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_file = f.name
        
        try:
            result = resume_llmstxt.extract_processed_urls(temp_file)
            assert result == set()
        finally:
            os.unlink(temp_file)
    
    def test_extract_processed_urls_mixed_content(self):
        """Test extracting URLs from a file with mixed content."""
        content = """# LLMs.txt for example.com

## Documentation
- [Getting Started](https://example.com/docs/getting-started)
- [API Reference](https://example.com/docs/api)

## External Links
- [GitHub](https://github.com/example/repo)
- [Documentation](https://docs.example.com)

## Invalid Links (should be ignored)
- [Broken Link](not-a-url)
- [Another Broken](ftp://example.com)
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_file = f.name
        
        try:
            result = resume_llmstxt.extract_processed_urls(temp_file)
            expected = {
                "https://example.com/docs/getting-started",
                "https://example.com/docs/api",
                "https://github.com/example/repo",
                "https://docs.example.com"
            }
            assert result == expected
        finally:
            os.unlink(temp_file)
    
    def test_extract_processed_urls_file_read_error(self):
        """Test handling file read errors gracefully."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Permission denied")
            
            result = resume_llmstxt.extract_processed_urls("test_file.txt")
            assert result == set()
    
    def test_filter_unprocessed_urls_no_processed(self):
        """Test filtering when no URLs have been processed."""
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
            result = resume_llmstxt.filter_unprocessed_urls(temp_file, set())
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_filter_unprocessed_urls_some_processed(self):
        """Test filtering when some URLs have been processed."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
            "https://example.com/page4"
        ]
        
        processed = {
            "https://example.com/page1",
            "https://example.com/page3"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            for url in urls:
                f.write(f"{url}\n")
            temp_file = f.name
        
        try:
            result = resume_llmstxt.filter_unprocessed_urls(temp_file, processed)
            expected = [
                "https://example.com/page2",
                "https://example.com/page4"
            ]
            assert result == expected
        finally:
            os.unlink(temp_file)
    
    def test_filter_unprocessed_urls_all_processed(self):
        """Test filtering when all URLs have been processed."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2"
        ]
        
        processed = {
            "https://example.com/page1",
            "https://example.com/page2"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            for url in urls:
                f.write(f"{url}\n")
            temp_file = f.name
        
        try:
            result = resume_llmstxt.filter_unprocessed_urls(temp_file, processed)
            assert result == []
        finally:
            os.unlink(temp_file)
    
    def test_filter_unprocessed_urls_with_comments(self):
        """Test filtering with comment lines in the input file."""
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
            result = resume_llmstxt.filter_unprocessed_urls(temp_file, set())
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_filter_unprocessed_urls_with_empty_lines(self):
        """Test filtering with empty lines in the input file."""
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
            result = resume_llmstxt.filter_unprocessed_urls(temp_file, set())
            assert result == urls
        finally:
            os.unlink(temp_file)
    
    def test_filter_unprocessed_urls_file_read_error(self):
        """Test handling file read errors in filter_unprocessed_urls."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Permission denied")
            
            with pytest.raises(SystemExit):
                resume_llmstxt.filter_unprocessed_urls("test_file.csv", set())
    
    def test_create_resume_file_success(self):
        """Test creating a resume file successfully."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            resume_llmstxt.create_resume_file(urls, temp_file)
            
            # Verify the file was created with correct content
            with open(temp_file, 'r') as f:
                content = f.read()
            
            expected_content = "https://example.com/page1\nhttps://example.com/page2\n"
            assert content == expected_content
        finally:
            os.unlink(temp_file)
    
    def test_create_resume_file_empty_urls(self):
        """Test creating a resume file with empty URL list."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            resume_llmstxt.create_resume_file([], temp_file)
            
            # Verify the file was created but is empty
            with open(temp_file, 'r') as f:
                content = f.read()
            
            assert content == ""
        finally:
            os.unlink(temp_file)
    
    def test_create_resume_file_write_error(self):
        """Test handling file write errors in create_resume_file."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Permission denied")
            
            with pytest.raises(SystemExit):
                resume_llmstxt.create_resume_file(["https://example.com"], "test_file.csv")
    
    @patch('sys.argv', ['resume_llmstxt.py', '--input-file', 'input.csv', '--llmstxt-file', 'llms.txt', '--output-file', 'output.csv'])
    @patch('resume_llmstxt.extract_processed_urls')
    @patch('resume_llmstxt.filter_unprocessed_urls')
    @patch('resume_llmstxt.create_resume_file')
    def test_main_success(self, mock_create, mock_filter, mock_extract):
        """Test main function with successful execution."""
        mock_extract.return_value = {"https://example.com/page1"}
        mock_filter.return_value = ["https://example.com/page2", "https://example.com/page3"]
        
        resume_llmstxt.main()
        
        mock_extract.assert_called_once_with("llms.txt")
        mock_filter.assert_called_once_with("input.csv", {"https://example.com/page1"})
        mock_create.assert_called_once_with(["https://example.com/page2", "https://example.com/page3"], "output.csv")
    
    @patch('sys.argv', ['resume_llmstxt.py', '--input-file', 'input.csv', '--llmstxt-file', 'llms.txt', '--output-file', 'output.csv'])
    @patch('resume_llmstxt.extract_processed_urls')
    @patch('resume_llmstxt.filter_unprocessed_urls')
    def test_main_all_processed(self, mock_filter, mock_extract):
        """Test main function when all URLs have been processed."""
        mock_extract.return_value = {"https://example.com/page1", "https://example.com/page2"}
        mock_filter.return_value = []
        
        resume_llmstxt.main()
        
        mock_extract.assert_called_once_with("llms.txt")
        mock_filter.assert_called_once_with("input.csv", {"https://example.com/page1", "https://example.com/page2"})
    
    @patch('sys.argv', ['resume_llmstxt.py', '--input-file', 'input.csv', '--llmstxt-file', 'llms.txt', '--output-file', 'output.csv', '--dry-run'])
    @patch('resume_llmstxt.extract_processed_urls')
    @patch('resume_llmstxt.filter_unprocessed_urls')
    def test_main_dry_run(self, mock_filter, mock_extract):
        """Test main function with dry-run option."""
        mock_extract.return_value = {"https://example.com/page1"}
        mock_filter.return_value = ["https://example.com/page2", "https://example.com/page3"]
        
        resume_llmstxt.main()
        
        mock_extract.assert_called_once_with("llms.txt")
        mock_filter.assert_called_once_with("input.csv", {"https://example.com/page1"})
        # create_resume_file should not be called in dry-run mode
