---
description: "Implementation tasks for Backend API (Phase II - Stage 2)"
---

# Tasks: Backend API

**Input**: Design documents from `/specs/003-backend-api/`
**Prerequisites**: spec.md, plan.md, Stage 1 (Database & Models Setup) complete

**Tests**: Tests are explicitly requested in the specification (70%+ coverage requirement, AC-007). All test tasks included below.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each endpoint.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (monorepo)**: `backend/src/`, `backend/tests/`
- This feature extends the `/backend/` directory structure from Stage 1

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: FastAPI project initialization and dependency installation

- [ ] T001 Add FastAPI 0.115.0+ dependency to backend/pyproject.toml (uv add fastapi>=0.115.0)
- [ ] T002 Add uvicorn[standard] 0.30.0+ dependency to backend/pyproject.toml (uv add "uvicorn[standard]>=0.30.0")
- [ ] T003 Add python-jose[cryptography] 3.3.0+ dependency to backend/pyproject.toml (uv add "python-jose[cryptography]>=3.3.0")
- [ ] T004 Add httpx 0.27.0+ dev dependency to backend/pyproject.toml for API testing (uv add --dev httpx>=0.27.0)
- [ ] T005 Add pytest-asyncio 0.24.0+ dev dependency to backend/pyproject.toml (uv add --dev pytest-asyncio>=0.24.0)
- [ ] T006 Create backend/src/api/ directory for API routes and dependencies
- [ ] T007 Create backend/src/api/routes/ directory for endpoint modules
- [ ] T008 Create backend/src/schemas/ directory for Pydantic request/response models
- [ ] T009 Create backend/src/core/ directory for auth and error handling
- [ ] T010 Create backend/tests/integration/ directory for API endpoint tests
- [ ] T011 Add JWT_SECRET_KEY, JWT_ALGORITHM, BETTER_AUTH_PUBLIC_KEY_URL to backend/.env.example
- [ ] T012 Update backend/.env with JWT configuration (use development secret for testing)

**Checkpoint**: FastAPI dependencies installed, directory structure created, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### T013-T020: Configuration & CRUD Extension

- [ ] T013 Extend backend/src/config.py to load JWT_SECRET_KEY from .env
- [ ] T014 Extend backend/src/config.py to load JWT_ALGORITHM from .env (default: HS256)
- [ ] T015 Extend backend/src/config.py to load BETTER_AUTH_PUBLIC_KEY_URL from .env (optional)
- [ ] T016 Extend backend/src/database/crud.py to add update_task(session, task_id: int, updates: dict) function
- [ ] T017 Extend backend/src/database/crud.py to add delete_task(session, task_id: int) → bool function
- [ ] T018 Write unit test in backend/tests/unit/test_crud.py to verify update_task() modifies task fields correctly
- [ ] T019 Write unit test in backend/tests/unit/test_crud.py to verify update_task() updates updated_at timestamp
- [ ] T020 Write unit test in backend/tests/unit/test_crud.py to verify delete_task() removes task and returns True (or False if not found)

### T021-T028: Pydantic Schemas

- [ ] T021 [P] Create backend/src/schemas/task.py with TaskCreate schema (title: str, description: str | None)
- [ ] T022 [P] Create TaskUpdate schema in backend/src/schemas/task.py (title: str, description: str | None, complete: bool)
- [ ] T023 [P] Create TaskPatch schema in backend/src/schemas/task.py (all fields optional)
- [ ] T024 [P] Create TaskResponse schema in backend/src/schemas/task.py with Config.from_attributes = True for ORM mode
- [ ] T025 [P] Create TaskListResponse schema in backend/src/schemas/task.py (tasks: list[TaskResponse], count: int)
- [ ] T026 [P] Write unit test in backend/tests/unit/test_schemas.py to verify TaskCreate validation (required title, optional description)
- [ ] T027 [P] Write unit test in backend/tests/unit/test_schemas.py to verify TaskCreate rejects title >200 chars
- [ ] T028 [P] Write unit test in backend/tests/unit/test_schemas.py to verify TaskPatch allows partial updates

