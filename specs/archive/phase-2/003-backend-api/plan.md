# Implementation Plan: Backend API (Phase II - Stage 2)

**Branch**: `003-backend-api` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-backend-api/spec.md`

**Note**: This plan builds on Stage 1 (Database & Models Setup) - `002-database-setup`.

## Summary

Implement RESTful API layer using FastAPI to expose CRUD operations for task management. This stage adds HTTP endpoints with JWT authentication, request/response validation via Pydantic schemas, proper error handling, and OpenAPI documentation. Technical approach extends Stage 1's database foundation with 6 REST endpoints (GET/POST/PUT/PATCH/DELETE), Better Auth JWT integration for authentication/authorization, and comprehensive integration tests (70%+ coverage maintained).

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI 0.115.0+, Uvicorn 0.30.0+, python-jose[cryptography] 3.3.0+, httpx 0.27.0+ (testing)
**Authentication**: Better Auth + JWT Bearer tokens
**Database**: Neon PostgreSQL (reused from Stage 1), SQLModel ORM (reused from Stage 1)
**Testing**: pytest with 70%+ minimum coverage, pytest-asyncio for async tests
**Target Platform**: ASGI web server (Uvicorn) on Linux
**Project Type**: Web application backend (REST API component of monorepo)
**Performance Goals**: p95 response time <200ms, 100 requests/second per user throughput
**Constraints**: JWT required for all endpoints, user isolation enforced, HTTPS in production, no SQL injection (SQLModel ORM)
**Scale/Scope**: Stage 2 of 5-stage implementation hierarchy (depends on Stage 1, enables Stage 3 frontend)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity First ✅
- **Check**: No unnecessary abstractions or over-engineering
- **Status**: PASS - Using FastAPI's dependency injection for auth, direct CRUD operations, no service layer or complex patterns
- **Justification**: API layer focused on HTTP routing + validation, business logic stays minimal (CRUD only), authentication delegated to Better Auth

### Principle II: Testing is Non-Negotiable ✅
- **Check**: 70%+ test coverage for all code
- **Status**: PASS - Spec requires 70%+ coverage with integration tests for all 6 endpoints + unit tests for schemas/auth
- **Acceptance Criteria**: AC-007 explicitly measures test coverage ≥70%

### Principle IV: Code Quality ✅
- **Check**: PEP8 compliance, ruff linting, type hints
- **Status**: PASS - FastAPI enforces type hints, spec requires `ruff check` to pass (Success Metrics)
- **Acceptance Criteria**: Definition of Done includes "All ruff checks passing"

### Principle VIII: Gradual Feature Implementation ✅
- **Check**: Features built in logical, hierarchical order with independent validation
- **Status**: PASS - This is Stage 2 (API) of 5-stage hierarchy, builds on Stage 1 database, enables Stage 3 frontend
- **Dependencies**: Requires Stage 1 (Database & Models Setup - COMPLETE ✅)

### Phase II Technology Stack ✅
- **Check**: Python 3.13+, FastAPI, Better Auth JWT
- **Status**: PASS - FastAPI 0.115.0+ specified in dependencies, JWT authentication required
- **Alignment**: Matches Phase II Stage 2 requirements from hackathon specification

### Monorepo Structure ✅
- **Check**: Backend code in `/backend/` directory
- **Status**: PASS - Extends existing `/backend/` structure from Stage 1
- **Project Type**: Web application (Stage 2 adds API layer to Stage 1 database)

**GATE RESULT: PASS** - No constitution violations. All principles and Phase II requirements satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-api/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-endpoints.md # REST API endpoint specifications
│   └── auth-flow.md     # JWT authentication flow
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/                      # NEW in Stage 2
│   │   ├── __init__.py
│   │   ├── dependencies.py       # JWT validation, get_current_user dependency
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py          # Task CRUD endpoints (6 routes)
│   ├── schemas/                  # NEW in Stage 2
│   │   ├── __init__.py
│   │   └── task.py               # Pydantic models: TaskCreate, TaskUpdate, TaskPatch, TaskResponse, TaskListResponse
│   ├── core/                     # NEW in Stage 2
│   │   ├── __init__.py
│   │   ├── auth.py               # JWT validation logic (decode_token, verify_user_id)
│   │   └── errors.py             # Custom exceptions, exception handlers
│   ├── database/                 # EXTENDED from Stage 1
│   │   ├── __init__.py
│   │   ├── connection.py         # (unchanged from Stage 1)
│   │   ├── init_db.py            # (unchanged from Stage 1)
│   │   └── crud.py               # EXTENDED: add update_task, delete_task functions
│   ├── models/                   # REUSED from Stage 1
│   │   ├── __init__.py
│   │   └── task.py               # (unchanged from Stage 1)
│   ├── config.py                 # EXTENDED: add JWT_SECRET_KEY, JWT_ALGORITHM, BETTER_AUTH_PUBLIC_KEY_URL
│   └── main.py                   # NEW: FastAPI app, router registration, CORS, exception handlers
├── tests/
│   ├── unit/
│   │   ├── test_task_model.py    # (unchanged from Stage 1)
│   │   ├── test_connection.py    # (unchanged from Stage 1)
│   │   ├── test_init_db.py       # (unchanged from Stage 1)
│   │   ├── test_crud.py          # EXTENDED: add test_update_task, test_delete_task
│   │   ├── test_schemas.py       # NEW: Pydantic schema validation tests
│   │   └── test_auth.py          # NEW: JWT validation unit tests
│   ├── integration/              # NEW directory in Stage 2
│   │   └── test_api.py           # API endpoint integration tests (auth, CRUD, errors)
│   └── conftest.py               # EXTENDED: add API test client fixtures, mock JWT tokens
├── .env                          # EXTENDED: add JWT_SECRET_KEY, JWT_ALGORITHM, BETTER_AUTH_PUBLIC_KEY_URL
├── .env.example                  # EXTENDED: add JWT config examples
├── pyproject.toml                # EXTENDED: add FastAPI, uvicorn, python-jose, httpx, pytest-asyncio
└── README.md                     # EXTENDED: add API usage examples, endpoint documentation

src/                              # Phase I CLI code (unchanged)
frontend/                         # Stage 3 will create this (NOT in this stage)
```

