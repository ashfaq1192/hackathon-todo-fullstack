"""
Integration tests for search, filter, and sort functionality.

Tests cover:
- Keyword search in title/description (ILIKE)
- Status filtering (all/pending/completed)
- Priority filtering
- Sort by created_at, due_date, priority, title
- Sort order (asc/desc)
- Combination of filters and sorts
"""

import pytest
from datetime import datetime, UTC, timedelta
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.task import Task, TaskPriority, RecurringType
from src.database.crud import get_tasks_filtered


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
    """Create a diverse set of tasks for testing search/filter/sort."""
    now = datetime.now(UTC)
    tasks = [
        Task(
            user_id="test_user",
            title="Buy groceries",
            description="Milk, eggs, bread from the store",
            priority=TaskPriority.medium,
            complete=False,
            due_date=now + timedelta(days=2),
            tags=["personal", "shopping"],
        ),
        Task(
            user_id="test_user",
            title="Review pull request",
            description="Review the backend API changes",
            priority=TaskPriority.high,
            complete=False,
            due_date=now + timedelta(days=1),
            tags=["work", "code"],
        ),
        Task(
            user_id="test_user",
            title="Schedule dentist appointment",
            description=None,
            priority=TaskPriority.low,
            complete=True,
            tags=["personal", "health"],
        ),
        Task(
            user_id="test_user",
            title="Write project report",
            description="Final report for the hackathon project",
            priority=TaskPriority.high,
            complete=False,
            due_date=now + timedelta(days=3),
            recurring=RecurringType.weekly,
            tags=["work", "writing"],
        ),
        Task(
            user_id="test_user",
            title="Clean the house",
            description="Vacuum and mop all rooms",
            priority=TaskPriority.low,
            complete=True,
            tags=["personal", "chores"],
        ),
        Task(
            user_id="other_user",
            title="Other user task",
            description="Should not appear",
            priority=TaskPriority.high,
            complete=False,
        ),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


def test_search_by_title(session, sample_tasks):
    """Test keyword search matches in title."""
    results = get_tasks_filtered(session, "test_user", search="groceries")
    assert len(results) == 1
    assert results[0].title == "Buy groceries"


def test_search_by_description(session, sample_tasks):
    """Test keyword search matches in description."""
    results = get_tasks_filtered(session, "test_user", search="hackathon")
    assert len(results) == 1
    assert results[0].title == "Write project report"


def test_search_case_insensitive(session, sample_tasks):
    """Test search is case-insensitive."""
    results = get_tasks_filtered(session, "test_user", search="PULL REQUEST")
    assert len(results) == 1
    assert results[0].title == "Review pull request"


def test_search_no_results(session, sample_tasks):
    """Test search with no matches returns empty list."""
    results = get_tasks_filtered(session, "test_user", search="nonexistent")
    assert len(results) == 0


def test_filter_pending_only(session, sample_tasks):
    """Test filtering for pending tasks only."""
    results = get_tasks_filtered(session, "test_user", status="pending")
    assert len(results) == 3
    assert all(not t.complete for t in results)


def test_filter_completed_only(session, sample_tasks):
    """Test filtering for completed tasks only."""
    results = get_tasks_filtered(session, "test_user", status="completed")
    assert len(results) == 2
    assert all(t.complete for t in results)


def test_filter_all_status(session, sample_tasks):
    """Test filtering with 'all' returns everything for user."""
    results = get_tasks_filtered(session, "test_user", status="all")
    assert len(results) == 5  # All test_user tasks


def test_filter_by_priority(session, sample_tasks):
    """Test filtering by priority level."""
    high_results = get_tasks_filtered(session, "test_user", priority="high")
    assert len(high_results) == 2
    assert all(t.priority == TaskPriority.high for t in high_results)

    low_results = get_tasks_filtered(session, "test_user", priority="low")
    assert len(low_results) == 2
    assert all(t.priority == TaskPriority.low for t in low_results)


def test_sort_by_title_asc(session, sample_tasks):
    """Test sorting by title ascending."""
    results = get_tasks_filtered(session, "test_user", sort_by="title", sort_order="asc")
    titles = [t.title for t in results]
    assert titles == sorted(titles)


def test_sort_by_title_desc(session, sample_tasks):
    """Test sorting by title descending."""
    results = get_tasks_filtered(session, "test_user", sort_by="title", sort_order="desc")
    titles = [t.title for t in results]
    assert titles == sorted(titles, reverse=True)


def test_sort_by_priority(session, sample_tasks):
    """Test sorting by priority (high > medium > low)."""
    results = get_tasks_filtered(session, "test_user", sort_by="priority", sort_order="desc")
    priority_values = {"high": 3, "medium": 2, "low": 1}
    values = [priority_values.get(t.priority.value, 0) for t in results]
    # Verify descending order
    for i in range(len(values) - 1):
        assert values[i] >= values[i + 1]


def test_sort_by_priority_asc(session, sample_tasks):
    """Test sorting by priority ascending (low first)."""
    results = get_tasks_filtered(session, "test_user", sort_by="priority", sort_order="asc")
    priority_values = {"high": 3, "medium": 2, "low": 1}
    values = [priority_values.get(t.priority.value, 0) for t in results]
    for i in range(len(values) - 1):
        assert values[i] <= values[i + 1]


def test_sort_by_created_at(session, sample_tasks):
    """Test sorting by created_at (default)."""
    results = get_tasks_filtered(session, "test_user", sort_by="created_at", sort_order="desc")
    dates = [t.created_at for t in results]
    for i in range(len(dates) - 1):
        assert dates[i] >= dates[i + 1]


def test_combined_search_and_filter(session, sample_tasks):
    """Test combining search with status filter."""
    # Search for 'report' among pending tasks
    results = get_tasks_filtered(
        session, "test_user",
        search="report",
        status="pending",
    )
    assert len(results) == 1
    assert results[0].title == "Write project report"
    assert results[0].complete is False


def test_combined_filter_and_sort(session, sample_tasks):
    """Test combining priority filter with sort."""
    results = get_tasks_filtered(
        session, "test_user",
        status="pending",
        sort_by="title",
        sort_order="asc",
    )
    assert len(results) == 3
    titles = [t.title for t in results]
    assert titles == sorted(titles)


def test_user_isolation(session, sample_tasks):
    """Test that filtering only returns user's own tasks."""
    results = get_tasks_filtered(session, "test_user")
    assert len(results) == 5

    other_results = get_tasks_filtered(session, "other_user")
    assert len(other_results) == 1
    assert other_results[0].title == "Other user task"


def test_invalid_priority_filter_ignored(session, sample_tasks):
    """Test that invalid priority values are silently ignored."""
    results = get_tasks_filtered(session, "test_user", priority="urgent")
    # Should return all tasks since invalid priority is ignored
    assert len(results) == 5
