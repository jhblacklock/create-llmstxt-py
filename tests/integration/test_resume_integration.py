"""Integration tests for resume functionality."""

import pytest
import tempfile
import os
import sys
import subprocess
import importlib.util
from unittest.mock import patch

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the resume_llmstxt module
spec = importlib.util.spec_from_file_location("resume_llmstxt", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resume_llmstxt.py"))
resume_llmstxt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resume_llmstxt)


class TestResumeIntegration:
    """Integration tests for resume functionality."""
    
    def test_resume_llmstxt_cli_help(self):
        """Test that the resume_llmstxt.py script shows help when requested."""
        result = subprocess.run(
            [sys.executable, "resume_llmstxt.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        
        assert result.returncode == 0
        assert "Resume interrupted llms.txt generation" in result.stdout
        assert "--input-file" in result.stdout
        assert "--llmstxt-file" in result.stdout
        assert "--output-file" in result.stdout
        assert "--dry-run" in result.stdout
    
    def test_resume_llmstxt_cli_missing_required_args(self):
        """Test that the resume_llmstxt.py script fails with missing required arguments."""
        result = subprocess.run(
            [sys.executable, "resume_llmstxt.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()
    
    def test_resume_llmstxt_cli_dry_run(self):
        """Test the resume_llmstxt.py script with dry-run option."""
        # Create test files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            input_file.write("https://example.com/page1\n")
            input_file.write("https://example.com/page2\n")
            input_file.write("https://example.com/page3\n")
            input_file_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as llms_file:
            llms_file.write("# LLMs.txt\n")
            llms_file.write("- [Page 1](https://example.com/page1)\n")
            llms_file_path = llms_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as output_file:
            output_file_path = output_file.name
        
        try:
            result = subprocess.run(
                [sys.executable, "resume_llmstxt.py", 
                 "--input-file", input_file_path,
                 "--llmstxt-file", llms_file_path,
                 "--output-file", output_file_path,
                 "--dry-run"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "DRY RUN" in result.stdout
            assert "Would process 2 remaining URLs" in result.stdout
            assert "https://example.com/page2" in result.stdout
            assert "https://example.com/page3" in result.stdout
            
            # Verify no output file was created in dry-run mode
            assert not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0
            
        finally:
            os.unlink(input_file_path)
            os.unlink(llms_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
    
    def test_resume_llmstxt_cli_full_execution(self):
        """Test the resume_llmstxt.py script with full execution."""
        # Create test files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            input_file.write("https://example.com/page1\n")
            input_file.write("https://example.com/page2\n")
            input_file.write("https://example.com/page3\n")
            input_file_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as llms_file:
            llms_file.write("# LLMs.txt\n")
            llms_file.write("- [Page 1](https://example.com/page1)\n")
            llms_file_path = llms_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as output_file:
            output_file_path = output_file.name
        
        try:
            result = subprocess.run(
                [sys.executable, "resume_llmstxt.py", 
                 "--input-file", input_file_path,
                 "--llmstxt-file", llms_file_path,
                 "--output-file", output_file_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "Found 1 already processed URLs" in result.stdout
            assert "Remaining to process: 2" in result.stdout
            assert "Created resume file" in result.stdout
            
            # Verify output file was created with correct content
            assert os.path.exists(output_file_path)
            with open(output_file_path, 'r') as f:
                content = f.read()
            
            assert "https://example.com/page2" in content
            assert "https://example.com/page3" in content
            assert "https://example.com/page1" not in content
            
        finally:
            os.unlink(input_file_path)
            os.unlink(llms_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
    
    def test_resume_llmstxt_cli_all_processed(self):
        """Test the resume_llmstxt.py script when all URLs have been processed."""
        # Create test files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            input_file.write("https://example.com/page1\n")
            input_file.write("https://example.com/page2\n")
            input_file_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as llms_file:
            llms_file.write("# LLMs.txt\n")
            llms_file.write("- [Page 1](https://example.com/page1)\n")
            llms_file.write("- [Page 2](https://example.com/page2)\n")
            llms_file_path = llms_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as output_file:
            output_file_path = output_file.name
        
        try:
            result = subprocess.run(
                [sys.executable, "resume_llmstxt.py", 
                 "--input-file", input_file_path,
                 "--llmstxt-file", llms_file_path,
                 "--output-file", output_file_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "All URLs have already been processed!" in result.stdout
            
        finally:
            os.unlink(input_file_path)
            os.unlink(llms_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
    
    def test_resume_llmstxt_cli_nonexistent_input_file(self):
        """Test the resume_llmstxt.py script with non-existent input file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as llms_file:
            llms_file.write("# LLMs.txt\n")
            llms_file_path = llms_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as output_file:
            output_file_path = output_file.name
        
        try:
            result = subprocess.run(
                [sys.executable, "resume_llmstxt.py", 
                 "--input-file", "nonexistent.csv",
                 "--llmstxt-file", llms_file_path,
                 "--output-file", output_file_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode != 0
            assert "Error reading" in result.stderr or "No such file" in result.stderr
            
        finally:
            os.unlink(llms_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
    
    def test_resume_llmstxt_cli_nonexistent_llmstxt_file(self):
        """Test the resume_llmstxt.py script with non-existent llms.txt file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            input_file.write("https://example.com/page1\n")
            input_file_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as output_file:
            output_file_path = output_file.name
        
        try:
            result = subprocess.run(
                [sys.executable, "resume_llmstxt.py", 
                 "--input-file", input_file_path,
                 "--llmstxt-file", "nonexistent.txt",
                 "--output-file", output_file_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "Found 0 already processed URLs" in result.stdout
            assert "Remaining to process: 1" in result.stdout
            
            # Verify output file was created with all URLs
            assert os.path.exists(output_file_path)
            with open(output_file_path, 'r') as f:
                content = f.read()
            
            assert "https://example.com/page1" in content
            
        finally:
            os.unlink(input_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
    
    def test_resume_llmstxt_cli_large_files(self):
        """Test the resume_llmstxt.py script with large files."""
        # Create large input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as input_file:
            for i in range(1000):
                input_file.write(f"https://example.com/page{i}\n")
            input_file_path = input_file.name
        
        # Create llms.txt file with some processed URLs
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as llms_file:
            llms_file.write("# LLMs.txt\n")
            for i in range(0, 1000, 2):  # Process every other URL
                llms_file.write(f"- [Page {i}](https://example.com/page{i})\n")
            llms_file_path = llms_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as output_file:
            output_file_path = output_file.name
        
        try:
            result = subprocess.run(
                [sys.executable, "resume_llmstxt.py", 
                 "--input-file", input_file_path,
                 "--llmstxt-file", llms_file_path,
                 "--output-file", output_file_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "Found 500 already processed URLs" in result.stdout
            assert "Remaining to process: 500" in result.stdout
            
            # Verify output file was created with correct content
            assert os.path.exists(output_file_path)
            with open(output_file_path, 'r') as f:
                content = f.read()
            
            # Should contain odd-numbered pages (1, 3, 5, ...)
            assert "https://example.com/page1" in content
            assert "https://example.com/page3" in content
            assert "https://example.com/page999" in content
            
            # Should not contain even-numbered pages (0, 2, 4, ...)
            assert "https://example.com/page0" not in content
            assert "https://example.com/page2" not in content
            assert "https://example.com/page998" not in content
            
        finally:
            os.unlink(input_file_path)
            os.unlink(llms_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
