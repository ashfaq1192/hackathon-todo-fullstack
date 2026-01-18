# Implementation Tasks: CLI Todo App with Basic CRUD Operations

**Feature**: CLI Todo App with Basic CRUD Operations
**Branch**: `001-cli-todo-app`
**Date**: 2025-12-17
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Task Overview

This document provides an actionable, dependency-aware task breakdown for implementing the CLI Todo App. Tasks are organized by user story to enable independent implementation and testing following Test-Driven Development (TDD) principles.

### Task Counts

- **Total Tasks**: 48
- **Setup Phase**: 5 tasks
- **Foundational Phase**: 6 tasks
- **User Story 1** (Create and View Tasks): 10 tasks
- **User Story 2** (Mark Complete/Incomplete): 6 tasks
- **User Story 3** (Update Task Details): 6 tasks
- **User Story 4** (Delete Tasks): 6 tasks
- **Polish Phase**: 9 tasks

### Parallelization Opportunities

- Setup: 0 parallel tasks (sequential setup required)
- Foundational: 3 parallel tasks (models, CLI utilities)
- User Story 1: 4 parallel tasks (independent test files)
- User Story 2: 3 parallel tasks (tests + implementation)
- User Story 3: 3 parallel tasks (tests + implementation)
- User Story 4: 3 parallel tasks (tests + implementation)
- Polish: 5 parallel tasks (independent quality improvements)

### MVP Scope

**Minimum Viable Product** (70% coverage, basic functionality):
- Phase 1: Setup (all tasks)
- Phase 2: Foundational (all tasks)
- Phase 3: User Story 1 - Create and View Tasks (all tasks)
- Phase 4: User Story 2 - Mark Complete/Incomplete (all tasks)
- Deliverables: Working CLI with Add, View, and Mark Complete operations

**Production-Ready** (80% coverage, all features):
- Add Phase 5: User Story 3 - Update Task Details
- Add Phase 6: User Story 4 - Delete Tasks
- Add Phase 7: Polish & Cross-Cutting Concerns

---

## Phase 1: Setup (Project Initialization)

**Goal**: Initialize project structure, configure environment, and install dependencies

**Prerequisites**: None (starting point)

**Independent Test**: Project structure created, virtual environment working, dependencies installed

### Tasks

- [X] T001 Create project directory structure (src/models/, src/services/, src/cli/, tests/unit/, tests/integration/) per plan.md:lines 75-101
- [X] T002 Initialize Python package structure with __init__.py files in all directories (src/, src/models/, src/services/, src/cli/, tests/, tests/unit/, tests/integration/)
- [X] T003 Create virtual environment using `uv venv` and activate it
- [X] T004 Install development dependencies using `uv add pytest pytest-cov ruff`
- [X] T005 Create .env file with LOG_LEVEL=DEBUG and APP_NAME=evolution-todo per quickstart.md

**Completion Criteria**:
- ✅ All directories exist with correct structure
- ✅ Virtual environment activated
- ✅ Dependencies installed: `pytest --version`, `ruff --version` succeed
- ✅ .env file present with required variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement core infrastructure needed by all user stories

**Prerequisites**: Phase 1 complete

**Independent Test**: Foundational components tested independently, no user story dependencies

### Tasks

- [X] T0*6 [P] Create test file tests/unit/models/test_task.py with test structure for task validation
- [X] T0*7 [P] Create test file tests/unit/services/test_task_service.py with test structure for CRUD operations
- [X] T0*8 [P] Create test file tests/unit/cli/test_menu.py with test structure for menu functions
- [X] T0*9 Implement logging configuration in src/services/task_service.py per constitution logging standards (stdlib logging, INFO level, format: %(asctime)s - %(name)s - %(levelname)s - %(message)s)
- [X] T0*10 Write test for logging configuration in tests/unit/services/test_task_service.py::test_logging_configured
- [X] T0*11 Implement module-level state management in src/services/task_service.py (tasks list, next_id counter) per data-model.md:lines 48-55

**Completion Criteria**:
- ✅ All test files created with proper structure
- ✅ Logging configured and tested
- ✅ Module-level state initialized
- ✅ Tests pass: `pytest tests/unit/`

**Parallelization**: T006, T007, T008 can run in parallel (independent test files)

---

## Phase 3: User Story 1 - Create and View Tasks

**User Story**: As a user, I want to add new tasks with titles, descriptions, and priority levels (High/Medium/Low), then view them in a list so I can track what I need to do and understand task urgency.

