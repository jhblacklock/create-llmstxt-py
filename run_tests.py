#!/usr/bin/env python3
"""
Quick test runner script for the Firecrawl LLMs.txt Generator project.

This script provides convenient commands to run different types of tests.
"""

import subprocess
import sys
import argparse


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run tests for Firecrawl LLMs.txt Generator")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "contract", "quick"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run with verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=.", "--cov-report=html"])
    
    success = True
    
    if args.test_type == "all":
        success = run_command(base_cmd + ["tests/"], "All Tests")
        
    elif args.test_type == "unit":
        success = run_command(base_cmd + ["tests/unit/"], "Unit Tests")
        
    elif args.test_type == "integration":
        success = run_command(base_cmd + ["tests/integration/"], "Integration Tests")
        
    elif args.test_type == "contract":
        success = run_command(base_cmd + ["tests/contract/"], "Contract Tests")
        
    elif args.test_type == "quick":
        # Run a subset of critical tests quickly
        success = run_command(base_cmd + [
            "tests/unit/test_url_filtering.py",
            "tests/unit/test_pattern_validation.py",
            "tests/integration/test_cli_integration.py"
        ], "Quick Tests (Critical Path)")
    
    if success:
        print(f"\n✅ {args.test_type.title()} tests passed!")
        return 0
    else:
        print(f"\n❌ {args.test_type.title()} tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
