# CLI Interface Contract: Include Patterns Filter

**Feature**: Include Patterns Filter  
**Date**: 2025-01-27  
**Type**: Command Line Interface Contract

## New CLI Arguments

### --include-patterns
**Type**: String  
**Required**: No  
**Default**: None (no filtering applied)  
**Description**: Regex pattern to filter URLs before processing

**Usage Examples**:
```bash
# Filter for documentation pages
python generate-llmstxt.py https://example.com --include-patterns ".*/docs/.*"

# Filter for blog posts
python generate-llmstxt.py https://example.com --include-patterns ".*/blog/.*"

# Filter for API endpoints
python generate-llmstxt.py https://example.com --include-patterns ".*/api/.*"

# Combine with existing options
python generate-llmstxt.py https://example.com --include-patterns ".*/docs/.*" --max-urls 50
```

## Argument Validation

### Pattern Validation
- **Syntax Check**: Pattern must be valid regex syntax
- **Compilation Check**: Pattern must compile successfully with `re.compile()`
- **Empty Check**: Pattern cannot be empty string

### Error Messages
- **Invalid Syntax**: "Invalid regex pattern: {pattern}. Error: {error_message}"
- **Empty Pattern**: "Pattern cannot be empty. Use a valid regex pattern."
- **Compilation Error**: "Pattern compilation failed: {error_message}"

## Integration with Existing Arguments

### Argument Order
1. `url` (required)
2. `--include-patterns` (optional)
3. `--max-urls` (optional)
4. `--output-dir` (optional)
5. Other existing arguments

### Processing Order
1. Discover URLs via Firecrawl mapping
2. Apply regex filtering (if `--include-patterns` provided)
3. Apply max-urls limiting
4. Process remaining URLs

## Help Text

```
--include-patterns PATTERN
                        Regex pattern to filter URLs before processing.
                        Only URLs matching this pattern will be included
                        in the generated llms.txt files. Examples:
                        ".*/docs/.*" for documentation pages,
                        ".*/blog/.*" for blog posts,
                        ".*/api/.*" for API endpoints.
```

## Output Messages

### Success Messages
- **Pattern Applied**: "Applied regex filter: {pattern}"
- **URLs Filtered**: "Filtered {filtered_count} URLs from {total_count} discovered URLs"
- **No Matches**: "No URLs matched the pattern '{pattern}'. No llms.txt files will be generated."

### Error Messages
- **Pattern Validation**: "Error: {validation_error_message}"
- **No Matches Warning**: "Warning: No URLs matched the provided pattern."

## Backward Compatibility

### Existing Usage
- All existing command-line usage remains unchanged
- No breaking changes to existing arguments
- Default behavior (no filtering) when `--include-patterns` not provided

### Migration Path
- No migration required
- Feature is purely additive
- Existing scripts continue to work unchanged
