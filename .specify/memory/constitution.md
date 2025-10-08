<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0
Modified principles: N/A (initial creation)
Added sections: Core Principles, API Integration Standards, Error Handling, Development Workflow
Removed sections: N/A
Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md
Follow-up TODOs: None
-->

# Create LLMs.txt Python Tool Constitution

## Core Principles

### I. CLI-First Design
Every feature MUST be accessible via command-line interface with clear, intuitive arguments. The tool MUST support both interactive and non-interactive usage patterns. All output MUST be human-readable by default with optional structured formats (JSON) when needed. Error messages MUST be descriptive and actionable.

### II. API Integration Reliability
External API integrations (Firecrawl, OpenAI) MUST be implemented with proper error handling, rate limiting, and retry logic. API keys MUST be configurable via environment variables, .env files, or command-line arguments. All API calls MUST include appropriate timeouts and logging for debugging.

### III. Test-Driven Development (NON-NEGOTIABLE)
TDD is MANDATORY: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. All new features MUST have corresponding unit tests. Integration tests REQUIRED for API interactions and file generation workflows.

### IV. Content Quality Standards
Generated llms.txt files MUST be well-formatted, readable, and useful for LLM consumption. Page titles MUST be concise (3-4 words) and descriptions MUST be informative (9-10 words). Content MUST be properly escaped and formatted according to llms.txt specification. Duplicate or low-quality content MUST be filtered out.

### V. Performance & Scalability
The tool MUST handle large websites efficiently through batch processing and parallel execution. Memory usage MUST be optimized for processing hundreds of pages. Progress indicators MUST be provided for long-running operations. Configuration options MUST allow limiting resource usage.

## API Integration Standards

### Firecrawl Integration
- MUST use proper authentication headers and error handling
- MUST implement retry logic with exponential backoff
- MUST respect rate limits with configurable delays
- MUST handle partial failures gracefully (continue with successful pages)

### OpenAI Integration
- MUST use structured output format (JSON) for consistent parsing
- MUST implement token limits to prevent API errors
- MUST handle API failures with fallback to basic titles/descriptions
- MUST log all API usage for monitoring and debugging

## Error Handling

### Graceful Degradation
- Failed page scrapes MUST NOT stop the entire process
- API failures MUST fall back to basic content extraction
- Invalid URLs MUST be logged and skipped
- Partial results MUST be saved even if some pages fail

### Logging Requirements
- MUST use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)
- MUST log all API calls, errors, and processing statistics
- MUST provide verbose mode for detailed debugging
- MUST include timestamps and context in all log messages

## Development Workflow

### Code Quality
- MUST follow Python PEP 8 style guidelines
- MUST use type hints for all function parameters and return values
- MUST include comprehensive docstrings for all public functions
- MUST use meaningful variable and function names

### Testing Requirements
- Unit tests MUST cover all core functionality
- Integration tests MUST verify API interactions
- Contract tests MUST validate output format compliance
- Tests MUST be runnable independently and in parallel

### Documentation
- README MUST include clear installation and usage instructions
- Code MUST be self-documenting with clear comments
- Examples MUST be provided for common use cases
- Error scenarios MUST be documented with solutions

## Governance

All development work MUST verify compliance with this constitution. Any deviations MUST be documented with clear justification. The constitution supersedes all other development practices. Amendments require documentation, team approval, and migration plan for existing code.

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27