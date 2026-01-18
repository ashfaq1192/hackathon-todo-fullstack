# Stage 2: Backend API Specification

**Feature**: RESTful API for Todo CRUD Operations
**Stage**: 2 of 5 (Phase II: Backend Development)
**Branch**: `003-backend-api`
**Status**: Planning
**Created**: 2025-12-20

---

## Overview

Implement a FastAPI-based REST API to expose CRUD operations for the todo application. This stage builds on Stage 1's database foundation to provide HTTP endpoints for task management with proper authentication, validation, and error handling.

### Context
- **Depends On**: Stage 1 (Database & Models Setup) - `002-database-setup` ✅
- **Enables**: Stage 3 (Frontend Integration), Stage 4 (User Auth), Stage 5 (AI Features)
- **Technology Stack**:
  - FastAPI 0.115.0+ (web framework)
  - Better Auth + JWT (authentication)
  - Pydantic 2.0+ (validation)
  - SQLModel (ORM - reused from Stage 1)
  - Neon PostgreSQL (database - reused from Stage 1)

### Success Criteria
- ✅ All 6 RESTful endpoints implemented and tested
- ✅ JWT authentication integrated with Better Auth
- ✅ Request/response validation with Pydantic schemas
- ✅ Comprehensive error handling with proper HTTP status codes
- ✅ OpenAPI/Swagger documentation auto-generated
- ✅ 70%+ test coverage maintained
- ✅ All integration tests passing

---

## User Stories

### US-1: List User's Tasks
**As a** todo application user
**I want to** retrieve all my tasks via API
**So that** I can view my todo list in any client application

**Acceptance Criteria**:
- GET `/api/{user_id}/tasks` returns all tasks for the user
- Response includes task id, title, description, complete status, timestamps
- Empty list returned for users with no tasks
- 401 Unauthorized if JWT token is missing/invalid
- 403 Forbidden if user_id doesn't match JWT token

### US-2: Create New Task
**As a** todo application user
**I want to** create a new task via API
**So that** I can add todos from any client

**Acceptance Criteria**:
- POST `/api/{user_id}/tasks` creates a new task
- Request body requires: `title` (1-200 chars), optional `description` (max 1000 chars)
- Response returns created task with auto-generated id and timestamps
- 400 Bad Request for invalid data (missing title, too long, etc.)
- 401 Unauthorized if JWT token is missing/invalid
- 403 Forbidden if user_id doesn't match JWT token

### US-3: Retrieve Single Task
**As a** todo application user
**I want to** retrieve a specific task by ID via API
**So that** I can view task details

**Acceptance Criteria**:
- GET `/api/{user_id}/tasks/{task_id}` returns single task
- 404 Not Found if task doesn't exist
- 403 Forbidden if task belongs to different user
- 401 Unauthorized if JWT token is missing/invalid

### US-4: Update Task
**As a** todo application user
**I want to** update task details via API
**So that** I can modify title, description, or completion status

**Acceptance Criteria**:
- PUT `/api/{user_id}/tasks/{task_id}` replaces entire task (full update)
- PATCH `/api/{user_id}/tasks/{task_id}` updates specific fields (partial update)
- Request validates field constraints (title length, etc.)
- `updated_at` timestamp auto-updated on modification
- 404 Not Found if task doesn't exist
- 403 Forbidden if task belongs to different user
- 400 Bad Request for validation errors
- 401 Unauthorized if JWT token is missing/invalid

### US-5: Delete Task
**As a** todo application user
**I want to** delete a task via API
**So that** I can remove completed or unwanted todos

**Acceptance Criteria**:
- DELETE `/api/{user_id}/tasks/{task_id}` removes task
- 204 No Content on successful deletion
- 404 Not Found if task doesn't exist
- 403 Forbidden if task belongs to different user
- 401 Unauthorized if JWT token is missing/invalid

### US-6: Mark Task Complete/Incomplete
**As a** todo application user
**I want to** toggle task completion status via API
**So that** I can mark tasks as done or reopen them

