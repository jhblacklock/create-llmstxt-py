# Quickstart: Include Patterns Filter

**Feature**: Include Patterns Filter  
**Date**: 2025-01-27  
**Purpose**: Quick guide to using regex pattern filtering with the llms.txt generator

## Overview

The `--include-patterns` option allows you to filter URLs before processing, creating more focused llms.txt files that contain only content matching your specified regex pattern.

## Basic Usage

### Filter Documentation Pages
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/docs/.*"
```

This will only include URLs containing `/docs/` in their path.

### Filter Blog Posts
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/blog/.*"
```

This will only include URLs containing `/blog/` in their path.

### Filter API Endpoints
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/api/.*"
```

This will only include URLs containing `/api/` in their path.

## Advanced Patterns

### Multiple Path Segments
```bash
# Filter for both docs and guides
python generate-llmstxt.py https://example.com --include-patterns ".*/(docs|guides)/.*"
```

### File Extensions
```bash
# Filter for only HTML pages
python generate-llmstxt.py https://example.com --include-patterns ".*\.html$"
```

### Specific Subdomains
```bash
# Filter for specific subdomain
python generate-llmstxt.py https://example.com --include-patterns "https://docs\.example\.com/.*"
```

## Combining with Existing Options

### Limit Filtered Results
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/docs/.*" --max-urls 50
```

This filters for docs pages and limits to 50 URLs maximum.

### Custom Output Directory
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/blog/.*" --output-dir ./blog-content
```

This filters for blog posts and saves to a custom directory.

### Verbose Logging
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/api/.*" --verbose
```

This shows detailed filtering information during processing.

## Common Regex Patterns

### Documentation Sites
```bash
# Common documentation patterns
".*/docs/.*"           # /docs/ path
".*/documentation/.*"   # /documentation/ path
".*/help/.*"           # /help/ path
".*/guide/.*"          # /guide/ path
```

### Blog and Content
```bash
# Blog and content patterns
".*/blog/.*"           # /blog/ path
".*/posts/.*"          # /posts/ path
".*/articles/.*"       # /articles/ path
".*/news/.*"           # /news/ path
```

### API Documentation
```bash
# API documentation patterns
".*/api/.*"            # /api/ path
".*/reference/.*"      # /reference/ path
".*/v[0-9]+/.*"        # Versioned API paths
```

### File Types
```bash
# Specific file types
".*\.html$"            # HTML files only
".*\.php$"             # PHP files only
".*\.aspx$"            # ASPX files only
```

## Error Handling

### Invalid Regex Pattern
```bash
python generate-llmstxt.py https://example.com --include-patterns "[invalid"
# Error: Invalid regex pattern: [invalid. Error: unexpected end of regular expression
```

### Empty Pattern
```bash
python generate-llmstxt.py https://example.com --include-patterns ""
# Error: Pattern cannot be empty. Use a valid regex pattern.
```

### No Matching URLs
```bash
python generate-llmstxt.py https://example.com --include-patterns ".*/nonexistent/.*"
# Warning: No URLs matched the pattern '.*/nonexistent/.*'. No llms.txt files will be generated.
```

## Output Examples

### Successful Filtering
```bash
$ python generate-llmstxt.py https://example.com --include-patterns ".*/docs/.*"
Applied regex filter: .*/docs/.*
Filtered 15 URLs from 100 discovered URLs
Processing batch 1/2
...
Success! Processed 15 out of 15 URLs
Files saved to ./
```

### No Matches Found
```bash
$ python generate-llmstxt.py https://example.com --include-patterns ".*/nonexistent/.*"
Applied regex filter: .*/nonexistent/.*
No URLs matched the pattern '.*/nonexistent/.*'. No llms.txt files will be generated.
```

## Generated Files

The filtering affects both output files:

### llms.txt
Contains only URLs matching the pattern:
```
# https://example.com llms.txt

- [Getting Started](https://example.com/docs/getting-started): Guide to getting started with our platform
- [API Reference](https://example.com/docs/api-reference): Complete API documentation and examples
- [Troubleshooting](https://example.com/docs/troubleshooting): Common issues and solutions
```

### llms-full.txt
Contains full content only for matching URLs:
```
# https://example.com llms-full.txt

<|firecrawl-page-1-lllmstxt|>
## Getting Started
Full markdown content of the getting started page...

<|firecrawl-page-2-lllmstxt|>
## API Reference
Full markdown content of the API reference page...
```

## Performance Tips

### Efficient Patterns
- Use specific patterns when possible: `.*/docs/.*` is faster than `.*docs.*`
- Avoid overly complex patterns that might cause performance issues
- Test patterns on small subsets first

### Large Websites
- Combine with `--max-urls` to limit processing time
- Use more specific patterns to reduce the URL set
- Consider running during off-peak hours for large sites

## Troubleshooting

### Pattern Not Working
1. Test your pattern with a regex tester online
2. Use `--verbose` to see which URLs are being filtered
3. Start with simple patterns and add complexity gradually

### Performance Issues
1. Use more specific patterns to reduce the URL set
2. Combine with `--max-urls` to limit processing
3. Check if the website has rate limiting

### No Results
1. Verify the pattern syntax is correct
2. Check if the website structure matches your pattern
3. Try a broader pattern first, then narrow it down

## Next Steps

- Read the full [specification](./spec.md) for detailed requirements
- Check the [implementation plan](./plan.md) for technical details
- Review the [data model](./data-model.md) for entity definitions
- See the [API contracts](./contracts/) for implementation details
