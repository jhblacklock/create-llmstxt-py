# Firecrawl LLMs.txt Generator

A Python script that generates `llms.txt` and `llms-full.txt` files for any website using Firecrawl API and page metadata extraction.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "FIRECRAWL_API_KEY=your-key" > .env

# Generate llms.txt files
python generate-llmstxt.py https://example.com

# Run tests
python run_tests.py all
```

## What is llms.txt?

`llms.txt` is a standardized format for making website content more accessible to Large Language Models (LLMs). It provides:

- **llms.txt**: A concise index of all pages with titles and descriptions
- **llms-full.txt**: Complete content of all pages for comprehensive access

## Features

- 🗺️ **Website Mapping**: Automatically discovers all URLs on a website using Firecrawl's map endpoint
- 📄 **Content Scraping**: Extracts markdown content from each page
- 📝 **Metadata Extraction**: Pulls titles and descriptions from page metadata (title, og:title, twitter:title, description, og:description, twitter:description)
- ⚡ **Parallel Processing**: Processes multiple URLs concurrently for faster generation
- 🎯 **Configurable Limits**: Set maximum number of URLs to process
- 📁 **Flexible Output**: Choose to generate both files or just llms.txt
- 🔍 **URL Filtering**: Filter URLs using multiple regex patterns to create focused llms.txt files
- 🚀 **No External AI Dependencies**: Uses page metadata instead of requiring OpenAI API

## Prerequisites

- Python 3.7+
- Firecrawl API key ([Get one here](https://firecrawl.dev))

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up API key (choose one method):

   **Option A: Using .env file (recommended)**

   ```bash
   echo "FIRECRAWL_API_KEY=your-firecrawl-api-key" > .env
   ```

   **Option B: Using environment variables**

   ```bash
   export FIRECRAWL_API_KEY="your-firecrawl-api-key"
   ```

   **Option C: Using command line arguments**
   (See usage examples below)

## Usage

### Basic Usage

Generate llms.txt and llms-full.txt for a website:

```bash
python generate-llmstxt.py https://example.com
```

### With Options

```bash
# Limit to 50 URLs
python generate-llmstxt.py https://example.com --max-urls 50

# Filter URLs using regex patterns (can be used multiple times)
python generate-llmstxt.py https://example.com --include-pattern ".*/docs/.*"

# Use multiple patterns for complex filtering
python generate-llmstxt.py https://example.com \
  --include-pattern ".*/blog/.*" \
  --include-pattern ".*/docs/.*" \
  --max-urls 30 \
  --output-dir ./content

# Save to specific directory
python generate-llmstxt.py https://example.com --output-dir ./output

# Only generate llms.txt (skip full text)
python generate-llmstxt.py https://example.com --no-full-text

# Enable verbose logging
python generate-llmstxt.py https://example.com --verbose

# Specify API key via command line
python generate-llmstxt.py https://example.com \
  --firecrawl-api-key "fc-..."
```

### Command Line Options

- `url` (required): The website URL to process
- `--include-pattern`: Regex pattern to filter URLs before processing. Can be used multiple times. Only URLs matching any of these patterns will be included in the generated llms.txt files. Examples: `".*/docs/.*"` for documentation pages, `".*/blog/.*"` for blog posts, `".*/api/.*"` for API endpoints.
- `--max-urls`: Maximum number of URLs to process (default: 20)
- `--output-dir`: Directory to save output files (default: current directory)
- `--firecrawl-api-key`: Firecrawl API key (defaults to .env file or FIRECRAWL_API_KEY env var)
- `--no-full-text`: Only generate llms.txt, skip llms-full.txt
- `--verbose`: Enable verbose logging for debugging

## Output Format

### llms.txt

```
# https://example.com llms.txt

