"""Unit tests for add_task MCP tool.

Tests cover:
- Successful task creation with all fields
- Successful task creation with minimal fields (title only)
- Validation errors (missing title, too long title/description)
- Invalid priority values
- Database error handling
"""

import pytest
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.task import Task
from src.mcp.tools.add_task import add_task


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


def test_add_task_success_full_details(session):
    """Test adding task with all fields provided."""
    result = add_task(
        user_id="test_user_123",
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="high",
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] is not None
    assert result["title"] == "Buy groceries"
    assert "SUCCESS: Task" in result["message"]

    # Verify task was saved to database
    task = session.get(Task, result["task_id"])
    assert task is not None
    assert task.user_id == "test_user_123"
    assert task.title == "Buy groceries"
    assert task.complete is False


def test_add_task_success_minimal_fields(session):
    """Test adding task with only required title field."""
    result = add_task(
        user_id="test_user_456",
        title="Simple task",
        db=session,
    )

    assert result["success"] is True
    assert result["task_id"] is not None
    assert result["title"] == "Simple task"
    assert "Priority: medium" in result["message"]

    # Verify in database
    task = session.get(Task, result["task_id"])
    assert task is not None
    assert task.description is None
    assert task.priority.value == "medium"


def test_add_task_strips_whitespace(session):
    """Test that title and description whitespace is stripped."""
    result = add_task(
        user_id="test_user",
        title="  Task with spaces  ",
        description="  Description with spaces  ",
        db=session,
    )

    assert result["success"] is True
    assert result["title"] == "Task with spaces"

    # Verify task was saved to database and check stripped description
    task = session.get(Task, result["task_id"])
    assert task.title == "Task with spaces"
    assert task.description == "Description with spaces"



def test_add_task_missing_title(session):
    """Test error when title is empty or missing."""
    result = add_task(
        user_id="test_user",
        title="",
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Empty title"
    assert "provide a task title" in result["message"]


def test_add_task_title_too_long(session):
    """Test error when title exceeds 200 characters."""
    long_title = "A" * 201  # 201 characters

    result = add_task(
        user_id="test_user",
        title=long_title,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Title too long"
    assert "200 characters or less" in result["message"]
    assert "201" in result["message"]


def test_add_task_description_too_long(session):
    """Test error when description exceeds 1000 characters."""
    long_description = "B" * 1001  # 1001 characters

    result = add_task(
        user_id="test_user",
        title="Valid title",
        description=long_description,
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Description too long"
    assert "1000 characters or less" in result["message"]
    assert "1001" in result["message"]


def test_add_task_invalid_priority(session):
    """Test error when invalid priority value is provided."""
    result = add_task(
        user_id="test_user",
        title="Task with invalid priority",
        priority="urgent",  # Invalid - should be low/medium/high
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Invalid priority"
    assert "low" in result["message"]
    assert "medium" in result["message"]
    assert "high" in result["message"]


def test_add_task_missing_database_session():
    """Test error when database session is not provided."""
    result = add_task(
        user_id="test_user",
        title="Task without DB",
        db=None,
    )

    assert result["success"] is False
    assert result["error"] == "Database session not provided"
    assert "database connection missing" in result["message"]


def test_add_task_user_isolation(session):
    """Test that tasks are properly isolated by user_id."""
    # Create tasks for two different users
    result1 = add_task(
        user_id="user_alice",
        title="Alice's task",
        db=session,
    )

    result2 = add_task(
        user_id="user_bob",
        title="Bob's task",
        db=session,
    )

    assert result1["success"] is True
    assert result2["success"] is True

    # Verify tasks are stored with correct user_ids
    task1 = session.get(Task, result1["task_id"])
    task2 = session.get(Task, result2["task_id"])

    assert task1.user_id == "user_alice"
    assert task2.user_id == "user_bob"
    assert task1.id != task2.id


def test_add_task_priority_variations(session):
    """Test all valid priority values."""
    for priority in ["low", "medium", "high"]:
        result = add_task(
            user_id="test_user",
            title=f"Task with {priority} priority",
            priority=priority,
            db=session,
        )

        assert result["success"] is True

        task = session.get(Task, result["task_id"])
        assert task.priority.value == priority


def test_add_task_with_due_date(session):
    """Test adding task with a due date."""
    result = add_task(
        user_id="test_user",
        title="Task with deadline",
        due_date="2026-02-15T10:00:00",
        db=session,
    )

    assert result["success"] is True
    assert "Due:" in result["message"]

    task = session.get(Task, result["task_id"])
    assert task.due_date is not None


def test_add_task_with_invalid_due_date(session):
    """Test error when due date format is invalid."""
    result = add_task(
        user_id="test_user",
        title="Task with bad date",
        due_date="not-a-date",
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Invalid due_date"


def test_add_task_with_recurring(session):
    """Test adding task with recurring schedule."""
    result = add_task(
        user_id="test_user",
        title="Daily standup",
        recurring="daily",
        db=session,
    )

    assert result["success"] is True
    assert "Recurring: daily" in result["message"]

    task = session.get(Task, result["task_id"])
    assert task.recurring.value == "daily"


def test_add_task_with_invalid_recurring(session):
    """Test error when recurring type is invalid."""
    result = add_task(
        user_id="test_user",
        title="Task with bad recurring",
        recurring="biweekly",
        db=session,
    )

    assert result["success"] is False
    assert result["error"] == "Invalid recurring type"


def test_add_task_with_tags(session):
    """Test adding task with tags."""
    result = add_task(
        user_id="test_user",
        title="Tagged task",
        tags=["work", "urgent"],
        db=session,
    )

    assert result["success"] is True
    assert "Tags:" in result["message"]

    task = session.get(Task, result["task_id"])
    assert task.tags == ["work", "urgent"]


def test_add_task_tags_cleaned(session):
    """Test that tags are lowercased and stripped."""
    result = add_task(
        user_id="test_user",
        title="Task with messy tags",
        tags=["  Work  ", "URGENT", ""],
        db=session,
    )

    assert result["success"] is True

    task = session.get(Task, result["task_id"])
    assert "work" in task.tags
    assert "urgent" in task.tags
    assert "" not in task.tags


def test_add_task_with_all_new_fields(session):
    """Test adding task with all advanced fields."""
    result = add_task(
        user_id="test_user",
        title="Complete task",
        description="With all fields",
        priority="high",
        due_date="2026-03-01T09:00:00",
        recurring="weekly",
        tags=["project", "review"],
        db=session,
    )

    assert result["success"] is True
    assert "Due:" in result["message"]
    assert "Recurring: weekly" in result["message"]
    assert "Tags:" in result["message"]

    task = session.get(Task, result["task_id"])
    assert task.due_date is not None
    assert task.recurring.value == "weekly"
    assert task.tags == ["project", "review"]
