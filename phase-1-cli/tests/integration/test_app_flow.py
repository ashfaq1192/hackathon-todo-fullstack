"""Integration tests for complete application workflows.

This module contains end-to-end tests that verify complete user workflows
combining service layer, CLI layer, and data flow.
"""

from src.services import task_service


class TestIntegrationFlows:
    """Test suite for end-to-end application workflows."""

    def setup_method(self):
        """Reset task service state before each test."""
        task_service.tasks = []
        task_service.next_id = 1

    def test_add_and_view_task_flow(self):
        """Test complete workflow: add task and view it in list."""
        # User Story 1: Add and View Tasks

        # Step 1: Create a task
        success, message, task = task_service.create_task(
            "Buy groceries", "Milk, bread, eggs", "High"
        )

        assert success is True
        assert task["id"] == 1
        assert task["title"] == "Buy groceries"
        assert task["complete"] is False

        # Step 2: View all tasks
        success, message, tasks = task_service.get_all_tasks()

        assert success is True
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Buy groceries"

    def test_toggle_completion_flow(self):
        """Test complete workflow: create task, mark complete, mark incomplete."""
        # User Story 2: Mark Complete/Incomplete

        # Create a task
        task_service.create_task("Complete this task", "Test description", "High")

        # Mark as complete
        success, message, task = task_service.toggle_task_completion(1)
        assert success is True
        assert task["complete"] is True

        # Mark as incomplete
        success, message, task = task_service.toggle_task_completion(1)
        assert success is True
        assert task["complete"] is False

    def test_update_task_flow(self):
        """Test complete workflow: create task and update it."""
        # User Story 3: Update Task

        # Create a task
        task_service.create_task("Original title", "Original description", "Low")

        # Update multiple fields
        success, message, task = task_service.update_task(1, title="Updated title", priority="High")

        assert success is True
        assert task["title"] == "Updated title"
        assert task["description"] == "Original description"  # Unchanged
        assert task["priority"] == "High"

    def test_delete_task_flow(self):
        """Test complete workflow: create multiple tasks, delete one, verify list."""
        # User Story 4: Delete Task

        # Create multiple tasks
        task_service.create_task("Task 1", "", "High")
        task_service.create_task("Task 2", "", "Medium")
        task_service.create_task("Task 3", "", "Low")

        # Delete task 2
        success, message, _ = task_service.delete_task(2)
        assert success is True

        # Verify remaining tasks
        success, message, tasks = task_service.get_all_tasks()
        assert len(tasks) == 2
        task_ids = [t["id"] for t in tasks]
        assert 1 in task_ids
        assert 3 in task_ids
        assert 2 not in task_ids

    def test_full_crud_lifecycle(self):
        """Test complete CRUD lifecycle: create, read, update, delete."""
        # Create
        success, _, task = task_service.create_task("Test task", "Description", "Medium")
        assert success is True
        task_id = task["id"]

        # Read (view all)
        success, _, tasks = task_service.get_all_tasks()
        assert len(tasks) == 1

        # Update
        success, _, updated_task = task_service.update_task(task_id, priority="High")
        assert updated_task["priority"] == "High"

        # Delete
        success, _, _ = task_service.delete_task(task_id)
        assert success is True

        # Verify empty
        success, _, tasks = task_service.get_all_tasks()
        assert len(tasks) == 0

    def test_task_sorting_with_multiple_tasks(self):
        """Test task sorting across completion status and priorities."""
        # Create tasks in random order
        task_service.create_task("Low priority", "", "Low")  # ID 1
        task_service.create_task("High priority", "", "High")  # ID 2
        task_service.create_task("Medium priority", "", "Medium")  # ID 3

        # Mark ID 2 as complete
        task_service.toggle_task_completion(2)

        # Get sorted list
        success, _, tasks = task_service.get_all_tasks()

        # Verify sorting: incomplete first (by priority), then completed
        assert tasks[0]["id"] == 3  # Medium, incomplete
        assert tasks[1]["id"] == 1  # Low, incomplete
        assert tasks[2]["id"] == 2  # High, complete

    def test_error_handling_workflow(self):
        """Test error handling across operations."""
        # Try to get task that doesn't exist
        success, _, _ = task_service.get_task_by_id(999)
        assert success is False

        # Try to update non-existent task
        success, _, _ = task_service.update_task(999, title="New")
        assert success is False

        # Try to delete non-existent task
        success, _, _ = task_service.delete_task(999)
        assert success is False

        # Try to toggle non-existent task
        success, _, _ = task_service.toggle_task_completion(999)
        assert success is False
