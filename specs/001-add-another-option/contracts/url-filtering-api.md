# URL Filtering API Contract: Include Patterns Filter

**Feature**: Include Patterns Filter  
**Date**: 2025-01-27  
**Type**: Internal API Contract

## URL Filtering Service

### filter_urls(urls: List[str], pattern: str) -> FilteredURLSet
**Purpose**: Filter a list of URLs using a regex pattern

**Parameters**:
- `urls` (List[str]): List of URLs to filter
- `pattern` (str): Regex pattern string

**Returns**: `FilteredURLSet` object containing:
- `filtered_urls` (List[str]): URLs that match the pattern
- `original_count` (int): Number of original URLs
- `filtered_count` (int): Number of filtered URLs
- `filter_ratio` (float): Ratio of filtered to original URLs

**Raises**:
- `ValueError`: If pattern is empty or invalid
- `re.error`: If pattern is not valid regex syntax

**Example**:
```python
urls = ["https://example.com/docs/page1", "https://example.com/blog/post1", "https://example.com/api/endpoint1"]
pattern = ".*/docs/.*"
result = filter_urls(urls, pattern)
# result.filtered_urls = ["https://example.com/docs/page1"]
# result.filtered_count = 1
# result.original_count = 3
# result.filter_ratio = 0.33
```

## Pattern Validation Service

### validate_pattern(pattern: str) -> PatternValidationResult
**Purpose**: Validate a regex pattern before use

**Parameters**:
- `pattern` (str): Regex pattern string to validate

**Returns**: `PatternValidationResult` object containing:
- `is_valid` (bool): Whether pattern is valid
- `error_message` (str, optional): Error message if invalid
- `compiled_pattern` (re.Pattern, optional): Compiled pattern if valid

**Raises**: None (always returns result object)

**Example**:
```python
result = validate_pattern(".*/docs/.*")
# result.is_valid = True
# result.compiled_pattern = <re.Pattern object>

result = validate_pattern("[invalid")
# result.is_valid = False
# result.error_message = "unexpected end of regular expression"
```

## Integration Points

### Firecrawl Integration
- **Input**: List of discovered URLs from Firecrawl mapping
- **Processing**: Apply regex filtering before API calls
- **Output**: Filtered URL list for processing

### OpenAI Integration
- **Input**: Filtered URL list
- **Processing**: Generate titles/descriptions for filtered URLs only
- **Output**: llms.txt content for filtered URLs only

### Logging Integration
- **Pattern Usage**: Log pattern application and results
- **Filtering Stats**: Log filtering statistics
- **Error Handling**: Log validation errors and warnings

## Performance Requirements

### Pattern Compilation
- **Timing**: Must complete within 100ms for typical patterns
- **Caching**: Compiled patterns should be cached for reuse
- **Memory**: Minimal memory overhead for pattern storage

### URL Filtering
- **Timing**: Must complete within 1 second for 1000 URLs
- **Memory**: Should not significantly increase memory usage
- **Scalability**: Linear time complexity O(n) where n is URL count

## Error Handling

### Pattern Validation Errors
- **Empty Pattern**: Return validation error with helpful message
- **Invalid Syntax**: Return validation error with syntax details
- **Compilation Failure**: Return validation error with suggestions

### Filtering Errors
- **Empty URL List**: Return empty filtered result
- **Pattern Mismatch**: Return empty filtered result with warning
- **Memory Issues**: Handle gracefully with appropriate error messages

## Testing Requirements

### Unit Tests
- Pattern validation with valid/invalid patterns
- URL filtering with various pattern types
- Error handling for edge cases
- Performance with large URL lists

### Integration Tests
- End-to-end filtering workflow
- Integration with existing Firecrawl/OpenAI calls
- CLI argument processing
- Output file generation

### Contract Tests
- API contract compliance
- Error message format validation
- Performance requirement verification
- Memory usage validation
