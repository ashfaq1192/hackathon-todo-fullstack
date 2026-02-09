# Testing Strategy and Implementation

## Overview

Implement comprehensive testing that covers CRUD operations, API endpoints, authentication/authorization, error handling, and edge cases. Aim for minimum 80% code coverage.

## Decision Point: Test Coverage Strategy

Determine what to test:
- **Unit tests**: CRUD operations, pure functions
- **Integration tests**: API endpoints, database interactions
- **Authentication tests**: Valid/invalid tokens, authorization checks
- **Error handling tests**: All error paths and status codes
- **Edge cases**: Empty strings, null values, large inputs, boundary conditions

## Test File Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_crud.py        # CRUD operation tests
│   └── test_auth.py        # JWT validation tests
└── integration/
    └── test_api.py         # API endpoint tests
```

## Test Fixtures (conftest.py)

Create reusable fixtures for common test setup.

### Database Session Fixture

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()  # Rollback any uncommitted changes
```

### FastAPI Test Client Fixture

```python
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(name="client")
def client_fixture():
    """Create test client for API testing."""
    return TestClient(app)
```

### JWT Token Generator Fixture

```python
import jwt
from datetime import datetime, timedelta
import os

@pytest.fixture
def jwt_secret():
    """JWT secret for testing."""
    return os.getenv("JWT_SECRET_KEY", "test-secret-key-at-least-32-characters")

@pytest.fixture
def jwt_token(jwt_secret):
    """Generate valid JWT tokens for testing.

    Usage:
        token = jwt_token("user123")
        expired_token = jwt_token("user123", expired=True)
    """
    def _generate_token(user_id: str, expired: bool = False) -> str:
        exp_delta = timedelta(hours=-1) if expired else timedelta(hours=24)
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + exp_delta
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")
    return _generate_token
```

### Sample Entity Fixtures

```python
from src.database.crud import create_task

@pytest.fixture
def sample_task(session):
    """Create a sample task for testing."""
    return create_task(
        session,
        user_id="user123",
        title="Sample Task",
        description="Sample description"
    )

@pytest.fixture
def multiple_tasks(session):
    """Create multiple tasks for different users."""
    tasks = [
        create_task(session, "user123", "Task 1", "Description 1"),
        create_task(session, "user123", "Task 2", "Description 2"),
        create_task(session, "user456", "Task 3", "Description 3"),
    ]
    return tasks
```

## Unit Tests: CRUD Operations

Test database operations in isolation.

### Test Create Operation

```python
from src.database.crud import create_task

def test_create_task(session):
    """Test task creation."""
    task = create_task(session, user_id="user123", title="Test Task")

    assert task.id is not None
    assert task.user_id == "user123"
    assert task.title == "Test Task"
    assert task.description is None
    assert task.complete is False
    assert task.created_at is not None
    assert task.updated_at is not None

def test_create_task_with_description(session):
    """Test task creation with description."""
    task = create_task(
        session,
        user_id="user123",
        title="Test Task",
        description="Test Description"
    )

    assert task.description == "Test Description"
```

### Test Read Operations

```python
from src.database.crud import get_task_by_id, get_tasks_by_user

def test_get_task_by_id(session, sample_task):
    """Test retrieving task by ID."""
    task = get_task_by_id(session, sample_task.id)

    assert task is not None
    assert task.id == sample_task.id
    assert task.title == sample_task.title

def test_get_task_not_found(session):
    """Test retrieving non-existent task."""
    task = get_task_by_id(session, task_id=99999)
    assert task is None

def test_get_tasks_by_user(session, multiple_tasks):
    """Test filtering tasks by user."""
    tasks = get_tasks_by_user(session, user_id="user123")

    assert len(tasks) == 2
    assert all(task.user_id == "user123" for task in tasks)

def test_get_tasks_by_user_empty(session):
    """Test retrieving tasks for user with no tasks."""
    tasks = get_tasks_by_user(session, user_id="nonexistent")
    assert tasks == []
```

### Test Update Operation

