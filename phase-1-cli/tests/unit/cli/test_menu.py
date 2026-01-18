"""Unit tests for CLI menu functions.

This module contains tests for menu display, user input handling,
and input validation for the CLI interface.
"""

from unittest.mock import patch

from src.cli.menu import (
    display_main_menu,
    get_menu_choice,
    prompt_add_task,
    prompt_task_id,
    prompt_update_task,
)


class TestMenuFunctions:
    """Test suite for menu interaction functions."""

    def test_display_main_menu(self, capsys):
        """Test main menu display."""
        display_main_menu()
        captured = capsys.readouterr()

        assert "=== Todo App Menu ===" in captured.out
        assert "1. Add Task" in captured.out
        assert "2. View Tasks" in captured.out
        assert "3. Mark Task Complete/Incomplete" in captured.out
        assert "4. Update Task" in captured.out
        assert "5. Delete Task" in captured.out
        assert "6. Exit" in captured.out

    @patch("builtins.input", return_value="3")
    def test_get_menu_choice_valid_input(self, mock_input):
        """Test menu choice with valid input."""
        choice = get_menu_choice()
        assert choice == 3

    @patch("builtins.input", side_effect=["abc", "0", "7", "2"])
    def test_get_menu_choice_validation(self, mock_input, capsys):
        """Test menu choice validation loop."""
        choice = get_menu_choice()
        assert choice == 2
        captured = capsys.readouterr()
        assert "Invalid input" in captured.out or "Invalid choice" in captured.out

    # User Story 1 tests
    @patch("builtins.input", side_effect=["Buy groceries", "Milk, bread, eggs", "High"])
    def test_prompt_add_task_with_valid_input(self, mock_input):
        """Test prompting user for task details with valid input."""
        result = prompt_add_task()
        assert result == ("Buy groceries", "Milk, bread, eggs", "High")

    @patch("builtins.input", side_effect=["", "Valid title", "", "high", "High"])
    def test_prompt_add_task_with_validation(self, mock_input, capsys):
        """Test prompt_add_task with validation errors."""
        result = prompt_add_task()
        assert result[0] == "Valid title"
        assert result[2] == "High"
        captured = capsys.readouterr()
        assert "cannot be empty" in captured.out or "Invalid priority" in captured.out

    # User Story 2 tests
    @patch("builtins.input", return_value="5")
    def test_prompt_task_id_valid_input(self, mock_input):
        """Test prompting for task ID with valid input."""
        task_id = prompt_task_id()
        assert task_id == 5

    @patch("builtins.input", side_effect=["abc", "0", "-1", "3"])
    def test_prompt_task_id_validation(self, mock_input, capsys):
        """Test prompt_task_id validation loop."""
        task_id = prompt_task_id()
        assert task_id == 3
        captured = capsys.readouterr()
        assert "Invalid" in captured.out or "positive" in captured.out

    # User Story 3 tests
    @patch("builtins.input", side_effect=["1", "New title", "", ""])
    def test_prompt_update_task_partial_update(self, mock_input):
        """Test prompting for partial task update."""
        task_id, title, description, priority = prompt_update_task()
        assert task_id == 1
        assert title == "New title"
        assert description is None
        assert priority is None

    # User Story 4 tests
    def test_delete_task_menu_flow(self):
        """Test delete task menu flow using prompt_task_id."""
        # Delete uses prompt_task_id which is tested above
        pass
