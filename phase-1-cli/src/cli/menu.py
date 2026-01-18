"""CLI menu functions for user input and navigation.

This module handles all user input gathering including menu choices,
task details, and ID prompts.
"""


def display_main_menu() -> None:
    """Display the main menu options to the user.

    Prints:
        Numbered menu with options:
        1. Add Task
        2. View Tasks
        3. Mark Task Complete/Incomplete
        4. Update Task
        5. Delete Task
        6. Exit

    Returns:
        None

    Raises:
        None
    """
    print("\n=== Todo App Menu ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task Complete/Incomplete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")


def get_menu_choice() -> int:
    """Prompt user for menu choice and validate input.

    Returns:
        int: Valid menu choice (1-6)

    Raises:
        None (loops until valid input received)
    """
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            choice_int = int(choice)

            if 1 <= choice_int <= 6:
                return choice_int
            else:
                print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def prompt_add_task() -> tuple[str, str, str] | None:
    """Prompt user for task details (title, description, priority).

    Returns:
        tuple: (title, description, priority) if successful
        None: if user cancels

    Raises:
        None
    """
    # Prompt for title with validation
    while True:
        title = input("\nEnter task title: ").strip()
        if title:
            break
        print("Title cannot be empty. Please try again.")

    # Prompt for description (optional)
    description = input("Enter task description (optional): ")

    # Prompt for priority with validation
    while True:
        priority = input("Enter priority (High/Medium/Low): ")
        if priority in ["High", "Medium", "Low"]:
            break
        print("Invalid priority. Must be exactly 'High', 'Medium', or 'Low'.")

    return (title, description, priority)


def prompt_task_id(prompt_message: str = "Enter task ID: ") -> int:
    """Prompt user for a task ID and validate numeric input.

    Args:
        prompt_message: Custom prompt text (default: "Enter task ID: ")

    Returns:
        int: Positive integer task ID

    Raises:
        None (loops until valid input received)
    """
    while True:
        try:
            task_id_str = input(f"\n{prompt_message}").strip()
            task_id = int(task_id_str)

            if task_id > 0:
                return task_id
            else:
                print("Task ID must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def prompt_update_task() -> tuple[int, str | None, str | None, str | None]:
    """Prompt user for task ID and fields to update.

    Returns:
        tuple: (task_id, title or None, description or None, priority or None)
            At least one field (title/description/priority) will be non-None

    Raises:
        None
    """
    # Get task ID
    task_id = prompt_task_id()

    # Prompt for optional field updates
    while True:
        title_input = input("Enter new title (or press Enter to skip): ").strip()
        title = title_input if title_input else None

        # Validate title if provided
        if title is not None and not title:
            print("Title cannot be empty. Please try again.")
            continue

        description_input = input("Enter new description (or press Enter to skip): ")
        # For description: if user provides anything (including empty string), we consider it
        # as an update. If they just press Enter with no input at all, it's None (skip)
        # However, the contract says pressing Enter should skip, so empty string means skip
        description = None if description_input == "" else description_input

        priority_input = input("Enter new priority (or press Enter to skip): ")
        priority = priority_input if priority_input else None

        # Validate priority if provided
        if priority is not None and priority not in ["High", "Medium", "Low"]:
            print("Invalid priority. Must be exactly 'High', 'Medium', or 'Low'.")
            continue

        # Ensure at least one field is being updated
        if title is None and description is None and priority is None:
            print("At least one field must be updated. Please try again.")
            continue

        return (task_id, title, description, priority)
