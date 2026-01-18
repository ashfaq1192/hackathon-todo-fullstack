"""Main application entry point for CLI Todo App.

This module contains the main application loop that integrates all
CLI and service layer functions to provide a complete todo management system.
"""

from src.cli.display import display_error_message, display_success_message, display_task_list
from src.cli.menu import (
    display_main_menu,
    get_menu_choice,
    prompt_add_task,
    prompt_task_id,
    prompt_update_task,
)
from src.services.task_service import (
    create_task,
    delete_task,
    get_all_tasks,
    toggle_task_completion,
    update_task,
)


def handle_add_task():
    """Handle the add task operation."""
    result = prompt_add_task()
    if result is None:
        return

    title, description, priority = result
    success, message, task = create_task(title, description, priority)

    if success:
        display_success_message(message)
    else:
        display_error_message(message)


def handle_view_tasks():
    """Handle the view tasks operation."""
    success, message, tasks = get_all_tasks()
    display_task_list(tasks)


def handle_toggle_completion():
    """Handle the mark complete/incomplete operation."""
    task_id = prompt_task_id("Enter task ID to toggle completion: ")

    success, message, task = toggle_task_completion(task_id)

    if success:
        display_success_message(message)
    else:
        display_error_message(message)


def handle_update_task():
    """Handle the update task operation."""
    task_id, title, description, priority = prompt_update_task()

    success, message, task = update_task(task_id, title, description, priority)

    if success:
        display_success_message(message)
    else:
        display_error_message(message)


def handle_delete_task():
    """Handle the delete task operation."""
    task_id = prompt_task_id("Enter task ID to delete: ")

    success, message, _ = delete_task(task_id)

    if success:
        display_success_message(message)
    else:
        display_error_message(message)


def main():
    """Main application loop."""
    print("\n" + "=" * 50)
    print("Welcome to the Todo App!")
    print("=" * 50)

    while True:
        display_main_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task()
        elif choice == 2:
            handle_view_tasks()
        elif choice == 3:
            handle_toggle_completion()
        elif choice == 4:
            handle_update_task()
        elif choice == 5:
            handle_delete_task()
        elif choice == 6:
            print("\nThank you for using Todo App. Goodbye!")
            break


if __name__ == "__main__":
    main()
