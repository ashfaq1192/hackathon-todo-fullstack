"""CLI display functions for task formatting and output.

This module handles all user-facing output including task display,
success messages, and error messages.
"""


def display_task(task: dict) -> None:
    """Display a single task with all fields formatted.

    Args:
        task: Task dictionary with id, title, description, priority, complete

    Returns:
        None

    Raises:
        None
    """
    status = "Complete" if task["complete"] else "Incomplete"
    description = task["description"] if task["description"] else "(no description)"

    print(f"[ID: {task['id']}] {task['title']}")
    print(f"  Priority: {task['priority']}")
    print(f"  Status: {status}")
    print(f"  Description: {description}")


def display_task_list(tasks: list[dict]) -> None:
    """Display all tasks in a formatted list.

    Args:
        tasks: List of task dictionaries (already sorted)

    Returns:
        None

    Raises:
        None
    """
    print(f"\n=== Your Tasks ({len(tasks)} total) ===\n")

    if not tasks:
        print("No tasks to display. Add a task to get started!")
    else:
        for i, task in enumerate(tasks):
            display_task(task)
            # Add blank line between tasks (but not after the last one)
            if i < len(tasks) - 1:
                print()


def display_success_message(message: str) -> None:
    """Display a success message with visual indicator.

    Args:
        message: Success message text

    Returns:
        None

    Raises:
        None
    """
    print(f"✓ {message}")


def display_error_message(message: str) -> None:
    """Display an error message with visual indicator.

    Args:
        message: Error message text

    Returns:
        None

    Raises:
        None
    """
    print(f"✗ {message}")
