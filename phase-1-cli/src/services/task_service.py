"""Task service layer for CRUD operations.

This module provides the business logic for managing tasks including create,
read, update, delete operations, and task state management.
"""

import logging
import os

from src.models.task import create_task_dict, validate_priority, validate_title

# Configure logging per constitution requirements
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Module-level state management
tasks: list[dict] = []
next_id: int = 1


def get_logger():
    """Get the configured logger instance.

    Returns:
        logging.Logger: Configured logger for task service
    """
    return logger


def create_task(title: str, description: str, priority: str) -> tuple[bool, str, dict | None]:
    """Create a new task with auto-generated ID.

    Args:
        title: Task title (required, will be trimmed)
        description: Task description (optional, can be empty)
        priority: Priority level (must be "High", "Medium", or "Low")

    Returns:
        tuple: (success, message, task_dict or None)
            success: True if task created, False if validation failed
            message: Confirmation or error message
            task_dict: Created task with all fields if success, None if failure
    """
    global next_id

    # Validate title
    is_valid, error = validate_title(title)
    if not is_valid:
        return (False, error, None)

    # Validate priority
    is_valid, error = validate_priority(priority)
    if not is_valid:
        return (False, error, None)

    # Create task
    task = create_task_dict(next_id, title, description, priority)

    # Update state
    tasks.append(task)
    next_id += 1

    # Log operation
    logger.info(f"Task created - ID: {task['id']}, Title: {task['title']}")

    return (True, "Task added successfully", task)


def get_all_tasks() -> tuple[bool, str, list[dict]]:
    """Get all tasks sorted by completion, priority, and ID.

    Returns:
        tuple: (success, message, task_list)
            success: Always True
            message: Status message
            task_list: List of task dicts, sorted or empty list
    """
    if not tasks:
        return (True, "No tasks found", [])

    # Multi-level sort: completion (False first), priority (High→Medium→Low), ID (ascending)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_tasks = sorted(
        tasks, key=lambda t: (t["complete"], priority_order[t["priority"]], t["id"])
    )

    return (True, f"Found {len(sorted_tasks)} tasks", sorted_tasks)


def get_task_by_id(task_id: int) -> tuple[bool, str, dict | None]:
    """Find a task by its ID.

    Args:
        task_id: Task ID to search for

    Returns:
        tuple: (success, message, task_dict or None)
            success: True if found, False if not found
            message: Status or error message
            task_dict: Task dict if found, None if not found

    Raises:
        None (returns error tuple instead)
    """
    for task in tasks:
        if task["id"] == task_id:
            return (True, "Task found", task)

    return (False, "Task not found", None)


def toggle_task_completion(task_id: int) -> tuple[bool, str, dict | None]:
    """Toggle task completion status (False ↔ True).

    Args:
        task_id: ID of task to toggle

    Returns:
        tuple: (success, message, task_dict or None)
            success: True if toggled, False if not found
            message: Confirmation or error message
            task_dict: Updated task if success, None if failure

    Raises:
        None (returns error tuple instead)
    """
    success, message, task = get_task_by_id(task_id)

    if not success:
        return (False, message, None)

    # Toggle completion status
    task["complete"] = not task["complete"]
    status = "complete" if task["complete"] else "incomplete"

    # Log operation
    logger.info(f"Task completion toggled - ID: {task_id}, Complete: {task['complete']}")

    return (True, f"Task marked as {status}", task)


def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
) -> tuple[bool, str, dict | None]:
    """Update task fields. Only provided (non-None) fields are changed.

    Args:
        task_id: ID of task to update
        title: New title (optional, will be trimmed if provided)
        description: New description (optional)
        priority: New priority (optional, must be valid if provided)

    Returns:
        tuple: (success, message, task_dict or None)
            success: True if updated, False if validation failed or not found
            message: Confirmation or error message
            task_dict: Updated task if success, None if failure

    Raises:
        None (returns error tuple instead)
    """
    # Check if at least one field is provided
    if title is None and description is None and priority is None:
        return (False, "No fields to update", None)

    # Find task
    success, message, task = get_task_by_id(task_id)
    if not success:
        return (False, message, None)

    # Track changed fields for logging
    changed_fields = []

    # Update title if provided
    if title is not None:
        is_valid, error = validate_title(title)
        if not is_valid:
            return (False, error, None)
        task["title"] = title.strip()
        changed_fields.append("title")

    # Update description if provided
    if description is not None:
        task["description"] = description
        changed_fields.append("description")

    # Update priority if provided
    if priority is not None:
        is_valid, error = validate_priority(priority)
        if not is_valid:
            return (False, error, None)
        task["priority"] = priority
        changed_fields.append("priority")

    # Log operation
    logger.info(f"Task updated - ID: {task_id}, Fields: {', '.join(changed_fields)}")

    return (True, "Task updated successfully", task)


def delete_task(task_id: int) -> tuple[bool, str, None]:
    """Delete a task permanently.

    Args:
        task_id: ID of task to delete

    Returns:
        tuple: (success, message, None)
            success: True if deleted, False if not found
            message: Confirmation or error message
            data: Always None (no data returned for deletion)

    Raises:
        None (returns error tuple instead)
    """
    # Find task
    success, message, task = get_task_by_id(task_id)
    if not success:
        return (False, message, None)

    # Remove task from list
    tasks.remove(task)

    # Log operation
    logger.info(f"Task deleted - ID: {task_id}")

    return (True, "Task deleted successfully", None)