**Structure Decision**: Web application monorepo structure. This stage (Stage 2) extends the existing `/backend/` directory from Stage 1 by adding FastAPI application, API routes, Pydantic schemas, and auth logic. Stage 1's database models and connection remain unchanged.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**N/A** - Constitution Check passed with no violations. All complexity is justified by Phase II requirements and follows Principle I (Simplicity First).

---

## Phase 0: Research Summary

**Status**: ⏳ In Progress

### Key Questions to Resolve

1. **FastAPI Dependency Injection for JWT**:
   - How to implement reusable `get_current_user` dependency?
   - What's the best practice for extracting user_id from JWT claims?
   - How to handle 401/403 errors in dependencies?

2. **Better Auth Integration**:
   - JWT token structure (claims: sub, user_id, exp)?
   - Public key retrieval for signature validation?
   - Mock JWT tokens for development/testing?

3. **Pydantic Schema Design**:
   - Separate schemas for request (TaskCreate, TaskUpdate, TaskPatch) vs response (TaskResponse)?
   - `from_attributes = True` for SQLModel to Pydantic conversion?
   - Optional fields in TaskPatch (partial updates)?

4. **Error Handling**:
   - FastAPI exception handlers for 401/403/404/500?
   - Custom HTTPException subclasses or use built-in?
   - Error response format (detail, error_code, timestamp)?

5. **Testing Strategy**:
   - `TestClient` from `httpx` for integration tests?
   - Mock JWT tokens in conftest.py?
   - Separate test database or reuse in-memory SQLite from Stage 1?

6. **CRUD Extension**:
   - `update_task(session, task_id, updates)` signature?
   - `delete_task(session, task_id)` return value?
   - Handling non-existent tasks (raise exception or return None)?

### Decisions to Document in research.md

- JWT validation library choice (python-jose vs PyJWT)
- OpenAPI documentation customization
- CORS configuration for frontend integration
- Health check endpoint design
- Production deployment considerations (Uvicorn workers, reverse proxy)

---

## Phase 1: Design Summary

**Status**: ⏳ Pending (after Phase 0)

### Artifacts to Create

1. **contracts/api-endpoints.md**:
   - Full OpenAPI-style specification for all 6 endpoints
   - Request/response examples
   - Error response examples

2. **contracts/auth-flow.md**:
   - JWT authentication flow diagram
   - Token validation logic
   - Authorization checks (user_id matching)

