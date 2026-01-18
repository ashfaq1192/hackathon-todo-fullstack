"""Unit tests for complete_task MCP tool.

Tests cover:
- Successful task completion
- Completing already-completed tasks (idempotency)
- Task not found (404 handling)
- User isolation (cannot complete other users' tasks)
- Database error handling
"""

import pytest
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.task import Task, TaskPriority
from src.mcp.tools.complete_task import complete_task


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


def test_complete_task_success(session):
    """Test successfully marking a task as complete."""
    task = Task(
        user_id="test_user",
        title="Buy groceries",
        complete=False,
        priority=TaskPriority.medium,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = complete_task(
        user_id="test_user",
        task_id=task.id,
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] == task.id
    assert result["title"] == "Buy groceries"
    assert "complete" in result["message"].lower() or "✅" in result["message"]

    # Verify task is marked complete in database
    session.refresh(task)
    assert task.complete is True


def test_complete_task_already_complete(session):
    """Test completing an already-completed task (idempotency)."""
    task = Task(
        user_id="test_user",
        title="Already done",
        complete=True,  # Already complete
        priority=TaskPriority.low,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = complete_task(
        user_id="test_user",
        task_id=task.id,
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] == task.id
    assert "already" in result["message"].lower()
    assert result.get("already_complete") is True

    # Verify task is still complete
    session.refresh(task)
    assert task.complete is True


def test_complete_task_not_found(session):
    """Test error when task ID doesn't exist."""
    result = complete_task(
        user_id="test_user",
        task_id=99999,  # Non-existent ID
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Task not found"
    assert "not found" in result["message"].lower()


def test_complete_task_wrong_user(session):
    """Test that users cannot complete other users' tasks."""
    task = Task(
        user_id="user_alice",
        title="Alice's task",
        complete=False,
        priority=TaskPriority.high,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # user_bob tries to complete Alice's task
    result = complete_task(
        user_id="user_bob",
        task_id=task.id,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Task not found"
    assert "doesn't belong to you" in result["message"].lower()

    # Verify task is still incomplete
    session.refresh(task)
    assert task.complete is False


def test_complete_task_missing_database_session():
    """Test error when database session is not provided."""
    result = complete_task(
        user_id="test_user",
        task_id=1,
        db=None,
    )

    assert result["success"] is False
    assert result["error"] == "Database session not provided"
    assert "database connection missing" in result["message"].lower()


def test_complete_task_preserves_other_fields(session):
    """Test that completing a task doesn't affect other fields."""
    task = Task(
        user_id="test_user",
        title="Original title",
        description="Original description",
        complete=False,
        priority=TaskPriority.high,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    original_created_at = task.created_at

    result = complete_task(
        user_id="test_user",
        task_id=task.id,
        db=session,
    )

    assert result["success"] is True

    # Verify other fields are unchanged
    session.refresh(task)
    assert task.title == "Original title"
    assert task.description == "Original description"
    assert task.priority == TaskPriority.high
    assert task.created_at == original_created_at
    assert task.complete is True  # Only this should change


def test_complete_multiple_tasks(session):
    """Test completing multiple tasks sequentially."""
    task1 = Task(user_id="test_user", title="Task 1", complete=False)
    task2 = Task(user_id="test_user", title="Task 2", complete=False)
    task3 = Task(user_id="test_user", title="Task 3", complete=False)

    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)
    session.refresh(task3)

    # Complete them one by one
    result1 = complete_task(user_id="test_user", task_id=task1.id, db=session)
    result2 = complete_task(user_id="test_user", task_id=task2.id, db=session)
    result3 = complete_task(user_id="test_user", task_id=task3.id, db=session)

    assert result1["success"] is True
    assert result2["success"] is True
    assert result3["success"] is True

    # Verify all are complete
    session.refresh(task1)
    session.refresh(task2)
    session.refresh(task3)

    assert task1.complete is True
    assert task2.complete is True
    assert task3.complete is True


def test_complete_task_user_isolation_multiple_users(session):
    """Test that task completion respects user boundaries with multiple users."""
    task1 = Task(user_id="user_alice", title="Alice task", complete=False)
    task2 = Task(user_id="user_bob", title="Bob task", complete=False)

    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    # Alice completes her task
    result_alice = complete_task(user_id="user_alice", task_id=task1.id, db=session)
    assert result_alice["success"] is True

    # Bob tries to complete Alice's task - should fail
    result_bob_fail = complete_task(user_id="user_bob", task_id=task1.id, db=session)
    assert result_bob_fail["success"] is False

    # Bob completes his own task - should succeed
    result_bob_success = complete_task(user_id="user_bob", task_id=task2.id, db=session)
    assert result_bob_success["success"] is True

    # Verify final states
    session.refresh(task1)
    session.refresh(task2)
    assert task1.complete is True
    assert task2.complete is True


def test_complete_task_returns_task_title(session):
    """Test that response includes the task title for user feedback."""
    task = Task(user_id="test_user", title="Important Meeting", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    result = complete_task(user_id="test_user", task_id=task.id, db=session)

    assert result["success"] is True
    assert result["title"] == "Important Meeting"
    assert "Important Meeting" in result["message"]
