"""Contract tests for file pattern functionality."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
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


class TestFilePatternContract:
    """Contract tests ensuring file pattern behavior is consistent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SimpleLLMsTextGenerator()
    
    def test_file_urls_bypass_filtering(self):
        """Test that file URLs bypass include_pattern filtering."""
        file_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        include_patterns = [".*docs.*"]  # Pattern that wouldn't match any URLs
        
        # Mock the scraping methods to avoid actual HTTP requests
        with patch.object(self.generator, 'scrape_url') as mock_scrape, \
             patch.object(self.generator, 'process_url') as mock_process:
            
            # Mock successful scraping
            mock_scrape.return_value = {
                "url": "https://example.com/page1",
                "markdown": "# Test Page\nContent here",
                "metadata": {"title": "Test Page", "description": "Test description"}
            }
            
            mock_process.return_value = {
                "url": "https://example.com/page1",
                "title": "Test Page",
                "description": "Test description",
                "markdown": "# Test Page\nContent here",
                "index": 0
            }
            
            result = self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=10,
                show_full_text=True,
                show_summary=True,
                include_patterns=include_patterns,
                file_urls=file_urls
            )
            
            # Should process all file URLs despite pattern not matching
            assert result["num_urls_processed"] == len(file_urls)
            assert result["num_urls_total"] == len(file_urls)
    
    def test_file_pattern_priority_over_sitemap(self):
        """Test that file pattern takes priority over sitemap URLs."""
        file_urls = ["https://example.com/file-page"]
        sitemap_urls = ["https://example.com/sitemap.xml"]
        
        with patch.object(self.generator, 'parse_sitemap') as mock_parse_sitemap, \
             patch.object(self.generator, 'scrape_url') as mock_scrape, \
             patch.object(self.generator, 'process_url') as mock_process:
            
            # Mock sitemap parsing (should not be called)
            mock_parse_sitemap.return_value = ["https://example.com/sitemap-page"]
            
            # Mock successful scraping
            mock_scrape.return_value = {
                "url": "https://example.com/file-page",
                "markdown": "# File Page\nContent here",
                "metadata": {"title": "File Page", "description": "File description"}
            }
            
            mock_process.return_value = {
                "url": "https://example.com/file-page",
                "title": "File Page",
                "description": "File description",
                "markdown": "# File Page\nContent here",
                "index": 0
            }
            
            result = self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=10,
                show_full_text=True,
                show_summary=True,
                sitemap_urls=sitemap_urls,
                file_urls=file_urls
            )
            
            # Should use file URLs, not sitemap URLs
            assert result["num_urls_processed"] == 1
            assert result["num_urls_total"] == 1
            # Sitemap parsing should not be called
            mock_parse_sitemap.assert_not_called()
    
    def test_file_pattern_priority_over_crawler(self):
        """Test that file pattern takes priority over crawler discovery."""
        file_urls = ["https://example.com/file-page"]
        
        with patch.object(self.generator, 'map_website') as mock_crawler, \
             patch.object(self.generator, 'scrape_url') as mock_scrape, \
             patch.object(self.generator, 'process_url') as mock_process:
            
            # Mock crawler (should not be called)
            mock_crawler.return_value = ["https://example.com/crawled-page"]
            
            # Mock successful scraping
            mock_scrape.return_value = {
                "url": "https://example.com/file-page",
                "markdown": "# File Page\nContent here",
                "metadata": {"title": "File Page", "description": "File description"}
            }
            
            mock_process.return_value = {
                "url": "https://example.com/file-page",
                "title": "File Page",
                "description": "File description",
                "markdown": "# File Page\nContent here",
                "index": 0
            }
            
            result = self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=10,
                show_full_text=True,
                show_summary=True,
                file_urls=file_urls
            )
            
            # Should use file URLs, not crawler
            assert result["num_urls_processed"] == 1
            assert result["num_urls_total"] == 1
            # Crawler should not be called
            mock_crawler.assert_not_called()
    
    def test_output_format_matches_expected_structure(self):
        """Test that output format matches expected structure when using file URLs."""
        file_urls = [
            "https://example.com/page1",
            "https://example.com/page2"
        ]
        
        with patch.object(self.generator, 'scrape_url') as mock_scrape, \
             patch.object(self.generator, 'process_url') as mock_process:
            
            # Mock successful scraping
            def mock_scrape_side_effect(url):
                return {
                    "url": url,
                    "markdown": f"# {url}\nContent for {url}",
                    "metadata": {"title": f"Page {url.split('/')[-1]}", "description": f"Description for {url}"}
                }
            
            def mock_process_side_effect(url, index):
                return {
                    "url": url,
                    "title": f"Page {url.split('/')[-1]}",
                    "description": f"Description for {url}",
                    "markdown": f"# {url}\nContent for {url}",
                    "index": index
                }
            
            mock_scrape.side_effect = mock_scrape_side_effect
            mock_process.side_effect = mock_process_side_effect
            
            result = self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=10,
                show_full_text=True,
                show_summary=True,
                file_urls=file_urls
            )
            
            # Check output structure
            assert "llmstxt" in result
            assert "llms_fulltxt" in result
            assert "num_urls_processed" in result
            assert "num_urls_total" in result
            
            # Check content format
            llmstxt = result["llmstxt"]
            llms_fulltxt = result["llms_fulltxt"]
            
            # Summary should contain links
            assert "- [Page page1](https://example.com/page1): Description for https://example.com/page1" in llmstxt
            assert "- [Page page2](https://example.com/page2): Description for https://example.com/page2" in llmstxt
            
            # Full text should contain page separators
            assert "<|firecrawl-page-1-lllmstxt|>" in llms_fulltxt
            assert "<|firecrawl-page-2-lllmstxt|>" in llms_fulltxt
            
            # Check counts
            assert result["num_urls_processed"] == 2
            assert result["num_urls_total"] == 2
    
    def test_file_urls_with_max_urls_limit(self):
        """Test that max_urls limit is applied to file URLs."""
        file_urls = [f"https://example.com/page{i}" for i in range(10)]
        max_urls = 5
        
        with patch.object(self.generator, 'scrape_url') as mock_scrape, \
             patch.object(self.generator, 'process_url') as mock_process:
            
            # Mock successful scraping
            def mock_scrape_side_effect(url):
                return {
                    "url": url,
                    "markdown": f"# {url}\nContent for {url}",
                    "metadata": {"title": f"Page {url.split('/')[-1]}", "description": f"Description for {url}"}
                }
            
            def mock_process_side_effect(url, index):
                return {
                    "url": url,
                    "title": f"Page {url.split('/')[-1]}",
                    "description": f"Description for {url}",
                    "markdown": f"# {url}\nContent for {url}",
                    "index": index
                }
            
            mock_scrape.side_effect = mock_scrape_side_effect
            mock_process.side_effect = mock_process_side_effect
            
            result = self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=max_urls,
                show_full_text=True,
                show_summary=True,
                file_urls=file_urls
            )
            
            # Should process only max_urls URLs
            assert result["num_urls_processed"] == max_urls
            assert result["num_urls_total"] == max_urls
    
    def test_file_urls_with_empty_list(self):
        """Test behavior with empty file URLs list."""
        file_urls = []
        
        with pytest.raises(ValueError, match="No URLs found for the website"):
            self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=10,
                show_full_text=True,
                show_summary=True,
                file_urls=file_urls
            )
    
    def test_file_urls_ignores_include_patterns_warning(self):
        """Test that warning is logged when include_patterns are provided with file_urls."""
        file_urls = ["https://example.com/page1"]
        include_patterns = [".*docs.*"]
        
        with patch.object(self.generator, 'scrape_url') as mock_scrape, \
             patch.object(self.generator, 'process_url') as mock_process, \
             patch('generate_llmstxt.logger') as mock_logger:
            
            # Mock successful scraping
            mock_scrape.return_value = {
                "url": "https://example.com/page1",
                "markdown": "# Test Page\nContent here",
                "metadata": {"title": "Test Page", "description": "Test description"}
            }
            
            mock_process.return_value = {
                "url": "https://example.com/page1",
                "title": "Test Page",
                "description": "Test description",
                "markdown": "# Test Page\nContent here",
                "index": 0
            }
            
            self.generator.generate_llmstxt(
                url="https://example.com",
                max_urls=10,
                show_full_text=True,
                show_summary=True,
                include_patterns=include_patterns,
                file_urls=file_urls
            )
            
            # Should log warning about ignoring include_patterns
            mock_logger.warning.assert_called_with(
                "--include-pattern is ignored when using --file-pattern. URLs from file are used directly."
            )