```python
from src.database.crud import update_task

def test_update_task(session, sample_task):
    """Test updating task."""
    updated = update_task(
        session,
        sample_task.id,
        {"title": "Updated Title", "complete": True}
    )

    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.complete is True
    assert updated.updated_at > sample_task.updated_at

def test_update_task_not_found(session):
    """Test updating non-existent task."""
    result = update_task(session, task_id=99999, updates={"title": "New"})
    assert result is None

def test_update_task_partial(session, sample_task):
    """Test partial update (only one field)."""
    original_title = sample_task.title
    updated = update_task(session, sample_task.id, {"complete": True})

    assert updated.title == original_title  # Unchanged
    assert updated.complete is True  # Changed
```

### Test Delete Operation

```python
from src.database.crud import delete_task

def test_delete_task(session, sample_task):
    """Test deleting task."""
    result = delete_task(session, sample_task.id)

    assert result is True
    assert get_task_by_id(session, sample_task.id) is None

def test_delete_task_not_found(session):
    """Test deleting non-existent task."""
    result = delete_task(session, task_id=99999)
    assert result is False
```

## Integration Tests: API Endpoints

Test complete request/response cycles through FastAPI.

### Test LIST Endpoint (GET /api/{user_id}/tasks)

```python
def test_list_tasks_requires_auth(client):
    """Test that listing tasks requires authentication."""
    response = client.get("/api/user123/tasks")
    assert response.status_code == 401

def test_list_tasks_success(client, jwt_token, session, multiple_tasks):
    """Test listing tasks for authenticated user."""
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["tasks"]) == 2
    assert all(task["user_id"] == "user123" for task in data["tasks"])

def test_list_tasks_wrong_user(client, jwt_token):
    """Test user cannot list another user's tasks."""
    response = client.get(
        "/api/user456/tasks",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 403
```

### Test CREATE Endpoint (POST /api/{user_id}/tasks)

```python
def test_create_task_success(client, jwt_token):
    """Test creating a new task."""
    response = client.post(
        "/api/user123/tasks",
        json={"title": "New Task", "description": "New Description"},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "New Description"
    assert data["user_id"] == "user123"
    assert "id" in data
    assert "created_at" in data

def test_create_task_missing_title(client, jwt_token):
    """Test creating task without required title."""
    response = client.post(
        "/api/user123/tasks",
        json={"description": "Missing title"},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 400

def test_create_task_empty_title(client, jwt_token):
    """Test creating task with empty title."""
    response = client.post(
        "/api/user123/tasks",
        json={"title": ""},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 400

def test_create_task_forbidden(client, jwt_token):
    """Test user cannot create task for another user."""
    response = client.post(
        "/api/user456/tasks",
        json={"title": "Forbidden Task"},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 403
```

### Test GET Endpoint (GET /api/{user_id}/tasks/{task_id})

```python
def test_get_task_success(client, jwt_token, sample_task):
    """Test retrieving a specific task."""
    response = client.get(
        f"/api/user123/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_task.id
    assert data["title"] == sample_task.title

def test_get_task_not_found(client, jwt_token):
    """Test retrieving non-existent task."""
    response = client.get(
        "/api/user123/tasks/99999",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 404

def test_get_task_wrong_user(client, jwt_token, sample_task):
    """Test user cannot access another user's task."""
    response = client.get(
        f"/api/user456/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {jwt_token('user456')}"}
    )
    # Could be 403 or 404 depending on implementation
    assert response.status_code in [403, 404]
```

### Test PUT Endpoint (PUT /api/{user_id}/tasks/{task_id})

```python
def test_update_task_full_replacement(client, jwt_token, sample_task):
    """Test full task replacement with PUT."""
    response = client.put(
        f"/api/user123/tasks/{sample_task.id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "complete": True
        },
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["complete"] is True

def test_update_task_missing_fields(client, jwt_token, sample_task):
    """Test PUT requires all fields."""
    response = client.put(
        f"/api/user123/tasks/{sample_task.id}",
        json={"title": "Only Title"},  # Missing required fields
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 400
```

### Test PATCH Endpoint (PATCH /api/{user_id}/tasks/{task_id})

