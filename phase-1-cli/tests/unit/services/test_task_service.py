"""Unit tests for task service CRUD operations.

This module contains tests for the task service layer including create, read,
update, delete operations, task sorting, and state management.
"""

import logging

from src.services import task_service


class TestTaskServiceCRUD:
    """Test suite for CRUD operations."""

    def setup_method(self):
        """Reset task service state before each test."""
        task_service.tasks = []
        task_service.next_id = 1

    def test_logging_configured(self):
        """Test that logging is properly configured."""
        logger = task_service.get_logger()

        # Verify logger exists and has correct name
        assert logger is not None
        assert logger.name == "src.services.task_service"

        # Verify logger has handlers configured
        assert len(logger.handlers) > 0 or len(logging.root.handlers) > 0

    # User Story 1 tests
    def test_create_task_success(self):
        """Test successful task creation with valid inputs."""
        success, message, task = task_service.create_task(
            "Buy groceries", "Milk, bread, eggs", "High"
        )

        assert success is True
        assert "success" in message.lower() or "added" in message.lower()
        assert task is not None
        assert task["id"] == 1
        assert task["title"] == "Buy groceries"
        assert task["description"] == "Milk, bread, eggs"
        assert task["priority"] == "High"
        assert task["complete"] is False

        # Verify state updated
        assert len(task_service.tasks) == 1
        assert task_service.next_id == 2

    def test_create_task_empty_title(self):
        """Test that empty title is rejected."""
        success, message, task = task_service.create_task("", "Description", "High")

        assert success is False
        assert "empty" in message.lower() or "title" in message.lower()
        assert task is None
        assert len(task_service.tasks) == 0

    def test_create_task_invalid_priority(self):
        """Test that invalid priority is rejected."""
        success, message, task = task_service.create_task(
            "Valid title",
            "Description",
            "Urgent",  # Invalid priority
        )

        assert success is False
        assert "priority" in message.lower()
        assert task is None
        assert len(task_service.tasks) == 0

    def test_get_all_tasks_sorted(self):
        """Test that tasks are sorted by completion, priority, ID."""
        # Create tasks in non-sorted order
        task_service.create_task("Low incomplete", "", "Low")  # ID 1
        task_service.create_task("High complete", "", "High")  # ID 2
        task_service.create_task("Medium incomplete", "", "Medium")  # ID 3
        task_service.create_task("High incomplete", "", "High")  # ID 4

        # Mark task 2 as complete
        task_service.tasks[1]["complete"] = True

        success, message, tasks = task_service.get_all_tasks()

        assert success is True
        assert len(tasks) == 4

        # Verify sorting: incomplete first, then by priority, then by ID
        # Expected order: ID 4 (High, incomplete), ID 3 (Medium, incomplete),
        #                 ID 1 (Low, incomplete), ID 2 (High, complete)
        assert tasks[0]["id"] == 4  # High, incomplete
        assert tasks[1]["id"] == 3  # Medium, incomplete
        assert tasks[2]["id"] == 1  # Low, incomplete
        assert tasks[3]["id"] == 2  # High, complete

    def test_get_all_tasks_empty(self):
        """Test empty list handling."""
        success, message, tasks = task_service.get_all_tasks()

        assert success is True
        assert isinstance(tasks, list)
        assert len(tasks) == 0
        assert "no tasks" in message.lower() or "found" in message.lower()

    # User Story 2 tests
    def test_toggle_completion_mark_complete(self):
        """Test marking task as complete (false→true)."""
        # Create a task
        task_service.create_task("Test task", "Description", "High")

        # Toggle to complete
        success, message, task = task_service.toggle_task_completion(1)

        assert success is True
        assert "complete" in message.lower()
        assert task["complete"] is True

    def test_toggle_completion_mark_incomplete(self):
        """Test marking task as incomplete (true→false)."""
        # Create a task and mark it complete
        task_service.create_task("Test task", "Description", "High")
        task_service.tasks[0]["complete"] = True

        # Toggle to incomplete
        success, message, task = task_service.toggle_task_completion(1)

        assert success is True
        assert "incomplete" in message.lower()
        assert task["complete"] is False

    def test_toggle_completion_task_not_found(self):
        """Test error handling for non-existent task."""
        success, message, task = task_service.toggle_task_completion(999)

        assert success is False
        assert "not found" in message.lower()
        assert task is None

    # User Story 3 tests
    def test_update_task_partial_title_only(self):
        """Test updating only title field."""
        # Create a task
        task_service.create_task("Original title", "Original description", "High")

        # Update only title
        success, message, task = task_service.update_task(1, title="Updated title")

        assert success is True
        assert "updated" in message.lower()
        assert task["title"] == "Updated title"
        assert task["description"] == "Original description"
        assert task["priority"] == "High"

    def test_update_task_all_fields(self):
        """Test updating all fields together."""
        # Create a task
        task_service.create_task("Original title", "Original description", "High")

        # Update all fields
        success, message, task = task_service.update_task(
            1, title="New title", description="New description", priority="Low"
        )

        assert success is True
        assert task["title"] == "New title"
        assert task["description"] == "New description"
        assert task["priority"] == "Low"

    def test_update_task_validation_errors(self):
        """Test validation errors during update."""
        # Create a task
        task_service.create_task("Original title", "Description", "High")

        # Test empty title
        success, message, task = task_service.update_task(1, title="")
        assert success is False
        assert "empty" in message.lower()

        # Test invalid priority
        success, message, task = task_service.update_task(1, priority="Urgent")
        assert success is False
        assert "priority" in message.lower()

        # Test task not found
        success, message, task = task_service.update_task(999, title="New title")
        assert success is False
        assert "not found" in message.lower()

    # User Story 4 tests
    def test_delete_task_success(self):
        """Test successful task deletion."""
        # Create a task
        task_service.create_task("Task to delete", "Description", "High")

        # Delete it
        success, message, result = task_service.delete_task(1)

        assert success is True
        assert "deleted" in message.lower()
        assert result is None
        assert len(task_service.tasks) == 0

    def test_delete_task_not_found(self):
        """Test error handling for deleting non-existent task."""
        success, message, result = task_service.delete_task(999)

        assert success is False
        assert "not found" in message.lower()
        assert result is None

    def test_delete_task_id_not_reused(self):
        """Test that IDs are never reused after deletion."""
        # Create task with ID 1
        task_service.create_task("Task 1", "", "High")
        assert task_service.next_id == 2

        # Create task with ID 2
        task_service.create_task("Task 2", "", "Medium")
        assert task_service.next_id == 3

        # Delete task 1
        task_service.delete_task(1)

        # Create new task - should get ID 3, not reuse ID 1
        task_service.create_task("Task 3", "", "Low")
        assert task_service.next_id == 4

        # Verify task IDs are 2 and 3 (not 1 and 2)
        task_ids = [t["id"] for t in task_service.tasks]
        assert 2 in task_ids
        assert 3 in task_ids
        assert 1 not in task_ids
