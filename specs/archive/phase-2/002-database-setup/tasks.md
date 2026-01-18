---
description: "Implementation tasks for Database & Models Setup (Phase II - Stage 1)"
---

# Tasks: Database & Models Setup

**Input**: Design documents from `/specs/002-database-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are explicitly requested in the specification (70%+ coverage requirement, NFR-005). All test tasks included below.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (monorepo)**: `backend/src/`, `backend/tests/`
- This feature creates the `/backend/` directory structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and backend structure

- [X] T001 Create backend directory structure (backend/src/, backend/tests/, backend/tests/unit/)
- [X] T002 Initialize backend pyproject.toml with Python 3.13+ and UV package manager
- [X] T003 [P] Add SQLModel 0.0.22+ dependency to backend/pyproject.toml
- [X] T004 [P] Add psycopg2-binary dependency to backend/pyproject.toml
- [X] T005 [P] Add python-dotenv dependency to backend/pyproject.toml
- [X] T006 [P] Add pytest and pytest-cov dev dependencies to backend/pyproject.toml
- [X] T007 Create backend/.env.example with DATABASE_URL template
- [X] T008 Add backend/.env to .gitignore (if not already present)
- [X] T009 [P] Configure ruff for linting in backend directory

**Checkpoint**: Backend project structure created, dependencies configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Create backend/src/config.py to load DATABASE_URL from .env using python-dotenv
- [X] T011 Add validation in backend/src/config.py to ensure DATABASE_URL is not empty

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Database Connection Established (Priority: P1) 🎯 MVP

**Goal**: Establish reliable connection to Neon PostgreSQL database so backend can store and retrieve task data persistently

**Independent Test**: Run a simple script that connects to the database, creates a test record, reads it back, and verifies the data matches

**Acceptance Scenarios (from spec.md)**:
1. Given DATABASE_URL is configured in .env, When application starts, Then database connection is established successfully
2. Given database connection is active, When connection is tested, Then no errors are raised and connection state is healthy
3. Given invalid DATABASE_URL, When application attempts connection, Then clear error message is displayed with troubleshooting guidance

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Create backend/tests/conftest.py with pytest fixtures for test database engine (SQLite in-memory)
- [X] T013 [P] [US1] Write unit test in backend/tests/unit/test_connection.py to verify successful database connection
- [X] T014 [P] [US1] Write unit test in backend/tests/unit/test_connection.py to verify connection health check
- [X] T015 [P] [US1] Write unit test in backend/tests/unit/test_connection.py to verify error handling for invalid DATABASE_URL

### Implementation for User Story 1

- [X] T016 [US1] Create backend/src/database/connection.py with SQLModel engine creation (pool_size=5, max_overflow=15, pool_pre_ping=True)
- [X] T017 [US1] Add SSL/TLS connection config (sslmode=require) in backend/src/database/connection.py
- [X] T018 [US1] Implement get_session() function in backend/src/database/connection.py to provide database sessions
- [X] T019 [US1] Add connection error handling with clear error messages in backend/src/database/connection.py
- [X] T020 [US1] Run tests for User Story 1 and verify all pass (pytest backend/tests/unit/test_connection.py)

**Checkpoint**: At this point, database connection should be fully functional and testable independently. Tests pass, connection established with proper error handling.

---

## Phase 4: User Story 2 - Task Model Defined (Priority: P1)

**Goal**: Define SQLModel Task model with proper schema so backend can enforce data integrity and type safety for task records

**Independent Test**: Create Task instances with valid/invalid data and verify validation rules work correctly

**Acceptance Scenarios (from spec.md)**:
1. Given Task model is defined, When creating a task with valid data (title, description, user_id), Then task instance is created successfully
2. Given Task model validation rules, When creating a task without required user_id, Then validation error is raised
3. Given Task model with defaults, When creating a new task, Then complete=False, and timestamps are auto-generated

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US2] Write unit test in backend/tests/unit/test_task_model.py to verify Task creation with valid data
- [X] T022 [P] [US2] Write unit test in backend/tests/unit/test_task_model.py to verify user_id is required (reject None/empty)
- [X] T023 [P] [US2] Write unit test in backend/tests/unit/test_task_model.py to verify title is required and max 200 chars
- [X] T024 [P] [US2] Write unit test in backend/tests/unit/test_task_model.py to verify description is optional and max 1000 chars
- [X] T025 [P] [US2] Write unit test in backend/tests/unit/test_task_model.py to verify complete defaults to False
- [X] T026 [P] [US2] Write unit test in backend/tests/unit/test_task_model.py to verify timestamps auto-generate (created_at, updated_at)

### Implementation for User Story 2

- [X] T027 [US2] Create backend/src/models/task.py with Task SQLModel class
- [X] T028 [US2] Define Task fields in backend/src/models/task.py: id (Optional[int], primary_key), user_id (str, indexed, non-null)
- [X] T029 [US2] Define Task fields in backend/src/models/task.py: title (str, max 200 chars, non-null), description (Optional[str], max 1000 chars)
- [X] T030 [US2] Define Task fields in backend/src/models/task.py: complete (bool, default False)
- [X] T031 [US2] Define Task timestamp fields in backend/src/models/task.py: created_at (datetime, auto-generated), updated_at (datetime, auto-updated with onupdate)
- [X] T032 [US2] Add table name __tablename__ = "tasks" to Task model in backend/src/models/task.py
- [X] T033 [US2] Add Pydantic Config with example JSON to Task model in backend/src/models/task.py
- [X] T034 [US2] Run tests for User Story 2 and verify all pass (pytest backend/tests/unit/test_task_model.py)

**Checkpoint**: At this point, Task model should be fully defined with validation rules. Tests pass, model enforces all constraints from data-model.md.

---

## Phase 5: User Story 3 - Database Tables Created (Priority: P1)

**Goal**: Automatically create database tables from models so backend can start storing data without manual SQL scripts

**Independent Test**: Run table creation script and verify table structure matches model schema

**Acceptance Scenarios (from spec.md)**:
1. Given Task model is defined, When migration/init script runs, Then tasks table is created in database
2. Given tasks table exists, When inspecting schema, Then all columns (id, user_id, title, description, complete, created_at, updated_at) are present
3. Given tasks table schema, When checking constraints, Then user_id is indexed and title is NOT NULL

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T035 [P] [US3] Write unit test in backend/tests/unit/test_init_db.py to verify init_db() creates tables successfully
- [X] T036 [P] [US3] Write unit test in backend/tests/unit/test_init_db.py to verify tasks table has all required columns
- [X] T037 [P] [US3] Write unit test in backend/tests/unit/test_init_db.py to verify user_id index exists on tasks table

### Implementation for User Story 3

- [X] T038 [US3] Create backend/src/database/init_db.py with init_db(engine) function
- [X] T039 [US3] Implement SQLModel.metadata.create_all(engine) in init_db() function in backend/src/database/init_db.py
- [X] T040 [US3] Add error handling for table creation failures in backend/src/database/init_db.py
- [X] T041 [US3] Create backend/src/database/__init__.py to export init_db and connection functions
- [X] T042 [US3] Run tests for User Story 3 and verify all pass (pytest backend/tests/unit/test_init_db.py)

**Checkpoint**: At this point, database tables should be auto-created. Tests pass, tasks table created with correct schema.

---

## Phase 6: User Story 4 - CRUD Operations Work (Priority: P1)

**Goal**: Implement basic create/read operations on Task model so backend layer is fully functional and validated end-to-end

**Independent Test**: Write unit tests that create tasks, query them, and verify results

**Acceptance Scenarios (from spec.md)**:
1. Given database connection and Task model, When creating a task programmatically, Then task is saved to database and returns task ID
2. Given task exists in database, When querying by task ID, Then correct task data is retrieved
3. Given multiple tasks for different users, When querying by user_id, Then only that user's tasks are returned

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T043 [P] [US4] Write unit test in backend/tests/unit/test_crud.py to verify create_task() saves task and returns ID
- [X] T044 [P] [US4] Write unit test in backend/tests/unit/test_crud.py to verify get_task_by_id() retrieves correct task
- [X] T045 [P] [US4] Write unit test in backend/tests/unit/test_crud.py to verify get_tasks_by_user() filters by user_id correctly
- [X] T046 [P] [US4] Write unit test in backend/tests/unit/test_crud.py to verify multi-user isolation (user A cannot see user B's tasks)

### Implementation for User Story 4

- [X] T047 [US4] Create backend/src/database/crud.py for CRUD operations
- [X] T048 [US4] Implement create_task(session, user_id, title, description) function in backend/src/database/crud.py
- [X] T049 [US4] Implement get_task_by_id(session, task_id) function in backend/src/database/crud.py
- [X] T050 [US4] Implement get_tasks_by_user(session, user_id) function in backend/src/database/crud.py using SQLModel select()
- [X] T051 [US4] Add error handling for database operations in backend/src/database/crud.py
- [X] T052 [US4] Run tests for User Story 4 and verify all pass (pytest backend/tests/unit/test_crud.py)

**Checkpoint**: At this point, all CRUD operations should work. Tests pass, can create/read tasks with proper multi-user isolation.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final quality checks

- [ ] T053 [P] Create backend/README.md with setup instructions from quickstart.md
- [ ] T054 [P] Document DATABASE_URL environment variable in backend/README.md
- [ ] T055 [P] Add example Neon PostgreSQL setup steps to backend/README.md
- [ ] T056 Run full test suite with coverage (pytest backend/tests/ --cov=backend/src --cov-report=term-missing)
- [ ] T057 Verify 70%+ test coverage requirement (NFR-005) is met
- [ ] T058 Run ruff check on backend/src/ and fix any linting errors
- [ ] T059 Run ruff format on backend/src/ to ensure consistent formatting
- [ ] T060 Validate all 10 acceptance criteria from spec.md are met
- [ ] T061 Run quickstart.md validation (follow guide and verify all steps work)
- [ ] T062 [P] Add __init__.py files to all backend/src/ subdirectories for proper module structure

**Final Checkpoint**: All acceptance criteria met, tests pass with 70%+ coverage, code is PEP8 compliant, README documents setup.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational
  - User Story 2 (Phase 4): Depends on User Story 1 (needs connection established)
  - User Story 3 (Phase 5): Depends on User Story 2 (needs Task model defined)
  - User Story 4 (Phase 6): Depends on User Stories 1-3 (needs connection, model, and tables)
- **Polish (Phase 7)**: Depends on all user stories (Phase 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on User Story 1 (needs database connection to test model)
- **User Story 3 (P1)**: Depends on User Story 2 (needs Task model to create tables)
- **User Story 4 (P1)**: Depends on User Stories 1-3 (needs connection, model, tables for CRUD)

**Note**: All 4 user stories have P1 priority because they form a hierarchical dependency chain. Each builds on the previous.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation tasks follow test creation
- Run tests after implementation to verify all pass
- Story complete before moving to next

### Parallel Opportunities

- **Phase 1 (Setup)**: T003-T006 (add dependencies) can run in parallel, T009 can run in parallel
- **Phase 3 (US1 Tests)**: T012-T015 can all run in parallel (different test files/functions)
- **Phase 4 (US2 Tests)**: T021-T026 can all run in parallel (different test functions)
- **Phase 5 (US3 Tests)**: T035-T037 can all run in parallel (different test functions)
- **Phase 6 (US4 Tests)**: T043-T046 can all run in parallel (different test functions)
- **Phase 7 (Polish)**: T053-T055 (documentation) can run in parallel, T058-T059 can run in parallel, T062 can run in parallel

**Important**: User stories CANNOT run in parallel due to hierarchical dependencies (each story builds on previous).

---

## Parallel Example: User Story 1 (Database Connection)

```bash
# Launch all tests for User Story 1 together:
Task: "Create backend/tests/conftest.py with pytest fixtures"
Task: "Write test to verify successful database connection"
Task: "Write test to verify connection health check"
Task: "Write test to verify error handling for invalid DATABASE_URL"