**Priority**: High (MVP Critical)

**Prerequisites**: Phase 2 complete

**Independent Test**: Can add tasks and view them sorted by priority with incomplete tasks first. Empty list shows appropriate message.

**Acceptance Criteria** (from spec.md:lines 28-30):
1. Task created with unique ID, stored with complete=false and priority
2. All tasks displayed with ID, title, description, priority, completion status, ordered by priority (High→Medium→Low), incomplete before completed
3. Empty list shows "No tasks" message

### Tasks

#### Models Layer

- [X] T0*12 [P] [US1] Write test tests/unit/models/test_task.py::test_validate_title_non_empty for title validation
- [X] T0*13 [P] [US1] Write test tests/unit/models/test_task.py::test_validate_priority_valid_values for priority validation
- [X] T0*14 [US1] Implement task validation functions in src/models/task.py (validate_title, validate_priority) per data-model.md:lines 24-78
- [X] T0*15 [US1] Run tests for task validation: `pytest tests/unit/models/test_task.py -v`

#### Services Layer

- [X] T016 [P] [US1] Write test tests/unit/services/test_task_service.py::test_create_task_success for successful task creation
- [X] T017 [P] [US1] Write test tests/unit/services/test_task_service.py::test_create_task_empty_title for empty title validation
- [X] T018 [P] [US1] Write test tests/unit/services/test_task_service.py::test_create_task_invalid_priority for invalid priority validation
- [X] T019 [US1] Implement create_task function in src/services/task_service.py per service_contract.md:lines 21-67
- [X] T020 [P] [US1] Write test tests/unit/services/test_task_service.py::test_get_all_tasks_sorted for task list sorting (completion→priority→ID)
- [X] T021 [P] [US1] Write test tests/unit/services/test_task_service.py::test_get_all_tasks_empty for empty list handling
- [X] T022 [US1] Implement get_all_tasks function in src/services/task_service.py with multi-level sorting per data-model.md:lines 209-238
- [X] T023 [US1] Run tests for service layer: `pytest tests/unit/services/ -k "create_task or get_all_tasks" -v`

#### CLI Layer

- [X] T024 [US1] Implement display_task function in src/cli/display.py per cli_contract.md:lines 111-157
- [X] T025 [US1] Implement display_task_list function in src/cli/display.py per cli_contract.md:lines 161-199
- [X] T026 [US1] Implement prompt_add_task function in src/cli/menu.py per cli_contract.md:lines 92-143
- [X] T027 [US1] Write test tests/unit/cli/test_menu.py::test_prompt_add_task_with_valid_input using mock input
- [X] T028 [US1] Write test tests/unit/cli/test_display.py::test_display_task_list_with_tasks for display formatting
- [X] T029 [US1] Run CLI tests: `pytest tests/unit/cli/ -v`

#### Integration

- [X] T030 [US1] Write integration test tests/integration/test_app_flow.py::test_add_and_view_task_flow for complete workflow
- [X] T031 [US1] Run integration test: `pytest tests/integration/test_app_flow.py::test_add_and_view_task_flow -v`

**Completion Criteria**:
- ✅ All User Story 1 tests passing
- ✅ Can add task with title, description, priority
- ✅ Task list displays sorted correctly (priority-based)
- ✅ Empty list shows appropriate message
- ✅ Task IDs auto-increment starting from 1
- ✅ Test coverage for US1 components ≥70%

**Parallelization**: T012-T013, T016-T018, T020-T021 can run in parallel (independent test files)

---

## Phase 4: User Story 2 - Mark Tasks Complete/Incomplete

**User Story**: As a user, I want to mark tasks as complete or incomplete so I can track my progress, distinguish finished work from pending work, and reopen tasks if needed.

**Priority**: High (MVP Critical)

**Prerequisites**: Phase 3 complete (requires create_task and get_all_tasks)

**Independent Test**: Can toggle task completion status bidirectionally. Completed tasks appear after incomplete tasks in sorted list.

**Acceptance Criteria** (from spec.md:lines 46-49):
1. Task completion status changes from false to true
2. Completed tasks display with complete=true
3. Can toggle from complete back to incomplete
4. Error message shown for non-existent task ID

### Tasks

#### Services Layer

