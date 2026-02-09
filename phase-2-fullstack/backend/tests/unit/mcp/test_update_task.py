"""Unit tests for update_task MCP tool.

Tests cover:
- Successful task updates (partial updates for each field)
- Updating multiple fields simultaneously
- Validation errors (empty title, too long, invalid priority)
- Task not found (404 handling)
- User isolation (cannot update other users' tasks)
- Database error handling
"""

import pytest
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.task import Task, TaskPriority
from src.mcp.tools.update_task import update_task


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Task.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_update_task_title_only(session):
    """Test updating only the title field."""
    task = Task(
        user_id="test_user",
        title="Old Title",
        description="Original description",
        priority=TaskPriority.medium,
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        title="New Title",
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] == task.id
    assert result["updated_fields"] == ["title"]
    assert "title" in result["message"].lower()

    # Verify changes
    session.refresh(task)
    assert task.title == "New Title"
    assert task.description == "Original description"  # Unchanged
    assert task.priority == TaskPriority.medium  # Unchanged


def test_update_task_description_only(session):
    """Test updating only the description field."""
    task = Task(
        user_id="test_user",
        title="Task Title",
        description="Old description",
        priority=TaskPriority.low,
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        description="New detailed description",
        db=session,
    )

    assert result["success"] is True
    assert result["updated_fields"] == ["description"]

    session.refresh(task)
    assert task.description == "New detailed description"
    assert task.title == "Task Title"  # Unchanged


def test_update_task_priority_only(session):
    """Test updating only the priority field."""
    task = Task(
        user_id="test_user",
        title="Task",
        priority=TaskPriority.low,
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        priority="high",
        db=session,
    )

    assert result["success"] is True
    assert result["updated_fields"] == ["priority"]

    session.refresh(task)
    assert task.priority == TaskPriority.high


def test_update_task_multiple_fields(session):
    """Test updating multiple fields simultaneously."""
    task = Task(
        user_id="test_user",
        title="Old",
        description="Old desc",
        priority=TaskPriority.low,
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        title="New Title",
        description="New description",
        priority="high",
        db=session,
    )

    assert result["success"] is True
    assert set(result["updated_fields"]) == {"title", "description", "priority"}

    session.refresh(task)
    assert task.title == "New Title"
    assert task.description == "New description"
    assert task.priority == TaskPriority.high


def test_update_task_no_fields_provided(session):
    """Test error when no fields are provided for update."""
    task = Task(user_id="test_user", title="Task", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "No fields to update"
    assert "at least one field" in result["message"].lower()


def test_update_task_empty_title(session):
    """Test error when title is empty or whitespace."""
    task = Task(user_id="test_user", title="Original", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        title="   ",  # Whitespace only
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Title cannot be empty"


def test_update_task_title_too_long(session):
    """Test error when title exceeds 200 characters."""
    task = Task(user_id="test_user", title="Original", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    long_title = "A" * 201  # 201 characters

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        title=long_title,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Title too long"
    assert "200 characters" in result["message"]


def test_update_task_description_too_long(session):
    """Test error when description exceeds 1000 characters."""
    task = Task(user_id="test_user", title="Task", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    long_desc = "B" * 1001  # 1001 characters

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        description=long_desc,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Description too long"
    assert "1000 characters" in result["message"]


def test_update_task_invalid_priority(session):
    """Test error when priority is invalid."""
    task = Task(user_id="test_user", title="Task", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        priority="urgent",  # Invalid - should be low/medium/high
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Invalid priority"
    assert "low" in result["message"].lower()
    assert "medium" in result["message"].lower()
    assert "high" in result["message"].lower()


def test_update_task_not_found(session):
    """Test error when task ID doesn't exist."""
    result = update_task(
        user_id="test_user",
        task_id=99999,  # Non-existent
        title="New Title",
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Task not found"
    assert "not found" in result["message"].lower()


def test_update_task_wrong_user(session):
    """Test that users cannot update other users' tasks."""
    task = Task(user_id="user_alice", title="Alice's task", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    # user_bob tries to update Alice's task
    result = update_task(
        user_id="user_bob",
        task_id=task.id,
        title="Bob's update",
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Task not found"
    assert "doesn't belong to you" in result["message"].lower()

    # Verify task is unchanged
    session.refresh(task)
    assert task.title == "Alice's task"


def test_update_task_strips_whitespace(session):
    """Test that title and description whitespace is stripped."""
    task = Task(user_id="test_user", title="Original", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        title="  New Title  ",
        description="  New Description  ",
        db=session,
    )

    assert result["success"] is True

    session.refresh(task)
    assert task.title == "New Title"
    assert task.description == "New Description"


def test_update_task_clear_description(session):
    """Test clearing description by setting to empty string."""
    task = Task(
        user_id="test_user",
        title="Task",
        description="Has description",
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        description="",
        db=session,
    )

    assert result["success"] is True

    session.refresh(task)
    assert task.description is None  # Empty string becomes None


def test_update_task_preserves_complete_status(session):
    """Test that updating doesn't affect complete status."""
    task = Task(
        user_id="test_user",
        title="Completed Task",
        complete=True,  # Already complete
        priority=TaskPriority.low,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = update_task(
        user_id="test_user",
        task_id=task.id,
        title="Updated Title",
        db=session,
    )

    assert result["success"] is True

    session.refresh(task)
    assert task.complete is True  # Should remain complete
    assert task.title == "Updated Title"


def test_update_task_missing_database_session():
    """Test error when database session is not provided."""
    result = update_task(
        user_id="test_user",
        task_id=1,
        title="New Title",
        db=None,
    )

    assert result["success"] is False
    assert result["error"] == "Database session not provided"


def test_update_task_all_priority_values(session):
    """Test updating to all valid priority values."""
    task = Task(user_id="test_user", title="Task", priority=TaskPriority.medium, complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Update to low
    result_low = update_task(user_id="test_user", task_id=task.id, priority="low", db=session)
    assert result_low["success"] is True
    session.refresh(task)
    assert task.priority == TaskPriority.low

    # Update to high
    result_high = update_task(user_id="test_user", task_id=task.id, priority="high", db=session)
    assert result_high["success"] is True
    session.refresh(task)
    assert task.priority == TaskPriority.high

    # Update back to medium
    result_medium = update_task(user_id="test_user", task_id=task.id, priority="medium", db=session)
    assert result_medium["success"] is True
    session.refresh(task)
    assert task.priority == TaskPriority.medium