**Acceptance Criteria**:
- PATCH `/api/{user_id}/tasks/{task_id}` with `{"complete": true/false}` toggles status
- Response returns updated task
- `updated_at` timestamp auto-updated
- 404 Not Found if task doesn't exist
- 403 Forbidden if task belongs to different user
- 401 Unauthorized if JWT token is missing/invalid

---

## API Endpoint Specifications

### Base URL
```
Development: http://localhost:8000
Production: https://api.hackathon-todo.com
```

### Authentication
All endpoints require JWT Bearer token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

Token must contain `user_id` claim matching the `{user_id}` path parameter.

### Common Response Codes
| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | user_id mismatch (accessing other user's tasks) |
| 404 | Not Found | Task doesn't exist |
| 422 | Unprocessable Entity | Pydantic validation error |
| 500 | Internal Server Error | Database error, unexpected failure |

---

### Endpoint 1: List Tasks

**Route**: `GET /api/{user_id}/tasks`
**Auth**: Required (JWT)
**Description**: Retrieve all tasks for a user

**Path Parameters**:
```json
{
  "user_id": "string (required) - User identifier from JWT token"
}
```

**Query Parameters** (Optional - Future Enhancement):
```json
{
  "complete": "boolean - Filter by completion status",
  "limit": "integer - Max tasks to return (default: 100)",
  "offset": "integer - Pagination offset (default: 0)"
}
```

**Response 200**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user_abc123",
      "title": "Complete Phase II Stage 2",
      "description": "Implement FastAPI REST API",
      "complete": false,
      "created_at": "2025-12-20T10:30:00Z",
      "updated_at": "2025-12-20T10:30:00Z"
    }
  ],
  "count": 1
}
```

**Response 401**:
```json
{
  "detail": "Missing or invalid JWT token"
}
```

**Response 403**:
```json
{
  "detail": "Access denied: user_id mismatch"
}
```

---

### Endpoint 2: Create Task

**Route**: `POST /api/{user_id}/tasks`
**Auth**: Required (JWT)
**Description**: Create a new task

**Path Parameters**:
```json
{
  "user_id": "string (required) - User identifier from JWT token"
}
```

**Request Body**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)"
}
```

**Response 201**:
```json
{
  "id": 2,
  "user_id": "user_abc123",
  "title": "New Task",
  "description": "Task description",
  "complete": false,
  "created_at": "2025-12-20T11:00:00Z",
  "updated_at": "2025-12-20T11:00:00Z"
}
```

**Response 400**:
```json
{
  "detail": "Validation error: title is required"
}
```

**Response 422**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

---

### Endpoint 3: Get Single Task

**Route**: `GET /api/{user_id}/tasks/{task_id}`
**Auth**: Required (JWT)
**Description**: Retrieve a specific task

**Path Parameters**:
```json
{
  "user_id": "string (required) - User identifier from JWT token",
  "task_id": "integer (required) - Task ID"
}
```

**Response 200**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete Phase II Stage 2",
  "description": "Implement FastAPI REST API",
  "complete": false,
  "created_at": "2025-12-20T10:30:00Z",
  "updated_at": "2025-12-20T10:30:00Z"
}
```

**Response 404**:
```json
{
  "detail": "Task not found"
}
```

**Response 403**:
```json
{
  "detail": "Access denied: task belongs to different user"
}
```

---

### Endpoint 4: Update Task (Full)

**Route**: `PUT /api/{user_id}/tasks/{task_id}`
**Auth**: Required (JWT)
**Description**: Replace entire task (full update)

**Path Parameters**:
```json
{
  "user_id": "string (required) - User identifier from JWT token",
  "task_id": "integer (required) - Task ID"
}
```

**Request Body**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "complete": "boolean (required)"
}
```

**Response 200**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Updated Task",
  "description": "Updated description",
  "complete": true,
  "created_at": "2025-12-20T10:30:00Z",
  "updated_at": "2025-12-20T11:15:00Z"
}
```

---

### Endpoint 5: Update Task (Partial)

**Route**: `PATCH /api/{user_id}/tasks/{task_id}`
**Auth**: Required (JWT)
**Description**: Update specific fields (partial update)

**Path Parameters**:
```json
{
  "user_id": "string (required) - User identifier from JWT token",
  "task_id": "integer (required) - Task ID"
}
```

**Request Body** (all fields optional):
```json
{
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "complete": "boolean (optional)"
}
```

**Response 200**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete Phase II Stage 2",
  "description": "Implement FastAPI REST API",
  "complete": true,
  "created_at": "2025-12-20T10:30:00Z",
  "updated_at": "2025-12-20T11:20:00Z"
}
```