```python
def test_patch_task_partial_update(client, jwt_token, sample_task):
    """Test partial task update with PATCH."""
    original_title = sample_task.title

    response = client.patch(
        f"/api/user123/tasks/{sample_task.id}",
        json={"complete": True},  # Only update one field
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == original_title  # Unchanged
    assert data["complete"] is True  # Changed

def test_patch_task_empty_body(client, jwt_token, sample_task):
    """Test PATCH with no fields returns 400."""
    response = client.patch(
        f"/api/user123/tasks/{sample_task.id}",
        json={},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 400
```

### Test DELETE Endpoint (DELETE /api/{user_id}/tasks/{task_id})

```python
def test_delete_task_success(client, jwt_token, sample_task):
    """Test deleting a task."""
    response = client.delete(
        f"/api/user123/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 204

    # Verify task is deleted
    get_response = client.get(
        f"/api/user123/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert get_response.status_code == 404

def test_delete_task_not_found(client, jwt_token):
    """Test deleting non-existent task."""
    response = client.delete(
        "/api/user123/tasks/99999",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 404
```

## Authentication and Authorization Tests

Test all authentication scenarios.

### JWT Token Tests

```python
def test_missing_authorization_header(client):
    """Test request without Authorization header."""
    response = client.get("/api/user123/tasks")
    assert response.status_code == 401
    assert "Authorization" in response.json()["message"]

def test_invalid_authorization_format(client):
    """Test malformed Authorization header."""
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == 401

def test_expired_token(client, jwt_token):
    """Test request with expired token."""
    expired_token = jwt_token("user123", expired=True)
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["message"].lower()

def test_invalid_token_signature(client):
    """Test token with invalid signature."""
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == 401
```

### User Isolation Tests

```python
def test_user_isolation_list(client, jwt_token, multiple_tasks):
    """Test users only see their own tasks."""
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert all(task["user_id"] == "user123" for task in tasks)
    assert len(tasks) == 2  # Only user123's tasks

def test_user_cannot_access_others_resources(client, jwt_token):
    """Test user cannot access another user's resource path."""
    response = client.get(
        "/api/user456/tasks",
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 403
```

## Error Response Format Tests

Verify consistent error response structure.

```python
def test_error_response_format(client):
    """Test all errors follow consistent format."""
    response = client.get("/api/user123/tasks")  # 401 error

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert "status_code" in data
    assert data["status_code"] == 401

def test_validation_error_format(client, jwt_token):
    """Test validation errors include details."""
    response = client.post(
        "/api/user123/tasks",
        json={"title": ""},  # Invalid
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "detail" in data
```

## Edge Case Tests

Test boundary conditions and special cases.

```python
def test_create_task_max_length_title(client, jwt_token):
    """Test creating task with maximum length title."""
    long_title = "x" * 200  # Max length
    response = client.post(
        "/api/user123/tasks",
        json={"title": long_title},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 201

def test_create_task_exceeds_max_length(client, jwt_token):
    """Test creating task with too long title."""
    too_long_title = "x" * 201  # Exceeds max
    response = client.post(
        "/api/user123/tasks",
        json={"title": too_long_title},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 400

def test_special_characters_in_title(client, jwt_token):
    """Test task title with special characters."""
    special_title = "Task with émojis 🎉 and symbols !@#$%"
    response = client.post(
        "/api/user123/tasks",
        json={"title": special_title},
        headers={"Authorization": f"Bearer {jwt_token('user123')}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == special_title
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_crud.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Tests Matching Pattern

```bash
pytest tests/ -k "auth" -v  # Run all auth-related tests
```

## Test Coverage Goals

Aim for minimum 80% coverage:

- ✅ **Unit tests**: 100% coverage of CRUD functions
- ✅ **Integration tests**: All API endpoints with success and error cases
- ✅ **Authentication**: All auth/authz scenarios
- ✅ **Error handling**: All exception handlers
- ✅ **Edge cases**: Boundary conditions, special characters, max lengths

## Testing Best Practices

- **Use fixtures**: Share setup code across tests
- **Test one thing**: Each test should verify one specific behavior
- **Clear names**: Test names should describe what they verify
- **Arrange-Act-Assert**: Organize tests with clear structure
- **Independent tests**: Tests should not depend on each other
- **Fast tests**: Use in-memory SQLite for speed
- **Realistic data**: Use realistic test data, not "foo" and "bar"
