#!/usr/bin/env python3
"""Minimal test to verify CSV processing works."""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test if we can import the module."""
    try:
        from generate_llmstxt import SimpleLLMsTextGenerator
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_csv_reading():
    """Test CSV reading."""
    try:
        from generate_llmstxt import SimpleLLMsTextGenerator
        generator = SimpleLLMsTextGenerator()
        
        # Test reading a small sample
        urls = generator.read_urls_from_file('urls/llms_urls.csv')
        print(f"✅ Read {len(urls)} URLs from CSV")
        
        if len(urls) > 0:
            print(f"   First URL: {urls[0]}")
            return True
        else:
            print("❌ No URLs read from CSV")
            return False
            
    except Exception as e:
        print(f"❌ CSV reading failed: {e}")
        return False

def test_dry_run():
    """Test dry run functionality."""
    try:
        from generate_llmstxt import SimpleLLMsTextGenerator
        generator = SimpleLLMsTextGenerator()
        
        # Read a small sample of URLs
        urls = generator.read_urls_from_file('urls/llms_urls.csv')
        sample_urls = urls[:3]  # Just first 3 URLs
        
        # Test dry run
        result = generator.generate_llmstxt(
            url="https://www.truecar.com",
            max_urls=3,
            show_full_text=False,
            show_summary=True,
            file_urls=sample_urls
        )
        
        print(f"✅ Dry run successful - processed {result['num_urls_processed']} URLs")
        return True
        
    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        return False

def main():
    """Run minimal tests."""
    print("🧪 Minimal CSV Processing Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_import),
        ("CSV Reading Test", test_csv_reading),
        ("Dry Run Test", test_dry_run)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            passed += 1
    
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! CSV processing is working.")
        return 0
    else:
        print("💥 Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
