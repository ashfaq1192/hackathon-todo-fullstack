
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.task import Task


def test_patch_task_with_valid_data_returns_200(
    api_client: TestClient, create_jwt_token, test_engine
):
    """
    Test patching a task with valid data returns 200
    """
    # Arrange
    user_id = "user123"
    token = create_jwt_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    patch_data = {"title": "Patched Title"}

    # Act
    response = api_client.patch(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=patch_data
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert updated_task["title"] == "Patched Title"
    assert updated_task["description"] == "Test Description"  # Description should not change
    assert updated_task["id"] == task_id

    # Verify the task is updated in the database
    with Session(test_engine) as session:
        db_task = session.get(Task, task_id)
        assert db_task.title == "Patched Title"
        assert db_task.description == "Test Description"


def test_patch_task_with_complete_only_returns_200(
    api_client: TestClient, create_jwt_token, test_engine
):
    """
    Test patching a task with only 'complete' field returns 200
    """
    # Arrange
    user_id = "user123"
    token = create_jwt_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id, complete=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    patch_data = {"complete": True}

    # Act
    response = api_client.patch(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=patch_data
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert updated_task["complete"] is True
    assert updated_task["title"] == "Test Task"  # Title should not change

    # Verify the task is updated in the database
    with Session(test_engine) as session:
        db_task = session.get(Task, task_id)
        assert db_task.complete is True


def test_patch_task_non_existent_returns_404(
    api_client: TestClient, create_jwt_token
):
    """
    Test patching a non-existent task returns 404
    """
    # Arrange
    user_id = "user123"
    token = create_jwt_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    patch_data = {"title": "Patched Title"}

    # Act
    response = api_client.patch(
        f"/api/{user_id}/tasks/999", headers=headers, json=patch_data
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_patch_task_with_different_user_returns_403(
    api_client: TestClient, create_jwt_token, test_engine
):
    """
    Test patching a task with a different user returns 403
    """
    # Arrange
    user_id = "user123"
    other_user_id = "user456"
    token = create_jwt_token(other_user_id)
    headers = {"Authorization": f"Bearer {token}"}
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    patch_data = {"title": "Patched Title"}

    # Act
    response = api_client.patch(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=patch_data
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_patch_task_without_token_returns_401(
    api_client: TestClient, test_engine
):
    """
    Test patching a task without a token returns 401
    """
    # Arrange
    user_id = "user123"
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    patch_data = {"title": "Patched Title"}

    # Act
    response = api_client.patch(
        f"/api/{user_id}/tasks/{task_id}", json=patch_data
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_patch_task_with_no_data_returns_400(
    api_client: TestClient, create_jwt_token, test_engine
):
    """
    Test patching a task with no data returns 400
    """
    # Arrange
    user_id = "user123"
    token = create_jwt_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    patch_data = {}

    # Act
    response = api_client.patch(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=patch_data
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    