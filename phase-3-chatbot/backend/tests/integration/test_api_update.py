
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from fastapi import status

from src.models.task import Task


def test_update_task_with_valid_data_returns_200(
    api_client: TestClient, create_jwt_token, test_engine
):
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

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "complete": True,
    }

    # Act
    response = api_client.put(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=update_data
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Updated Description"
    assert updated_task["complete"] is True
    assert updated_task["id"] == task_id

    # Verify the task is updated in the database
    with Session(test_engine) as session:
        db_task = session.get(Task, task_id)
        assert db_task.title == "Updated Title"
        assert db_task.description == "Updated Description"
        assert db_task.complete is True


def test_update_task_with_invalid_data_returns_422(
    api_client: TestClient, create_jwt_token, test_engine
):
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

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        # "complete": True,  Missing 'complete' field
    }

    # Act
    response = api_client.put(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=update_data
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_task_non_existent_returns_404(
    api_client: TestClient, create_jwt_token
):
    # Arrange
    user_id = "user123"
    token = create_jwt_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "complete": True,
    }

    # Act
    response = api_client.put(
        f"/api/{user_id}/tasks/999", headers=headers, json=update_data
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_task_with_different_user_returns_403(
    api_client: TestClient, create_jwt_token, test_engine
):
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

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "complete": True,
    }

    # Act
    response = api_client.put(
        f"/api/{user_id}/tasks/{task_id}", headers=headers, json=update_data
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_task_without_token_returns_401(
    api_client: TestClient, test_engine
):
    # Arrange
    user_id = "user123"
    with Session(test_engine) as session:
        task = Task(title="Test Task", description="Test Description", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "complete": True,
    }

    # Act
    response = api_client.put(
        f"/api/{user_id}/tasks/{task_id}", json=update_data
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    