**Response 400**:
```json
{
  "detail": "At least one field must be provided for update"
}
```

---

### Endpoint 6: Delete Task

**Route**: `DELETE /api/{user_id}/tasks/{task_id}`
**Auth**: Required (JWT)
**Description**: Delete a task

**Path Parameters**:
```json
{
  "user_id": "string (required) - User identifier from JWT token",
  "task_id": "integer (required) - Task ID"
}
```

**Response 204**: No Content (successful deletion)

**Response 404**:
```json
{
  "detail": "Task not found"
}
```

---

## Pydantic Schemas

### TaskCreate (Request)
```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
```

### TaskUpdate (Request - Full)
```python
class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    complete: bool
```

### TaskPatch (Request - Partial)
```python
class TaskPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    complete: bool | None = None
```

### TaskResponse (Response)
```python
from datetime import datetime

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    complete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel conversion
```

### TaskListResponse (Response)
```python
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    count: int
```

---

## Better Auth + JWT Integration

### Authentication Flow
1. **User Login**: Frontend sends credentials to Better Auth server
2. **Token Generation**: Better Auth returns JWT token with `user_id` claim
3. **API Requests**: Client includes token in `Authorization: Bearer <token>` header
4. **Token Validation**: FastAPI middleware validates JWT signature and extracts claims
5. **Authorization**: Endpoint checks if JWT `user_id` matches path `{user_id}` parameter

### JWT Token Structure
```json
{
  "sub": "user_abc123",
  "user_id": "user_abc123",
  "email": "user@example.com",
  "exp": 1703088000,
  "iat": 1703084400
}
```

