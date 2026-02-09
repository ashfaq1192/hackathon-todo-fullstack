"""Unit tests for delete_task MCP tool.

Tests cover:
- Successful task deletion
- Task not found (404 handling)
- User isolation (cannot delete other users' tasks)
- Verifying task is permanently removed from database
- Database error handling
"""

import pytest
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool

from src.models.task import Task, TaskPriority
from src.mcp.tools.delete_task import delete_task


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


def test_delete_task_success(session):
    """Test successfully deleting a task."""
    task = Task(
        user_id="test_user",
        title="Task to delete",
        complete=False,
        priority=TaskPriority.medium,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    result = delete_task(
        user_id="test_user",
        task_id=task_id,
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] == task_id
    assert result["title"] == "Task to delete"
    assert "deleted" in result["message"].lower() or "🗑️" in result["message"]

    # Verify task is permanently removed from database
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_not_found(session):
    """Test error when task ID doesn't exist."""
    result = delete_task(
        user_id="test_user",
        task_id=99999,  # Non-existent ID
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Task not found"
    assert "not found" in result["message"].lower()


def test_delete_task_wrong_user(session):
    """Test that users cannot delete other users' tasks."""
    task = Task(
        user_id="user_alice",
        title="Alice's task",
        complete=False,
        priority=TaskPriority.high,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # user_bob tries to delete Alice's task
    result = delete_task(
        user_id="user_bob",
        task_id=task.id,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Task not found"
    assert "doesn't belong to you" in result["message"].lower()

    # Verify task still exists
    session.refresh(task)
    assert task is not None


def test_delete_task_missing_database_session():
    """Test error when database session is not provided."""
    result = delete_task(
        user_id="test_user",
        task_id=1,
        db=None,
    )

    assert result["success"] is False
    assert result["error"] == "Database session not provided"
    assert "database connection missing" in result["message"].lower()


def test_delete_completed_task(session):
    """Test deleting a task that's already completed."""
    task = Task(
        user_id="test_user",
        title="Completed task",
        complete=True,  # Already completed
        priority=TaskPriority.low,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    result = delete_task(
        user_id="test_user",
        task_id=task_id,
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] == task_id

    # Verify deletion
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_user_isolation(session):
    """Test that deletion respects user boundaries."""
    task1 = Task(user_id="user_alice", title="Alice task", complete=False)
    task2 = Task(user_id="user_bob", title="Bob task", complete=False)

    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    # Alice deletes her task - should succeed
    result_alice = delete_task(user_id="user_alice", task_id=task1.id, db=session)
    assert result_alice["success"] is True

    # Verify Alice's task is deleted
    assert session.get(Task, task1.id) is None

    # Verify Bob's task still exists
    assert session.get(Task, task2.id) is not None

    # Bob tries to delete Alice's already-deleted task - should fail
    result_bob_fail = delete_task(user_id="user_bob", task_id=task1.id, db=session)
    assert result_bob_fail["success"] is False


def test_delete_multiple_tasks_sequentially(session):
    """Test deleting multiple tasks one by one."""
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

    task1_id = task1.id
    task2_id = task2.id
    task3_id = task3.id

    # Delete them sequentially
    result1 = delete_task(user_id="test_user", task_id=task1_id, db=session)
    result2 = delete_task(user_id="test_user", task_id=task2_id, db=session)
    result3 = delete_task(user_id="test_user", task_id=task3_id, db=session)

    assert result1["success"] is True
    assert result2["success"] is True
    assert result3["success"] is True

    # Verify all are deleted
    assert session.get(Task, task1_id) is None
    assert session.get(Task, task2_id) is None
    assert session.get(Task, task3_id) is None


def test_delete_task_preserves_other_users_tasks(session):
    """Test that deleting one user's tasks doesn't affect others."""
    alice_task = Task(user_id="user_alice", title="Alice task", complete=False)
    bob_task1 = Task(user_id="user_bob", title="Bob task 1", complete=False)
    bob_task2 = Task(user_id="user_bob", title="Bob task 2", complete=False)

    session.add(alice_task)
    session.add(bob_task1)
    session.add(bob_task2)
    session.commit()
    session.refresh(alice_task)
    session.refresh(bob_task1)
    session.refresh(bob_task2)

    # Bob deletes one of his tasks
    result = delete_task(user_id="user_bob", task_id=bob_task1.id, db=session)
    assert result["success"] is True

    # Verify Bob's other task and Alice's task are unaffected
    assert session.get(Task, bob_task2.id) is not None
    assert session.get(Task, alice_task.id) is not None


def test_delete_task_returns_task_details(session):
    """Test that response includes task details for user feedback."""
    task = Task(
        user_id="test_user",
        title="Important Meeting",
        description="With CEO",
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    result = delete_task(user_id="test_user", task_id=task_id, db=session)

    assert result["success"] is True
    assert result["task_id"] == task_id
    assert result["title"] == "Important Meeting"
    assert "Important Meeting" in result["message"]


def test_delete_task_count_verification(session):
    """Test that total task count decreases after deletion."""
    # Create 3 tasks
    for i in range(3):
        task = Task(user_id="test_user", title=f"Task {i}", complete=False)
        session.add(task)
    session.commit()

    # Verify initial count
    initial_count = len(session.exec(select(Task).where(Task.user_id == "test_user")).all())
    assert initial_count == 3

    # Delete one task
    task_to_delete = session.exec(select(Task).where(Task.user_id == "test_user")).first()
    result = delete_task(user_id="test_user", task_id=task_to_delete.id, db=session)
    assert result["success"] is True

    # Verify count decreased
    final_count = len(session.exec(select(Task).where(Task.user_id == "test_user")).all())
    assert final_count == 2


def test_delete_task_with_high_priority(session):
    """Test deleting a high-priority task (no special handling)."""
    task = Task(
        user_id="test_user",
        title="Critical task",
        priority=TaskPriority.high,
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    result = delete_task(user_id="test_user", task_id=task_id, db=session)

    assert result["success"] is True
    assert session.get(Task, task_id) is None


def test_delete_task_double_delete_attempt(session):
    """Test that attempting to delete the same task twice fails on second attempt."""
    task = Task(user_id="test_user", title="Task", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # First delete - should succeed
    result1 = delete_task(user_id="test_user", task_id=task_id, db=session)
    assert result1["success"] is True

    # Second delete - should fail (task no longer exists)
    result2 = delete_task(user_id="test_user", task_id=task_id, db=session)
    assert result2["success"] is False
    assert result2["error"] == "Task not found"
