"""Unit tests for list_tasks MCP tool.

Tests cover:
- Successful task listing with all statuses (all/pending/completed)
- Empty task lists with appropriate messages
- User isolation (different users see different tasks)
- Status filtering functionality
- Database error handling
"""

import pytest
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.task import Task, TaskPriority
from src.mcp.tools.list_tasks import list_tasks


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


@pytest.fixture(name="sample_tasks")
def sample_tasks_fixture(session):
    """Create sample tasks for testing."""
    tasks = [
        Task(user_id="test_user", title="Pending task 1", complete=False, priority=TaskPriority.high),
        Task(user_id="test_user", title="Pending task 2", complete=False, priority=TaskPriority.medium),
        Task(user_id="test_user", title="Completed task 1", complete=True, priority=TaskPriority.low),
        Task(user_id="test_user", title="Completed task 2", complete=True, priority=TaskPriority.medium),
        Task(user_id="other_user", title="Other user task", complete=False, priority=TaskPriority.high),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


def test_list_all_tasks_success(session, sample_tasks):
    """Test listing all tasks (pending + completed)."""
    result = list_tasks(
        user_id="test_user",
        status="all",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 4  # 2 pending + 2 completed for test_user
    assert len(result["tasks"]) == 4
    assert "4" in result["message"]

    # Verify task details are included
    for task in result["tasks"]:
        assert "id" in task
        assert "title" in task
        assert "complete" in task
        assert "priority" in task
        assert "created_at" in task


def test_list_pending_tasks_only(session, sample_tasks):
    """Test filtering for pending tasks only."""
    result = list_tasks(
        user_id="test_user",
        status="pending",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 2  # 2 pending tasks
    assert len(result["tasks"]) == 2

    # Verify all returned tasks are pending
    for task in result["tasks"]:
        assert task["complete"] is False


def test_list_completed_tasks_only(session, sample_tasks):
    """Test filtering for completed tasks only."""
    result = list_tasks(
        user_id="test_user",
        status="completed",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 2  # 2 completed tasks
    assert len(result["tasks"]) == 2

    # Verify all returned tasks are completed
    for task in result["tasks"]:
        assert task["complete"] is True


def test_list_tasks_empty_all(session):
    """Test listing all tasks when user has none."""
    result = list_tasks(
        user_id="user_with_no_tasks",
        status="all",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 0
    assert len(result["tasks"]) == 0
    assert "no tasks" in result["message"].lower()


def test_list_tasks_empty_pending(session, sample_tasks):
    """Test listing pending tasks when all are completed."""
    # Mark all test_user tasks as complete
    for task in sample_tasks[:4]:  # First 4 are test_user's tasks
        task.complete = True
        session.add(task)
    session.commit()

    result = list_tasks(
        user_id="test_user",
        status="pending",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 0
    assert "no pending tasks" in result["message"].lower()
    assert "great job" in result["message"].lower() or "🎉" in result["message"]


def test_list_tasks_empty_completed(session):
    """Test listing completed tasks when none exist."""
    # Create only pending tasks
    task = Task(user_id="test_user", title="Pending", complete=False)
    session.add(task)
    session.commit()

    result = list_tasks(
        user_id="test_user",
        status="completed",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 0
    assert "no completed tasks" in result["message"].lower()


def test_list_tasks_user_isolation(session, sample_tasks):
    """Test that users only see their own tasks."""
    # test_user should see 4 tasks
    result_test = list_tasks(
        user_id="test_user",
        status="all",
        db=session,
    )

    # other_user should see 1 task
    result_other = list_tasks(
        user_id="other_user",
        status="all",
        db=session,
    )

    assert result_test["count"] == 4
    assert result_other["count"] == 1

    # Verify task titles don't leak between users
    test_user_titles = [task["title"] for task in result_test["tasks"]]
    other_user_titles = [task["title"] for task in result_other["tasks"]]

    assert "Other user task" not in test_user_titles
    assert "Pending task 1" not in other_user_titles


def test_list_tasks_includes_all_fields(session):
    """Test that all task fields are included in response."""
    task = Task(
        user_id="test_user",
        title="Test Task",
        description="Test description",
        complete=False,
        priority=TaskPriority.high,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    result = list_tasks(
        user_id="test_user",
        status="all",
        db=session,
    )

    assert result["success"] is True
    task_data = result["tasks"][0]

    assert task_data["id"] == task.id
    assert task_data["title"] == "Test Task"
    assert task_data["description"] == "Test description"
    assert task_data["complete"] is False
    assert task_data["priority"] == "high"
    assert "created_at" in task_data


def test_list_tasks_missing_database_session():
    """Test error when database session is not provided."""
    result = list_tasks(
        user_id="test_user",
        status="all",
        db=None,
    )

    assert result["success"] is False
    assert result["error"] == "Database session not provided"
    assert result["count"] == 0
    assert result["tasks"] == []


def test_list_tasks_default_status_all(session, sample_tasks):
    """Test that default status is 'all'."""
    result = list_tasks(
        user_id="test_user",
        db=session,
    )

    assert result["success"] is True
    assert result["count"] == 4  # Should get all tasks (default)


def test_list_tasks_message_variations(session):
    """Test different message variations based on count and status."""
    # No tasks at all
    result_empty = list_tasks(user_id="user1", status="all", db=session)
    assert "no tasks" in result_empty["message"].lower()

    # Single task
    task = Task(user_id="user2", title="Single", complete=False)
    session.add(task)
    session.commit()

    result_one = list_tasks(user_id="user2", status="all", db=session)
    assert "1 task" in result_one["message"].lower()
    assert "tasks" not in result_one["message"] or "1 task" in result_one["message"]  # Singular form

    # Multiple tasks
    task2 = Task(user_id="user3", title="Task 1", complete=False)
    task3 = Task(user_id="user3", title="Task 2", complete=False)
    session.add(task2)
    session.add(task3)
    session.commit()

    result_multiple = list_tasks(user_id="user3", status="all", db=session)
    assert "2" in result_multiple["message"]
    assert "tasks" in result_multiple["message"].lower()  # Plural form


def test_list_tasks_priority_values(session):
    """Test that priority values are correctly returned."""
    tasks = [
        Task(user_id="test_user", title="Low", priority=TaskPriority.low, complete=False),
        Task(user_id="test_user", title="Medium", priority=TaskPriority.medium, complete=False),
        Task(user_id="test_user", title="High", priority=TaskPriority.high, complete=False),
    ]
    for task in tasks:
        session.add(task)
    session.commit()

    result = list_tasks(user_id="test_user", status="all", db=session)

    priorities = [task["priority"] for task in result["tasks"]]
    assert "low" in priorities
    assert "medium" in priorities
    assert "high" in priorities
