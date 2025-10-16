"""Integration tests for enhanced resume functionality in bash scripts."""

import pytest
import tempfile
import os
import sys
import subprocess
from unittest.mock import patch, mock_open

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEnhancedResumeFunctionality:
    """Integration tests for enhanced resume functionality in truecar-llms scripts."""
    
    def test_truecar_llms_summary_help(self):
        """Test truecar-llms-summary script shows help when requested."""
        result = subprocess.run(
            ["./bin/truecar-llms-summary", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "--resume" in result.stdout
        assert "--force-fresh" in result.stdout
        assert "--help" in result.stdout
    
    def test_truecar_llms_full_help(self):
        """Test truecar-llms-full script shows help when requested."""
        result = subprocess.run(
            ["./bin/truecar-llms-full", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "--resume" in result.stdout
        assert "--force-fresh" in result.stdout
        assert "--help" in result.stdout
    
    def test_auto_detect_resume_needed(self):
        """Test that scripts auto-detect when resume is needed."""
        # Create out directory
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "out")
        os.makedirs(out_dir, exist_ok=True)
        
        # Create urls directory
        urls_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "urls")
        os.makedirs(urls_dir, exist_ok=True)
        
        # Create partial llms.txt file
        llms_out_path = os.path.join(out_dir, "truecar.com-llms.txt")
        with open(llms_out_path, 'w') as f:
            f.write("# LLMs.txt for truecar.com\n")
            f.write("- [Page 1](https://www.truecar.com/page1)\n")
            f.write("- [Page 2](https://www.truecar.com/page2)\n")
        
        # Create urls file with more URLs
        urls_out_path = os.path.join(urls_dir, "llms_urls.csv")
        with open(urls_out_path, 'w') as f:
            f.write("https://www.truecar.com/page1\n")
            f.write("https://www.truecar.com/page2\n")
            f.write("https://www.truecar.com/page3\n")
            f.write("https://www.truecar.com/page4\n")
        
        try:
            # Mock the user input to say 'n' (no)
            with patch('builtins.input', return_value='n'):
                result = subprocess.run(
                    ["./bin/truecar-llms-summary"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                )
            
            assert result.returncode == 0
            assert "Resume Mode: Continuing from where you left off" in result.stdout
            assert "Current Progress:" in result.stdout
            assert "Processed: 2 URLs" in result.stdout
            assert "Total: 4 URLs" in result.stdout
            assert "Remaining: 2 URLs" in result.stdout
            assert "Starting fresh instead" in result.stdout
            
        finally:
            # Clean up
            if os.path.exists(llms_out_path):
                os.unlink(llms_out_path)
            if os.path.exists(urls_out_path):
                os.unlink(urls_out_path)
    
    def test_all_urls_processed_detection(self):
        """Test that scripts detect when all URLs have been processed."""
        # Create out directory
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "out")
        os.makedirs(out_dir, exist_ok=True)
        
        # Create urls directory
        urls_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "urls")
        os.makedirs(urls_dir, exist_ok=True)
        
        # Create complete llms.txt file
        llms_out_path = os.path.join(out_dir, "truecar.com-llms.txt")
        with open(llms_out_path, 'w') as f:
            f.write("# LLMs.txt for truecar.com\n")
            f.write("- [Page 1](https://www.truecar.com/page1)\n")
            f.write("- [Page 2](https://www.truecar.com/page2)\n")
        
        # Create urls file with same URLs
        urls_out_path = os.path.join(urls_dir, "llms_urls.csv")
        with open(urls_out_path, 'w') as f:
            f.write("https://www.truecar.com/page1\n")
            f.write("https://www.truecar.com/page2\n")
        
        try:
            result = subprocess.run(
                ["./bin/truecar-llms-summary"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "All URLs have already been processed!" in result.stdout
            assert "Final Progress: 2/2 URLs completed" in result.stdout
            assert "Use --force-fresh to start over" in result.stdout
            
        finally:
            # Clean up
            if os.path.exists(llms_out_path):
                os.unlink(llms_out_path)
            if os.path.exists(urls_out_path):
                os.unlink(urls_out_path)
    
    def test_force_fresh_option(self):
        """Test that --force-fresh option works correctly."""
        # Create out directory
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "out")
        os.makedirs(out_dir, exist_ok=True)
        
        # Create urls directory
        urls_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "urls")
        os.makedirs(urls_dir, exist_ok=True)
        
        # Create partial llms.txt file
        llms_out_path = os.path.join(out_dir, "truecar.com-llms.txt")
        with open(llms_out_path, 'w') as f:
            f.write("# LLMs.txt for truecar.com\n")
            f.write("- [Page 1](https://www.truecar.com/page1)\n")
        
        # Create urls file
        urls_out_path = os.path.join(urls_dir, "llms_urls.csv")
        with open(urls_out_path, 'w') as f:
            f.write("https://www.truecar.com/page1\n")
            f.write("https://www.truecar.com/page2\n")
        
        try:
            result = subprocess.run(
                ["./bin/truecar-llms-summary", "--force-fresh"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "Fresh Start: Processing all URLs" in result.stdout
            assert "Resume Mode" not in result.stdout
            
        finally:
            # Clean up
            if os.path.exists(llms_out_path):
                os.unlink(llms_out_path)
            if os.path.exists(urls_out_path):
                os.unlink(urls_out_path)
    
    def test_explicit_resume_option(self):
        """Test that --resume option works correctly."""
        # Create out directory
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "out")
        os.makedirs(out_dir, exist_ok=True)
        
        # Create urls directory
        urls_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "urls")
        os.makedirs(urls_dir, exist_ok=True)
        
        # Create partial llms.txt file
        llms_out_path = os.path.join(out_dir, "truecar.com-llms.txt")
        with open(llms_out_path, 'w') as f:
            f.write("# LLMs.txt for truecar.com\n")
            f.write("- [Page 1](https://www.truecar.com/page1)\n")
        
        # Create urls file
        urls_out_path = os.path.join(urls_dir, "llms_urls.csv")
        with open(urls_out_path, 'w') as f:
            f.write("https://www.truecar.com/page1\n")
            f.write("https://www.truecar.com/page2\n")
        
        try:
            result = subprocess.run(
                ["./bin/truecar-llms-summary", "--resume"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            
            assert result.returncode == 0
            assert "Resume Mode: Continuing from where you left off" in result.stdout
            assert "Current Progress:" in result.stdout
            assert "Processed: 1 URLs" in result.stdout
            assert "Total: 2 URLs" in result.stdout
            assert "Remaining: 1 URLs" in result.stdout
            
        finally:
            # Clean up
            if os.path.exists(llms_out_path):
                os.unlink(llms_out_path)
            if os.path.exists(urls_out_path):
                os.unlink(urls_out_path)
