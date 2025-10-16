#!/usr/bin/env python3
"""
Resume LLMs.txt Generation Script

This script helps you resume interrupted llms.txt generation by:
1. Tracking which URLs have already been processed
2. Continuing from where you left off
3. Appending new results to existing files
"""

import os
import sys
import argparse
import re
import yaml
from urllib.parse import urlparse

def read_yaml_file(file_path):
    """Read YAML file and return structured data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        print(f"❌ Error reading YAML file {file_path}: {e}")
        return None

def extract_processed_urls(llmstxt_file):
    """Extract URLs that have already been processed from an existing llms.txt file."""
    processed_urls = set()
    
    if not os.path.exists(llmstxt_file):
        return processed_urls
    
    try:
        with open(llmstxt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract URLs from markdown links: [title](url)
        url_pattern = r'\[.*?\]\((https?://[^)]+)\)'
        matches = re.findall(url_pattern, content)
        
        for url in matches:
            processed_urls.add(url)
            
        print(f"📊 Found {len(processed_urls)} already processed URLs in {llmstxt_file}")
        
    except Exception as e:
        print(f"⚠️  Error reading {llmstxt_file}: {e}")
    
    return processed_urls

def filter_unprocessed_urls(input_file, processed_urls, file_format='csv'):
    """Filter out URLs that have already been processed."""
    unprocessed_urls = []
    unprocessed_sections = None
    
    try:
        if file_format == 'yaml':
            # Handle YAML format
            data = read_yaml_file(input_file)
            if not data:
                sys.exit(1)
            
            # Check if it's flat YAML or structured YAML
            if 'urls' in data and isinstance(data['urls'], list):
                # Flat YAML
                for url in data['urls']:
                    if url and not url.startswith('#'):
                        if url not in processed_urls:
                            unprocessed_urls.append(url)
                        else:
                            print(f"⏭️  Skipping already processed: {url}")
                
                print(f"📋 Total URLs in flat YAML: {len(data['urls'])}")
                print(f"✅ Already processed: {len(processed_urls)}")
                print(f"🔄 Remaining to process: {len(unprocessed_urls)}")
                
            elif 'sections' in data and isinstance(data['sections'], list):
                # Structured YAML - preserve section structure
                sections = []
                total_urls = 0
                unprocessed_count = 0
                
                for section in data['sections']:
                    section_urls = []
                    for url in section.get('urls', []):
                        if url and not url.startswith('#'):
                            total_urls += 1
                            if url not in processed_urls:
                                section_urls.append(url)
                                unprocessed_count += 1
                            else:
                                print(f"⏭️  Skipping already processed: {url}")
                    
                    if section_urls:  # Only include sections with remaining URLs
                        section_data = {
                            'header': section.get('header', ''),
                            'description': section.get('description', ''),
                            'urls': section_urls
                        }
                        sections.append(section_data)
                
                unprocessed_sections = {'sections': sections}
                print(f"📋 Total URLs in structured YAML: {total_urls}")
                print(f"✅ Already processed: {len(processed_urls)}")
                print(f"🔄 Remaining to process: {unprocessed_count}")
                print(f"📊 Sections with remaining URLs: {len(sections)}")
                
            else:
                print(f"❌ Invalid YAML format in {input_file}")
                sys.exit(1)
                
        else:
            # Handle CSV format (original behavior)
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    url = line.strip()
                    if url and not url.startswith('#'):
                        if url not in processed_urls:
                            unprocessed_urls.append(url)
                        else:
                            print(f"⏭️  Skipping already processed: {url}")
            
            print(f"📋 Total URLs in CSV: {line_num}")
            print(f"✅ Already processed: {len(processed_urls)}")
            print(f"🔄 Remaining to process: {len(unprocessed_urls)}")
        
    except Exception as e:
        print(f"❌ Error reading {input_file}: {e}")
        sys.exit(1)
    
    return unprocessed_urls, unprocessed_sections

def create_resume_file(unprocessed_urls, output_file, unprocessed_sections=None, file_format='csv'):
    """Create a new file with only unprocessed URLs."""
    try:
        if file_format == 'yaml' and unprocessed_sections:
            # Create YAML resume file with sections
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(unprocessed_sections, f, default_flow_style=False, sort_keys=False, width=120)
            
            total_urls = sum(len(section.get('urls', [])) for section in unprocessed_sections.get('sections', []))
            print(f"📝 Created YAML resume file: {output_file}")
            print(f"🔢 Contains {total_urls} URLs across {len(unprocessed_sections.get('sections', []))} sections")
            
        else:
            # Create CSV resume file (original behavior)
            with open(output_file, 'w', encoding='utf-8') as f:
                for url in unprocessed_urls:
                    f.write(f"{url}\n")
            
            print(f"📝 Created resume file: {output_file}")
            print(f"🔢 Contains {len(unprocessed_urls)} URLs to process")
        
    except Exception as e:
        print(f"❌ Error creating resume file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Resume interrupted llms.txt generation')
    parser.add_argument('--input-file', required=True, help='Original URLs file (CSV or YAML format)')
    parser.add_argument('--llmstxt-file', required=True, help='Existing llms.txt file to check for processed URLs')
    parser.add_argument('--output-file', required=True, help='Output file for remaining URLs')
    parser.add_argument('--format', choices=['csv', 'yaml'], help='File format (auto-detected if not specified)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without creating files')
    
    args = parser.parse_args()
    
    # Auto-detect format if not specified
    if not args.format:
        if args.input_file.endswith('.yaml') or args.input_file.endswith('.yml'):
            args.format = 'yaml'
        else:
            args.format = 'csv'
    
    print("🔄 Resume LLMs.txt Generation")
    print("=" * 50)
    print(f"📁 Input format: {args.format.upper()}")
    
    # Extract already processed URLs
    processed_urls = extract_processed_urls(args.llmstxt_file)
    
    # Filter unprocessed URLs
    unprocessed_urls, unprocessed_sections = filter_unprocessed_urls(args.input_file, processed_urls, args.format)
    
    if not unprocessed_urls and not unprocessed_sections:
        print("🎉 All URLs have already been processed!")
        return
    
    if args.dry_run:
        if unprocessed_sections:
            total_urls = sum(len(section.get('urls', [])) for section in unprocessed_sections.get('sections', []))
            print(f"\n🔍 DRY RUN: Would process {total_urls} remaining URLs across {len(unprocessed_sections.get('sections', []))} sections")
            print("Sections with remaining URLs:")
            for section in unprocessed_sections.get('sections', []):
                print(f"  - {section.get('header', 'Unknown')}: {len(section.get('urls', []))} URLs")
        else:
            print(f"\n🔍 DRY RUN: Would process {len(unprocessed_urls)} remaining URLs")
            print("First 10 URLs to process:")
            for i, url in enumerate(unprocessed_urls[:10], 1):
                print(f"  {i}. {url}")
            if len(unprocessed_urls) > 10:
                print(f"  ... and {len(unprocessed_urls) - 10} more")
    else:
        # Create resume file
        create_resume_file(unprocessed_urls, args.output_file, unprocessed_sections, args.format)
        
        print(f"\n🚀 To resume processing, run:")
        if args.format == 'yaml' and unprocessed_sections:
            print(f"python generate-llmstxt.py https://www.truecar.com \\")
            print(f"  --file-pattern {args.output_file} \\")
            print(f"  --output-dir ./out")
        else:
            total_urls = len(unprocessed_urls)
            print(f"python generate-llmstxt.py https://www.truecar.com \\")
            print(f"  --file-pattern {args.output_file} \\")
            print(f"  --output-dir ./out \\")
            print(f"  --max-urls {total_urls}")

if __name__ == "__main__":
    main()
