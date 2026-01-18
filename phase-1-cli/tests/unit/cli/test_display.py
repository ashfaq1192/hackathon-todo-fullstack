"""Unit tests for CLI display functions.

This module tests the display formatting and output functions.
"""

from src.cli.display import (
    display_error_message,
    display_success_message,
    display_task,
    display_task_list,
)


class TestDisplayFunctions:
    """Test suite for display functions."""

    def test_display_task_with_description(self, capsys):
        """Test display_task with a complete task."""
        task = {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, bread, eggs",
            "priority": "High",
            "complete": False,
        }

        display_task(task)
        captured = capsys.readouterr()

        assert "[ID: 1] Buy groceries" in captured.out
        assert "Priority: High" in captured.out
        assert "Status: Incomplete" in captured.out
        assert "Description: Milk, bread, eggs" in captured.out

    def test_display_task_without_description(self, capsys):
        """Test display_task with empty description."""
        task = {
            "id": 2,
            "title": "Call dentist",
            "description": "",
            "priority": "Low",
            "complete": True,
        }

        display_task(task)
        captured = capsys.readouterr()

        assert "[ID: 2] Call dentist" in captured.out
        assert "Priority: Low" in captured.out
        assert "Status: Complete" in captured.out
        assert "Description: (no description)" in captured.out

    def test_display_task_list_with_tasks(self, capsys):
        """Test display_task_list with multiple tasks."""
        tasks = [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Desc 1",
                "priority": "High",
                "complete": False,
            },
            {
                "id": 2,
                "title": "Task 2",
                "description": "",
                "priority": "Medium",
                "complete": True,
            },
        ]

        display_task_list(tasks)
        captured = capsys.readouterr()

        assert "=== Your Tasks (2 total) ===" in captured.out
        assert "[ID: 1] Task 1" in captured.out
        assert "[ID: 2] Task 2" in captured.out

    def test_display_task_list_empty(self, capsys):
        """Test display_task_list with empty list."""
        display_task_list([])
        captured = capsys.readouterr()

        assert "=== Your Tasks (0 total) ===" in captured.out
        assert "No tasks to display" in captured.out

    def test_display_success_message(self, capsys):
        """Test success message formatting."""
        display_success_message("Task added successfully")
        captured = capsys.readouterr()

        assert "✓ Task added successfully" in captured.out

    def test_display_error_message(self, capsys):
        """Test error message formatting."""
        display_error_message("Task not found")
        captured = capsys.readouterr()

        assert "✗ Task not found" in captured.out
