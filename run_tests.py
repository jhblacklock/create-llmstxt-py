#!/usr/bin/env python3
"""Run the TrueCar scripts and verify they work."""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """Run a script and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Make sure the script is executable
        script_path = Path(script_name)
        if script_path.exists():
            os.chmod(script_path, 0o755)
        
        # Run the script
        result = subprocess.run(
            [script_name],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Script timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def main():
    """Run both TrueCar scripts."""
    print("🚀 Testing TrueCar CSV Processing Scripts")
    print("=" * 60)
    
    # Test scripts
    scripts = [
        ("bin/truecar-llms-summary", "TrueCar LLMs.txt Generator (Summary)"),
        ("bin/truecar-llms-full", "TrueCar LLMs-full.txt Generator (Full)")
    ]
    
    results = []
    
    for script, description in scripts:
        success = run_script(script, description)
        results.append((script, success))
        
        if success:
            print(f"✅ {description} completed successfully!")
        else:
            print(f"❌ {description} failed!")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for script, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {script}")
    
    print(f"\nOverall: {passed}/{total} scripts passed")
    
    if passed == total:
        print("🎉 All scripts completed successfully!")
        return 0
    else:
        print("💥 Some scripts failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())