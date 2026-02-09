# Error Handling and Exception Management

## Overview

Implement comprehensive error handling that provides clear feedback to clients while protecting sensitive information. Use consistent error response formats and appropriate HTTP status codes.

## Decision Point: Error Type Categorization

Map application errors to HTTP status codes:

- **400 Bad Request**: Validation errors, missing required fields, malformed JSON
- **401 Unauthorized**: Invalid/missing JWT, expired token
- **403 Forbidden**: User doesn't own resource, insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Duplicate resource (e.g., unique constraint violation)
- **500 Internal Server Error**: Database errors, unexpected exceptions

## Custom Exception Classes

Create domain-specific exceptions in `errors.py`.

### Base Exceptions

```python
class AuthError(Exception):
    """Authentication failures (invalid JWT, expired token)."""
    pass

class ForbiddenError(Exception):
    """Authorization failures (user doesn't own resource)."""
    pass

class NotFoundError(Exception):
    """Resource not found."""
    pass

class ConflictError(Exception):
    """Resource conflict (duplicate, constraint violation)."""
    pass

class DatabaseError(Exception):
    """Database operation failures."""
    pass
```

### Usage in Application Code

```python
# In auth.py
if not token:
    raise AuthError("Missing authentication token")

# In route handler
if not task:
    raise NotFoundError(f"Task {task_id} not found")

if task.user_id != current_user:
    raise ForbiddenError("Cannot access task owned by another user")
```

## Error Response Format

Use consistent JSON format for all errors.

### Standard Error Response

```json
{
    "error": "Error Type",
    "message": "Human-readable description",
    "status_code": 400
}
```

### Implementation

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
```

## Global Exception Handlers

Register handlers in FastAPI app to intercept exceptions and convert to HTTP responses.

### Authentication Error Handler (401)

```python
from fastapi import Request
from fastapi.responses import JSONResponse

async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    """Handle authentication errors with 401 status."""
    logger.warning(f"Authentication error: {str(exc)}")
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Error",
            "message": str(exc),
            "status_code": 401
        },
        headers={"WWW-Authenticate": "Bearer"}
    )
```

### Forbidden Error Handler (403)

```python
async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """Handle authorization errors with 403 status."""
    logger.warning(f"Authorization denied: {str(exc)}")
    return JSONResponse(
        status_code=403,
        content={
            "error": "Forbidden",
            "message": str(exc),
            "status_code": 403
        }
    )
```

### Not Found Error Handler (404)

```python
async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle resource not found with 404 status."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc),
            "status_code": 404
        }
    )
```

### Conflict Error Handler (409)

```python
async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """Handle resource conflicts with 409 status."""
    logger.info(f"Resource conflict: {str(exc)}")
    return JSONResponse(
        status_code=409,
        content={
            "error": "Conflict",
            "message": str(exc),
            "status_code": 409
        }
    )
```

### Database Error Handler (500)

```python
from sqlalchemy.exc import SQLAlchemyError

async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors with 500 status.

    IMPORTANT: Never expose internal database errors to clients.
    Log full details server-side but return generic message.
    """
    logger.error(f"Database error: {type(exc).__name__} - {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "message": "An error occurred while processing your request",
            "status_code": 500
        }
    )
```

### HTTP Exception Handler

Handle FastAPI's built-in HTTPException:

```python
from fastapi import HTTPException

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request Error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )
```

### General Exception Handler (500 Catch-All)

```python
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions.

    Log full stack trace but return generic error to client.
    """
    logger.exception(f"Unexpected error: {type(exc).__name__}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500
        }
    )
```

## Register Exception Handlers

In `main.py`, register all handlers with the FastAPI app:

```python
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