### T029-T036: Authentication & Authorization

- [ ] T029 Create backend/src/core/auth.py with decode_jwt_token(token: str) → dict function using python-jose
- [ ] T030 Add extract_user_id_from_token(token: str) → str function in backend/src/core/auth.py
- [ ] T031 Create backend/src/api/dependencies.py with get_current_user(authorization: str = Header()) dependency
- [ ] T032 Add verify_user_id_match(current_user: str, path_user_id: str) function in backend/src/api/dependencies.py (raises 403 if mismatch)
- [ ] T033 [P] Write unit test in backend/tests/unit/test_auth.py to verify decode_jwt_token() extracts claims correctly
- [ ] T034 [P] Write unit test in backend/tests/unit/test_auth.py to verify decode_jwt_token() raises exception for invalid/expired token
- [ ] T035 [P] Write unit test in backend/tests/unit/test_auth.py to verify extract_user_id_from_token() returns user_id from claims
- [ ] T036 [P] Write unit test in backend/tests/unit/test_auth.py to verify verify_user_id_match() raises 403 for mismatch

### T037-T041: Error Handling

- [ ] T037 Create backend/src/core/errors.py with custom exceptions (AuthError, ForbiddenError, NotFoundError)
- [ ] T038 Add exception handlers in backend/src/core/errors.py for HTTPException → JSON response
- [ ] T039 Add exception handler in backend/src/core/errors.py for DatabaseError → 500 response
- [ ] T040 Add exception handler in backend/src/core/errors.py for general Exception → 500 with generic message
- [ ] T041 Create backend/src/main.py with FastAPI app instance and register exception handlers

### T042-T044: Test Infrastructure

- [ ] T042 Extend backend/tests/conftest.py with API test client fixture (TestClient from fastapi.testclient)
- [ ] T043 Add mock_jwt_token fixture in backend/tests/conftest.py (creates valid test JWT with user_id claim)
- [ ] T044 Add mock_invalid_token fixture in backend/tests/conftest.py (expired or malformed JWT)

**Checkpoint**: Foundation ready - config extended, CRUD complete, schemas defined, auth logic implemented, error handling configured, test infrastructure ready

---

## Phase 3: User Story 1 - List User's Tasks (Priority: P1) 🎯 MVP

**Goal**: Implement GET /api/{user_id}/tasks endpoint to retrieve all tasks for a user

**Independent Test**: Make authenticated GET request and verify response contains user's tasks

**Acceptance Scenarios (from spec.md)**:
1. Given valid JWT token, When GET /api/{user_id}/tasks, Then return all tasks for that user with 200 OK
2. Given no JWT token, When GET /api/{user_id}/tasks, Then return 401 Unauthorized
3. Given JWT user_id doesn't match path user_id, When GET /api/{user_id}/tasks, Then return 403 Forbidden

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045 [P] [US1] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks with valid token returns 200 and task list
- [ ] T046 [P] [US1] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks without token returns 401
- [ ] T047 [P] [US1] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks with user_id mismatch returns 403
- [ ] T048 [P] [US1] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks with empty task list returns {"tasks": [], "count": 0}

### Implementation for User Story 1

- [ ] T049 [US1] Create backend/src/api/routes/tasks.py with APIRouter instance
- [ ] T050 [US1] Implement GET /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py with get_current_user dependency
- [ ] T051 [US1] Add user_id verification in GET /api/{user_id}/tasks endpoint (call verify_user_id_match)
- [ ] T052 [US1] Query tasks using get_tasks_by_user(session, user_id) from CRUD module
- [ ] T053 [US1] Return TaskListResponse with tasks and count
- [ ] T054 [US1] Register tasks router in backend/src/main.py with app.include_router()
- [ ] T055 [US1] Run tests for User Story 1 and verify all pass (pytest backend/tests/integration/test_api.py::test_list_tasks -v)

