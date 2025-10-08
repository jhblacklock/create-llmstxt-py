# Feature Specification: Include Patterns Filter

**Feature Branch**: `001-add-another-option`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Add another option called include-patterns that takes a regex pattern to search by."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter URLs by Regex Pattern (Priority: P1)

A user wants to generate llms.txt files that only include pages matching specific URL patterns, such as documentation pages, blog posts, or API endpoints.

**Why this priority**: This is the core functionality that enables users to focus on specific content types and reduce noise in their llms.txt files, making them more useful for LLM consumption.

**Independent Test**: Can be fully tested by running the tool with a regex pattern and verifying that only matching URLs are included in the output files.

**Acceptance Scenarios**:

1. **Given** a website with mixed content (docs, blog, API pages), **When** user runs tool with `--include-patterns ".*/docs/.*"`, **Then** only documentation pages are included in llms.txt
2. **Given** a website with blog posts and other content, **When** user runs tool with `--include-patterns ".*/blog/.*"`, **Then** only blog post pages are included in llms.txt
3. **Given** a website with API endpoints, **When** user runs tool with `--include-patterns ".*/api/.*"`, **Then** only API endpoint pages are included in llms.txt

---

### User Story 2 - Handle Invalid Regex Patterns (Priority: P2)

A user provides an invalid regex pattern and expects clear error messaging and graceful handling.

**Why this priority**: Error handling is critical for user experience and prevents tool crashes from malformed input.

**Independent Test**: Can be fully tested by providing invalid regex patterns and verifying appropriate error messages are displayed.

**Acceptance Scenarios**:

1. **Given** user provides invalid regex pattern `[unclosed`, **When** tool processes the pattern, **Then** clear error message is displayed and tool exits gracefully
2. **Given** user provides empty regex pattern, **When** tool processes the pattern, **Then** appropriate validation error is shown
3. **Given** user provides regex that matches no URLs, **When** tool processes the pattern, **Then** informative message about no matches found is displayed

---

### User Story 3 - Combine with Existing Options (Priority: P3)

A user wants to use include-patterns alongside existing options like max-urls and output-dir to create focused llms.txt files.

**Why this priority**: This ensures the new feature integrates well with existing functionality and doesn't break current workflows.

**Independent Test**: Can be fully tested by running the tool with multiple options and verifying all work together correctly.

**Acceptance Scenarios**:

1. **Given** user runs tool with `--include-patterns ".*/docs/.*" --max-urls 50`, **When** tool processes, **Then** only documentation pages are included up to the specified limit
2. **Given** user runs tool with `--include-patterns ".*/blog/.*" --output-dir ./output`, **When** tool processes, **Then** filtered blog pages are saved to the specified directory

---

### Edge Cases

- What happens when regex pattern matches all URLs on the website?
- What happens when regex pattern matches no URLs on the website?
- How does system handle very complex regex patterns that might cause performance issues?
- How does system handle regex patterns with special characters that need escaping?
- What happens when include-patterns is used with very large websites (1000+ URLs)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept `--include-patterns` command-line argument with regex pattern
- **FR-002**: System MUST filter discovered URLs using the provided regex pattern before processing
- **FR-003**: System MUST validate regex pattern syntax and provide clear error messages for invalid patterns
- **FR-004**: System MUST display count of URLs matching the pattern in processing output
- **FR-005**: System MUST handle case where no URLs match the pattern with informative messaging

### CLI Requirements *(mandatory for CLI tools)*

- **CLI-001**: System MUST provide `--include-patterns` argument with clear help text describing regex filtering
- **CLI-002**: System MUST support regex pattern as a string argument (not requiring file input)
- **CLI-003**: System MUST display human-readable output showing how many URLs matched the pattern
- **CLI-004**: System MUST provide structured error messages for invalid regex patterns
- **CLI-005**: System MUST display descriptive error messages when no URLs match the pattern

### API Integration Requirements *(mandatory for API integrations)*

- **API-001**: System MUST apply regex filtering after URL discovery but before API calls to Firecrawl
- **API-002**: System MUST log regex pattern usage and filtering results for debugging
- **API-003**: System MUST handle regex filtering without impacting rate limiting or API call efficiency
- **API-004**: System MUST continue processing other URLs if regex filtering reduces the set significantly
- **API-005**: System MUST log filtered URL counts for monitoring and debugging

### Content Quality Requirements *(mandatory for content generation)*

- **CQ-001**: Filtered content MUST maintain same quality standards as unfiltered content
- **CQ-002**: Page titles and descriptions MUST be generated for all matching URLs
- **CQ-003**: Generated llms.txt files MUST only contain pages matching the regex pattern
- **CQ-004**: Content formatting MUST remain consistent regardless of filtering
- **CQ-005**: System MUST not include pages that don't match the pattern in output files

### Key Entities *(include if feature involves data)*

- **URL Pattern**: Represents the regex pattern used for filtering, must be valid regex syntax
- **Filtered URL Set**: Collection of URLs that match the provided pattern, subset of discovered URLs
- **Pattern Validation Result**: Indicates whether regex pattern is valid and can be used for filtering

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can filter URLs using regex patterns with 100% accuracy (no false positives or negatives)
- **SC-002**: Invalid regex patterns are rejected within 1 second with clear error messages
- **SC-003**: Regex filtering reduces processing time proportionally to the filtering ratio (50% fewer URLs = ~50% faster processing)
- **SC-004**: 95% of users can successfully use regex patterns without syntax errors on first attempt
- **SC-005**: Generated llms.txt files contain only URLs matching the specified pattern with 100% accuracy