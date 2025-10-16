#!/usr/bin/env python3
"""Test script to verify the TrueCar scripts work correctly."""

import subprocess
import sys
import os
from pathlib import Path

def test_csv_reading():
    """Test CSV reading functionality."""
    print("Testing CSV reading functionality...")
    
    try:
        from generate_llmstxt import SimpleLLMsTextGenerator
        generator = SimpleLLMsTextGenerator()
        
        # Test reading llms_urls.csv
        urls = generator.read_urls_from_file('urls/llms_urls.csv')
        print(f"✅ Read {len(urls)} URLs from llms_urls.csv")
        
        # Test reading llms_full_urls.csv
        full_urls = generator.read_urls_from_file('urls/llms_full_urls.csv')
        print(f"✅ Read {len(full_urls)} URLs from llms_full_urls.csv")
        
        return True
    except Exception as e:
        print(f"❌ CSV reading test failed: {e}")
        return False

def test_file_pattern_dry_run():
    """Test file pattern with dry run."""
    print("\nTesting file pattern with dry run...")
    
    try:
        cmd = [
            sys.executable, "generate-llmstxt.py",
            "https://www.truecar.com",
            "--file-pattern", "urls/llms_urls.csv",
            "--max-urls", "5",
            "--dry-run"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Dry run test passed")
            print("Output preview:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print(f"❌ Dry run test failed with return code {result.returncode}")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Dry run test failed with exception: {e}")
        return False

def test_script_execution():
    """Test script execution."""
    print("\nTesting script execution...")
    
    try:
        # Test truecar-llms-summary script
        print("Testing truecar-llms-summary script...")
        cmd = [sys.executable, "generate-llmstxt.py", "https://www.truecar.com", 
               "--file-pattern", "urls/llms_urls.csv", "--max-urls", "3", 
               "--output-dir", "./out", "--no-full-text"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ truecar-llms-summary script test passed")
            # Check if output file was created
            if os.path.exists("out/truecar.com-llms.txt"):
                print("✅ Output file created successfully")
                return True
            else:
                print("❌ Output file not created")
                return False
        else:
            print(f"❌ truecar-llms-summary script failed with return code {result.returncode}")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Script execution test failed with exception: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing TrueCar CSV processing functionality...")
    print("=" * 60)
    
    tests = [
        test_csv_reading,
        test_file_pattern_dry_run,
        test_script_execution
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The CSV processing functionality is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