**Checkpoint**: GET endpoint functional, returns task list with auth/authorization checks

---

## Phase 4: User Story 2 - Create New Task (Priority: P1)

**Goal**: Implement POST /api/{user_id}/tasks endpoint to create new tasks

**Independent Test**: Make authenticated POST request with valid data and verify task is created

**Acceptance Scenarios (from spec.md)**:
1. Given valid JWT token and valid request body, When POST /api/{user_id}/tasks, Then create task and return 201 Created
2. Given missing title in request body, When POST /api/{user_id}/tasks, Then return 422 Unprocessable Entity
3. Given title >200 chars, When POST /api/{user_id}/tasks, Then return 422 validation error

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T056 [P] [US2] Write integration test in backend/tests/integration/test_api.py: POST /api/{user_id}/tasks with valid data returns 201 and created task
- [ ] T057 [P] [US2] Write integration test in backend/tests/integration/test_api.py: POST /api/{user_id}/tasks without token returns 401
- [ ] T058 [P] [US2] Write integration test in backend/tests/integration/test_api.py: POST /api/{user_id}/tasks with missing title returns 422
- [ ] T059 [P] [US2] Write integration test in backend/tests/integration/test_api.py: POST /api/{user_id}/tasks with title >200 chars returns 422

### Implementation for User Story 2

- [ ] T060 [US2] Implement POST /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [ ] T061 [US2] Add get_current_user dependency to POST endpoint
- [ ] T062 [US2] Add user_id verification in POST endpoint (call verify_user_id_match)
- [ ] T063 [US2] Parse request body as TaskCreate schema (FastAPI automatic validation)
- [ ] T064 [US2] Create task using create_task(session, user_id, title, description) from CRUD module
- [ ] T065 [US2] Return TaskResponse with 201 status code
- [ ] T066 [US2] Run tests for User Story 2 and verify all pass (pytest backend/tests/integration/test_api.py::test_create_task -v)

**Checkpoint**: POST endpoint functional, creates tasks with validation and auth checks

---

## Phase 5: User Story 3 - Retrieve Single Task (Priority: P1)

**Goal**: Implement GET /api/{user_id}/tasks/{task_id} endpoint to retrieve specific task

**Independent Test**: Make authenticated GET request for specific task_id and verify correct task returned

**Acceptance Scenarios (from spec.md)**:
1. Given valid JWT token and existing task_id, When GET /api/{user_id}/tasks/{task_id}, Then return task with 200 OK
2. Given task_id doesn't exist, When GET /api/{user_id}/tasks/{task_id}, Then return 404 Not Found
3. Given task belongs to different user, When GET /api/{user_id}/tasks/{task_id}, Then return 403 Forbidden

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T067 [P] [US3] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks/{task_id} with valid token returns 200 and task
- [ ] T068 [P] [US3] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks/{task_id} for non-existent task returns 404
- [ ] T069 [P] [US3] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks/{task_id} for other user's task returns 403
- [ ] T070 [P] [US3] Write integration test in backend/tests/integration/test_api.py: GET /api/{user_id}/tasks/{task_id} without token returns 401

### Implementation for User Story 3

- [ ] T071 [US3] Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py
- [ ] T072 [US3] Add get_current_user dependency to GET single task endpoint
- [ ] T073 [US3] Add user_id verification in GET single task endpoint
- [ ] T074 [US3] Query task using get_task_by_id(session, task_id) from CRUD module
- [ ] T075 [US3] Raise 404 HTTPException if task is None
- [ ] T076 [US3] Verify task.user_id matches path user_id (raise 403 if mismatch)
- [ ] T077 [US3] Return TaskResponse with 200 status code
- [ ] T078 [US3] Run tests for User Story 3 and verify all pass (pytest backend/tests/integration/test_api.py::test_get_single_task -v)

