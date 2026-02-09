"""MCP tool for deleting tasks via natural language.

This tool removes tasks from the database.
It's registered with the Swarm Agent and called when the user requests to
delete, remove, or cancel a task.
"""

import logging

from sqlmodel import Session, select

from src.models.task import Task

logger = logging.getLogger(__name__)


def delete_task(
    user_id: str,
    task_id: int,
    db: Session | None = None,
) -> dict:
    """Delete a task.

    This MCP tool permanently removes a task from the database. It verifies
    that the task belongs to the authenticated user before deletion.

    Args:
        user_id: User ID from authenticated JWT token
        task_id: ID of the task to delete
        db: SQLModel database session (injected by chat service)

    Returns:
        dict: Result with success status and deleted task details
            {
                "success": bool,
                "task_id": int,
                "title": str,
                "message": str
            }

    Example:
        >>> result = delete_task(
        ...     user_id="user_123",
        ...     task_id=42
        ... )
        >>> # Returns: {"success": True, "task_id": 42, "title": "Buy groceries", ...}
    """
    # T060: Log MCP tool invocation
    logger.info(f"delete_task invoked: user_id={user_id}, task_id={task_id}")

    if not db:
        logger.error("delete_task failed: Database session not provided")
        return {
            "success": False,
            "task_id": task_id,
            "message": "ERROR: Internal error - database connection missing",
            "error": "Database session not provided"
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

        # Store task details before deletion
        task_title = task.title
        task_id_value = task.id

        # Delete task
        db.delete(task)
        db.commit()

        logger.info(f"delete_task success: task_id={task_id_value}, user_id={user_id}")
        return {
            "success": True,
            "task_id": task_id_value,
            "title": task_title,
            "message": f"🗑️ Task '{task_title}' (ID: {task_id_value}) deleted successfully!"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"delete_task failed: user_id={user_id}, task_id={task_id}, error={str(e)}")
        return {
            "success": False,
            "task_id": task_id,
            "message": f"ERROR: Failed to delete task. Please try again.",
            "error": str(e)
        }


# OpenAI function calling schema for Swarm Agent registration
DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Delete a task permanently. Use this when the user wants to delete, remove, cancel, or get rid of a task.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to delete",
            },
        },
        "required": ["task_id"],
    },
}
