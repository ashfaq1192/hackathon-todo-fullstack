"""MCP tool for updating tasks via natural language.

This tool modifies task details (title, description, priority) in the database.
It's registered with the Swarm Agent and called when the user requests to
update, change, or edit a task.
"""

import logging
from typing import Literal

from sqlmodel import Session, select

from src.models.task import Task, TaskPriority

logger = logging.getLogger(__name__)


def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: Literal["low", "medium", "high"] | None = None,
    db: Session | None = None,
) -> dict:
    """Update a task's details.

    This MCP tool modifies task fields. Only provided fields are updated;
    omitted fields remain unchanged. Verifies task ownership before updating.

    Args:
        user_id: User ID from authenticated JWT token
        task_id: ID of the task to update
        title: New title (optional, max 200 characters)
        description: New description (optional, max 1000 characters)
        priority: New priority level (optional: low/medium/high)
        db: SQLModel database session (injected by chat service)

    Returns:
        dict: Result with success status and updated task details
            {
                "success": bool,
                "task_id": int,
                "updated_fields": list[str],
                "message": str
            }

    Example:
        >>> result = update_task(
        ...     user_id="user_123",
        ...     task_id=42,
        ...     priority="high"
        ... )
        >>> # Returns: {"success": True, "task_id": 42, "updated_fields": ["priority"], ...}
    """
    # T060: Log MCP tool invocation
    logger.info(f"update_task invoked: user_id={user_id}, task_id={task_id}")

    if not db:
        logger.error("update_task failed: Database session not provided")
        return {
            "success": False,
            "task_id": task_id,
            "message": "ERROR: Internal error - database connection missing",
            "error": "Database session not provided"
        }

    # Validate at least one field is provided
    if title is None and description is None and priority is None:
        return {
            "success": False,
            "task_id": task_id,
            "message": "ERROR: Please specify at least one field to update (title, description, or priority).",
            "error": "No fields to update"
        }

    # Validate field lengths
    if title is not None:
        if len(title.strip()) == 0:
            return {
                "success": False,
                "task_id": task_id,
                "message": "ERROR: Task title cannot be empty.",
                "error": "Empty title"
            }
        if len(title) > 200:
            return {
                "success": False,
                "task_id": task_id,
                "message": f"ERROR: Task title must be 200 characters or less (got {len(title)}).",
                "error": "Title too long"
            }

    if description is not None and len(description) > 1000:
        return {
            "success": False,
            "task_id": task_id,
            "message": f"ERROR: Task description must be 1000 characters or less (got {len(description)}).",
            "error": "Description too long"
        }

    try:
        # Fetch task and verify ownership
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = db.exec(statement).first()

        if not task:
            return {
                "success": False,
                "task_id": task_id,
                "message": f"ERROR: Task with ID {task_id} not found or doesn't belong to you.",
                "error": "Task not found or unauthorized"
            }

        # Track updated fields
        updated_fields = []

        # Update title if provided
        if title is not None:
            task.title = title.strip()
            updated_fields.append("title")

        # Update description if provided
        if description is not None:
            task.description = description.strip() if description.strip() else None
            updated_fields.append("description")

        # Update priority if provided
        if priority is not None:
            try:
                task.priority = TaskPriority(priority)
                updated_fields.append("priority")
            except ValueError:
                return {
                    "success": False,
                    "task_id": task_id,
                    "message": f"ERROR: Priority must be 'low', 'medium', or 'high' (got '{priority}').",
                    "error": "Invalid priority"
                }

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        # Build update message
        fields_text = ", ".join(updated_fields)
        logger.info(f"update_task success: task_id={task.id}, user_id={user_id}, updated={updated_fields}")
        return {
            "success": True,
            "task_id": task.id,
            "updated_fields": updated_fields,
            "message": f"✏️ Task '{task.title}' (ID: {task.id}) updated successfully! Changed: {fields_text}"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"update_task failed: user_id={user_id}, task_id={task_id}, error={str(e)}")
        return {
            "success": False,
            "task_id": task_id,
            "message": f"ERROR: Failed to update task. Please try again.",
            "error": str(e)
        }


# OpenAI function calling schema for Swarm Agent registration
UPDATE_TASK_SCHEMA = {
    "name": "update_task",
    "description": "Update a task's details (title, description, or priority). Use this when the user wants to update, change, modify, or edit a task.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to update",
            },
            "title": {
                "type": "string",
                "description": "New task title (optional, max 200 characters)",
            },
            "description": {
                "type": "string",
                "description": "New task description (optional, max 1000 characters)",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "New task priority level (optional)",
            },
        },
        "required": ["task_id"],
    },
}
