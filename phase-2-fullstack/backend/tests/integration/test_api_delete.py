
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.task import Task


def test_delete_task_with_valid_data_returns_204(
    api_client: TestClient, create_jwt_token, test_engine
):
    """
    Test deleting a task with valid data returns 204
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

    # Act
    response = api_client.delete(
        f"/api/{user_id}/tasks/{task_id}", headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the task is deleted from the database
    with Session(test_engine) as session:
        db_task = session.get(Task, task_id)
        assert db_task is None


def test_delete_task_non_existent_returns_404(
    api_client: TestClient, create_jwt_token
):
    """
    Test deleting a non-existent task returns 404
    """
    # Arrange
    user_id = "user123"
    token = create_jwt_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Act
    response = api_client.delete(
        f"/api/{user_id}/tasks/999", headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_task_with_different_user_returns_403(
    api_client: TestClient, create_jwt_token, test_engine
):
    """
    Test deleting a task with a different user returns 403
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

    # Act
    response = api_client.delete(
        f"/api/{user_id}/tasks/{task_id}", headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_task_without_token_returns_401(
    api_client: TestClient, test_engine
):
    """
    Test deleting a task without a token returns 401
    """
    # Arrange
    user_id = "user123"
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    # Act
    response = api_client.delete(f"/api/{user_id}/tasks/{task_id}")

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    