- [X] T032 [P] [US2] Write test tests/unit/services/test_task_service.py::test_toggle_completion_mark_complete for false→true toggle
- [X] T033 [P] [US2] Write test tests/unit/services/test_task_service.py::test_toggle_completion_mark_incomplete for true→false toggle
- [X] T034 [P] [US2] Write test tests/unit/services/test_task_service.py::test_toggle_completion_task_not_found for error handling
- [X] T035 [US2] Implement toggle_task_completion function in src/services/task_service.py per service_contract.md:lines 223-273
- [X] T036 [US2] Run tests: `pytest tests/unit/services/test_task_service.py -k "toggle_completion" -v`

#### CLI Layer

- [X] T037 [US2] Implement prompt_task_id function in src/cli/menu.py per cli_contract.md:lines 147-175
- [X] T038 [US2] Write test tests/unit/cli/test_menu.py::test_prompt_task_id_valid_input using mock input
- [X] T039 [US2] Write integration test tests/integration/test_app_flow.py::test_toggle_completion_flow for complete workflow

#### Integration

- [X] T040 [US2] Run all User Story 2 tests: `pytest -k "toggle" -v`

**Completion Criteria**:
- ✅ All User Story 2 tests passing
- ✅ Can mark task complete (false→true)
- ✅ Can mark task incomplete (true→false)
- ✅ Completed tasks sort after incomplete tasks
- ✅ Error handling for invalid task IDs
- ✅ Combined coverage (US1+US2) ≥70%

**Parallelization**: T032-T034 can run in parallel (independent test cases)

**Dependencies**: Requires create_task (T019) and get_all_tasks (T022) from US1

---

## Phase 5: User Story 3 - Update Task Details

**User Story**: As a user, I want to edit a task's title, description, or priority level individually or in combination so I can correct mistakes, refine task details, or adjust urgency as situations change.

**Priority**: Medium (Production-Ready)

**Prerequisites**: Phase 3 complete (requires create_task and get_all_tasks)

**Independent Test**: Can update individual fields (title only, description only, priority only) or multiple fields together. Non-updated fields remain unchanged.

**Acceptance Criteria** (from spec.md:lines 63-66):
1. Can update only title, leaving description and priority unchanged
2. Can update all fields (title, description, priority) together
3. Updated task displays with new values, complete status unchanged
4. Error message for non-existent task ID

### Tasks

#### Services Layer

- [X] T041 [P] [US3] Write test tests/unit/services/test_task_service.py::test_update_task_partial_title_only for partial update
- [X] T042 [P] [US3] Write test tests/unit/services/test_task_service.py::test_update_task_all_fields for full update
- [X] T043 [P] [US3] Write test tests/unit/services/test_task_service.py::test_update_task_validation_errors for empty title and invalid priority
- [X] T044 [US3] Implement update_task function in src/services/task_service.py per service_contract.md:lines 177-243
- [X] T045 [US3] Run tests: `pytest tests/unit/services/test_task_service.py -k "update_task" -v`

#### CLI Layer

- [X] T046 [US3] Implement prompt_update_task function in src/cli/menu.py per cli_contract.md:lines 179-223
- [X] T047 [US3] Write test tests/unit/cli/test_menu.py::test_prompt_update_task_partial_update using mock input
- [X] T048 [US3] Write integration test tests/integration/test_app_flow.py::test_update_task_flow for complete workflow

#### Integration

- [X] T049 [US3] Run all User Story 3 tests: `pytest -k "update" -v`

**Completion Criteria**:
- ✅ All User Story 3 tests passing
- ✅ Can update title only (description and priority unchanged)
- ✅ Can update all fields together
- ✅ Validation enforced (empty title rejected, invalid priority rejected)
- ✅ Error handling for invalid task IDs
- ✅ Combined coverage (US1+US2+US3) ≥75%

**Parallelization**: T041-T043 can run in parallel (independent test cases)

**Dependencies**: Requires create_task (T019) and get_all_tasks (T022) from US1

---

## Phase 6: User Story 4 - Delete Tasks

**User Story**: As a user, I want to delete tasks I no longer need so I can keep my task list clean and relevant.

**Priority**: Medium (Production-Ready)

**Prerequisites**: Phase 3 complete (requires create_task and get_all_tasks)

**Independent Test**: Can delete task by ID. Deleted task no longer appears in list. Task IDs are never reused.

**Acceptance Criteria** (from spec.md:lines 80-82):
1. Task removed from storage permanently
2. Deleted task not present in task list
3. Error message for non-existent task ID

### Tasks

#### Services Layer

