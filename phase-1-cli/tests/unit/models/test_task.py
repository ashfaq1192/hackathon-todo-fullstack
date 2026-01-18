"""Unit tests for task validation.

This module contains tests for task entity validation logic including
title validation, priority validation, and task data structure.
"""

from src.models.task import create_task_dict, validate_priority, validate_title


class TestTaskValidation:
    """Test suite for task validation functions."""

    def test_validate_title_non_empty(self):
        """Test that empty titles are rejected."""
        is_valid, error = validate_title("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_title_whitespace_only(self):
        """Test that whitespace-only titles are rejected."""
        is_valid, error = validate_title("   ")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_title_valid(self):
        """Test that valid titles are accepted."""
        is_valid, error = validate_title("Buy groceries")
        assert is_valid is True
        assert error == ""

    def test_validate_priority_valid_values(self):
        """Test that only High, Medium, Low are accepted for priority."""
        # Test valid priorities
        for priority in ["High", "Medium", "Low"]:
            is_valid, error = validate_priority(priority)
            assert is_valid is True, f"{priority} should be valid"
            assert error == ""

    def test_validate_priority_case_sensitive(self):
        """Test that priority values are case-sensitive."""
        # Test invalid case variations
        for invalid in ["high", "HIGH", "medium", "MEDIUM", "low", "LOW", "Urgent"]:
            is_valid, error = validate_priority(invalid)
            assert is_valid is False, f"{invalid} should be invalid"
            assert "High" in error and "Medium" in error and "Low" in error

    def test_create_task_dict(self):
        """Test task dictionary creation."""
        task = create_task_dict(1, "Test Task", "Description", "High")
        assert task["id"] == 1
        assert task["title"] == "Test Task"
        assert task["description"] == "Description"
        assert task["priority"] == "High"
        assert task["complete"] is False
