---
name: backend-crud-api
description: Implement backend APIs using either a modern MCP Tool-based architecture or a traditional RESTful approach. Use when (1) Creating backend services for AI agents with custom tools (MCP), (2) Building traditional REST APIs for web/mobile clients, (3) Adding JWT authentication, (4) Implementing user data isolation, (5) Setting up error handling and database integration with SQLModel/SQLAlchemy.
---

# Backend API Architecture

This skill provides two architectural patterns for building secure, production-ready backend APIs: a modern MCP Tool-based architecture for AI agents, and a traditional RESTful architecture for standard clients.

## Architectural Patterns

Choose the pattern that best fits your application's needs.

### **1. Modern MCP Tool-Based Pattern (Phase III+)**

This pattern is ideal for AI-powered applications where a conversational agent needs to perform actions. Instead of exposing REST endpoints for each action, you create stateless "tools" that the AI agent can invoke.

**Core Concept:** The backend exposes a single chat endpoint. The AI agent interprets natural language, decides which tool to use (e.g., `add_task`), and calls it through a Model Context Protocol (MCP) server.

#### Quick Start: MCP Tool Example

Here's a complete example of creating and exposing an `add_task` MCP tool in FastAPI.

##### Step 1: Define the MCP Tool

A tool is a simple Python function with type hints. It contains the business logic for a specific action.

`backend/src/mcp/tools/add_task.py`:
```python
from sqlmodel import Session
from src.models import Task

def add_task(
    session: Session,
    user_id: str,
    title: str,
    description: str | None = None
) -> dict:
    """
    MCP tool for adding a task for a given user.
    """
    # [T060] Log MCP tool invocation (not shown)
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    session.commit()
    session.refresh(task)
    return {
        "task_id": task.id,
        "title": task.title,
        "status": "created",
    }
```

##### Step 2: Create the MCP Server

The MCP server discovers and registers all your tools. The official `mcp` library simplifies this.

`backend/src/mcp/server.py`:
```python
from mcp.server.fastmcp import FastMCP
from src.mcp.tools.add_task import add_task as add_task_fn
# ... import other tools

# Create FastMCP server instance
mcp = FastMCP(
    name="todo-mcp-server",
    description="MCP server for managing tasks.",
    # ... other configuration
)

# Register the tool with the server
@mcp.tool()
def add_task(
    title: str,
    description: str | None = None,
    # Session and user_id are injected via dependencies, not part of public schema
) -> dict:
    # This just defines the schema for the agent.
    # The actual implementation is in add_task_fn.
    pass

# You would have similar @mcp.tool() definitions for list_tasks, etc.
```

##### Step 3: Expose via FastAPI

Finally, expose the MCP server and a chat endpoint through your main FastAPI application.

`backend/src/main.py`:
```python
# ... imports
from src.api.routes.chat import router as chat_router
from src.api.routes.mcp import router as mcp_router

app = FastAPI()

# Include the router for the chat endpoint
app.include_router(chat_router, prefix="/api", tags=["Chat"])
# Include the router for MCP tool discovery and health checks
app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP"])
```

**Key Advantages of MCP Pattern:**
-   **AI-Native:** Designed for AI agents to discover and use tools.
-   **Decoupled:** The AI agent (logic) is decoupled from the tools (actions).
-   **Scalable:** The stateless nature of tools allows for easy scaling.
-   **Extensible:** Adding new capabilities is as simple as creating a new tool function.

---

### **2. Legacy RESTful Pattern (Phase II)**

This is the traditional approach for building web and mobile backends. It involves creating a unique HTTP endpoint (e.g., `POST /api/tasks`) for each CRUD operation. This pattern is still perfectly valid for services that are not driven by an AI agent.


# Backend CRUD API with JWT Authentication

## Overview

Build secure, production-ready RESTful CRUD API endpoints that coordinate data modeling, database operations, authentication, authorization, validation, error handling, and API documentation.

**Core Challenge:** Consistently implement CRUD operations across different entities while maintaining security, reliability, and maintainability.

## Process Overview

Follow these steps sequentially to build a complete CRUD API:

1. **Define Data Models and Schemas** → See [references/data-models.md](references/data-models.md)
   - Create SQLModel database models with constraints
   - Design Pydantic API schemas (Create, Update, Patch, Response, ListResponse)
   - Configure timestamps and validation rules

2. **Implement CRUD Database Operations** → See [references/crud-operations.md](references/crud-operations.md)
   - Create: Add entity to database, commit, refresh
   - Read: Query by ID or filter by user
   - Update: Full replacement (PUT) or partial update (PATCH)
   - Delete: Remove entity and commit
   - Handle transactions with proper rollback

3. **Set Up JWT Authentication** → See [references/authentication.md](references/authentication.md)
   - Decode and validate JWT tokens
   - Extract user_id from token claims
   - Create FastAPI dependencies for authentication
   - Verify user_id matches path parameter

4. **Create API Route Handlers**
   - LIST: `GET /api/{user_id}/entities` → Return all user's entities
   - CREATE: `POST /api/{user_id}/entities` → Create new entity (201)
   - GET: `GET /api/{user_id}/entities/{id}` → Retrieve single entity
   - UPDATE: `PUT /api/{user_id}/entities/{id}` → Full replacement (200)
   - PATCH: `PATCH /api/{user_id}/entities/{id}` → Partial update (200)
   - DELETE: `DELETE /api/{user_id}/entities/{id}` → Remove entity (204)

