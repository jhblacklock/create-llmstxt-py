"""Integration tests for file pattern CLI functionality."""

import pytest
import tempfile
import os
import subprocess
import sys
from pathlib import Path


class TestFilePatternCLI:
    """Integration tests for --file-pattern CLI option."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        self.temp_file = None
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)
    
    def create_temp_csv_file(self, urls):
        """Create a temporary CSV file with the given URLs."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            for url in urls:
                f.write(f"{url}\n")
            self.temp_file = f.name
        return self.temp_file
    
    def run_cli_command(self, args):
        """Run the CLI command and return the result."""
        cmd = [sys.executable, "generate-llmstxt.py"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        return result
    
    def test_file_pattern_with_valid_file(self):
        """Test --file-pattern with a valid file."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        assert f"Total URLs from file: {len(self.test_urls)}" in result.stdout
        assert "No pattern filtering applied (using file URLs directly)" in result.stdout
    
    def test_file_pattern_with_no_summary(self):
        """Test --file-pattern with --no-summary flag."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--max-urls", "10",
            "--no-summary",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        assert "No pattern filtering applied (using file URLs directly)" in result.stdout
    
    def test_file_pattern_with_no_full_text(self):
        """Test --file-pattern with --no-full-text flag."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--max-urls", "10",
            "--no-full-text",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        assert "No pattern filtering applied (using file URLs directly)" in result.stdout
    
    def test_file_pattern_overrides_include_pattern(self):
        """Test that --file-pattern overrides --include-pattern."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--include-pattern", ".*docs.*",
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        assert "No pattern filtering applied (using file URLs directly)" in result.stdout
        # Should not show pattern filtering messages
        assert "Testing regex filters" not in result.stdout
    
    def test_file_pattern_with_nonexistent_file(self):
        """Test --file-pattern with a non-existent file."""
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", "nonexistent_file.csv",
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode != 0
        assert "File not found" in result.stderr or "No such file" in result.stderr
    
    def test_file_pattern_priority_over_sitemap(self):
        """Test that --file-pattern takes priority over --sitemap."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--sitemap", "https://example.com/sitemap.xml",
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        # Should not show sitemap processing
        assert "Using sitemap URLs" not in result.stdout
    
    def test_file_pattern_priority_over_crawler(self):
        """Test that --file-pattern takes priority over crawler discovery."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        # Should not show crawler processing
        assert "Using simple crawler" not in result.stdout
    
    def test_file_pattern_with_empty_file(self):
        """Test --file-pattern with an empty file."""
        csv_file = self.create_temp_csv_file([])
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode != 0
        assert "No URLs found" in result.stdout
    
    def test_file_pattern_with_large_file(self):
        """Test --file-pattern with a large file."""
        large_urls = [f"https://example.com/page{i}" for i in range(100)]
        csv_file = self.create_temp_csv_file(large_urls)
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", csv_file,
            "--max-urls", "50",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        assert "Total URLs from file: 100" in result.stdout
        assert "Limited to 50 URLs" in result.stdout
    
    def test_file_pattern_with_comments_and_empty_lines(self):
        """Test --file-pattern with file containing comments and empty lines."""
        urls_with_comments = [
            "# Header comment",
            "https://example.com/page1",
            "",
            "# Section comment", 
            "https://example.com/page2",
            "  ",
            "https://example.com/page3",
            "# Footer comment"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            for line in urls_with_comments:
                f.write(f"{line}\n")
            self.temp_file = f.name
        
        result = self.run_cli_command([
            "https://example.com",
            "--file-pattern", self.temp_file,
            "--max-urls", "10",
            "--dry-run"
        ])
        
        assert result.returncode == 0
        assert "Using file URLs" in result.stdout
        assert "Total URLs from file: 3" in result.stdout  # Only the 3 actual URLs
    
    def test_file_pattern_output_files(self):
        """Test that file pattern generates correct output files."""
        csv_file = self.create_temp_csv_file(self.test_urls)
        
        # Create a temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli_command([
                "https://example.com",
                "--file-pattern", csv_file,
                "--max-urls", "10",
                "--output-dir", temp_dir,
                "--dry-run"
            ])
            
            assert result.returncode == 0
            assert "Using file URLs" in result.stdout
