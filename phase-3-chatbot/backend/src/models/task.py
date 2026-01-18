"""
Task model for persistent todo storage.

This module defines the Task SQLModel with proper validation,
defaults, and timestamp management for the Neon PostgreSQL database.
"""

from datetime import UTC, datetime
from enum import Enum

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class TaskPriority(str, Enum):
    """
    Priority levels for tasks.

    Values:
        low: Low priority task
        medium: Medium priority task (default)
        high: High priority task
    """
    low = "low"
    medium = "medium"
    high = "high"


class Task(SQLModel, table=True):
    """
    Task model for persistent todo storage.

    Attributes:
        id: Auto-generated primary key
        user_id: Owner of the task (indexed for multi-user queries)
        title: Task title (required, max 200 chars)
        description: Optional detailed description (max 1000 chars)
        complete: Completion status (defaults to False)
        priority: Task priority (low/medium/high, defaults to medium)
        created_at: Creation timestamp (auto-generated UTC)
        updated_at: Last modification timestamp (auto-updated UTC)
    """

    __tablename__ = "tasks"

    # Primary key - auto-generated
    id: int | None = Field(default=None, primary_key=True)

    # User identification - required and indexed for efficient queries
    user_id: str = Field(index=True, min_length=1)

    # Task content - title is required, description is optional
    title: str = Field(max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=1000)

    # Completion status - defaults to False for new tasks
    complete: bool = Field(default=False)

    # Priority level - defaults to medium for new tasks
    priority: TaskPriority = Field(default=TaskPriority.medium)

    # Timestamps - auto-generated and auto-updated
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "user_abc123",
                "title": "Complete Phase II Stage 1",
                "description": "Set up database with Neon and SQLModel",
                "complete": False,
                "priority": "medium",
            }
        }
    )
