"""MCP tool for listing tasks via natural language.

This tool retrieves tasks from the database with optional filtering by status.
It's registered with the Swarm Agent and called when the user requests to
view, show, or list their tasks.
"""

import logging
from typing import Literal

from sqlmodel import Session, select

from src.models.task import Task

logger = logging.getLogger(__name__)


def list_tasks(
    user_id: str,
    status: Literal["all", "pending", "completed"] = "all",
    db: Session | None = None,
) -> dict:
    """List tasks for the user with optional status filtering.

    This MCP tool retrieves tasks from the database and formats them for
    display. It's designed to be called by the Swarm Agent when the user
    requests to see their tasks (e.g., "Show me my pending tasks").

    Args:
        user_id: User ID from authenticated JWT token
        status: Filter by status (all/pending/completed, default: all)
        db: SQLModel database session (injected by chat service)

    Returns:
        dict: Result with success status and task list
            {
                "success": bool,
                "tasks": list[dict],  # List of task objects
                "count": int,
                "message": str
            }

    Example:
        >>> result = list_tasks(
        ...     user_id="user_123",
        ...     status="pending"
        ... )
        >>> # Returns: {"success": True, "tasks": [...], "count": 5, ...}
    """
    # T060: Log MCP tool invocation
    logger.info(f"list_tasks invoked: user_id={user_id}, status={status}")

    if not db:
        logger.error("list_tasks failed: Database session not provided")
        return {
            "success": False,
            "tasks": [],
            "count": 0,
            "message": "ERROR: Internal error - database connection missing",
            "error": "Database session not provided"
        }

    try:
        # Build query with status filter
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.complete == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.complete == True)  # noqa: E712
        # "all" status includes both completed and pending

        # Execute query and get results
        tasks = db.exec(statement).all()

        # Format tasks for response
        # Note: Gemini API doesn't handle null values, so we use empty string for optional fields
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description or "",  # Convert None to empty string for Gemini
                "complete": task.complete,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
            })

        # Generate formatted response for Gemini API compatibility
        logger.info(f"list_tasks success: user_id={user_id}, count={len(task_list)}")

        if len(task_list) == 0:
            message = ""
            if status == "pending":
                message = "You have no pending tasks. Great job! 🎉"
            elif status == "completed":
                message = "You have no completed tasks yet."
            else:
                message = "You have no tasks. Start by adding one!"
            return {
                "success": True,
                "tasks": [],
                "count": 0,
                "message": message
            }

        # Format tasks as readable string
        lines = [f"Found {len(task_list)} task{'s' if len(task_list) != 1 else ''}:"]
        for task in task_list:
            status_emoji = "✅" if task["complete"] else "⏳"
            lines.append(f"  {status_emoji} [{task['id']}] {task['title']} ({task['priority']})")

        return {
            "success": True,
            "tasks": task_list,
            "count": len(task_list),
            "message": "\n".join(lines)
        }

    except Exception as e:
        logger.error(f"list_tasks failed: user_id={user_id}, error={str(e)}")
        return {
            "success": False,
            "tasks": [],
            "count": 0,
            "message": "ERROR: Failed to retrieve tasks. Please try again.",
            "error": str(e)
        }


# OpenAI function calling schema for Swarm Agent registration
LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": "Retrieve the user's tasks with optional filtering by status. Use this when the user wants to see, show, list, or view their tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter tasks by completion status (default: all)",
            },
        },
        "required": [],
    },
}