### Implementation Requirements
- Use `python-jose[cryptography]` for JWT validation
- Validate token signature with Better Auth public key
- Extract `user_id` from token claims
- Compare with path parameter for authorization
- Return 401 for invalid/expired tokens
- Return 403 for user_id mismatch

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-12-20T11:30:00Z"
}
```

### Error Taxonomy
| Error Code | HTTP Status | Meaning |
|------------|-------------|---------|
| `AUTH_MISSING` | 401 | No JWT token provided |
| `AUTH_INVALID` | 401 | Invalid/expired JWT token |
| `AUTH_FORBIDDEN` | 403 | user_id mismatch |
| `VALIDATION_ERROR` | 400/422 | Request validation failed |
| `NOT_FOUND` | 404 | Task doesn't exist |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Exception Handlers
- `ValidationError` → 422 Unprocessable Entity
- `HTTPException` → Appropriate status code
- `DatabaseError` → 500 Internal Server Error
- Uncaught exceptions → 500 with generic message (don't leak internals)

---

## Non-Functional Requirements

### Performance
- **Response Time**: p95 < 200ms for all endpoints (excluding network latency)
- **Throughput**: Support 100 requests/second per user
- **Database**: Reuse connection pooling from Stage 1

### Security
- **Authentication**: JWT token required for all endpoints
- **Authorization**: Verify user_id match between JWT and path parameter
- **Input Validation**: Pydantic schemas validate all request data
- **SQL Injection**: SQLModel ORM prevents SQL injection (parameterized queries)
- **Secrets**: JWT secret key in environment variable (never hardcoded)
- **HTTPS**: Enforce HTTPS in production (TLS 1.2+)

### Reliability
- **Error Handling**: All exceptions caught and logged
- **Database Failures**: Return 500 with retry-after header
- **Idempotency**: PUT/DELETE are idempotent, POST creates unique resources

### Observability
- **Logging**: Log all requests with user_id, endpoint, status, duration
- **Metrics**: Track request count, error rate, response times
- **Health Check**: `GET /health` endpoint (no auth required)

---

## Testing Requirements

### Unit Tests
- ✅ Pydantic schema validation (valid/invalid inputs)
- ✅ JWT token parsing and validation
- ✅ Authorization logic (user_id matching)

### Integration Tests
- ✅ Each endpoint with valid JWT token
- ✅ 401 responses for missing/invalid tokens
- ✅ 403 responses for user_id mismatch
- ✅ 404 responses for non-existent tasks
- ✅ 400/422 responses for validation errors
- ✅ Database persistence verification

### Test Coverage
- **Target**: 70%+ overall coverage
- **Critical Paths**: 100% coverage for auth/authorization logic
- **Edge Cases**: Empty lists, max length strings, special characters

### Test Database
- Use in-memory SQLite for unit tests (from Stage 1 conftest.py)
- Use separate Neon test database for integration tests (optional)

---

## Acceptance Criteria

### AC-1: Endpoint Implementation ✅
**Given**: Database from Stage 1 is operational
**When**: All 6 REST endpoints are implemented
**Then**:
- GET `/api/{user_id}/tasks` lists all user tasks
- POST `/api/{user_id}/tasks` creates new task
- GET `/api/{user_id}/tasks/{task_id}` retrieves single task
- PUT `/api/{user_id}/tasks/{task_id}` updates entire task
- PATCH `/api/{user_id}/tasks/{task_id}` updates specific fields
- DELETE `/api/{user_id}/tasks/{task_id}` deletes task

**Test**: Integration tests for each endpoint with valid data

---

### AC-2: Authentication & Authorization ✅
**Given**: User has valid JWT token with user_id claim
**When**: Making API requests
**Then**:
- Requests without token return 401 Unauthorized
- Requests with invalid/expired token return 401
- Requests with valid token but user_id mismatch return 403 Forbidden
- Requests with valid token and matching user_id succeed

**Test**: Auth integration tests with various token scenarios

---

### AC-3: Request/Response Validation ✅
**Given**: API endpoint receives request
**When**: Validating request data
**Then**:
- Missing required fields return 400/422
- Fields exceeding max length return 422
- Invalid data types return 422
- Successful requests return properly formatted responses

**Test**: Schema validation tests with boundary cases

---

### AC-4: Error Handling ✅
**Given**: API encounters errors
**When**: Processing requests
**Then**:
- Non-existent tasks return 404
- Database errors return 500
- All errors include descriptive messages
- No internal details leaked in production

**Test**: Error scenario tests (404, 500, validation errors)

---

### AC-5: OpenAPI Documentation ✅
**Given**: FastAPI application is running
**When**: Accessing `/docs` or `/redoc`
**Then**:
- Interactive API documentation is displayed
- All endpoints are documented
- Request/response schemas are shown
- Authentication requirements are documented

**Test**: Manual verification of Swagger UI

---

### AC-6: Database Integration ✅
**Given**: CRUD operations are executed via API
**When**: Interacting with database
**Then**:
- Tasks are persisted to Neon PostgreSQL
- Timestamps auto-generate/update correctly
- User isolation enforced (can't access other users' tasks)
- Database connection pooling from Stage 1 is reused

**Test**: Integration tests verify database state after API calls

---

### AC-7: Test Coverage ✅
**Given**: Test suite is executed
**When**: Running pytest with coverage
**Then**:
- Overall coverage ≥ 70%
- All endpoints have integration tests
- Auth/authorization logic has unit tests
- Coverage report generated

**Test**: `pytest --cov=src --cov-report=term-missing`

---

## Implementation Dependencies

### New Dependencies to Add
```bash
# API framework
uv add fastapi>=0.115.0

# ASGI server
uv add uvicorn[standard]>=0.30.0

# JWT handling
uv add python-jose[cryptography]>=3.3.0

