#!/usr/bin/env python3
"""
Generate llms.txt and llms-full.txt files for a website using requests + BeautifulSoup.

This script:
1. Maps all URLs from a website using simple web crawling
2. Scrapes each URL to get the content and metadata
3. Extracts titles and descriptions from page metadata
4. Creates llms.txt (list of pages with descriptions) and llms-full.txt (full content)
"""

import os
import sys
import json
import time
import argparse
import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dotenv import load_dotenv
from url_filtering import PatternValidationService, URLFilteringService, ErrorHandlingService
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleLLMsTextGenerator:
    """Generate llms.txt files using requests + BeautifulSoup."""
    
    def __init__(self):
        """Initialize the generator."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; LLMsTxtGenerator/1.0)'
        })
        
        # Configure html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True
        self.h2t.body_width = 0  # Don't wrap lines
        self.h2t.unicode_snob = True
        self.h2t.escape_snob = True
    
    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Parse XML sitemap to extract URLs."""
        logger.info(f"Parsing sitemap: {sitemap_url}")
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle sitemap index (contains other sitemaps)
            if root.tag.endswith('sitemapindex'):
                logger.info("Found sitemap index, parsing sub-sitemaps...")
                urls = []
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        sitemap_url = loc.text
                        # Skip sitemap-listings files (individual car listings)
                        if 'sitemap-listings_' in sitemap_url:
                            logger.debug(f"Skipping listings sitemap: {sitemap_url}")
                            continue
                        sub_urls = self.parse_sitemap(sitemap_url)
                        urls.extend(sub_urls)
                return urls
            
            # Handle regular sitemap (contains URLs)
            elif root.tag.endswith('urlset'):
                urls = []
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        urls.append(loc.text)
                logger.info(f"Found {len(urls)} URLs in sitemap")
                return urls
            
            else:
                logger.warning(f"Unknown sitemap format: {root.tag}")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
            return []

    def parse_sitemap_sample(self, sitemap_url: str, max_sub_sitemaps: int = 3) -> List[str]:
        """Parse XML sitemap to extract a sample of URLs for dry-run estimation."""
        logger.info(f"Sampling sitemap: {sitemap_url}")
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle sitemap index (contains other sitemaps)
            if root.tag.endswith('sitemapindex'):
                logger.info("Found sitemap index, sampling sub-sitemaps...")
                urls = []
                sub_sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
                
                # Skip listings sitemaps and sample only a few others
                sampled_count = 0
                for sitemap in sub_sitemaps:
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        sitemap_url = loc.text
                        # Skip sitemap-listings files (individual car listings)
                        if 'sitemap-listings_' in sitemap_url:
                            continue
                        if sampled_count >= max_sub_sitemaps:
                            break
                        sub_urls = self.parse_sitemap(sitemap_url)
                        urls.extend(sub_urls)
                        sampled_count += 1
                        logger.info(f"Sampled {sampled_count}/{max_sub_sitemaps} sub-sitemaps")
                
                # Estimate total based on sample
                total_sub_sitemaps = 0
                for s in sub_sitemaps:
                    loc = s.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and 'sitemap-listings_' not in loc.text:
                        total_sub_sitemaps += 1
                if total_sub_sitemaps > 0:
                    avg_urls_per_sitemap = len(urls) / sampled_count if sampled_count > 0 else 0
                    estimated_total = int(avg_urls_per_sitemap * total_sub_sitemaps)
                    logger.info(f"Estimated total URLs: {estimated_total:,} (from {sampled_count} samples)")
                
                return urls
            
            # Handle regular sitemap (contains URLs)
            elif root.tag.endswith('urlset'):
                urls = []
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        urls.append(loc.text)
                logger.info(f"Found {len(urls)} URLs in sitemap")
                return urls
            
            else:
                logger.warning(f"Unknown sitemap format: {root.tag}")
                return []
                
        except Exception as e:
            logger.error(f"Error sampling sitemap {sitemap_url}: {e}")
            return []

    def estimate_sitemap_urls(self, sitemap_url: str, max_sub_sitemaps: int = 3) -> Dict:
        """Estimate total URLs from sitemap sampling and return sample for pattern testing."""
        logger.info(f"Estimating URLs from sitemap: {sitemap_url}")
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle sitemap index (contains other sitemaps)
            if root.tag.endswith('sitemapindex'):
                logger.info("Found sitemap index, estimating from sub-sitemaps...")
                sub_sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
                
                # Count non-listing sitemaps
                non_listing_sitemaps = []
                for sitemap in sub_sitemaps:
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and 'sitemap-listings_' not in loc.text:
                        non_listing_sitemaps.append(loc.text)
                
                # Sample a few sitemaps to get average URLs per sitemap
                sample_urls = []
                sampled_count = 0
                for sitemap_url in non_listing_sitemaps:
                    if sampled_count >= max_sub_sitemaps:
                        break
                    sub_urls = self.parse_sitemap(sitemap_url)
                    sample_urls.extend(sub_urls)
                    sampled_count += 1
                    logger.info(f"Sampled {sampled_count}/{max_sub_sitemaps} sub-sitemaps")
                
                # Calculate estimate
                total_sub_sitemaps = len(non_listing_sitemaps)
                avg_urls_per_sitemap = len(sample_urls) / sampled_count if sampled_count > 0 else 0
                estimated_total = int(avg_urls_per_sitemap * total_sub_sitemaps)
                
                logger.info(f"Estimated total URLs: {estimated_total:,} (from {sampled_count} samples of {total_sub_sitemaps} total sitemaps)")
                
                return {
                    'total_estimated': estimated_total,
                    'sample_urls': sample_urls,
                    'total_sitemaps': total_sub_sitemaps,
                    'sampled_sitemaps': sampled_count
                }
            
            # Handle regular sitemap (contains URLs)
            elif root.tag.endswith('urlset'):
                urls = []
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        urls.append(loc.text)
                logger.info(f"Found {len(urls)} URLs in sitemap")
                return {
                    'total_estimated': len(urls),
                    'sample_urls': urls,
                    'total_sitemaps': 1,
                    'sampled_sitemaps': 1
                }
            
            else:
                logger.warning(f"Unknown sitemap format: {root.tag}")
                return {'total_estimated': 0, 'sample_urls': [], 'total_sitemaps': 0, 'sampled_sitemaps': 0}
                
        except Exception as e:
            logger.error(f"Error estimating sitemap {sitemap_url}: {e}")
            return {'total_estimated': 0, 'sample_urls': [], 'total_sitemaps': 0, 'sampled_sitemaps': 0}

    def map_website(self, url: str, limit: int = 100) -> List[str]:
        """Map a website to get all URLs using simple crawling."""
        logger.info(f"Mapping website: {url} (limit: {limit})")
        
        try:
            # Parse the base URL
            parsed_url = urlparse(url)
            base_domain = parsed_url.netloc
            base_scheme = parsed_url.scheme
            
            discovered_urls = set()
            urls_to_visit = [url]
            visited_urls = set()
            
            while urls_to_visit and len(discovered_urls) < limit:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited_urls:
                    continue
                    
                visited_urls.add(current_url)
                
                try:
                    response = self.session.get(current_url, timeout=10)
                    response.raise_for_status()
                    
                    # Add current URL if it's from the same domain
                    if base_domain in current_url:
                        discovered_urls.add(current_url)
                    
                    # Parse HTML and extract links
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(current_url, href)
                        
                        # Only follow links from the same domain
                        if base_domain in absolute_url and absolute_url not in visited_urls:
                            if len(discovered_urls) < limit:
                                urls_to_visit.append(absolute_url)
                    
                    # Small delay to be respectful
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Error crawling {current_url}: {e}")
                    continue
            
            result = list(discovered_urls)[:limit]
            logger.info(f"Found {len(result)} URLs")
            return result
                
        except Exception as e:
            logger.error(f"Error mapping website: {e}")
            return []
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape a single URL using requests + BeautifulSoup + html2text."""
        logger.debug(f"Scraping URL: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            metadata = self._extract_metadata_from_soup(soup)
            
            # Clean up the HTML for better markdown conversion
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Convert to markdown
            html_content = str(soup)
            markdown_content = self.h2t.handle(html_content)
            
            # Clean up the markdown
            markdown_content = self._clean_markdown(markdown_content)
            
            return {
                "url": url,
                "markdown": markdown_content,
                "metadata": metadata
            }
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_metadata_from_soup(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from BeautifulSoup object."""
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_name = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif property_name == 'og:title':
                metadata['og:title'] = content
            elif property_name == 'og:description':
                metadata['og:description'] = content
            elif name == 'twitter:title':
                metadata['twitter:title'] = content
            elif name == 'twitter:description':
                metadata['twitter:description'] = content
        
        return metadata
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up markdown content."""
        # Remove excessive whitespace
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)
        
        # Remove page separators that might be left over
        markdown = re.sub(r'<\|firecrawl-page-\d+-lllmstxt\|>\n', '', markdown)
        
        # Clean up any remaining HTML tags
        markdown = re.sub(r'<[^>]+>', '', markdown)
        
        return markdown.strip()
    
    def extract_metadata(self, url: str, metadata: Dict) -> Tuple[str, str]:
        """Extract title and description from page metadata."""
        logger.debug(f"Extracting metadata for: {url}")
        
        # Extract title from metadata
        title = metadata.get("title", "")
        if not title:
            # Try alternative title fields
            title = metadata.get("og:title", "") or metadata.get("twitter:title", "")
        
        # Extract description from metadata
        description = metadata.get("description", "")
        if not description:
            # Try alternative description fields
            description = metadata.get("og:description", "") or metadata.get("twitter:description", "")
        
        # Clean up title - remove extra whitespace and limit length
        if title:
            title = re.sub(r'\s+', ' ', title.strip())
            # Limit to reasonable length for display
            if len(title) > 60:
                title = title[:57] + "..."
        else:
            title = "Page"
        
        # Clean up description - remove extra whitespace
        if description:
            description = re.sub(r'\s+', ' ', description.strip())
        else:
            description = "No description available"
        
        return title, description
    
    def process_url(self, url: str, index: int) -> Optional[Dict]:
        """Process a single URL: scrape and extract metadata."""
        scraped_data = self.scrape_url(url)
        if not scraped_data or not scraped_data.get("markdown"):
            return None
        
        title, description = self.extract_metadata(
            url, 
            scraped_data.get("metadata", {})
        )
        
        return {
            "url": url,
            "title": title,
            "description": description,
            "markdown": scraped_data["markdown"],
            "index": index
        }
    
    def remove_page_separators(self, text: str) -> str:
        """Remove page separators from text."""
        return re.sub(r'<\|firecrawl-page-\d+-lllmstxt\|>\n', '', text)
    
    def limit_pages(self, full_text: str, max_pages: int) -> str:
        """Limit the number of pages in full text."""
        pages = full_text.split('<|firecrawl-page-')
        if len(pages) <= 1:
            return full_text
        
        # First element is the header
        result = pages[0]
        
        # Add up to max_pages
        for i in range(1, min(len(pages), max_pages + 1)):
            result += '<|firecrawl-page-' + pages[i]
        
        return result
    
    def generate_llmstxt(self, url: str, max_urls: int = 100, show_full_text: bool = True, show_summary: bool = True, include_patterns: Optional[List[str]] = None, sitemap_urls: Optional[List[str]] = None) -> Dict[str, str]:
        """Generate llms.txt and llms-full.txt for a website."""
        logger.info(f"Generating llms.txt for {url}")
        
        # Step 1: Discover URLs
        if sitemap_urls:
            logger.info(f"Using sitemap URLs for discovery: {sitemap_urls}")
            urls = []
            for sitemap_url in sitemap_urls:
                sitemap_urls_found = self.parse_sitemap(sitemap_url)
                urls.extend(sitemap_urls_found)
            logger.info(f"Total URLs discovered from sitemaps: {len(urls)}")
        else:
            # Use simple crawler
            urls = self.map_website(url, max_urls)
        
        if not urls:
            raise ValueError("No URLs found for the website")
        
        # Step 2: Apply regex filtering if patterns provided
        if include_patterns:
            logger.info(f"Applying regex filters: {include_patterns}")
            
            # Validate all patterns first
            for pattern in include_patterns:
                validation_result = PatternValidationService.validate_pattern(pattern)
                if not validation_result.is_valid:
                    error_msg = ErrorHandlingService.generate_user_friendly_error(
                        re.error(validation_result.error_message or "Unknown error"), 
                        pattern
                    )
                    raise ValueError(error_msg)
            
            # Filter URLs using multiple patterns
            try:
                filtered_set = URLFilteringService.filter_urls_multiple_patterns(urls, include_patterns)
                urls = filtered_set.filtered_urls
                
                logger.info(f"Filtered {filtered_set.filter_count} URLs from {len(filtered_set.original_urls)} discovered URLs")
                
                if not urls:
                    no_matches_msg = ErrorHandlingService.generate_no_matches_message("|".join(include_patterns), len(filtered_set.original_urls))
                    logger.warning(no_matches_msg)
                    raise ValueError(no_matches_msg)
                    
            except re.error as e:
                error_msg = ErrorHandlingService.generate_user_friendly_error(e, str(e))
                raise ValueError(error_msg)
        
        # Step 3: Limit URLs to max_urls (after filtering)
        urls = urls[:max_urls]
        
        # Initialize output strings
        llmstxt = f"# {url} llms.txt\n\n" if show_summary else ""
        llms_fulltxt = f"# {url} llms-full.txt\n\n" if show_full_text else ""
        
        # Process URLs in batches of 10
        batch_size = 10
        all_results = []
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self.process_url, url, i + j): (url, i + j)
                    for j, url in enumerate(batch)
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            all_results.append(result)
                    except Exception as e:
                        url, idx = futures[future]
                        logger.error(f"Failed to process {url}: {e}")
            
            # Add a small delay between batches to avoid rate limiting
            if i + batch_size < len(urls):
                time.sleep(1)
        
        # Sort results by index to maintain order
        all_results.sort(key=lambda x: x["index"])
        
        # Build output strings
        for i, result in enumerate(all_results, 1):
            if show_summary:
                llmstxt += f"- [{result['title']}]({result['url']}): {result['description']}\n"
            if show_full_text:
                llms_fulltxt += f"<|firecrawl-page-{i}-lllmstxt|>\n## {result['title']}\n{result['markdown']}\n\n"
        
        # Optionally remove page separators for clean output
        clean_full_text = self.remove_page_separators(llms_fulltxt) if not show_full_text else llms_fulltxt
        
        return {
            "llmstxt": llmstxt,
            "llms_fulltxt": clean_full_text,
            "num_urls_processed": len(all_results),
            "num_urls_total": len(urls)
        }


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Generate llms.txt and llms-full.txt files for a website using requests + BeautifulSoup"
    )
    parser.add_argument("url", help="The website URL to process")
    parser.add_argument(
        "--include-pattern",
        type=str,
        action="append",
        help="Regex pattern to filter URLs before processing. Can be used multiple times. Only URLs matching any of these patterns will be included in the generated llms.txt files. Examples: '.*/docs/.*' for documentation pages, '.*/blog/.*' for blog posts, '.*/api/.*' for API endpoints."
    )
    parser.add_argument(
        "--sitemap",
        type=str,
        action="append",
        help="Specific sitemap URL to use for URL discovery. Can be specified multiple times. If provided, will parse XML sitemaps instead of using Firecrawl's map endpoint."
    )
    parser.add_argument(
        "--max-urls", 
        type=int, 
        default=20, 
        help="Maximum number of URLs to process (default: 20)"
    )
    parser.add_argument(
        "--output-dir", 
        default=".", 
        help="Directory to save output files (default: current directory)"
    )
    parser.add_argument(
        "--no-full-text",
        action="store_true",
        help="Don't generate llms-full.txt file"
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Don't generate llms.txt file (summary file). Use with --no-full-text to generate only llms-full.txt"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show report of URLs that would be scraped without actually scraping them"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # No API key needed with requests + BeautifulSoup
    
    # Validate that at least one file type will be generated
    if args.no_full_text and args.no_summary:
        logger.error("Cannot use both --no-full-text and --no-summary. At least one file type must be generated.")
        sys.exit(1)
    
    # Create generator
    generator = SimpleLLMsTextGenerator()
    
    try:
        if args.dry_run:
            # Dry run: just show URL discovery and filtering report
            print("🔍 DRY RUN MODE - No actual scraping will be performed")
            print("=" * 60)
            
            # Discover URLs (dry-run mode - estimate only)
            total_estimated_urls = 0
            if args.sitemap:
                print(f"📋 Using sitemap URLs: {args.sitemap}")
                print("🔍 DRY RUN: Estimating total URLs from sitemap sampling...")
                sample_urls = []
                for sitemap_url in args.sitemap:
                    # Get estimate and sample for pattern matching
                    estimate_result = generator.estimate_sitemap_urls(sitemap_url, max_sub_sitemaps=3)
                    total_estimated_urls += estimate_result['total_estimated']
                    sample_urls.extend(estimate_result['sample_urls'])
                print(f"📊 Total estimated URLs: {total_estimated_urls:,}")
                print(f"📊 Sample URLs for pattern testing: {len(sample_urls):,}")
                urls = sample_urls  # Use sample for pattern matching
            else:
                print(f"📋 Using simple crawler for: {args.url}")
                urls = generator.map_website(args.url, args.max_urls)
                print(f"📊 Total URLs discovered: {len(urls):,}")
            
            if not urls:
                print("❌ No URLs found!")
                sys.exit(1)
            
            # Apply filtering to sample URLs
            if args.include_pattern:
                print(f"🔍 Testing regex filters on sample: {args.include_pattern}")
                
                # Validate patterns
                for pattern in args.include_pattern:
                    validation_result = PatternValidationService.validate_pattern(pattern)
                    if not validation_result.is_valid:
                        error_msg = ErrorHandlingService.generate_user_friendly_error(
                            re.error(validation_result.error_message or "Unknown error"), 
                            pattern
                        )
                        print(f"❌ Invalid pattern: {error_msg}")
                        sys.exit(1)
                
                # Filter sample URLs to get match rate
                try:
                    filtered_set = URLFilteringService.filter_urls_multiple_patterns(urls, args.include_pattern)
                    sample_matches = len(filtered_set.filtered_urls)
                    sample_total = len(filtered_set.original_urls)
                    match_rate = (sample_matches / sample_total * 100) if sample_total > 0 else 0
                    
                    print(f"✅ Sample results: {sample_matches:,}/{sample_total:,} URLs matched ({match_rate:.1f}%)")
                    
                    if sample_matches == 0:
                        no_matches_msg = ErrorHandlingService.generate_no_matches_message("|".join(args.include_pattern), sample_total)
                        print(f"❌ {no_matches_msg}")
                        sys.exit(1)
                    
                    # Estimate total matches
                    if args.sitemap:
                        estimated_matches = int(total_estimated_urls * (match_rate / 100))
                        print(f"📊 Estimated total matches: {estimated_matches:,} URLs")
                        filtered_urls = filtered_set.filtered_urls[:args.max_urls]  # Limit to max_urls
                    else:
                        filtered_urls = filtered_set.filtered_urls
                        
                except re.error as e:
                    error_msg = ErrorHandlingService.generate_user_friendly_error(e, str(e))
                    print(f"❌ Pattern error: {error_msg}")
                    sys.exit(1)
            else:
                filtered_urls = urls[:args.max_urls] if args.sitemap else urls
                print("ℹ️  No pattern filtering applied")
            
            # Apply max_urls limit
            original_count = len(filtered_urls)
            filtered_urls = filtered_urls[:args.max_urls]
            if len(filtered_urls) < original_count:
                print(f"📏 Limited to {len(filtered_urls):,} URLs (from {original_count:,}) due to --max-urls {args.max_urls}")
            
            # Show sample URLs
            print(f"\n📋 URLs that would be scraped ({len(filtered_urls):,} total):")
            print("-" * 60)
            for i, url in enumerate(filtered_urls[:10], 1):
                print(f"{i:2d}. {url}")
            if len(filtered_urls) > 10:
                print(f"    ... and {len(filtered_urls) - 10:,} more URLs")
            
            print(f"\n✅ DRY RUN COMPLETE")
            print(f"📊 Would scrape {len(filtered_urls):,} URLs")
            print(f"💡 Note: Using requests + BeautifulSoup (free, no API costs)")
            
        else:
            # Normal mode: generate llms.txt files
            result = generator.generate_llmstxt(
                args.url,
                args.max_urls,
                not args.no_full_text,
                not args.no_summary,
                args.include_pattern,
                args.sitemap
            )
            
            # Create output directory if it doesn't exist
            os.makedirs(args.output_dir, exist_ok=True)
            
            # Extract domain from URL for filename
            from urllib.parse import urlparse
            domain = urlparse(args.url).netloc.replace("www.", "")
            
            # Save llms.txt if requested
            if not args.no_summary:
                llmstxt_path = os.path.join(args.output_dir, f"{domain}-llms.txt")
                with open(llmstxt_path, "w", encoding="utf-8") as f:
                    f.write(result["llmstxt"])
                logger.info(f"Saved llms.txt to {llmstxt_path}")
            
            # Save llms-full.txt if requested
            if not args.no_full_text:
                llms_fulltxt_path = os.path.join(args.output_dir, f"{domain}-llms-full.txt")
                with open(llms_fulltxt_path, "w", encoding="utf-8") as f:
                    f.write(result["llms_fulltxt"])
                logger.info(f"Saved llms-full.txt to {llms_fulltxt_path}")
            
            # Print summary
            print(f"\nSuccess! Processed {result['num_urls_processed']} out of {result['num_urls_total']} URLs")
            print(f"Files saved to {args.output_dir}/")
        
    except Exception as e:
        logger.error(f"Failed to generate llms.txt: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
