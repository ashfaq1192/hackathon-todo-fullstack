"""
Integration tests for Task API endpoints.

These tests verify the complete request/response cycle for all API endpoints,
including authentication, authorization, and database operations.
"""

import pytest
from fastapi import status


# User Story 1: List User's Tasks - Integration Tests (T045-T048)


def test_list_tasks_with_valid_token_returns_200(api_client, create_jwt_token, test_engine):
    """
    T045: Verify GET /api/{user_id}/tasks with valid token returns 200 and task list.

    Acceptance Scenario 1:
    Given valid JWT token, When GET /api/{user_id}/tasks,
    Then return all tasks for that user with 200 OK
    """
    # Arrange: Create JWT token for user123
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    # Arrange: Create some tasks for user123 using the same engine as api_client
    from sqlmodel import Session
    from src.database.crud import create_task

    # Store task IDs before session closes to avoid DetachedInstanceError
    task_ids_created = []
    with Session(test_engine) as session:
        task1 = create_task(session, "user123", "Task 1", "Description 1")
        task2 = create_task(session, "user123", "Task 2", "Description 2")
        task3 = create_task(session, "user123", "Task 3", None)
        # Access IDs while session is still open
        task_ids_created = [task1.id, task2.id, task3.id]

    # Act: Request tasks for user123
    response = api_client.get("/api/user123/tasks", headers=headers)

    # Assert: Should return 200 with task list
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "tasks" in data
    assert "count" in data
    assert data["count"] == 3
    assert len(data["tasks"]) == 3

    # Verify task structure and IDs
    task_ids_returned = {task["id"] for task in data["tasks"]}
    for task_id in task_ids_created:
        assert task_id in task_ids_returned

    # Verify all tasks belong to user123
    assert all(task["user_id"] == "user123" for task in data["tasks"])

    # Verify task fields are present
    first_task = data["tasks"][0]
    assert "id" in first_task
    assert "user_id" in first_task
    assert "title" in first_task
    assert "description" in first_task
    assert "complete" in first_task
    assert "created_at" in first_task
    assert "updated_at" in first_task


def test_list_tasks_without_token_returns_401(api_client):
    """
    T046: Verify GET /api/{user_id}/tasks without token returns 401.

    Acceptance Scenario 2:
    Given no JWT token, When GET /api/{user_id}/tasks,
    Then return 401 Unauthorized
    """
    # Act: Request tasks without Authorization header
    response = api_client.get("/api/user123/tasks")

    # Assert: Should return 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()
    assert "error" in data or "message" in data or "detail" in data


def test_list_tasks_with_user_id_mismatch_returns_403(api_client, create_jwt_token):
    """
    T047: Verify GET /api/{user_id}/tasks with user_id mismatch returns 403.

    Acceptance Scenario 3:
    Given JWT user_id doesn't match path user_id,
    When GET /api/{user_id}/tasks,
    Then return 403 Forbidden
    """
    # Arrange: Create token for user123
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    # Act: Try to access user456's tasks with user123's token
    response = api_client.get("/api/user456/tasks", headers=headers)

    # Assert: Should return 403 Forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN

    data = response.json()
    assert "error" in data or "message" in data or "detail" in data


def test_list_tasks_with_empty_list_returns_empty_array(api_client, create_jwt_token):
    """
    T048: Verify GET /api/{user_id}/tasks with empty task list returns {"tasks": [], "count": 0}.

    Edge Case:
    Given user has no tasks, When GET /api/{user_id}/tasks,
    Then return empty task list with count 0
    """
    # Arrange: Create token for user999 (new user with no tasks)
    token = create_jwt_token("user999")
    headers = {"Authorization": f"Bearer {token}"}

    # Act: Request tasks for user999 (who has no tasks)
    response = api_client.get("/api/user999/tasks", headers=headers)

    # Assert: Should return 200 with empty list
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["tasks"] == []
    assert data["count"] == 0


