"""
Pydantic schemas for Task API requests and responses.

These schemas define the structure and validation rules for API data,
separate from the database models to provide clear API contracts.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.task import RecurringType, TaskPriority


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    priority: TaskPriority = Field(default=TaskPriority.medium, description="Task priority level")
    due_date: datetime | None = Field(None, description="Task deadline")
    recurring: RecurringType = Field(default=RecurringType.none, description="Recurring schedule type")
    recurring_end_date: datetime | None = Field(None, description="End date for recurring schedule")
    tags: list[str] = Field(default_factory=list, description="Task tags/categories")


class TaskUpdate(BaseModel):
    """Schema for full task update (PUT request). All fields required."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    complete: bool = Field(..., description="Task completion status")
    priority: TaskPriority = Field(..., description="Task priority level")
    due_date: datetime | None = Field(None, description="Task deadline")
    recurring: RecurringType = Field(default=RecurringType.none, description="Recurring schedule type")
    recurring_end_date: datetime | None = Field(None, description="End date for recurring schedule")
    tags: list[str] = Field(default_factory=list, description="Task tags/categories")


class TaskPatch(BaseModel):
    """Schema for partial task update (PATCH request). All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    complete: bool | None = Field(None, description="Task completion status")
    priority: TaskPriority | None = Field(None, description="Task priority level")
    due_date: datetime | None = Field(None, description="Task deadline")
    recurring: RecurringType | None = Field(None, description="Recurring schedule type")
    recurring_end_date: datetime | None = Field(None, description="End date for recurring schedule")
    tags: list[str] | None = Field(None, description="Task tags/categories")


class TaskResponse(BaseModel):
    """Schema for task response (all endpoints return this)."""

    id: int
    user_id: str
    title: str
    description: str | None
    complete: bool
    priority: TaskPriority
    due_date: datetime | None
    recurring: RecurringType
    recurring_end_date: datetime | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
    count: int


class TaskQueryParams(BaseModel):
    """Query parameters for searching, filtering, and sorting tasks."""

    search: str | None = Field(None, description="Keyword search in title/description")
    status: str | None = Field(None, description="Filter by status: all/pending/completed")
    priority: TaskPriority | None = Field(None, description="Filter by priority level")
    tags: list[str] | None = Field(None, description="Filter by tags")
    sort_by: str = Field(default="created_at", description="Sort field: created_at/due_date/priority/title")
    sort_order: str = Field(default="desc", description="Sort order: asc/desc")