# Register custom exception handlers
app.add_exception_handler(AuthError, auth_error_handler)
app.add_exception_handler(ForbiddenError, forbidden_error_handler)
app.add_exception_handler(NotFoundError, not_found_error_handler)
app.add_exception_handler(ConflictError, conflict_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_error_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

### Handler Registration Order

Order matters! Register from most specific to most general:
1. Custom exceptions (AuthError, ForbiddenError, etc.)
2. HTTPException (FastAPI's built-in)
3. SQLAlchemyError (database layer)
4. Exception (catch-all)

## Decision Point: Error Message Detail Level

Balance security vs debuggability:

### Production: Generic Messages

```python
# PRODUCTION - hide internals
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")  # Log full details
    return JSONResponse(
        status_code=500,
        content={"message": "An error occurred"}  # Generic message
    )
```

### Development: Detailed Messages

```python
# DEVELOPMENT - show details
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": str(exc),  # Show actual error
            "type": type(exc).__name__,
            "traceback": traceback.format_exc()  # Include stack trace
        }
    )
```

### Environment-Based Configuration

```python
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")

    content = {
        "error": "Database Error",
        "status_code": 500
    }

    if DEBUG:
        content["message"] = str(exc)
        content["type"] = type(exc).__name__
    else:
        content["message"] = "An error occurred while processing your request"

    return JSONResponse(status_code=500, content=content)
```

## Validation Error Handling

FastAPI automatically handles Pydantic validation errors, but you can customize:

### Custom Validation Error Handler

```python
from fastapi.exceptions import RequestValidationError

async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with clear messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": errors,
            "status_code": 400
        }
    )

# Register handler
app.add_exception_handler(RequestValidationError, validation_error_handler)
```

### Example Validation Error Response

```json
{
    "error": "Validation Error",
    "message": "Invalid request data",
    "details": [
        "body -> title: field required",
        "body -> description: ensure this value has at most 1000 characters"
    ],
    "status_code": 400
}
```

## Logging Best Practices

### Log Levels

- **DEBUG**: Successful operations, detailed flow
- **INFO**: Important events (task created, user authenticated)
- **WARNING**: Recoverable issues (authentication failures, authorization denials)
- **ERROR**: Errors requiring attention (database errors, unexpected exceptions)
- **CRITICAL**: System-level failures

### What to Log

```python
# Authentication attempt
logger.debug(f"User {user_id} authenticated successfully")

# Authorization failure
logger.warning(f"User {current_user} attempted to access resources for {path_user_id}")

# Database error
logger.error(f"Error creating task: {type(exc).__name__} - {str(exc)}")

# Unexpected exception
logger.exception(f"Unexpected error in {request.url.path}")  # Includes stack trace
```

### What NOT to Log

- ❌ User passwords or tokens
- ❌ Full request/response bodies (may contain sensitive data)
- ❌ Database connection strings with passwords
- ❌ Personally identifiable information (PII)

## Error Testing

### Test All Error Paths

```python
def test_missing_auth_returns_401(client):
    response = client.get("/api/user123/tasks")
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"

def test_wrong_user_returns_403(client, jwt_token):
    response = client.get(
        "/api/user456/tasks",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 403

def test_task_not_found_returns_404(client, jwt_token):
    response = client.get(
        "/api/user123/tasks/99999",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 404

def test_invalid_data_returns_400(client, jwt_token):
    response = client.post(
        "/api/user123/tasks",
        json={"title": ""},  # Invalid: empty title
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 400
```

### Test Error Response Format

```python
def test_error_response_format(client):
    response = client.get("/api/user123/tasks")
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert "status_code" in data
    assert data["status_code"] == response.status_code
```

## Common Error Scenarios

### Scenario 1: Duplicate Resource

```python
@router.post("/{user_id}/tasks")
def create_task(user_id: str, task: TaskCreate, ...):
    # Check for duplicate title
    existing = get_task_by_title(session, user_id, task.title)
    if existing:
        raise ConflictError(f"Task with title '{task.title}' already exists")

    new_task = create_task(session, user_id, task.title, task.description)
    return TaskResponse.model_validate(new_task)
```

### Scenario 2: Empty PATCH Request

```python
@router.patch("/{user_id}/tasks/{task_id}")
def patch_task(user_id: str, task_id: int, updates: TaskPatch, ...):
    # Reject empty updates
    update_dict = updates.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    updated_task = update_task(session, task_id, update_dict)
    return TaskResponse.model_validate(updated_task)
```

### Scenario 3: Database Connection Error

Database errors are automatically caught by the SQLAlchemyError handler, ensuring clients never see internal database details.

## File Organization

```
src/
└── core/
    └── errors.py         # Custom exceptions and handlers
```

All error handling code in one file for easy maintenance:

```python
# errors.py

# Custom exceptions
class AuthError(Exception): ...
class ForbiddenError(Exception): ...
# ... more exceptions

# Exception handlers
async def auth_error_handler(...): ...
async def forbidden_error_handler(...): ...
# ... more handlers
```