def test_list_tasks_filters_by_user_id(api_client, create_jwt_token, test_engine):
    """
    Additional test: Verify tasks are properly filtered by user_id.

    Given multiple users with tasks, When GET /api/{user_id}/tasks,
    Then return only tasks belonging to that user
    """
    # Arrange: Create tasks for multiple users
    from sqlmodel import Session
    from src.database.crud import create_task

    with Session(test_engine) as session:
        # User1 tasks
        create_task(session, "user1", "User1 Task 1")
        create_task(session, "user1", "User1 Task 2")

        # User2 tasks
        create_task(session, "user2", "User2 Task 1")

    # Act: Request tasks for user1
    token1 = create_jwt_token("user1")
    response1 = api_client.get("/api/user1/tasks", headers={"Authorization": f"Bearer {token1}"})

    # Assert: User1 should only see their own tasks
    data1 = response1.json()
    assert response1.status_code == status.HTTP_200_OK
    assert data1["count"] == 2
    assert all(task["user_id"] == "user1" for task in data1["tasks"])
    assert all("User1" in task["title"] for task in data1["tasks"])

    # Act: Request tasks for user2
    token2 = create_jwt_token("user2")
    response2 = api_client.get("/api/user2/tasks", headers={"Authorization": f"Bearer {token2}"})

    # Assert: User2 should only see their own tasks
    data2 = response2.json()
    assert response2.status_code == status.HTTP_200_OK
    assert data2["count"] == 1
    assert all(task["user_id"] == "user2" for task in data2["tasks"])


def test_list_tasks_with_invalid_token_returns_401(api_client, mock_invalid_token):
    """
    Additional test: Verify expired/invalid token returns 401.
    """
    headers = {"Authorization": f"Bearer {mock_invalid_token}"}

    response = api_client.get("/api/user123/tasks", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# User Story 2: Create New Task - Integration Tests (T056-T059)


def test_create_task_with_valid_data_returns_201(api_client, create_jwt_token):
    """
    T056: Verify POST /api/{user_id}/tasks with valid data returns 201 Created.

    Acceptance Scenario 1:
    Given valid JWT token and valid request body,
    When POST /api/{user_id}/tasks,
    Then create task and return 201 Created
    """
    # Arrange
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "New Task",
        "description": "Task description"
    }

    # Act
    response = api_client.post("/api/user123/tasks", headers=headers, json=task_data)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == "user123"
    assert data["title"] == "New Task"
    assert data["description"] == "Task description"
    assert data["complete"] is False
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_without_title_returns_422(api_client, create_jwt_token):
    """
    T057: Verify POST /api/{user_id}/tasks without title returns 422 Unprocessable Entity.

    Acceptance Scenario 2:
    Given missing title in request body,
    When POST /api/{user_id}/tasks,
    Then return 422 Unprocessable Entity
    """
    # Arrange
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "description": "Description without title"
    }

    # Act
    response = api_client.post("/api/user123/tasks", headers=headers, json=task_data)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    data = response.json()
    assert "detail" in data


def test_create_task_with_long_title_returns_422(api_client, create_jwt_token):
    """
    T058: Verify POST /api/{user_id}/tasks with title >200 chars returns 422 validation error.

    Acceptance Scenario 3:
    Given title >200 chars,
    When POST /api/{user_id}/tasks,
    Then return 422 validation error
    """
    # Arrange
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "x" * 201,  # 201 characters (exceeds max 200)
        "description": "Valid description"
    }

    # Act
    response = api_client.post("/api/user123/tasks", headers=headers, json=task_data)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    data = response.json()
    assert "detail" in data


def test_create_task_without_description_returns_201(api_client, create_jwt_token):
    """
    T059: Verify POST /api/{user_id}/tasks without description still succeeds.

    Description is optional, so should return 201 with null description.
    """
    # Arrange
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Task without description"
    }

    # Act
    response = api_client.post("/api/user123/tasks", headers=headers, json=task_data)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["title"] == "Task without description"
    assert data["description"] is None


def test_create_task_without_token_returns_401(api_client):
    """
    Verify POST /api/{user_id}/tasks without token returns 401.
    """
    task_data = {"title": "New Task"}

    response = api_client.post("/api/user123/tasks", json=task_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_task_with_user_id_mismatch_returns_403(api_client, create_jwt_token):
    """
    Verify POST /api/{user_id}/tasks with user_id mismatch returns 403.
    """
    # Arrange: Token for user123
    token = create_jwt_token("user123")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {"title": "New Task"}

    # Act: Try to create task for user456 with user123's token
    response = api_client.post("/api/user456/tasks", headers=headers, json=task_data)

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
