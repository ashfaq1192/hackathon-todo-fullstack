"""
Task model for persistent todo storage.

This module defines the Task SQLModel with proper validation,
defaults, and timestamp management for the Neon PostgreSQL database.
"""

import json
from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import String, Text, TypeDecorator
from sqlmodel import Field, SQLModel


class StringArrayType(TypeDecorator):
    """Portable array type: uses ARRAY(String) on PostgreSQL, JSON-encoded TEXT on SQLite."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        return json.dumps(value or [])

    def process_result_value(self, value, dialect):
        if dialect.name == "postgresql":
            return value or []
        if not value:
            return []
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []


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


class RecurringType(str, Enum):
    """
    Recurring schedule types for tasks.

    Values:
        none: Non-recurring task (default)
        daily: Repeats every day
        weekly: Repeats every week
        monthly: Repeats every month
        yearly: Repeats every year
    """
    none = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


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
        due_date: Optional deadline for the task
        recurring: Recurring schedule type (none/daily/weekly/monthly/yearly)
        recurring_end_date: Optional end date for recurring schedule
        tags: List of tag labels (e.g., work, home, personal)
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

    # Due date - optional deadline
    due_date: Optional[datetime] = Field(default=None)

    # Recurring schedule
    recurring: RecurringType = Field(default=RecurringType.none)
    recurring_end_date: Optional[datetime] = Field(default=None)

    # Tags - portable array type (ARRAY on PostgreSQL, JSON on SQLite)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(StringArrayType(), nullable=False, server_default="{}"),
    )

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
                "title": "Complete Phase V Stage 1",
                "description": "Add advanced features to tasks",
                "complete": False,
                "priority": "medium",
                "due_date": "2026-02-15T10:00:00Z",
                "recurring": "none",
                "tags": ["work", "hackathon"],
            }
        }
    )
