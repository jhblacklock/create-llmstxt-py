# Implementation Plan: Include Patterns Filter

**Branch**: `001-add-another-option` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-add-another-option/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add regex pattern filtering capability to the existing llms.txt generator tool, allowing users to filter URLs before processing to create more focused llms.txt files. The feature integrates with existing CLI arguments and maintains all current functionality while adding URL filtering based on regex patterns.

## Technical Context

**Language/Version**: Python 3.7+ (existing project requirement)  
**Primary Dependencies**: requests, openai, python-dotenv (existing), re (built-in regex module)  
**Storage**: N/A (file-based output)  
**Testing**: pytest (existing), unittest (built-in)  
**Target Platform**: Cross-platform CLI tool (Linux, macOS, Windows)  
**Project Type**: Single project (CLI tool)  
**Performance Goals**: Regex filtering should not significantly impact processing time; 100% accuracy in URL matching  
**Constraints**: Must maintain backward compatibility; regex validation must be fast (<1 second); memory usage should not increase significantly  
**Scale/Scope**: Handle websites with 1000+ URLs; support complex regex patterns without performance degradation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### CLI-First Design Compliance
- [x] Feature MUST be accessible via command-line interface
- [x] Clear, intuitive arguments defined (`--include-patterns` with help text)
- [x] Human-readable output by default with optional structured formats
- [x] Descriptive and actionable error messages planned (regex validation errors, no matches)

### API Integration Reliability
- [x] External API integrations have proper error handling planned (existing Firecrawl/OpenAI handling)
- [x] Rate limiting and retry logic designed (existing implementation)
- [x] API key configuration methods defined (existing .env/env var support)
- [x] Appropriate timeouts and logging planned (existing structured logging)

### Test-Driven Development
- [x] TDD approach planned: Tests written → User approved → Tests fail → Then implement
- [x] Unit tests planned for all core functionality (regex validation, URL filtering)
- [x] Integration tests planned for API interactions (filtered URL processing)
- [x] Contract tests planned for output validation (filtered llms.txt format)

### Content Quality Standards
- [x] Output format compliance with llms.txt specification (maintains existing format)
- [x] Content filtering and quality control planned (regex-based URL filtering)
- [x] Proper escaping and formatting planned (existing content processing)

### Performance & Scalability
- [x] Batch processing and parallel execution planned (existing batch processing)
- [x] Memory usage optimization considered (filtering before API calls reduces memory)
- [x] Progress indicators planned for long-running operations (existing progress logging)
- [x] Resource usage limiting options designed (existing max-urls integration)

## Project Structure

### Documentation (this feature)

```
specs/001-add-another-option/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── cli-interface.md
│   └── url-filtering-api.md
├── checklists/          # Quality validation
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
generate-llmstxt.py          # Main CLI script (existing)
requirements.txt             # Python dependencies (existing)
README.md                    # Project documentation (existing)

tests/                       # Test directory (to be created)
├── unit/                    # Unit tests for regex filtering
├── integration/             # Integration tests for filtered processing
└── contract/                # Contract tests for output validation
```

**Structure Decision**: Single project structure maintained. The feature adds regex filtering functionality to the existing `generate-llmstxt.py` script without requiring new modules or significant structural changes. Tests will be organized in a new `tests/` directory following Python testing conventions.

## Phase 0: Research Complete ✅

**Research Document**: [research.md](./research.md)

Key decisions made:
- Use Python's built-in `re` module for regex processing
- Add `--include-patterns` CLI argument with argparse integration
- Filter URLs after discovery but before API calls for efficiency
- Implement early pattern validation with clear error messages
- Maintain full backward compatibility with existing features

## Phase 1: Design Complete ✅

**Data Model**: [data-model.md](./data-model.md)  
**Contracts**: [contracts/](./contracts/)  
**Quickstart**: [quickstart.md](./quickstart.md)  
**Agent Context**: Updated for Cursor IDE

### Generated Artifacts:
- **data-model.md**: Defines URL Pattern, Filtered URL Set, and Pattern Validation Result entities
- **contracts/cli-interface.md**: CLI argument specification and integration details
- **contracts/url-filtering-api.md**: Internal API contracts for filtering services
- **quickstart.md**: User guide with examples, patterns, and troubleshooting
- **Agent Context**: Updated with Python 3.7+, regex module, and CLI tool context

## Complexity Tracking

*No constitution violations identified - all requirements align with existing project architecture*

The feature integrates cleanly with existing codebase:
- No new dependencies required (uses built-in `re` module)
- Minimal code changes to existing `generate-llmstxt.py`
- Maintains all existing functionality and CLI options
- Follows established patterns for argument parsing and error handling