**Checkpoint**: GET single task endpoint functional with ownership verification

---

## Phase 6: User Story 4 - Update Task (Priority: P1)

**Goal**: Implement PUT and PATCH /api/{user_id}/tasks/{task_id} endpoints for task updates

**Independent Test**: Make authenticated PUT/PATCH requests and verify task is updated

**Acceptance Scenarios (from spec.md)**:
1. Given valid JWT token and PUT request with full data, When PUT /api/{user_id}/tasks/{task_id}, Then update entire task and return 200 OK
2. Given valid JWT token and PATCH request with partial data, When PATCH /api/{user_id}/tasks/{task_id}, Then update specified fields and return 200 OK
3. Given task_id doesn't exist, When PUT/PATCH /api/{user_id}/tasks/{task_id}, Then return 404 Not Found

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T079 [P] [US4] Write integration test in backend/tests/integration/test_api.py: PUT /api/{user_id}/tasks/{task_id} with valid data returns 200 and updated task
- [ ] T080 [P] [US4] Write integration test in backend/tests/integration/test_api.py: PUT /api/{user_id}/tasks/{task_id} for non-existent task returns 404
- [ ] T081 [P] [US4] Write integration test in backend/tests/integration/test_api.py: PATCH /api/{user_id}/tasks/{task_id} with {"complete": true} updates only complete field
- [ ] T082 [P] [US4] Write integration test in backend/tests/integration/test_api.py: PATCH /api/{user_id}/tasks/{task_id} without token returns 401
- [ ] T083 [P] [US4] Write integration test in backend/tests/integration/test_api.py: PATCH /api/{user_id}/tasks/{task_id} for other user's task returns 403

### Implementation for User Story 4

- [ ] T084 [US4] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py
- [ ] T085 [US4] Add get_current_user dependency and user_id verification to PUT endpoint
- [ ] T086 [US4] Parse request body as TaskUpdate schema (full update)
- [ ] T087 [US4] Verify task exists and belongs to user (get_task_by_id + ownership check)
- [ ] T088 [US4] Update task using update_task(session, task_id, updates) from CRUD module
- [ ] T089 [US4] Return updated TaskResponse with 200 status code
- [ ] T090 [US4] Implement PATCH /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py
- [ ] T091 [US4] Add get_current_user dependency and user_id verification to PATCH endpoint
- [ ] T092 [US4] Parse request body as TaskPatch schema (partial update)
- [ ] T093 [US4] Filter out None values from TaskPatch (only update provided fields)
- [ ] T094 [US4] Verify task exists and belongs to user
- [ ] T095 [US4] Update task using update_task(session, task_id, filtered_updates)
- [ ] T096 [US4] Return updated TaskResponse with 200 status code
- [ ] T097 [US4] Run tests for User Story 4 and verify all pass (pytest backend/tests/integration/test_api.py::test_update_task -v)

**Checkpoint**: PUT and PATCH endpoints functional, update tasks with ownership verification

---

## Phase 7: User Story 5 - Delete Task (Priority: P1)

**Goal**: Implement DELETE /api/{user_id}/tasks/{task_id} endpoint to remove tasks

**Independent Test**: Make authenticated DELETE request and verify task is removed

**Acceptance Scenarios (from spec.md)**:
1. Given valid JWT token and existing task_id, When DELETE /api/{user_id}/tasks/{task_id}, Then delete task and return 204 No Content
2. Given task_id doesn't exist, When DELETE /api/{user_id}/tasks/{task_id}, Then return 404 Not Found
3. Given task belongs to different user, When DELETE /api/{user_id}/tasks/{task_id}, Then return 403 Forbidden

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T098 [P] [US5] Write integration test in backend/tests/integration/test_api.py: DELETE /api/{user_id}/tasks/{task_id} with valid token returns 204
- [ ] T099 [P] [US5] Write integration test in backend/tests/integration/test_api.py: DELETE /api/{user_id}/tasks/{task_id} for non-existent task returns 404
- [ ] T100 [P] [US5] Write integration test in backend/tests/integration/test_api.py: DELETE /api/{user_id}/tasks/{task_id} for other user's task returns 403
- [ ] T101 [P] [US5] Write integration test in backend/tests/integration/test_api.py: DELETE /api/{user_id}/tasks/{task_id} without token returns 401

