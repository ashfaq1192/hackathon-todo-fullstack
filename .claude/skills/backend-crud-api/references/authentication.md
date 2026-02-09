# JWT Authentication and Authorization

## Overview

Implement JWT-based authentication that validates tokens, extracts user identity, and enforces user isolation. This ensures users can only access their own resources.

## Decision Points

### Decision Point 1: JWT Validation Strategy

- **JWT secret management**: Store in environment variables, never commit to code
- **Algorithm choice**: HS256 (symmetric) for single-service, RS256 (asymmetric) for multi-service
- **Token claim structure**: user_id in "sub" claim (standard) or custom claim
- **Expiration handling**: Return 401 for expired tokens with clear error messages

### Decision Point 2: Authorization Header Format

- **Format**: Enforce "Bearer <token>" format strictly
- **Missing header**: Return 401 with WWW-Authenticate header
- **Malformed header**: Return 401 with clear error message

## JWT Decoding and Validation

Create auth module for JWT operations.

### Basic JWT Decoding

```python
import jwt
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class AuthError(Exception):
    """Authentication error."""
    pass

def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token claims

    Raises:
        AuthError: If token is invalid, expired, or malformed
    """
    if not JWT_SECRET_KEY:
        logger.error("JWT_SECRET_KEY not configured")
        raise AuthError("Authentication configuration error")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": True}  # Verify expiration
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {str(e)}")
```

### Extract User ID from Token

```python
def extract_user_id_from_token(token: str) -> str:
    """Extract user_id from JWT token claims.

    Args:
        token: JWT token string

    Returns:
        User ID string

    Raises:
        AuthError: If token is invalid or missing user_id
    """
    payload = decode_jwt_token(token)

    # Try standard "sub" claim first
    user_id = payload.get("sub")
    if user_id:
        return str(user_id)

    # Fallback to custom "user_id" claim
    user_id = payload.get("user_id")
    if user_id:
        return str(user_id)

    raise AuthError("Token missing user identifier")
```

### Key Points

- **Environment variables**: Never hardcode secrets
- **Explicit verification**: Set `verify_exp=True` to validate expiration
- **Clear error messages**: Help clients understand what went wrong
- **Flexible claim extraction**: Support both "sub" and "user_id" claims
- **Type conversion**: Always convert user_id to string for consistency

## FastAPI Authentication Dependencies

Create dependency functions for route handlers.

### Get Current User Dependency

```python
from fastapi import Header, HTTPException, Depends

def get_current_user(authorization: str | None = Header(None)) -> str:
    """FastAPI dependency to extract authenticated user from JWT.

    Args:
        authorization: Authorization header value

    Returns:
        User ID string

    Raises:
        HTTPException: 401 if authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        user_id = extract_user_id_from_token(token)
        logger.debug(f"User {user_id} authenticated")
        return user_id
    except AuthError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### Key Points

- **Header parameter**: Use `Header(None)` to make header optional for better error messages
- **Explicit format check**: Validate "Bearer " prefix before extracting token
- **WWW-Authenticate header**: RFC 7235 compliant 401 responses
- **Logging**: Log authentication events for debugging (debug level to avoid noise)

## User ID Verification for Authorization

Enforce that authenticated user matches path user_id parameter.

### Verification Dependency

```python
def verify_user_id_match(current_user: str, path_user_id: str) -> None:
    """Verify that authenticated user matches path parameter.

    Args:
        current_user: User ID from JWT
        path_user_id: User ID from URL path

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if current_user != path_user_id:
        logger.warning(f"User {current_user} attempted to access resources for {path_user_id}")
        raise HTTPException(
            status_code=403,
            detail=f"Cannot access resources for user '{path_user_id}'"
        )
```

### Usage in Route Handlers

```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/{user_id}/tasks")
def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    # Now safe to proceed - user owns this data
    tasks = get_tasks_by_user(session, user_id)
    return tasks
```

### Key Points

- **403 vs 401**: Use 403 for authorization failures (authenticated but not authorized)
- **Security logging**: Log authorization failures for security monitoring
- **Clear error messages**: Tell user what they tried to access (helps debugging)
- **Call early**: Verify before any database operations

## Resource Ownership Verification

For individual resource access, verify both existence and ownership.

### Ownership Check Pattern

```python
@router.get("/{user_id}/tasks/{task_id}")
def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Step 1: Verify user_id match
    verify_user_id_match(current_user, user_id)

    # Step 2: Retrieve resource
    task = get_task_by_id(session, task_id)

    # Step 3: Check existence (404 if not found)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Step 4: Check ownership (403 if user doesn't own it)
    if task.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: task belongs to another user"
        )

    return TaskResponse.model_validate(task)
```

### Key Points

- **Order matters**: Check path user_id first, then resource ownership
- **404 before 403**: Don't leak existence of resources user doesn't own
- **Double check**: Verify both path user_id and resource's user_id field
- **Consistent messaging**: Use similar error messages across endpoints

## Security Best Practices

### Environment Configuration

```python
# config.py
import os
from functools import lru_cache

class Settings:
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    def validate(self):
        """Validate required settings."""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable is required")

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings
```

### .env File Template

```bash
# Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Security Checklist

- ✅ Never commit JWT_SECRET_KEY to version control
- ✅ Use strong secrets (minimum 32 characters, random)
- ✅ Enable token expiration verification
- ✅ Log authentication failures for monitoring
- ✅ Use HTTPS in production (prevents token interception)
- ✅ Validate token on every protected endpoint
- ✅ Check both authentication (valid token) and authorization (owns resource)
- ✅ Return WWW-Authenticate header on 401 responses

## Testing Authentication

### Test Fixtures

```python
# conftest.py
import pytest
import jwt
from datetime import datetime, timedelta

@pytest.fixture
def jwt_secret():
    return "test-secret-key-at-least-32-characters"

@pytest.fixture
def jwt_token(jwt_secret):
    """Generate valid JWT tokens for testing."""
    def _generate_token(user_id: str, expired: bool = False) -> str:
        exp_delta = timedelta(hours=-1) if expired else timedelta(hours=24)
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + exp_delta
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")
    return _generate_token
```

### Test Cases

```python
def test_missing_authorization_header(client):
    response = client.get("/api/user123/tasks")
    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]

def test_invalid_authorization_format(client):
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == 401

def test_expired_token(client, jwt_token):
    expired_token = jwt_token("user123", expired=True)
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

def test_user_id_mismatch(client, jwt_token):
    token = jwt_token("user123")
    response = client.get(
        "/api/user456/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_successful_authentication(client, jwt_token):
    token = jwt_token("user123")
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## File Organization

```
src/
├── core/
│   ├── auth.py           # JWT validation logic
│   └── errors.py         # Custom exceptions
├── api/
│   └── dependencies.py   # FastAPI dependencies
└── config.py            # Environment settings
```

## Common Pitfalls

### ❌ Don't: Skip Token Verification

```python
# BAD - trusts token without verification
def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    # Decoding without verification!
    payload = jwt.decode(token, options={"verify_signature": False})
    return payload["sub"]
```

### ✅ Do: Always Verify Signature and Expiration

```python
# GOOD - full verification
def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"verify_exp": True}
    )
    return payload["sub"]
```

### ❌ Don't: Return 404 for Authorization Failures

```python
# BAD - leaks information about resource existence
if task.user_id != current_user:
    raise HTTPException(status_code=404, detail="Not found")
```

### ✅ Do: Return 403 for Authorization Failures

```python
# GOOD - clear about authorization failure
if task.user_id != current_user:
    raise HTTPException(status_code=403, detail="Access denied")
```
