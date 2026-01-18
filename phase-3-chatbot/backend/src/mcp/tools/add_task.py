"""MCP tool for adding tasks via natural language.

This tool creates a new task in the database based on natural language input.
It's registered with the Swarm Agent and called when the user requests to
add, create, or make a new task.
"""

import logging
from typing import Literal

from sqlmodel import Session

from src.models.task import Task, TaskPriority

logger = logging.getLogger(__name__)


def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: Literal["low", "medium", "high"] = "medium",
    db: Session | None = None,
) -> dict:
    """Add a new task for the user.

    This MCP tool creates a task in the database with the provided details.
    It's designed to be called by the Swarm Agent when the user requests
    task creation via natural language (e.g., "Add a task to buy groceries").

    Args:
        user_id: User ID from authenticated JWT token
        title: Task title (required, max 200 characters)
        description: Optional task description (max 1000 characters)
        priority: Task priority level (low/medium/high, default: medium)
        db: SQLModel database session (injected by chat service)

    Returns:
        dict: Result with success status and task details
            {
                "success": bool,
                "task_id": int,
                "title": str,
                "message": str
            }

    Example:
        >>> result = add_task(
        ...     user_id="user_123",
        ...     title="Buy groceries",
        ...     description="Milk, eggs, bread",
        ...     priority="high"
        ... )
        >>> # Returns: {"success": True, "task_id": 42, "title": "Buy groceries", ...}
    """
    # T060: Log MCP tool invocation
    logger.info(f"add_task invoked: user_id={user_id}, title='{title[:50]}...', priority={priority}")

    if not db:
        logger.error("add_task failed: Database session not provided")
        return {
            "success": False,
            "message": "ERROR: Internal error - database connection missing",
            "error": "Database session not provided"
        }

    # Validate title length
    if not title or len(title.strip()) == 0:
        return {
            "success": False,
            "message": "ERROR: Please provide a task title",
            "error": "Empty title"
        }

    if len(title) > 200:
        return {
            "success": False,
            "message": f"ERROR: Task title must be 200 characters or less (got {len(title)})",
            "error": "Title too long"
        }

    # Validate description length if provided
    if description and len(description) > 1000:
        return {
            "success": False,
            "message": f"ERROR: Task description must be 1000 characters or less (got {len(description)})",
            "error": "Description too long"
        }

    # Convert priority string to enum
    try:
        priority_enum = TaskPriority(priority)
    except ValueError:
        return {
            "success": False,
            "message": f"ERROR: Priority must be 'low', 'medium', or 'high' (got '{priority}')",
            "error": "Invalid priority"
        }

    # Create task
    try:
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority_enum,
            complete=False,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"add_task success: task_id={task.id}, user_id={user_id}")
        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "message": f"SUCCESS: Task '{task.title}' created with ID {task.id}. Priority: {task.priority.value}"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"add_task failed: user_id={user_id}, error={str(e)}")
        return {
            "success": False,
            "message": f"ERROR: Failed to create task. Please try again.",
            "error": str(e)
        }


# OpenAI function calling schema for Swarm Agent registration
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task for the user. Use this when the user wants to add, create, or make a new task.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The task title (required, max 200 characters)",
            },
            "description": {
                "type": "string",
                "description": "Optional task description with additional details (max 1000 characters)",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Task priority level (default: medium)",
            },
        },
        "required": ["title"],
    },
}