- [X] T050 [P] [US4] Write test tests/unit/services/test_task_service.py::test_delete_task_success for successful deletion
- [X] T051 [P] [US4] Write test tests/unit/services/test_task_service.py::test_delete_task_not_found for error handling
- [X] T052 [P] [US4] Write test tests/unit/services/test_task_service.py::test_delete_task_id_not_reused to verify ID monotonicity per data-model.md:lines 56-63
- [X] T053 [US4] Implement delete_task function in src/services/task_service.py per service_contract.md:lines 277-311
- [X] T054 [US4] Run tests: `pytest tests/unit/services/test_task_service.py -k "delete_task" -v`

#### CLI Layer

- [X] T055 [US4] Write test tests/unit/cli/test_menu.py::test_delete_task_menu_flow using mock input
- [X] T056 [US4] Write integration test tests/integration/test_app_flow.py::test_delete_task_flow for complete workflow

#### Integration

- [X] T057 [US4] Run all User Story 4 tests: `pytest -k "delete" -v`

**Completion Criteria**:
- ✅ All User Story 4 tests passing
- ✅ Can delete task by ID
- ✅ Task no longer in list after deletion
- ✅ IDs never reused (next_id never decrements)
- ✅ Error handling for invalid task IDs
- ✅ Combined coverage (US1+US2+US3+US4) ≥80%

**Parallelization**: T050-T052 can run in parallel (independent test cases)

**Dependencies**: Requires create_task (T019) and get_all_tasks (T022) from US1

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Complete main application, add polish, ensure production-ready quality

**Prerequisites**: Phase 3 (MVP) or Phase 6 (Production-Ready) complete

**Independent Test**: Application runs end-to-end, all quality gates pass, documentation complete

### Tasks

#### Main Application

- [X] T058 [P] Implement display_main_menu function in src/cli/menu.py per cli_contract.md:lines 15-43
- [X] T059 [P] Implement get_menu_choice function in src/cli/menu.py per cli_contract.md:lines 47-88
- [X] T0*60 [P] Implement display_success_message and display_error_message functions in src/cli/display.py per cli_contract.md:lines 203-238
- [X] T0*61 Implement main application loop in src/main.py integrating all CLI and service functions
- [X] T0*62 Write test tests/unit/cli/test_menu.py::test_get_menu_choice_validation for menu input validation
- [X] T0*63 Run manual end-to-end test: `python src/main.py` and verify all operations work

#### Code Quality

- [X] T0*64 [P] Run linter and fix PEP8 violations: `ruff check src/ tests/ --fix`
- [X] T0*65 [P] Format all code: `ruff format src/ tests/`
- [X] T0*66 [P] Add Google-style docstrings to all public functions per constitution requirements
- [X] T0*67 [P] Run full test suite with coverage: `pytest --cov=src --cov-report=term-missing` and verify ≥70% for MVP or ≥80% for production-ready
- [X] T0*68 Verify all edge cases from spec.md:lines 88-102 are tested

#### Documentation

- [X] T0*69 Create README.md with setup instructions, usage examples, and running tests per quickstart.md
- [X] T0*70 Document all Claude Code sessions in CLAUDE.md per constitution requirement
- [X] T0*71 Create .gitignore file excluding .venv/, __pycache__/, .pytest_cache/, .coverage, htmlcov/

**Completion Criteria**:
- ✅ Application runs without errors
- ✅ All menu options functional
- ✅ PEP8 compliant (ruff check passes)
- ✅ All functions have docstrings
- ✅ Coverage ≥70% (MVP) or ≥80% (production-ready)
- ✅ README.md complete with setup and usage
- ✅ CLAUDE.md documents all sessions

**Parallelization**: T058-T060, T064-T067 can run in parallel (independent tasks)

---

## Dependency Graph

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (User Story 1) ← REQUIRED FOR MVP
    ↓
    ├─→ Phase 4 (User Story 2) ← REQUIRED FOR MVP
    ├─→ Phase 5 (User Story 3) ← Optional (Production-Ready)
    └─→ Phase 6 (User Story 4) ← Optional (Production-Ready)
    ↓
Phase 7 (Polish)
```

### Dependencies Between User Stories

- **User Story 1** (Create and View): No dependencies (foundational)
- **User Story 2** (Mark Complete): Depends on US1 (needs create_task, get_all_tasks)
- **User Story 3** (Update): Depends on US1 (needs create_task, get_all_tasks)
- **User Story 4** (Delete): Depends on US1 (needs create_task, get_all_tasks)

**Note**: US2, US3, US4 are independent of each other (can be implemented in parallel after US1)

### Critical Path for MVP

```
Setup → Foundational → User Story 1 → User Story 2 → Polish (MVP subset)
```

**MVP Deliverable**: Working CLI with Add, View, and Mark Complete operations (70% coverage)

### Critical Path for Production-Ready

```
Setup → Foundational → User Story 1 → [US2 + US3 + US4 in parallel] → Polish (full)
```

**Production-Ready Deliverable**: All CRUD operations (80% coverage)

---

## Parallel Execution Examples

### Phase 2 (Foundational) - 3 parallel tasks

```bash
# Terminal 1
pytest tests/unit/models/test_task.py -v

