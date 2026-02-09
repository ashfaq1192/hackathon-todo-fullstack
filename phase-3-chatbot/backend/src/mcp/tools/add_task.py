"""MCP tool for adding tasks via natural language.

This tool creates a new task in the database based on natural language input.
It's registered with the Swarm Agent and called when the user requests to
add, create, or make a new task.
"""

import logging
from datetime import datetime
from typing import Literal

from sqlmodel import Session

from src.models.task import Task, TaskPriority, RecurringType

logger = logging.getLogger(__name__)


def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: Literal["low", "medium", "high"] = "medium",
    due_date: str | None = None,
    recurring: Literal["none", "daily", "weekly", "monthly", "yearly"] = "none",
    tags: list[str] | None = None,
    db: Session | None = None,
) -> dict:
    """Add a new task for the user.

    Args:
        user_id: User ID from authenticated JWT token
        title: Task title (required, max 200 characters)
        description: Optional task description (max 1000 characters)
        priority: Task priority level (low/medium/high, default: medium)
        due_date: Optional due date in ISO 8601 format (e.g., "2026-02-15T10:00:00")
        recurring: Recurring schedule (none/daily/weekly/monthly/yearly, default: none)
        tags: Optional list of tags/categories (e.g., ["work", "urgent"])
        db: SQLModel database session (injected by chat service)

    Returns:
        dict: Result with success status and task details
    """
    logger.info(f"add_task invoked: user_id={user_id}, title='{title[:50]}...', priority={priority}")

    if not db:
        logger.error("add_task failed: Database session not provided")
        return {
            "success": False,
            "message": "ERROR: Internal error - database connection missing",
            "error": "Database session not provided"
        }

    # Validate title
    if not title or len(title.strip()) == 0:
        return {"success": False, "message": "ERROR: Please provide a task title", "error": "Empty title"}

    if len(title) > 200:
        return {"success": False, "message": f"ERROR: Task title must be 200 characters or less (got {len(title)})", "error": "Title too long"}

    if description and len(description) > 1000:
        return {"success": False, "message": f"ERROR: Task description must be 1000 characters or less (got {len(description)})", "error": "Description too long"}

    # Convert priority string to enum
    try:
        priority_enum = TaskPriority(priority)
    except ValueError:
        return {"success": False, "message": f"ERROR: Priority must be 'low', 'medium', or 'high' (got '{priority}')", "error": "Invalid priority"}

    # Convert recurring string to enum
    try:
        recurring_enum = RecurringType(recurring)
    except ValueError:
        return {"success": False, "message": f"ERROR: Recurring must be one of: none, daily, weekly, monthly, yearly (got '{recurring}')", "error": "Invalid recurring type"}

    # Parse due date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return {"success": False, "message": f"ERROR: Invalid date format. Use ISO 8601 (e.g., '2026-02-15T10:00:00')", "error": "Invalid due_date"}

    # Clean tags
    clean_tags = [t.strip().lower() for t in (tags or []) if t.strip()]

    # Create task
    try:
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority_enum,
            complete=False,
            due_date=parsed_due_date,
            recurring=recurring_enum,
            tags=clean_tags,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        # Build response message
        msg_parts = [f"Task '{task.title}' created with ID {task.id}. Priority: {task.priority.value}"]
        if parsed_due_date:
            msg_parts.append(f"Due: {parsed_due_date.strftime('%Y-%m-%d %H:%M')}")
        if recurring_enum != RecurringType.none:
            msg_parts.append(f"Recurring: {recurring_enum.value}")
        if clean_tags:
            msg_parts.append(f"Tags: {', '.join(clean_tags)}")

        logger.info(f"add_task success: task_id={task.id}, user_id={user_id}")
        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "message": "SUCCESS: " + " | ".join(msg_parts)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"add_task failed: user_id={user_id}, error={str(e)}")
        return {"success": False, "message": "ERROR: Failed to create task. Please try again.", "error": str(e)}


# OpenAI function calling schema for Swarm Agent registration
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task for the user. Use this when the user wants to add, create, or make a new task. Supports due dates, recurring schedules, and tags.",
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
            "due_date": {
                "type": "string",
                "description": "Due date in ISO 8601 format, e.g., '2026-02-15T10:00:00'. Use for deadlines and reminders.",
            },
            "recurring": {
                "type": "string",
                "enum": ["none", "daily", "weekly", "monthly", "yearly"],
                "description": "Recurring schedule type (default: none). When marked complete, a new occurrence is auto-created.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags/categories for the task, e.g., ['work', 'urgent']. Use for organization and filtering.",
            },
        },
        "required": ["title"],
    },
}