3. **Update quickstart.md** (or create new API-quickstart.md):
   - How to run FastAPI dev server
   - How to test endpoints with curl/httpx
   - How to view Swagger docs at `/docs`

4. **Update CLAUDE.md**:
   - Add FastAPI, uvicorn, python-jose to Active Technologies
   - Document Stage 2 completion

### Design Decisions to Make

- **API Versioning**: Include `/api/v1/` prefix or just `/api/`? (Recommendation: `/api/` for MVP, defer versioning)
- **Pagination**: Implement now or defer? (Recommendation: defer to enhancement, not required in spec)
- **Rate Limiting**: Include or defer? (Recommendation: defer to production enhancement)
- **CORS Policy**: Allow all origins in dev, specific origins in production
- **Health Check**: `/health` or `/api/health`? (Recommendation: `/health` for monitoring tools)

---

## Post-Design Constitution Check

*GATE: Re-check after Phase 1 design (required by plan template)*

**Status**: ⏳ Pending (will be filled after Phase 1 design)

### Principle I: Simplicity First
- **Re-check**: Design uses minimal abstractions
- **Status**: TBD after design
- **Evidence**: Count of API files, dependency injection patterns, error handling layers

### Principle II: Testing is Non-Negotiable
- **Re-check**: Test strategy covers all components
- **Status**: TBD after design
- **Evidence**: Integration test coverage for all 6 endpoints, unit test coverage for schemas/auth

### Principle IV: Code Quality
- **Re-check**: Design enforces type safety and linting
- **Status**: TBD after design
- **Evidence**: Type hints in FastAPI routes, ruff configuration

### Principle VIII: Gradual Feature Implementation
- **Re-check**: Stage 2 is independently testable and functional
- **Status**: TBD after design
- **Evidence**: API endpoints testable via curl/httpx, deferred frontend to Stage 3

### Phase II Technology Stack
- **Re-check**: All specified technologies used
- **Status**: TBD after design
- **Evidence**: Dependencies match hackathon specification

### Monorepo Structure
- **Re-check**: Backend code organized per constitution
- **Status**: TBD after design
- **Evidence**: `/backend/src/api/` structure follows conventions

**FINAL GATE RESULT**: ⏳ Pending

---

## Planning Status

**Branch**: `003-backend-api`
**Implementation Plan**: `/mnt/e/projects/hackathon-todo/specs/003-backend-api/plan.md` (this file)

**Generated Artifacts**:
- ✅ spec.md - Feature specification (created)
- ✅ plan.md (this file) - Architecture and structure
- ⏳ research.md - Technical decisions and rationale (pending)
- ⏳ contracts/api-endpoints.md - REST API endpoint specifications (pending)
- ⏳ contracts/auth-flow.md - JWT authentication flow (pending)
- ⏳ quickstart.md or API setup guide (pending)
- ⏳ CLAUDE.md update - Agent context (pending)

**Next Steps**:
1. Complete Phase 0 (Research) - Investigate FastAPI patterns, JWT validation, testing strategies
2. Complete Phase 1 (Design) - Create contracts, update quickstart, finalize design decisions
3. Run `/sp.tasks` to generate actionable implementation tasks from this plan

**Estimated Implementation Time**: 3-4 hours
- Extend config.py and CRUD module: 30 min
- Implement Pydantic schemas: 30 min
- Implement JWT auth logic: 45 min
- Implement 6 API endpoints: 90 min
- Write integration tests: 60 min
- Documentation and polish: 30 min

---

## Dependencies

### Blocked By (Must Complete First)
- ✅ Stage 1: Database & Models Setup (`002-database-setup`) - COMPLETE

### Blocks (Cannot Start Until This Completes)
- ⏳ Stage 3: Frontend Integration (Next.js + TailwindCSS)
- ⏳ Stage 4: User Authentication (Better Auth full integration)
- ⏳ Stage 5: AI Chat Features (Claude API integration)

### Parallel Work (Can Proceed Independently)
- None - Stage 2 is on critical path

---

## Risks and Mitigations

### Risk 1: Better Auth Integration Complexity
**Impact**: Medium - May delay authentication implementation
**Probability**: Medium (external dependency, documentation may be incomplete)
**Mitigation**:
- Start with mock JWT validation using `python-jose` (dev mode)
- Create test JWT tokens in conftest.py for integration tests
- Document Better Auth integration separately for Stage 4 refinement
- Use HS256 algorithm for development, defer RS256 (public key) to production