# Terminal 2
pytest tests/unit/services/test_task_service.py::test_logging_configured -v

# Terminal 3
pytest tests/unit/cli/test_menu.py -v
```

### Phase 3 (User Story 1) - 4 parallel test writes

```bash
# Can write these tests in parallel (different files)
# T012-T013 (models tests)
# T016-T018 (service tests)
# T020-T021 (service tests)
# T027-T028 (CLI tests)
```

### Phase 4-6 (User Stories 2-4) - After US1 complete

```bash
# These user stories can be implemented in parallel
# Terminal 1: Implement US2 (Mark Complete)
# Terminal 2: Implement US3 (Update)
# Terminal 3: Implement US4 (Delete)
```

---

## Implementation Strategy

### Recommended Approach: MVP-First

1. **Sprint 1** (MVP Core):
   - Phase 1: Setup (T001-T005)
   - Phase 2: Foundational (T006-T011)
   - Phase 3: User Story 1 (T012-T031)
   - Deliverable: Can add and view tasks

2. **Sprint 2** (MVP Complete):
   - Phase 4: User Story 2 (T032-T040)
   - Phase 7: Polish subset (T058-T063, T069-T071)
   - Deliverable: Working CLI with Add, View, Mark Complete

3. **Sprint 3** (Production-Ready):
   - Phase 5: User Story 3 (T041-T049)
   - Phase 6: User Story 4 (T050-T057)
   - Phase 7: Quality (T064-T068)
   - Deliverable: Full CRUD with 80% coverage

### Test-Driven Development (TDD) Workflow

For each task group:
1. Write tests first (RED)
2. Implement minimal code to pass (GREEN)
3. Refactor for quality (REFACTOR)
4. Verify coverage meets threshold
5. Move to next task group

### Incremental Delivery

Each user story phase represents a shippable increment:
- **After US1**: Users can add and view tasks (minimal but valuable)
- **After US2**: Users can track completion (basic task management)
- **After US3**: Users can fix mistakes (improved usability)
- **After US4**: Users can clean up list (full task lifecycle)

---

## Validation Checklist

### Task Format Validation

- ✅ All 71 tasks follow checklist format: `- [ ] [TaskID] [Labels] Description`
- ✅ All task IDs sequential (T001-T071)
- ✅ All user story tasks have [US#] labels
- ✅ All parallelizable tasks marked with [P]
- ✅ All tasks include specific file paths

### Completeness Validation

- ✅ All 4 user stories from spec.md represented
- ✅ All entities from data-model.md covered (Task entity)
- ✅ All 6 service functions from service_contract.md covered
- ✅ All CLI functions from cli_contract.md covered
- ✅ Independent test criteria defined for each phase
- ✅ Dependency graph shows story completion order
- ✅ Parallel execution opportunities identified

### Quality Validation

- ✅ TDD approach: tests written before implementation
- ✅ Coverage targets specified (70% MVP, 80% production)
- ✅ Constitution compliance checked (PEP8, docstrings, logging)
- ✅ MVP scope clearly defined (US1 + US2)
- ✅ Production-ready scope includes all user stories

---

## Quick Reference

### Run All Tests
```bash
pytest --cov=src --cov-report=term-missing
```

### Run Tests for Specific User Story
```bash
pytest -k "US1" -v           # User Story 1
pytest -k "US2" -v           # User Story 2
pytest -k "update" -v        # User Story 3
pytest -k "delete" -v        # User Story 4
```

### Check Code Quality
```bash
ruff check src/ tests/       # Lint
ruff format src/ tests/      # Format
```

### Run Application
```bash
python src/main.py
```

### Coverage by Phase
```bash
pytest --cov=src/models --cov-report=term       # Models layer
pytest --cov=src/services --cov-report=term     # Services layer
pytest --cov=src/cli --cov-report=term          # CLI layer
```

---

**Next Steps**: Run `/sp.implement` to execute these tasks via Claude Code following TDD workflow.
