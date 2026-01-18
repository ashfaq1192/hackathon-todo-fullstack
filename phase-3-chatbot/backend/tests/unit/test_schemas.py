"""
Unit tests for Pydantic schemas.

Tests validation rules for API request/response schemas.
"""

import pytest
from pydantic import ValidationError

from src.schemas.task import TaskCreate, TaskPatch, TaskResponse, TaskUpdate


def test_task_create_with_valid_data():
    """
    T026: Verify TaskCreate accepts valid data (required title, optional description).
    """
    # Valid with both title and description
    task = TaskCreate(title="Test Task", description="Test Description")
    assert task.title == "Test Task"
    assert task.description == "Test Description"

    # Valid with only title (description optional)
    task2 = TaskCreate(title="Another Task")
    assert task2.title == "Another Task"
    assert task2.description is None


def test_task_create_missing_title():
    """
    T026: Verify TaskCreate requires title field.
    """
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(description="Description without title")

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)
    assert any(error["type"] == "missing" for error in errors)


def test_task_create_empty_title():
    """
    T026: Verify TaskCreate rejects empty title (min_length=1).
    """
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="")

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)


def test_task_create_title_max_length():
    """
    T027: Verify TaskCreate rejects title >200 chars.
    """
    # Valid title with exactly 200 chars
    valid_title = "x" * 200
    task = TaskCreate(title=valid_title)
    assert len(task.title) == 200

    # Invalid title with 201 chars
    invalid_title = "x" * 201
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title=invalid_title)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)
    assert any("at most 200 characters" in str(error["msg"]).lower() for error in errors)


def test_task_create_description_max_length():
    """
    Verify TaskCreate rejects description >1000 chars.
    """
    # Valid description with exactly 1000 chars
    valid_desc = "x" * 1000
    task = TaskCreate(title="Task", description=valid_desc)
    assert len(task.description) == 1000

    # Invalid description with 1001 chars
    invalid_desc = "x" * 1001
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="Task", description=invalid_desc)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("description",) for error in errors)


def test_task_update_requires_all_fields():
    """
    Verify TaskUpdate requires all fields (title, description, complete).
    """
    # Valid with all fields
    task = TaskUpdate(title="Updated Task", description="Updated Desc", complete=True)
    assert task.title == "Updated Task"
    assert task.description == "Updated Desc"
    assert task.complete is True

    # Invalid without complete field
    with pytest.raises(ValidationError) as exc_info:
        TaskUpdate(title="Task", description="Desc")

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("complete",) for error in errors)


def test_task_patch_allows_partial_updates():
    """
    T028: Verify TaskPatch allows partial updates (all fields optional).
    """
    # Only title
    task1 = TaskPatch(title="New Title")
    assert task1.title == "New Title"
    assert task1.description is None
    assert task1.complete is None

    # Only complete
    task2 = TaskPatch(complete=True)
    assert task2.title is None
    assert task2.description is None
    assert task2.complete is True

    # Only description
    task3 = TaskPatch(description="New Description")
    assert task3.title is None
    assert task3.description == "New Description"
    assert task3.complete is None

    # All fields
    task4 = TaskPatch(title="Title", description="Desc", complete=False)
    assert task4.title == "Title"
    assert task4.description == "Desc"
    assert task4.complete is False

    # No fields (valid for PATCH)
    task5 = TaskPatch()
    assert task5.title is None
    assert task5.description is None
    assert task5.complete is None


def test_task_patch_validates_field_lengths():
    """
    Verify TaskPatch validates field lengths when provided.
    """
    # Invalid title >200 chars
    with pytest.raises(ValidationError) as exc_info:
        TaskPatch(title="x" * 201)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)

    # Invalid description >1000 chars
    with pytest.raises(ValidationError) as exc_info:
        TaskPatch(description="x" * 1001)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("description",) for error in errors)


def test_task_response_from_dict():
    """
    Verify TaskResponse can be created from dictionary (for ORM conversion).
    """
    task_data = {
        "id": 1,
        "user_id": "user123",
        "title": "Test Task",
        "description": "Test Description",
        "complete": False,
        "created_at": "2025-12-20T10:30:00",
        "updated_at": "2025-12-20T10:30:00",
    }

    task = TaskResponse(**task_data)
    assert task.id == 1
    assert task.user_id == "user123"
    assert task.title == "Test Task"
    assert task.complete is False
