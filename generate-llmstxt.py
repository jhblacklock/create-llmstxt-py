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
from typing import Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dotenv import load_dotenv
from url_filtering import PatternValidationService, URLFilteringService, ErrorHandlingService
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
import yaml

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
    
    def scrape_url(self, url: str, max_retries: int = 2) -> Optional[Dict]:
        """Scrape a single URL using requests + BeautifulSoup + html2text."""
        logger.debug(f"Scraping URL: {url}")
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Preprocess HTML content to fix common issues
                html_content = response.content.decode('utf-8', errors='ignore')
                
                # Fix common HTML issues that cause parsing errors
                html_content = self._preprocess_html(html_content)
                
                # Parse HTML with BeautifulSoup - use more lenient parser for malformed HTML
                soup = self._parse_html_safely(html_content, url)
                logger.debug(f"Successfully parsed HTML for {url} using {soup.__class__.__name__}")
                
                # Extract metadata
                metadata = self._extract_metadata_from_soup(soup)
                
                # Clean up the HTML for better markdown conversion
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Convert to markdown with better error handling
                html_content = str(soup)
                try:
                    markdown_content = self.h2t.handle(html_content)
                    logger.debug(f"Successfully converted {url} to markdown using html2text")
                except Exception as h2t_error:
                    # Check if it's a specific html2text error
                    if "we should not get here" in str(h2t_error):
                        logger.warning(f"html2text internal error for {url}: {h2t_error}. Using fallback method...")
                    elif "unexpected call to parse" in str(h2t_error):
                        logger.warning(f"html2text parsing error for {url}: {h2t_error}. Using fallback method...")
                    else:
                        logger.warning(f"html2text conversion failed for {url}: {h2t_error}. Using fallback method...")
                    
                    # Fallback: try to extract text directly from BeautifulSoup
                    try:
                        # Remove script and style elements first
                        for script in soup(["script", "style"]):
                            script.decompose()
                        # Get text content
                        markdown_content = soup.get_text(separator='\n', strip=True)
                        # Basic formatting
                        markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
                        logger.debug(f"Successfully extracted text from {url} using BeautifulSoup fallback")
                    except Exception as fallback_error:
                        logger.warning(f"Fallback text extraction also failed for {url}: {fallback_error}. Using raw HTML...")
                        # Last resort: use raw HTML content
                        markdown_content = html_content
                
                # Clean up the markdown
                markdown_content = self._clean_markdown(markdown_content)
                
                return {
                    "url": url,
                    "markdown": markdown_content,
                    "metadata": metadata
                }
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    logger.warning(f"Network error scraping {url} (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying...")
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    logger.error(f"Network error scraping {url} after {max_retries + 1} attempts: {e}")
                    return None
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Unexpected error scraping {url} (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying...")
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    logger.error(f"Unexpected error scraping {url} after {max_retries + 1} attempts: {e}")
                    return None
        
        return None
    
    def _preprocess_html(self, html_content: str) -> str:
        """Preprocess HTML content to fix common parsing issues."""
        try:
            # Fix common HTML issues that cause parsing errors
            # 1. Remove null bytes and control characters
            html_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', html_content)
            
            # 2. Fix malformed attributes (add quotes around unquoted values)
            html_content = re.sub(r'(\w+)=([^"\s>]+)(?=\s|>)', r'\1="\2"', html_content)
            
            # 3. Fix unclosed tags (basic attempt)
            html_content = re.sub(r'<([^>]+)(?<!/)>', r'<\1>', html_content)
            
            # 4. Fix common malformed HTML patterns
            # Remove any remaining malformed tags
            html_content = re.sub(r'<[^>]*$', '', html_content)
            
            # 5. Ensure proper encoding
            html_content = html_content.encode('utf-8', errors='ignore').decode('utf-8')
            
            # 6. Add basic HTML structure if missing
            if not html_content.strip().startswith('<'):
                html_content = f'<html><body>{html_content}</body></html>'
            
            return html_content
        except Exception as e:
            logger.warning(f"HTML preprocessing failed: {e}")
            return html_content
    
    def _parse_html_safely(self, html_content: str, url: str) -> BeautifulSoup:
        """Safely parse HTML content with multiple fallback strategies."""
        # Try different parsers in order of leniency
        parsers = ['html5lib', 'lxml', 'html.parser']
        
        for parser in parsers:
            try:
                soup = BeautifulSoup(html_content, parser)
                # Test if parsing was successful by checking if we can access the content
                if soup and soup.get_text():
                    return soup
            except Exception as parse_error:
                logger.warning(f"HTML parsing error for {url} with {parser}: {parse_error}. Trying next parser...")
                continue
        
        # If all parsers fail, try a more aggressive approach
        try:
            # Remove problematic content and try again
            cleaned_html = self._clean_html_aggressively(html_content)
            soup = BeautifulSoup(cleaned_html, 'html5lib')
            if soup and soup.get_text():
                return soup
        except Exception as e:
            logger.warning(f"Aggressive HTML cleaning also failed for {url}: {e}")
        
        # Last resort: create a minimal soup object with just the text content
        logger.error(f"All HTML parsing strategies failed for {url}. Using raw text extraction...")
        soup = BeautifulSoup('<html><body></body></html>', 'html.parser')
        # Extract text content manually
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        soup.body.string = text_content
        return soup
    
    def _clean_html_aggressively(self, html_content: str) -> str:
        """Aggressively clean HTML content to make it parseable."""
        try:
            # Remove script and style tags completely
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove comments
            html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
            
            # Remove any remaining problematic tags
            html_content = re.sub(r'<[^>]*$', '', html_content)
            
            # Ensure we have a basic HTML structure
            if not html_content.strip().startswith('<'):
                html_content = f'<html><body>{html_content}</body></html>'
            
            return html_content
        except Exception as e:
            logger.warning(f"Aggressive HTML cleaning failed: {e}")
            return html_content
    
    def _write_incremental_files(self, llmstxt_path: str, llms_fulltxt_path: str, all_results: List[Dict], show_summary: bool, show_full_text: bool, base_url: str, file_sections: Optional[Dict] = None):
        """Write files incrementally as batches complete."""
        try:
            # Build current content
            if file_sections and show_summary:
                # Generate with section headers like Stripe
                llmstxt = "# TrueCar\n\n"
            else:
                llmstxt = f"# {base_url} llms.txt\n\n" if show_summary else ""
            llms_fulltxt = f"# {base_url} llms-full.txt\n\n" if show_full_text else ""
            
            # Sort results by index to maintain order
            sorted_results = sorted(all_results, key=lambda x: x["index"])
            
            # Build content
            if file_sections and show_summary:
                # Generate grouped output with section headers
                for section in file_sections.get('sections', []):
                    section_header = section.get('header', '')
                    section_description = section.get('description', '')
                    section_urls = section.get('urls', [])
                    
                    if section_urls:
                        llmstxt += f"## {section_header}\n"
                        if section_description:
                            llmstxt += f"{section_description}\n\n"
                        
                        # Add URLs from this section that were successfully processed
                        for result in sorted_results:
                            if result['url'] in section_urls:
                                llmstxt += f"- [{result['title']}]({result['url']}): {result['description']}\n"
                        llmstxt += "\n"
            else:
                # Generate flat output (current behavior)
                for i, result in enumerate(sorted_results, 1):
                    if show_summary:
                        llmstxt += f"- [{result['title']}]({result['url']}): {result['description']}\n"
            
            # Always generate full text in flat format
            for i, result in enumerate(sorted_results, 1):
                if show_full_text:
                    llms_fulltxt += f"<|firecrawl-page-{i}-lllmstxt|>\n## {result['title']}\n{result['markdown']}\n\n"
            
            # Write files
            if show_summary:
                with open(llmstxt_path, "w", encoding="utf-8") as f:
                    f.write(llmstxt)
                logger.info(f"📝 Updated {llmstxt_path} with {len(sorted_results)} entries")
            
            if show_full_text:
                with open(llms_fulltxt_path, "w", encoding="utf-8") as f:
                    f.write(llms_fulltxt)
                logger.info(f"📝 Updated {llms_fulltxt_path} with {len(sorted_results)} entries")
                
        except Exception as e:
            logger.warning(f"Error writing incremental files: {e}")
    
    def _extract_metadata_from_soup(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from BeautifulSoup object."""
        metadata = {}
        
        try:
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                try:
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
                except Exception as meta_error:
                    # Skip malformed meta tags
                    logger.debug(f"Skipping malformed meta tag: {meta_error}")
                    continue
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up markdown content."""
        try:
            # Remove excessive whitespace
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)
            
            # Remove page separators that might be left over
            markdown = re.sub(r'<\|firecrawl-page-\d+-lllmstxt\|>\n', '', markdown)
            
            # Clean up any remaining HTML tags
            markdown = re.sub(r'<[^>]+>', '', markdown)
            
            return markdown.strip()
        except Exception as e:
            logger.warning(f"Error cleaning markdown: {e}")
            return markdown.strip() if markdown else ""
    
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
            # Keep full title - no truncation for llms.txt format
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
        try:
            # Validate URL before processing
            if not url or not url.strip():
                logger.warning(f"Empty or invalid URL at index {index}")
                return None
            
            # Basic URL validation
            parsed_url = urlparse(url.strip())
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.warning(f"Invalid URL format: {url}")
                return None
            
            scraped_data = self.scrape_url(url.strip())
            if not scraped_data or not scraped_data.get("markdown"):
                logger.warning(f"No content extracted from {url}")
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
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None
    
    def read_urls_from_file(self, file_path: str) -> List[str]:
        """Read URLs from a CSV file (one URL per line, no headers)."""
        logger.info(f"Reading URLs from file: {file_path}")
        urls = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    url = line.strip()
                    if url and not url.startswith('#'):  # Skip empty lines and comments
                        # Basic URL validation
                        try:
                            parsed_url = urlparse(url)
                            if parsed_url.scheme and parsed_url.netloc:
                                urls.append(url)
                            else:
                                logger.warning(f"Invalid URL format on line {line_num}: {url}")
                        except Exception as url_error:
                            logger.warning(f"Error parsing URL on line {line_num}: {url} - {url_error}")
                            continue
            logger.info(f"Read {len(urls)} valid URLs from {file_path}")
            return urls
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    def read_urls_from_yaml(self, file_path: str) -> Union[List[str], Dict]:
        """Read URLs from a YAML file. Returns either flat list or structured data with sections."""
        logger.info(f"Reading URLs from YAML file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check if it's a flat YAML (for llms-full.txt)
            if 'urls' in data and isinstance(data['urls'], list):
                urls = []
                for url in data['urls']:
                    if url and not url.startswith('#'):  # Skip empty lines and comments
                        # Basic URL validation
                        try:
                            parsed_url = urlparse(url)
                            if parsed_url.scheme and parsed_url.netloc:
                                urls.append(url)
                            else:
                                logger.warning(f"Invalid URL format: {url}")
                        except Exception as url_error:
                            logger.warning(f"Error parsing URL: {url} - {url_error}")
                            continue
                logger.info(f"Read {len(urls)} valid URLs from flat YAML {file_path}")
                return urls
            
            # Check if it's a structured YAML (for llms.txt with sections)
            elif 'sections' in data and isinstance(data['sections'], list):
                sections = []
                total_urls = 0
                for section in data['sections']:
                    if 'header' in section and 'urls' in section and isinstance(section['urls'], list):
                        section_urls = []
                        for url in section['urls']:
                            if url and not url.startswith('#'):  # Skip empty lines and comments
                                # Basic URL validation
                                try:
                                    parsed_url = urlparse(url)
                                    if parsed_url.scheme and parsed_url.netloc:
                                        section_urls.append(url)
                                    else:
                                        logger.warning(f"Invalid URL format in section '{section['header']}': {url}")
                                except Exception as url_error:
                                    logger.warning(f"Error parsing URL in section '{section['header']}': {url} - {url_error}")
                                    continue
                        
                        section_data = {
                            'header': section['header'],
                            'description': section.get('description', ''),
                            'urls': section_urls
                        }
                        sections.append(section_data)
                        total_urls += len(section_urls)
                        logger.info(f"Section '{section['header']}': {len(section_urls)} URLs")
                
                logger.info(f"Read {total_urls} total URLs from {len(sections)} sections in structured YAML {file_path}")
                return {'sections': sections}
            
            else:
                logger.error(f"Invalid YAML format in {file_path}. Expected 'urls' or 'sections' key.")
                raise ValueError(f"Invalid YAML format in {file_path}")
                
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading YAML file {file_path}: {e}")
            raise

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
    
    def generate_llmstxt(self, url: str, max_urls: int = 100, show_full_text: bool = True, show_summary: bool = True, include_patterns: Optional[List[str]] = None, sitemap_urls: Optional[List[str]] = None, file_urls: Optional[List[str]] = None, file_sections: Optional[Dict] = None, output_dir: str = ".") -> Dict[str, str]:
        """Generate llms.txt and llms-full.txt for a website."""
        logger.info(f"Generating llms.txt for {url}")
        
        # Step 1: Discover URLs (file_sections takes priority, then file_urls)
        if file_sections:
            logger.info(f"Using file sections for discovery: {len(file_sections.get('sections', []))} sections")
            # Extract all URLs from sections for processing
            urls = []
            for section in file_sections.get('sections', []):
                urls.extend(section.get('urls', []))
            logger.info(f"Total URLs from sections: {len(urls)}")
            # When using file sections, ignore include_patterns
            if include_patterns:
                logger.warning("--include-pattern is ignored when using --file-pattern with sections. URLs from file are used directly.")
        elif file_urls:
            logger.info(f"Using file URLs for discovery: {len(file_urls)} URLs")
            urls = file_urls
            # When using file URLs, ignore include_patterns
            if include_patterns:
                logger.warning("--include-pattern is ignored when using --file-pattern. URLs from file are used directly.")
        elif sitemap_urls:
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
        
        # Step 2: Apply regex filtering if patterns provided (skip if using file_urls or file_sections)
        if include_patterns and not file_urls and not file_sections:
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
        if file_sections and show_summary:
            # Generate with section headers like Stripe
            llmstxt = "# TrueCar\n\n"
        else:
            llmstxt = f"# {url} llms.txt\n\n" if show_summary else ""
        llms_fulltxt = f"# {url} llms-full.txt\n\n" if show_full_text else ""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract domain from URL for filename
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")
        
        # Initialize file paths
        llmstxt_path = os.path.join(output_dir, f"{domain}-llms.txt")
        llms_fulltxt_path = os.path.join(output_dir, f"{domain}-llms-full.txt")
        
        # Process URLs in batches of 10
        batch_size = 10
        all_results = []
        successful_urls = []
        failed_urls = []
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:  # Reduced workers to be more respectful
                futures = {
                    executor.submit(self.process_url, url, i + j): (url, i + j)
                    for j, url in enumerate(batch)
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=60)  # Add timeout for individual URL processing
                        if result:
                            all_results.append(result)
                            successful_urls.append(result['url'])
                            logger.info(f"✅ Successfully processed: {result['url']}")
                        else:
                            url, idx = futures[future]
                            failed_urls.append(url)
                            logger.warning(f"❌ Failed to process: {url}")
                    except Exception as e:
                        url, idx = futures[future]
                        failed_urls.append(url)
                        logger.error(f"❌ Error processing {url}: {e}")
                    except TimeoutError:
                        url, idx = futures[future]
                        failed_urls.append(url)
                        logger.error(f"⏰ Timeout processing {url}")
            
            # Add a longer delay between batches to be more respectful
            if i + batch_size < len(urls):
                time.sleep(2)  # Increased delay
            
            # Show progress summary
            total_processed = len(successful_urls) + len(failed_urls)
            success_rate = (len(successful_urls) / total_processed * 100) if total_processed > 0 else 0
            logger.info(f"📊 Progress: {total_processed}/{len(urls)} URLs processed, {success_rate:.1f}% success rate")
            
            # Write files incrementally after each batch
            self._write_incremental_files(llmstxt_path, llms_fulltxt_path, all_results, show_summary, show_full_text, url, file_sections)
        
        # Sort results by index to maintain order
        all_results.sort(key=lambda x: x["index"])
        
        # Build output strings (only if not using sections, since sections are handled incrementally)
        if not file_sections:
            # Generate flat output (current behavior)
            for i, result in enumerate(all_results, 1):
                if show_summary:
                    llmstxt += f"- [{result['title']}]({result['url']}): {result['description']}\n"
        else:
            # When using sections, read the content from the file that was written incrementally
            if show_summary and os.path.exists(llmstxt_path):
                with open(llmstxt_path, 'r', encoding='utf-8') as f:
                    llmstxt = f.read()
        
        # Always generate full text in flat format
        for i, result in enumerate(all_results, 1):
            if show_full_text:
                llms_fulltxt += f"<|firecrawl-page-{i}-lllmstxt|>\n## {result['title']}\n{result['markdown']}\n\n"
        
        # Optionally remove page separators for clean output
        clean_full_text = self.remove_page_separators(llms_fulltxt) if not show_full_text else llms_fulltxt
        
        # Final summary
        total_processed = len(successful_urls) + len(failed_urls)
        success_rate = (len(successful_urls) / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 Final Results:")
        logger.info(f"   ✅ Successfully processed: {len(successful_urls)} URLs")
        logger.info(f"   ❌ Failed to process: {len(failed_urls)} URLs")
        logger.info(f"   📊 Success rate: {success_rate:.1f}%")
        
        if failed_urls:
            logger.info(f"   🔍 Failed URLs (first 10): {failed_urls[:10]}")
        
        return {
            "llmstxt": llmstxt,
            "llms_fulltxt": clean_full_text,
            "num_urls_processed": len(all_results),
            "num_urls_total": len(urls),
            "successful_urls": successful_urls,
            "failed_urls": failed_urls,
            "success_rate": success_rate
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
        "--file-pattern",
        type=str,
        help="File path containing URLs to process (CSV or YAML format). If provided, will use these URLs directly instead of discovering them. Takes priority over --sitemap and crawler discovery."
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
    
    # Read file URLs if file pattern is provided
    file_urls = None
    file_sections = None
    if args.file_pattern:
        # Check if it's a YAML file
        if args.file_pattern.endswith('.yaml') or args.file_pattern.endswith('.yml'):
            yaml_data = generator.read_urls_from_yaml(args.file_pattern)
            if isinstance(yaml_data, list):
                # Flat YAML (for llms-full.txt)
                file_urls = yaml_data
            elif isinstance(yaml_data, dict) and 'sections' in yaml_data:
                # Structured YAML (for llms.txt with sections)
                file_sections = yaml_data
        else:
            # CSV file
            file_urls = generator.read_urls_from_file(args.file_pattern)
    
    try:
        if args.dry_run:
            # Dry run: just show URL discovery and filtering report
            print("🔍 DRY RUN MODE - No actual scraping will be performed")
            print("=" * 60)
            
            # Discover URLs (dry-run mode - estimate only)
            total_estimated_urls = 0
            if file_sections:
                print(f"📋 Using file sections: {args.file_pattern}")
                print(f"📊 Total sections: {len(file_sections.get('sections', []))}")
                # Extract all URLs from sections for counting
                urls = []
                for section in file_sections.get('sections', []):
                    urls.extend(section.get('urls', []))
                print(f"📊 Total URLs from sections: {len(urls):,}")
            elif file_urls:
                print(f"📋 Using file URLs: {args.file_pattern}")
                print(f"📊 Total URLs from file: {len(file_urls):,}")
                urls = file_urls
            elif args.sitemap:
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
            
            # Apply filtering to sample URLs (skip if using file_urls or file_sections)
            if args.include_pattern and not file_urls and not file_sections:
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
                if file_urls:
                    print("ℹ️  No pattern filtering applied (using file URLs directly)")
                else:
                    print("ℹ️  No pattern filtering applied")
                filtered_urls = urls[:args.max_urls] if args.sitemap else urls
            
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
                args.sitemap,
                file_urls,
                file_sections,
                args.output_dir
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
