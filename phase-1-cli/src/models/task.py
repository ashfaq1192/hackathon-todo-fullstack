"""Task entity and validation functions.

This module defines the task data structure and provides validation
functions for task fields per the data model specification.
"""


def validate_title(title: str) -> tuple[bool, str]:
    """Validate task title.

    Args:
        title: Task title to validate

    Returns:
        tuple: (is_valid, error_message)
            is_valid: True if title is valid, False otherwise
            error_message: Empty string if valid, error description if invalid
    """
    if not isinstance(title, str):
        return (False, "Title must be a string")

    trimmed = title.strip()
    if not trimmed:
        return (False, "Title cannot be empty")

    return (True, "")


def validate_priority(priority: str) -> tuple[bool, str]:
    """Validate task priority.

    Args:
        priority: Priority level to validate

    Returns:
        tuple: (is_valid, error_message)
            is_valid: True if priority is valid, False otherwise
            error_message: Empty string if valid, error description if invalid
    """
    if not isinstance(priority, str):
        return (False, "Priority must be a string")

    valid_priorities = ["High", "Medium", "Low"]
    if priority not in valid_priorities:
        return (False, "Priority must be exactly 'High', 'Medium', or 'Low'")

    return (True, "")


def create_task_dict(task_id: int, title: str, description: str, priority: str) -> dict:
    """Create a task dictionary with all required fields.

    Args:
        task_id: Unique task identifier
        title: Task title (already validated)
        description: Task description (optional, can be empty)
        priority: Task priority (already validated)

    Returns:
        dict: Task dictionary with id, title, description, priority, complete fields
    """
    return {
        "id": task_id,
        "title": title.strip(),
        "description": description,
        "priority": priority,
        "complete": False,
    }
