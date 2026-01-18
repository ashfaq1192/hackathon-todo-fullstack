"""
Pydantic schemas for Task API requests and responses.

These schemas define the structure and validation rules for API data,
separate from the database models to provide clear API contracts.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.task import TaskPriority


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Attributes:
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        priority: Task priority (low/medium/high, defaults to medium)

    Example:
        {
            "title": "Complete Phase II Stage 2",
            "description": "Implement FastAPI REST API",
            "priority": "medium"
        }
    """

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    priority: TaskPriority = Field(default=TaskPriority.medium, description="Task priority level")


class TaskUpdate(BaseModel):
    """
    Schema for full task update (PUT request).

    All fields are required for PUT (full replacement).

    Attributes:
        title: Task title (required, 1-200 chars)
        description: Optional task description (max 1000 chars)
        complete: Task completion status
        priority: Task priority level

    Example:
        {
            "title": "Updated Task Title",
            "description": "Updated description",
            "complete": true,
            "priority": "high"
        }
    """

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    complete: bool = Field(..., description="Task completion status")
    priority: TaskPriority = Field(..., description="Task priority level")


class TaskPatch(BaseModel):
    """
    Schema for partial task update (PATCH request).

    All fields are optional for PATCH (partial update).

    Attributes:
        title: Task title (optional, 1-200 chars if provided)
        description: Task description (optional, max 1000 chars if provided)
        complete: Task completion status (optional)
        priority: Task priority level (optional)

    Example:
        {
            "complete": true,
            "priority": "high"
        }
    """

    title: str | None = Field(None, min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")
    complete: bool | None = Field(None, description="Task completion status")
    priority: TaskPriority | None = Field(None, description="Task priority level")


class TaskResponse(BaseModel):
    """
    Schema for task response (all endpoints return this).

    Includes all task fields from the database model.

    Attributes:
        id: Task ID (auto-generated)
        user_id: Owner of the task
        title: Task title
        description: Task description (nullable)
        complete: Task completion status
        priority: Task priority level
        created_at: Task creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC)

    Example:
        {
            "id": 1,
            "user_id": "user_abc123",
            "title": "Complete Phase II Stage 2",
            "description": "Implement FastAPI REST API",
            "complete": false,
            "priority": "medium",
            "created_at": "2025-12-20T10:30:00Z",
            "updated_at": "2025-12-20T10:30:00Z"
        }
    """

    id: int
    user_id: str
    title: str
    description: str | None
    complete: bool
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode to convert SQLModel objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """
    Schema for task list response (GET /api/{user_id}/tasks).

    Attributes:
        tasks: List of task objects
        count: Total number of tasks returned

    Example:
        {
            "tasks": [
                {
                    "id": 1,
                    "user_id": "user_abc123",
                    "title": "Task 1",
                    "description": null,
                    "complete": false,
                    "priority": "medium",
                    "created_at": "2025-12-20T10:30:00Z",
                    "updated_at": "2025-12-20T10:30:00Z"
                }
            ],
            "count": 1
        }
    """

    tasks: list[TaskResponse]
    count: int