- [Page Title](https://example.com/page1): Brief description of the page content here
- [Another Page](https://example.com/page2): Another concise description of page content
```

### llms-full.txt

```
# https://example.com llms-full.txt

<|firecrawl-page-1-lllmstxt|>
## Page Title
Full markdown content of the page...

<|firecrawl-page-2-lllmstxt|>
## Another Page
Full markdown content of another page...
```

## How It Works

1. **Website Mapping**: Uses Firecrawl's `/map` endpoint to discover all URLs on the website
2. **URL Filtering**: If `--include-pattern` is provided, filters URLs using the regex patterns (OR logic - URL matches if it matches any pattern)
3. **Batch Processing**: Processes URLs in batches of 10 for efficiency
4. **Content Extraction**: Scrapes each URL to extract markdown content
5. **Metadata Extraction**: For each page, extracts title and description from:
   - HTML `<title>` tag
   - Open Graph `og:title` and `og:description` meta tags
   - Twitter `twitter:title` and `twitter:description` meta tags
6. **File Generation**: Creates formatted llms.txt and llms-full.txt files

## Testing

This project includes comprehensive test coverage with unit tests, integration tests, and contract tests.

### Running Tests

**Run all tests:**
```bash
python -m pytest tests/ -v
```

**Run specific test categories:**
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# Contract tests only
python -m pytest tests/contract/ -v
```

**Run tests with coverage:**
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

**Run a specific test file:**
```bash
python -m pytest tests/unit/test_url_filtering.py -v
```

**Run a specific test:**
```bash
python -m pytest tests/unit/test_url_filtering.py::TestURLFilteringService::test_filter_urls_basic_patterns -v
```

**Using the test runner script (recommended):**
```bash
# Run all tests
python run_tests.py all

# Run quick tests (critical path only)
python run_tests.py quick

# Run unit tests with coverage
python run_tests.py unit --coverage

# Run integration tests with verbose output
python run_tests.py integration --verbose
```

### Test Structure

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - `test_url_filtering.py`: URL filtering service tests
  - `test_pattern_validation.py`: Regex pattern validation tests
  - `test_edge_cases.py`: Edge cases and error handling tests

- **Integration Tests** (`tests/integration/`): Test component interactions
  - `test_cli_integration.py`: CLI argument parsing and execution tests
  - `test_end_to_end.py`: Complete workflow tests
  - `test_option_combinations.py`: Various CLI option combination tests

- **Contract Tests** (`tests/contract/`): Test API contracts and data structures
  - `test_error_contracts.py`: Error message format and consistency tests
  - `test_processing_order.py`: Processing order and data flow tests

### Test Configuration

The project uses `pytest` with the following configuration in `pytest.ini`:
- Test discovery in `tests/` directory
- Verbose output by default
- Coverage reporting support
- Custom markers for different test types

### Continuous Integration

All tests must pass before merging code. The test suite includes:
- 79 total tests
- Unit tests for core functionality
- Integration tests for CLI behavior
- Contract tests for API consistency
- Error handling and edge case coverage

## Error Handling

- Failed URL scrapes are logged and skipped
- If no URLs are found, the script exits with an error
- Invalid regex patterns show clear error messages with suggestions
- If no URLs match the filter pattern, the script exits with an informative message
- API errors are logged with details for debugging
- Rate limiting is handled with delays between batches

## Performance Considerations

- Processing time depends on the number of URLs and response times
- Default batch size is 10 URLs processed concurrently
- Small delays between batches prevent rate limiting
- For large websites, consider using `--max-urls` to limit processing

## Examples

### Small Website

```bash
python generate-llmstxt.py https://small-blog.com --max-urls 20
```

### Documentation Only

```bash
python generate-llmstxt.py https://docs.example.com --include-pattern ".*/docs/.*" --max-urls 100
```

### Blog Posts Only

```bash
python generate-llmstxt.py https://example.com --include-pattern ".*/blog/.*" --verbose
```

### API Endpoints Only

```bash
python generate-llmstxt.py https://api.example.com --include-pattern ".*/api/.*" --no-full-text
```

### Multiple Content Types

```bash
python generate-llmstxt.py https://example.com \
  --include-pattern ".*/docs/.*" \
  --include-pattern ".*/blog/.*" \
  --include-pattern ".*/guides/.*" \
  --max-urls 200
```

### Large Website with Limited Scope

```bash
python generate-llmstxt.py https://docs.example.com --max-urls 100 --verbose
```

### Quick Index Only

```bash
python generate-llmstxt.py https://example.com --no-full-text --max-urls 50
```

### Complex Pattern Matching

```bash
# Match only HTML files in specific directories
python generate-llmstxt.py https://example.com --include-pattern ".*/(docs|blog)/.*\.html$"

# Match URLs with specific query parameters
python generate-llmstxt.py https://example.com --include-pattern ".*\?category=.*"

# Multiple complex patterns for a car website
python generate-llmstxt.py https://www.truecar.com \
  --include-pattern '^/$' \
  --include-pattern '^/compare/' \
  --include-pattern '^/rankings/' \
  --include-pattern '^/[a-z0-9-]+/[a-z0-9-]+/[0-9]{4}/$' \
  --include-pattern '^/[a-z0-9-]+/$' \
  --include-pattern '^/calculators?/' \
  --include-pattern '^/deals/' \
  --include-pattern '^/used-cars-for-sale/listings/[a-z0-9-]+/[a-z0-9-]+/' \
  --include-pattern '^/used-cars-for-sale/listings/bodytype/' \
  --include-pattern '^/used-cars-for-sale/listings/location/' \
  --include-pattern '^/used-cars-for-sale/listings/' \
  --include-pattern '^/sell-your-car/?$' \
  --include-pattern '^/lease/?$' \
  --include-pattern '^/trade-in/?$' \
  --include-pattern '^/ev-tax-credit/?$' \
  --include-pattern '^/tariffs/?$'
```

## Configuration Priority

The script checks for API keys in this order:

1. Command line arguments (`--firecrawl-api-key`)
2. `.env` file in the current directory
3. Environment variables (`FIRECRAWL_API_KEY`)

## Troubleshooting

### No API Keys Found

Ensure you've either:

- Created a `.env` file with your API key: `echo "FIRECRAWL_API_KEY=your-key" > .env`
- Set environment variable: `export FIRECRAWL_API_KEY="your-key"`
- Or pass it via command line argument: `--firecrawl-api-key "your-key"`

### Rate Limiting

If you encounter rate limits:

- Reduce concurrent workers in the code
- Add longer delays between batches
- Process fewer URLs at once

### Memory Issues

For very large websites:

- Use `--max-urls` to limit the number of pages
- Process in smaller batches
- Use `--no-full-text` to skip full content generation

## License

MIT License - see LICENSE file for details