### Risk 2: Test Coverage Below 70%
**Impact**: High - Blocks Stage 2 completion per acceptance criteria
**Probability**: Low (Stage 1 achieved 82% coverage)
**Mitigation**:
- Write integration tests alongside endpoint implementation (TDD approach)
- Focus on critical paths: auth (401/403), CRUD operations, error handling
- Use `pytest --cov` reports to identify coverage gaps before completion

### Risk 3: JWT Token Validation Performance
**Impact**: Low - May increase response time
**Probability**: Low (JWT validation is fast <10ms)
**Mitigation**:
- Cache public key for Better Auth signature validation
- Use FastAPI's dependency injection for efficient auth checks
- Measure p95 latency in integration tests, alert if >200ms

### Risk 4: Database Connection Issues
**Impact**: Medium - API requests fail if database unreachable
**Probability**: Low (Stage 1 connection stable, 17/17 tests passing)
**Mitigation**:
- Reuse proven connection pooling from Stage 1 (`get_engine()`)
- Add health check endpoint `/health` to monitor database connectivity
- Implement proper error handling for database failures (500 with retry-after)

### Risk 5: Pydantic Validation Errors
**Impact**: Low - 422 errors returned to client
**Probability**: Low (Pydantic well-documented, widely used)
**Mitigation**:
- Write unit tests for schema validation (valid/invalid inputs)
- Use FastAPI's automatic 422 handling for Pydantic errors
- Test boundary cases: max length strings, missing required fields

---

## Success Metrics

- ✅ 6 RESTful endpoints implemented and tested
- ✅ JWT authentication integrated (mock tokens for dev)
- ✅ 70%+ test coverage maintained
- ✅ All integration tests passing (100% endpoint coverage)
- ✅ OpenAPI documentation accessible at `/docs`
- ✅ No ruff linting errors
- ✅ All code formatted with ruff
- ✅ CRUD module extended with update/delete operations
- ✅ p95 response time <200ms (measured in integration tests)

---

## Out of Scope (Deferred)

- ❌ User registration/login endpoints (Stage 4: Better Auth full integration)
- ❌ Frontend Next.js application (Stage 3)
- ❌ AI chat features (Stage 5)
- ❌ Pagination for task lists (enhancement, not required by spec)
- ❌ Task filtering by date/status/priority (enhancement)
- ❌ Rate limiting (production enhancement)
- ❌ Comprehensive production monitoring/alerting (production enhancement)
- ❌ Database migrations (Alembic) - using `create_all()` for now
- ❌ API versioning (`/api/v1/`) - using `/api/` for MVP

---

## Definition of Done

- [ ] Phase 0 (Research) complete: All technical questions resolved
- [ ] Phase 1 (Design) complete: All design artifacts created
- [ ] All 6 REST endpoints implemented (`/api/{user_id}/tasks` CRUD)
- [ ] Pydantic request/response schemas defined (TaskCreate, TaskUpdate, TaskPatch, TaskResponse, TaskListResponse)
- [ ] JWT authentication middleware functional (mock tokens for dev)
- [ ] Authorization checks enforce user isolation (user_id match between JWT and path)
- [ ] Error handling with proper HTTP status codes (401, 403, 404, 422, 500)
- [ ] Integration tests for all endpoints (100% endpoint coverage)
- [ ] Unit tests for schemas and auth logic
- [ ] Test coverage ≥ 70%
- [ ] OpenAPI documentation accessible at `/docs`
- [ ] README updated with API usage examples
- [ ] All ruff checks passing (`ruff check src/`)
- [ ] Code formatted with ruff (`ruff format src/`)
- [ ] CRUD module extended with `update_task()`, `delete_task()` functions
- [ ] Health check endpoint `/health` implemented
- [ ] All tests passing (unit + integration)
- [ ] Changes committed to git with descriptive messages
- [ ] CLAUDE.md updated with Stage 2 technologies

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Better Auth Documentation](https://www.better-auth.com/)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- Phase II Hackathon Specification (PDF pages 7-8)
- Stage 1 Specification: `specs/002-database-setup/spec.md`
- Stage 1 Implementation Plan: `specs/002-database-setup/plan.md`

---

**Next Stage**: Stage 3 - Frontend Integration (Next.js + TailwindCSS)
**Previous Stage**: Stage 1 - Database & Models Setup (`002-database-setup`) ✅