### Implementation for User Story 5

- [ ] T102 [US5] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py
- [ ] T103 [US5] Add get_current_user dependency and user_id verification to DELETE endpoint
- [ ] T104 [US5] Verify task exists and belongs to user (get_task_by_id + ownership check)
- [ ] T105 [US5] Delete task using delete_task(session, task_id) from CRUD module
- [ ] T106 [US5] Return 204 No Content status code (no response body)
- [ ] T107 [US5] Run tests for User Story 5 and verify all pass (pytest backend/tests/integration/test_api.py::test_delete_task -v)

**Checkpoint**: DELETE endpoint functional, removes tasks with ownership verification

---

## Phase 8: User Story 6 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Convenience endpoint for toggling task completion (uses PATCH from US4)

**Independent Test**: Make authenticated PATCH request with {"complete": true/false} and verify status updated

**Note**: This user story is implemented as part of Phase 6 (US4 - PATCH endpoint). No additional implementation needed.

### Tests for User Story 6

- [ ] T108 [P] [US6] Write integration test in backend/tests/integration/test_api.py: PATCH /api/{user_id}/tasks/{task_id} with {"complete": true} marks task complete
- [ ] T109 [P] [US6] Write integration test in backend/tests/integration/test_api.py: PATCH /api/{user_id}/tasks/{task_id} with {"complete": false} marks task incomplete
- [ ] T110 [P] [US6] Write integration test in backend/tests/integration/test_api.py: Verify updated_at timestamp changes after marking complete

**Checkpoint**: Completion toggle tests pass (implementation already covered by PATCH endpoint in Phase 6)

---

## Phase 9: Cross-Cutting Concerns & Documentation

**Purpose**: Health check, OpenAPI docs, CORS, and final quality checks