# After tests written, implement connection module:
Task: "Create backend/src/database/connection.py with engine creation"
# (subsequent implementation tasks run sequentially)
```

---

## Parallel Example: User Story 2 (Task Model)

```bash
# Launch all tests for User Story 2 together:
Task: "Write test to verify Task creation with valid data"
Task: "Write test to verify user_id is required"
Task: "Write test to verify title is required and max 200 chars"
Task: "Write test to verify description is optional and max 1000 chars"
Task: "Write test to verify complete defaults to False"
Task: "Write test to verify timestamps auto-generate"

# After tests written, implement Task model:
Task: "Create backend/src/models/task.py with Task SQLModel class"
# (subsequent field definitions can be done in single task or grouped)
```

---

## Implementation Strategy

### MVP First (All User Stories Sequential - Required Due to Dependencies)

Since all 4 user stories have P1 priority and hierarchical dependencies, they must be completed sequentially:

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Database Connection) → Test independently
4. Complete Phase 4: User Story 2 (Task Model) → Test independently
5. Complete Phase 5: User Story 3 (Database Tables) → Test independently
6. Complete Phase 6: User Story 4 (CRUD Operations) → Test independently
7. **STOP and VALIDATE**: Run full test suite, verify 70%+ coverage
8. Complete Phase 7: Polish (README, validation)

### Validation Checkpoints

After each user story phase:
1. Run tests for that story: `pytest backend/tests/unit/test_[name].py -v`
2. Verify all tests pass
3. Verify independent test criteria from spec.md
4. Only proceed to next story when current story fully validated

After Phase 7 (Polish):
1. Run full test suite: `pytest backend/tests/ --cov=backend/src`
2. Verify 70%+ coverage (NFR-005)
3. Run linting: `ruff check backend/src/`
4. Verify README complete
5. Validate all 10 acceptance criteria from spec.md

---

## Notes

- [P] tasks = different files/functions, can run in parallel
- [Story] label maps task to specific user story (US1, US2, US3, US4)
- Each user story builds on previous (hierarchical dependencies)
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at each checkpoint to validate story independently
- All 4 stories required for Stage 1 completion (all P1 priority)
- Stage 2 (Backend API) will build on this foundation

---

## Task Count Summary

- **Total Tasks**: 62
- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 2 tasks
- **Phase 3 (US1 - Connection)**: 9 tasks (4 tests + 5 implementation)
- **Phase 4 (US2 - Task Model)**: 14 tasks (6 tests + 8 implementation)
- **Phase 5 (US3 - Tables)**: 8 tasks (3 tests + 5 implementation)
- **Phase 6 (US4 - CRUD)**: 10 tasks (4 tests + 6 implementation)
- **Phase 7 (Polish)**: 10 tasks

**Test Coverage**: 17 test tasks ensuring 70%+ coverage requirement

**Parallel Opportunities**: 20 tasks marked [P] can run in parallel within their phases

**MVP Scope**: All 4 user stories (P1 priority, hierarchical dependencies) = Complete Stage 1 foundation
