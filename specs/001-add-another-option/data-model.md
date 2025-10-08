# Data Model: Include Patterns Filter

**Feature**: Include Patterns Filter  
**Date**: 2025-01-27  
**Phase**: 1 - Design & Contracts

## Entities

### URL Pattern
Represents the regex pattern used for filtering URLs.

**Attributes**:
- `pattern_string` (str): Raw regex pattern string from user input
- `compiled_pattern` (re.Pattern): Compiled regex pattern for efficient matching
- `is_valid` (bool): Whether the pattern is syntactically valid
- `validation_error` (str, optional): Error message if pattern is invalid

**Validation Rules**:
- Must be valid regex syntax
- Cannot be empty string
- Must be compilable by Python's `re` module

**State Transitions**:
- `raw` → `validated` → `compiled` (success path)
- `raw` → `invalid` (validation failure)

### Filtered URL Set
Collection of URLs that match the provided regex pattern.

**Attributes**:
- `original_urls` (List[str]): All URLs discovered from website mapping
- `filtered_urls` (List[str]): URLs that match the regex pattern
- `filter_count` (int): Number of URLs that matched the pattern
- `filter_ratio` (float): Ratio of filtered URLs to original URLs (0.0 to 1.0)

**Validation Rules**:
- `filtered_urls` must be a subset of `original_urls`
- `filter_count` must be <= length of `original_urls`
- `filter_ratio` must be between 0.0 and 1.0

**State Transitions**:
- `discovered` → `filtered` (successful filtering)
- `discovered` → `empty` (no matches found)

### Pattern Validation Result
Indicates the result of regex pattern validation.

**Attributes**:
- `is_valid` (bool): Whether the pattern is syntactically valid
- `error_message` (str, optional): Human-readable error message if invalid
- `suggestion` (str, optional): Suggested correction if pattern is close to valid

**Validation Rules**:
- `error_message` must be present if `is_valid` is False
- `suggestion` is optional and only present for common syntax errors

**State Transitions**:
- `validating` → `valid` (successful validation)
- `validating` → `invalid` (validation failure)

## Relationships

### URL Pattern → Filtered URL Set
- **Type**: One-to-One
- **Description**: A URL Pattern filters a set of URLs to create a Filtered URL Set
- **Constraints**: Pattern must be valid before filtering can occur

### Pattern Validation Result → URL Pattern
- **Type**: One-to-One
- **Description**: Validation result determines if a URL Pattern can be used
- **Constraints**: Invalid patterns cannot be used for filtering

## Data Flow

1. **Input**: User provides `--include-patterns` argument with regex string
2. **Validation**: Pattern string is validated using `re.compile()`
3. **Compilation**: Valid pattern is compiled for efficient matching
4. **Discovery**: Website URLs are discovered via Firecrawl mapping
5. **Filtering**: Discovered URLs are filtered using compiled pattern
6. **Processing**: Only filtered URLs are sent to Firecrawl/OpenAI APIs
7. **Output**: llms.txt files contain only matching URLs

## Error Handling

### Invalid Regex Pattern
- **Trigger**: User provides malformed regex syntax
- **Response**: Display clear error message with syntax help
- **Recovery**: Exit gracefully, suggest correction if possible

### No Matching URLs
- **Trigger**: Valid pattern matches no discovered URLs
- **Response**: Display informative message about no matches
- **Recovery**: Continue with empty result set, don't fail

### Pattern Compilation Failure
- **Trigger**: Pattern is too complex or causes compilation issues
- **Response**: Display error message with simplified pattern suggestion
- **Recovery**: Exit gracefully with helpful error message

## Performance Considerations

- **Pattern Compilation**: Done once at startup, cached for reuse
- **URL Filtering**: O(n) operation where n is number of discovered URLs
- **Memory Usage**: Reduces memory by filtering before API calls
- **API Efficiency**: Reduces API calls proportional to filtering ratio

## Integration Points

### Existing Code Integration
- **CLI Arguments**: Integrates with existing argparse setup
- **URL Discovery**: Works with existing Firecrawl mapping
- **API Processing**: Integrates with existing batch processing
- **Output Generation**: Maintains existing llms.txt format

### New Code Requirements
- **Pattern Validation**: New validation logic for regex patterns
- **URL Filtering**: New filtering logic for URL matching
- **Error Handling**: New error messages for regex-specific issues
- **Logging**: New log messages for filtering operations
