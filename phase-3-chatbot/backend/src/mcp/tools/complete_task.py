"""MCP tool for marking tasks complete via natural language.

This tool updates a task's completion status in the database.
It's registered with the Swarm Agent and called when the user requests to
complete, finish, or mark a task as done.
"""

import logging

from sqlmodel import Session, select

from src.models.task import Task

logger = logging.getLogger(__name__)


def complete_task(
    user_id: str,
    task_id: int,
    db: Session | None = None,
) -> dict:
    """Mark a task as complete.

    This MCP tool updates the task's complete field to True. It verifies that
    the task belongs to the authenticated user before making changes.

    Args:
        user_id: User ID from authenticated JWT token
        task_id: ID of the task to mark complete
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
        >>> result = complete_task(
        ...     user_id="user_123",
        ...     task_id=42
        ... )
        >>> # Returns: {"success": True, "task_id": 42, "title": "Buy groceries", ...}
    """
    # T060: Log MCP tool invocation
    logger.info(f"complete_task invoked: user_id={user_id}, task_id={task_id}")

    if not db:
        logger.error("complete_task failed: Database session not provided")
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

        # Check if already complete
        if task.complete:
            return {
                "success": True, # Task is already in the desired state
                "task_id": task_id,
                "title": task.title,
                "message": f"Task '{task.title}' is already marked as complete! ✅"
            }

        # Mark as complete
        task.complete = True
        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"complete_task success: task_id={task.id}, user_id={user_id}")
        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "message": f"✅ Task '{task.title}' (ID: {task.id}) marked as complete!"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"complete_task failed: user_id={user_id}, task_id={task_id}, error={str(e)}")
        return {
            "success": False,
            "task_id": task_id,
            "message": f"ERROR: Failed to complete task. Please try again.",
            "error": str(e)
        }


# OpenAI function calling schema for Swarm Agent registration
COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as complete. Use this when the user wants to complete, finish, or mark a task as done.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to mark complete",
            },
        },
        "required": ["task_id"],
    },
}