- [ ] T111 [P] Implement GET /health endpoint in backend/src/main.py (no auth required, checks database connectivity)
- [ ] T112 [P] Configure CORS middleware in backend/src/main.py (allow all origins for dev, specific origins for production)
- [ ] T113 [P] Customize OpenAPI documentation in backend/src/main.py (title, description, version)
- [ ] T114 [P] Add tags to API routes in backend/src/api/routes/tasks.py for OpenAPI grouping
- [ ] T115 [P] Update backend/README.md with API usage examples (curl commands or Python httpx examples)
- [ ] T116 [P] Document JWT token requirements in backend/README.md (how to get token, how to use in Authorization header)
- [ ] T117 [P] Add Swagger UI access instructions to backend/README.md (http://localhost:8000/docs)

**Checkpoint**: Cross-cutting features implemented, documentation updated

---

## Phase 10: Polish & Final Validation

**Purpose**: Testing, linting, coverage verification, and acceptance criteria validation

- [ ] T118 Run full test suite with coverage (pytest backend/tests/ --cov=backend/src --cov-report=term-missing)
- [ ] T119 Verify 70%+ test coverage requirement (AC-007) is met
- [ ] T120 Run ruff check on backend/src/ and fix any linting errors
- [ ] T121 Run ruff format on backend/src/ to ensure consistent formatting
- [ ] T122 Validate all 7 acceptance criteria from spec.md are met (AC-001 through AC-007)
- [ ] T123 Verify OpenAPI documentation accessible at /docs and /redoc
- [ ] T124 Test health check endpoint (/health) returns database status
- [ ] T125 Verify all integration tests pass (pytest backend/tests/integration/ -v)
- [ ] T126 Verify all unit tests pass (pytest backend/tests/unit/ -v)
- [ ] T127 Update CLAUDE.md with Stage 2 completion status and technologies
- [ ] T128 [P] Add __init__.py files to backend/src/api/, backend/src/schemas/, backend/src/core/ if missing

**Final Checkpoint**: All acceptance criteria met, tests pass with 70%+ coverage, code is PEP8 compliant, OpenAPI docs accessible, README documents API usage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Depends on Stage 1 completion - can start immediately after Stage 1
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational
  - User Story 2 (Phase 4): Can start after Foundational (parallel with US1)
  - User Story 3 (Phase 5): Can start after Foundational (parallel with US1, US2)
  - User Story 4 (Phase 6): Can start after Foundational (parallel with US1, US2, US3)
  - User Story 5 (Phase 7): Can start after Foundational (parallel with US1, US2, US3, US4)
  - User Story 6 (Phase 8): Can start after Phase 6 (US4 PATCH endpoint implemented)
- **Cross-Cutting (Phase 9)**: Can run in parallel with user stories (independent features)
- **Polish (Phase 10)**: Depends on all user stories (Phase 3-8) being complete

### User Story Dependencies

**Note**: Unlike Stage 1, Stage 2 user stories are INDEPENDENT and can run in PARALLEL after Foundational phase is complete. Each endpoint is self-contained.

- **User Story 1 (P1)**: List tasks - Independent, can start after Foundational
- **User Story 2 (P1)**: Create task - Independent, can start after Foundational
- **User Story 3 (P1)**: Get single task - Independent, can start after Foundational
- **User Story 4 (P1)**: Update task - Independent, can start after Foundational
- **User Story 5 (P1)**: Delete task - Independent, can start after Foundational
- **User Story 6 (P2)**: Toggle complete - Depends on User Story 4 (uses PATCH endpoint)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation tasks follow test creation
- Run tests after implementation to verify all pass
- Story complete before moving to next (or run in parallel if independent)

### Parallel Opportunities

- **Phase 1 (Setup)**: T001-T005 (add dependencies) can run sequentially with uv add
- **Phase 2 (Foundational)**:
  - T013-T015 (config updates) can run in parallel
  - T021-T025 (schema creation) can run in parallel
  - T026-T028 (schema tests) can run in parallel
  - T033-T036 (auth tests) can run in parallel
- **Phase 3-7 (User Stories)**: All user stories US1-US5 can run in PARALLEL after Foundational phase
- **Phase 9 (Cross-Cutting)**: T111-T117 can all run in parallel (independent features)
- **Phase 10 (Polish)**: T120-T121 (linting/formatting) can run in parallel, T128 can run in parallel

**Critical Path**: Setup → Foundational → User Stories (parallel) → Polish

---

## Parallel Example: After Foundational Phase

```bash
# All user stories can be implemented in parallel after Foundational:
Team Member 1: Implement User Story 1 (GET /api/{user_id}/tasks)
Team Member 2: Implement User Story 2 (POST /api/{user_id}/tasks)
Team Member 3: Implement User Story 3 (GET /api/{user_id}/tasks/{task_id})
Team Member 4: Implement User Story 4 (PUT/PATCH /api/{user_id}/tasks/{task_id})
Team Member 5: Implement User Story 5 (DELETE /api/{user_id}/tasks/{task_id})

# Or, for solo developer, implement in sequence or grouped by HTTP method:
# Group 1: GET endpoints (US1, US3)
# Group 2: POST endpoint (US2)
# Group 3: PUT/PATCH endpoints (US4)
# Group 4: DELETE endpoint (US5)
```

---

## Implementation Strategy

### Recommended Approach (Solo Developer)

1. **Complete Phase 1: Setup** (install dependencies, create directories)
2. **Complete Phase 2: Foundational** (CRITICAL - blocks all stories)
   - Extend config for JWT settings
   - Extend CRUD with update/delete operations
   - Create all Pydantic schemas
   - Implement auth logic and dependencies
   - Set up error handling and test infrastructure
3. **Implement User Stories in Groups** (after Foundational):
   - **Group 1 (READ)**: US1 (list tasks) + US3 (get single task) → Test independently
   - **Group 2 (CREATE)**: US2 (create task) → Test independently
   - **Group 3 (UPDATE)**: US4 (update task - PUT/PATCH) → Test independently
   - **Group 4 (DELETE)**: US5 (delete task) → Test independently
   - **Group 5 (CONVENIENCE)**: US6 (toggle complete - reuses US4 PATCH) → Test independently
4. **Complete Phase 9: Cross-Cutting** (health check, CORS, OpenAPI customization)
5. **STOP and VALIDATE**: Run full test suite, verify 70%+ coverage
6. **Complete Phase 10: Polish** (README, documentation, validation)

### Validation Checkpoints

After each user story group:
1. Run integration tests for that group: `pytest backend/tests/integration/test_api.py::test_[name] -v`
2. Verify all tests pass for implemented endpoints
3. Manually test endpoint using curl or Swagger UI at `/docs`

After Phase 10 (Polish):
1. Run full test suite: `pytest backend/tests/ --cov=backend/src --cov-report=term-missing`
2. Verify 70%+ coverage (AC-007)
3. Run linting: `ruff check backend/src/`
4. Verify OpenAPI docs accessible at `/docs`
5. Validate all 7 acceptance criteria from spec.md

---

## Notes

- [P] tasks = different files/functions, can run in parallel
- [Story] label maps task to specific user story (US1-US6)
- User stories are INDEPENDENT (unlike Stage 1) - can run in parallel after Foundational phase
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at each checkpoint to validate story independently
- All 6 user stories required for Stage 2 completion (US1-US5 are P1, US6 is P2)
- Stage 3 (Frontend Integration) will consume this API

---

## Task Count Summary

- **Total Tasks**: 128
- **Phase 1 (Setup)**: 12 tasks
- **Phase 2 (Foundational)**: 32 tasks (4 config + 3 CRUD + 3 tests + 8 schemas + 8 auth + 4 errors + 2 main.py)
- **Phase 3 (US1 - List Tasks)**: 11 tasks (4 tests + 7 implementation)
- **Phase 4 (US2 - Create Task)**: 11 tasks (4 tests + 7 implementation)
- **Phase 5 (US3 - Get Single Task)**: 12 tasks (4 tests + 8 implementation)
- **Phase 6 (US4 - Update Task)**: 19 tasks (5 tests + 14 implementation for PUT + PATCH)
- **Phase 7 (US5 - Delete Task)**: 10 tasks (4 tests + 6 implementation)
- **Phase 8 (US6 - Toggle Complete)**: 3 tasks (3 tests, implementation covered by US4 PATCH)
- **Phase 9 (Cross-Cutting)**: 7 tasks (health check, CORS, OpenAPI, docs)
- **Phase 10 (Polish)**: 11 tasks (testing, linting, validation)

**Test Coverage**:
- Unit tests: 11 tasks (schema validation, auth logic, CRUD extension)
- Integration tests: 24 tasks (all 6 endpoints with auth/error scenarios)
- Total: 35 test tasks ensuring 70%+ coverage requirement

**Parallel Opportunities**: ~40 tasks marked [P] can run in parallel within their phases

**MVP Scope**: All 6 user stories (US1-US6) = Complete Stage 2 API layer

---

## Start Command

**Development Server**:
```bash
# From backend/ directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Swagger UI**:
```
http://localhost:8000/docs
```

**Run Tests**:
```bash
# All tests with coverage
pytest --cov=src --cov-report=term-missing

# Integration tests only
pytest tests/integration/ -v

# Specific endpoint tests
pytest tests/integration/test_api.py::test_list_tasks -v
```