# Testing
uv add --dev httpx>=0.27.0  # FastAPI test client
uv add --dev pytest-asyncio>=0.24.0  # Async test support
```

### Updated pyproject.toml Dependencies
```toml
[project]
dependencies = [
    "sqlmodel>=0.0.22",
    "psycopg2-binary>=2.9.0",
    "python-dotenv>=1.0.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "python-jose[cryptography]>=3.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "httpx>=0.27.0",
    "pytest-asyncio>=0.24.0",
]
```

### Environment Variables (.env)
```bash
# Existing from Stage 1
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# New for Stage 2
JWT_SECRET_KEY=your-secret-key-here  # For development only
JWT_ALGORITHM=HS256
BETTER_AUTH_PUBLIC_KEY_URL=https://auth.hackathon-todo.com/.well-known/jwks.json
```

---

## File Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py       # JWT validation, get_current_user
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py          # Task endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py               # Pydantic request/response models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py               # JWT validation logic
│   │   └── errors.py             # Custom exceptions, error handlers
│   ├── database/                 # Reused from Stage 1
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── init_db.py
│   │   └── crud.py               # Extended with update/delete
│   ├── models/                   # Reused from Stage 1
│   │   ├── __init__.py
│   │   └── task.py
│   ├── config.py                 # Extended with JWT settings
│   └── main.py                   # FastAPI application entry point
├── tests/
│   ├── unit/
│   │   ├── test_schemas.py       # Pydantic schema tests
│   │   ├── test_auth.py          # JWT validation tests
│   │   └── test_crud_extended.py # Update/delete CRUD tests
│   ├── integration/
│   │   └── test_api.py           # API endpoint integration tests
│   └── conftest.py               # Extended with API test fixtures
├── .env                          # Add JWT configuration
├── .env.example                  # Add JWT example config
├── pyproject.toml                # Add FastAPI dependencies
└── README.md                     # Update with API usage
```

---

## Out of Scope (Deferred to Later Stages)

- ❌ User registration/login endpoints (Stage 4)
- ❌ Frontend Next.js application (Stage 3)
- ❌ AI chat features (Stage 5)
- ❌ Pagination for task lists (enhancement, not required)
- ❌ Task filtering by date/status (enhancement, not required)
- ❌ Rate limiting (production enhancement)
- ❌ Comprehensive production monitoring (production enhancement)

---

## Risks and Mitigations

### Risk 1: Better Auth Integration Complexity
**Impact**: Medium - May delay authentication implementation
**Probability**: Medium
**Mitigation**:
- Start with mock JWT validation using `python-jose`
- Document Better Auth integration separately
- Use test JWT tokens for development

### Risk 2: Test Coverage Below 70%
**Impact**: High - Blocks Stage 2 completion
**Probability**: Low
**Mitigation**:
- Write tests alongside implementation (TDD approach)
- Focus on critical paths (auth, CRUD operations)
- Use coverage reports to identify gaps

### Risk 3: Database Connection Issues
**Impact**: Medium - API requests fail
**Probability**: Low (Stage 1 connection stable)
**Mitigation**:
- Reuse proven connection pooling from Stage 1
- Add health check endpoint for monitoring
- Implement proper error handling for database failures

---

## Success Metrics

- ✅ 6 RESTful endpoints implemented and tested
- ✅ JWT authentication integrated
- ✅ 70%+ test coverage maintained
- ✅ All integration tests passing
- ✅ OpenAPI documentation accessible at `/docs`
- ✅ No ruff linting errors
- ✅ All code formatted with ruff

---

## Definition of Done

- [ ] All 6 REST endpoints implemented
- [ ] Pydantic request/response schemas defined
- [ ] JWT authentication middleware functional
- [ ] Authorization checks enforce user isolation
- [ ] Error handling with proper HTTP status codes
- [ ] Integration tests for all endpoints (100% endpoint coverage)
- [ ] Unit tests for schemas and auth logic
- [ ] Test coverage ≥ 70%
- [ ] OpenAPI documentation accessible
- [ ] README updated with API usage examples
- [ ] All ruff checks passing
- [ ] Code formatted with ruff
- [ ] CRUD module extended with update/delete operations
- [ ] Changes committed to git with descriptive messages

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Better Auth Documentation](https://www.better-auth.com/)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)
- Phase II Hackathon Specification (PDF pages 7-8)
- Stage 1 Database Specification: `specs/002-database-setup/spec.md`

---

**Next Stage**: Stage 3 - Frontend Integration (Next.js + TailwindCSS)