5. **Implement Error Handling** → See [references/error-handling.md](references/error-handling.md)
   - Create custom exception classes (AuthError, ForbiddenError, NotFoundError)
   - Register global exception handlers
   - Return consistent JSON error responses
   - Map errors to appropriate HTTP status codes

6. **Add Comprehensive Testing** → See [references/testing.md](references/testing.md)
   - Unit tests for CRUD operations
   - Integration tests for API endpoints
   - Authentication/authorization tests
   - Error handling and edge case tests

## Quick Start: Task CRUD Example

For a complete end-to-end implementation example (model → schemas → CRUD → auth → routes → error handling), see [references/quickstart-example.md](references/quickstart-example.md).

## Key Implementation Patterns

### REST Endpoint Structure

```
GET    /api/{user_id}/entities           → List all (200)
POST   /api/{user_id}/entities           → Create (201)
GET    /api/{user_id}/entities/{id}      → Get one (200)
PUT    /api/{user_id}/entities/{id}      → Full update (200)
PATCH  /api/{user_id}/entities/{id}      → Partial update (200)
DELETE /api/{user_id}/entities/{id}      → Delete (204)
```

### Authentication Flow

1. Extract token from `Authorization: Bearer <token>` header
2. Decode and validate JWT (check signature, expiration)
3. Extract user_id from token claims (`sub` or `user_id`)
4. Verify token user_id matches path user_id parameter
5. For individual resources, also verify resource ownership

### Error Response Format

All errors return consistent JSON:

```json
{
    "error": "Error Type",
    "message": "Human-readable description",
    "status_code": 400
}
```

### Security Checklist

- ✅ Validate JWT signature and expiration on every request
- ✅ Index user_id column for query performance
- ✅ Check both path user_id and resource ownership
- ✅ Return 404 before 403 (don't leak resource existence)
- ✅ Never expose internal database errors to clients
- ✅ Log authentication/authorization failures
- ✅ Use HTTPS in production
- ✅ Store JWT_SECRET_KEY in environment variables

## File Organization

```
backend/
├── src/
│   ├── main.py                    # FastAPI app with exception handlers
│   ├── config.py                  # Environment variables
│   ├── models/
│   │   └── entity.py              # SQLModel database models
│   ├── schemas/
│   │   └── entity.py              # Pydantic API schemas
│   ├── database/
│   │   ├── connection.py          # Database session management
│   │   └── crud.py                # CRUD operations
│   ├── core/
│   │   ├── auth.py                # JWT validation logic
│   │   └── errors.py              # Custom exceptions and handlers
│   └── api/
│       ├── dependencies.py        # FastAPI dependencies
│       └── routes/
│           └── entities.py        # API route handlers
└── tests/
    ├── conftest.py                # Test fixtures
    ├── unit/
    │   └── test_crud.py           # CRUD operation tests
    └── integration/
        └── test_api.py            # API endpoint tests
```

## Success Criteria

A successful implementation includes:

- ✅ All 6 CRUD endpoints functional
- ✅ JWT authentication enforced on all endpoints
- ✅ User isolation prevents cross-user access
- ✅ Proper HTTP status codes (200, 201, 204, 400, 401, 403, 404, 500)
- ✅ Consistent error response format
- ✅ Comprehensive test coverage (80%+ recommended)
- ✅ OpenAPI documentation accessible at `/docs`
- ✅ Database transactions handle errors with rollback
- ✅ Logging for debugging and monitoring
- ✅ Input validation on all request bodies

## Detailed References

For comprehensive guidance on each step:

- **[Quick Start Example](references/quickstart-example.md)** - Complete Task CRUD implementation (model → routes → error handling)
- **[Data Models and Schemas](references/data-models.md)** - SQLModel models, Pydantic schemas, validation rules
- **[CRUD Operations](references/crud-operations.md)** - Database functions, transaction management, error handling
- **[Authentication](references/authentication.md)** - JWT validation, user extraction, authorization checks
- **[Error Handling](references/error-handling.md)** - Custom exceptions, global handlers, error responses
- **[Testing](references/testing.md)** - Unit tests, integration tests, fixtures, coverage goals

## Common Adaptations

### Different Entity Types

Replace "Task" with your entity name throughout:
- Model: `class Project(SQLModel, table=True):`
- Schemas: `ProjectCreate`, `ProjectUpdate`, `ProjectPatch`, `ProjectResponse`
- CRUD: `create_project()`, `get_projects_by_user()`, etc.
- Routes: `/api/{user_id}/projects`

### Additional Fields

Add entity-specific fields to models and schemas:
```python
# For projects
priority: str = Field(max_length=20)
due_date: datetime | None = None
tags: list[str] = Field(default_factory=list)
```

### Relationships

Add foreign keys for related entities:
```python
# For comments on tasks
task_id: int = Field(foreign_key="tasks.id", index=True)
```

### Admin Access

Add role-based authorization:
```python
def require_admin(current_user: str = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
```