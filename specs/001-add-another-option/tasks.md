---
description: "Task list for include-patterns feature implementation"
---

# Tasks: Include Patterns Filter

**Input**: Design documents from `/specs/001-add-another-option/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Tests**: Tests are MANDATORY per constitution - TDD approach required for all functionality

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `generate-llmstxt.py` at repository root
- **Tests**: `tests/` directory with unit/, integration/, contract/ subdirectories
- Paths shown below assume single project structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create test directory structure per implementation plan
- [x] T002 [P] Configure pytest for testing framework
- [x] T003 [P] Setup type checking and mypy configuration
- [x] T004 [P] Configure logging infrastructure with structured logging
- [x] T005 [P] Setup code coverage reporting for tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create data model classes for URL Pattern, Filtered URL Set, and Pattern Validation Result
- [x] T007 [P] Implement pattern validation service with regex compilation
- [x] T008 [P] Implement URL filtering service with regex matching
- [x] T009 [P] Add CLI argument parsing for --include-patterns
- [x] T010 [P] Create error handling utilities for regex validation errors
- [x] T011 [P] Setup logging for filtering operations and statistics

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Filter URLs by Regex Pattern (Priority: P1) 🎯 MVP

**Goal**: Enable users to filter URLs using regex patterns to create focused llms.txt files

**Independent Test**: Run tool with regex pattern and verify only matching URLs are included in output files

### Tests for User Story 1 (MANDATORY per Constitution) ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US1] Unit test for pattern validation service in tests/unit/test_pattern_validation.py
- [x] T013 [P] [US1] Unit test for URL filtering service in tests/unit/test_url_filtering.py
- [x] T014 [P] [US1] Integration test for CLI argument processing in tests/integration/test_cli_integration.py
- [x] T015 [P] [US1] Contract test for filtered URL processing in tests/contract/test_filtered_processing.py

### Implementation for User Story 1

- [x] T016 [US1] Integrate pattern validation into main CLI argument processing
- [x] T017 [US1] Integrate URL filtering into existing URL discovery workflow
- [x] T018 [US1] Add filtering logic to main generate_llmstxt method
- [x] T019 [US1] Update logging to include filtering statistics and pattern usage
- [x] T020 [US1] Add CLI help text and usage examples for --include-patterns
- [x] T021 [US1] Update output messages to show filtering results

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Handle Invalid Regex Patterns (Priority: P2)

**Goal**: Provide clear error messaging and graceful handling for invalid regex patterns

**Independent Test**: Provide invalid regex patterns and verify appropriate error messages are displayed

### Tests for User Story 2 (MANDATORY per Constitution) ⚠️

- [x] T022 [P] [US2] Unit test for invalid pattern error handling in tests/unit/test_error_handling.py
- [x] T023 [P] [US2] Integration test for CLI error scenarios in tests/integration/test_cli_errors.py
- [x] T024 [P] [US2] Contract test for error message formats in tests/contract/test_error_contracts.py

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement comprehensive error message generation for regex validation failures
- [x] T026 [US2] Add graceful error handling for pattern compilation failures
- [x] T027 [US2] Implement user-friendly error messages with suggestions
- [x] T028 [US2] Add error logging for debugging invalid pattern issues
- [x] T029 [US2] Update CLI to handle and display validation errors appropriately

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Combine with Existing Options (Priority: P3)

**Goal**: Ensure include-patterns works seamlessly with existing CLI options

**Independent Test**: Run tool with multiple options and verify all work together correctly

### Tests for User Story 3 (MANDATORY per Constitution) ⚠️

- [x] T030 [P] [US3] Integration test for option combinations in tests/integration/test_option_combinations.py
- [x] T031 [P] [US3] Contract test for processing order validation in tests/contract/test_processing_order.py
- [x] T032 [P] [US3] End-to-end test for complete workflow in tests/integration/test_end_to_end.py

### Implementation for User Story 3

- [x] T033 [P] [US3] Ensure filtering happens before max-urls limiting
- [x] T034 [US3] Verify output directory handling works with filtered results
- [x] T035 [US3] Test integration with verbose logging and other existing options
- [x] T036 [US3] Validate backward compatibility with existing usage patterns
- [x] T037 [US3] Update documentation to show option combination examples

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T038 [P] Documentation updates in README.md with --include-patterns examples
- [x] T039 [P] Code cleanup and refactoring for maintainability
- [x] T040 [P] Performance optimization for large URL lists
- [x] T041 [P] Additional unit tests for edge cases in tests/unit/
- [x] T042 [P] Security review for regex pattern handling
- [x] T043 [P] Run quickstart.md validation with real examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for pattern validation service in tests/unit/test_pattern_validation.py"
Task: "Unit test for URL filtering service in tests/unit/test_url_filtering.py"
Task: "Integration test for CLI argument processing in tests/integration/test_cli_integration.py"
Task: "Contract test for filtered URL processing in tests/contract/test_filtered_processing.py"

# Launch implementation tasks for User Story 1 together:
Task: "Integrate pattern validation into main CLI argument processing"
Task: "Integrate URL filtering into existing URL discovery workflow"
Task: "Add filtering logic to main generate_llmstxt method"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
