# Service Layer Contract

**Feature**: CLI Todo App with Basic CRUD Operations
**Module**: `src/services/task_service.py`
**Date**: 2025-12-17

## Overview

This document defines the public interface contract for the task service layer. These functions are called by the CLI layer and encapsulate all business logic and data management.

## Response Format

All service functions return a tuple for consistent error handling:

```python
(success: bool, message: str, data: Optional[dict | list[dict]])
```

- **success**: `True` if operation succeeded, `False` if validation or logic error
- **message**: Human-readable message for user display (success confirmation or error description)
- **data**: Result data (task dict, task list, or None for delete/errors)

## Function Contracts

### create_task

**Purpose**: Add a new task to the task list

**Signature**:
```python
def create_task(title: str, description: str, priority: str) -> tuple[bool, str, Optional[dict]]:
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

    Raises:
        None (returns error tuple instead)
    """
```

**Input Validation**:
- `title`: Must not be empty after `strip()`
- `priority`: Must be exactly one of `["High", "Medium", "Low"]` (case-sensitive)
- `description`: Always valid (no constraints)

**Success Response**:
```python
(True, "Task added successfully", {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "High",
    "complete": False
})
```

**Error Responses**:
```python
# Empty title
(False, "Title cannot be empty", None)

# Invalid priority
(False, "Priority must be exactly 'High', 'Medium', or 'Low'", None)
```

**Side Effects**:
- Increments global `next_id` counter
- Appends task to global `tasks` list
- Logs: `INFO: Task created - ID: {id}, Title: {title}`

---

### get_all_tasks

**Purpose**: Retrieve all tasks sorted by priority and completion status

**Signature**:
```python
def get_all_tasks() -> tuple[bool, str, list[dict]]:
    """Get all tasks sorted by completion, priority, and ID.

    Returns:
        tuple: (success, message, task_list)
            success: Always True
            message: Status message
            task_list: List of task dicts, sorted or empty list

    Raises:
        None
    """
```

**Sort Order**:
1. Incomplete tasks before completed tasks
2. Within each group: High → Medium → Low priority
3. Within same priority/status: ID ascending (oldest first)

**Success Response (with tasks)**:
```python
(True, "Found 3 tasks", [
    {"id": 1, "title": "High priority task", "priority": "High", "complete": False, ...},
    {"id": 3, "title": "Medium priority task", "priority": "Medium", "complete": False, ...},
    {"id": 2, "title": "Completed high priority", "priority": "High", "complete": True, ...}
])
```

**Success Response (empty)**:
```python
(True, "No tasks found", [])
```

**Side Effects**: None (read-only operation)

---

### get_task_by_id

**Purpose**: Retrieve a single task by its ID

**Signature**:
```python
def get_task_by_id(task_id: int) -> tuple[bool, str, Optional[dict]]:
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
```

**Success Response**:
```python
(True, "Task found", {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "High",
    "complete": False
})
```

**Error Response**:
```python
# Task not found
(False, "Task not found", None)
```

**Side Effects**: None (read-only operation)

---

### update_task

**Purpose**: Update one or more fields of an existing task

**Signature**:
```python
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None
) -> tuple[bool, str, Optional[dict]]:
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
```

**Partial Update Behavior**:
- Only non-None arguments are used to update fields
- Unspecified fields (None) remain unchanged
- At least one field must be provided (not all None)

**Input Validation** (only for provided fields):
- `title` (if provided): Must not be empty after `strip()`
- `priority` (if provided): Must be exactly one of `["High", "Medium", "Low"]`
- `description` (if provided): Always valid
- `task_id`: Must exist in task list

**Success Response**:
```python
# Updated only title
(True, "Task updated successfully", {
    "id": 1,
    "title": "Buy organic groceries",  # Updated
    "description": "Milk, bread, eggs",  # Unchanged
    "priority": "High",  # Unchanged
    "complete": False
})
```

**Error Responses**:
```python
# Task not found
(False, "Task not found", None)

# Empty title provided
(False, "Title cannot be empty", None)

# Invalid priority provided
(False, "Priority must be exactly 'High', 'Medium', or 'Low'", None)

# No fields provided (all None)
(False, "No fields to update", None)
```

**Side Effects**:
- Modifies task dict in-place
- Logs: `INFO: Task updated - ID: {id}, Fields: {changed_fields}`

---

### toggle_task_completion

**Purpose**: Toggle task completion status between complete and incomplete

**Signature**:
```python
def toggle_task_completion(task_id: int) -> tuple[bool, str, Optional[dict]]:
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
```

**Toggle Behavior**:
- If `complete == False`, set to `True`
- If `complete == True`, set to `False`
- No validation beyond task existence

**Success Response**:
```python
# Marking complete
(True, "Task marked as complete", {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "High",
    "complete": True  # Toggled from False
})

# Marking incomplete
(True, "Task marked as incomplete", {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "High",
    "complete": False  # Toggled from True
})
```

**Error Response**:
```python
# Task not found
(False, "Task not found", None)
```

**Side Effects**:
- Modifies task `complete` field in-place
- Logs: `INFO: Task completion toggled - ID: {id}, Complete: {status}`

---

### delete_task

**Purpose**: Remove a task from the task list permanently

**Signature**:
```python
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
```

**Deletion Behavior**:
- Task removed from list permanently
- ID is never reused (no decrement of `next_id`)
- Cannot be undone within session

**Success Response**:
```python
(True, "Task deleted successfully", None)
```

**Error Response**:
```python
# Task not found
(False, "Task not found", None)
```

**Side Effects**:
- Removes task from global `tasks` list
- Does NOT decrement `next_id` counter
- Logs: `INFO: Task deleted - ID: {id}`

---

## State Management

### Module-Level State

```python
# Global state in task_service.py
tasks: list[dict] = []       # Task storage
next_id: int = 1             # ID counter
```

**Access Pattern**:
- CLI layer calls service functions; never accesses state directly
- Service layer encapsulates all state mutation
- State is session-scoped (cleared on app exit)

### Thread Safety

**Not Required**: Single-threaded CLI application, blocking I/O, no concurrency.

## Error Handling Philosophy

### Service Layer Responsibilities

- **Validate** all business rules (title non-empty, priority valid, task exists)
- **Return** error tuples instead of raising exceptions
- **Log** all operations at INFO level (success and failure)
- **Provide** user-friendly error messages

### CLI Layer Responsibilities

- **Display** error messages from service layer
- **Re-prompt** user on validation errors
- **Format** success confirmations for user
- **Never** access tasks list or next_id directly

## Usage Examples

### Example 1: Add Task Flow

```python
# CLI layer calls service
success, message, task = create_task("Buy milk", "Whole milk", "High")

if success:
    print(f"✓ {message}")
    print(f"Task ID: {task['id']}")
else:
    print(f"✗ {message}")
    # Re-prompt user
```

### Example 2: View All Tasks

```python
# CLI layer calls service
success, message, task_list = get_all_tasks()

if not task_list:
    print("No tasks to display")
else:
    print(f"{message}")
    for task in task_list:
        # Format and display each task
        pass
```

### Example 3: Partial Update

```python
# Update only priority, leave title and description unchanged
success, message, task = update_task(
    task_id=1,
    priority="Low"  # Only this field updates
)

if success:
    print(f"✓ {message}")
else:
    print(f"✗ {message}")
```

### Example 4: Toggle Completion

```python
# Toggle between complete/incomplete
success, message, task = toggle_task_completion(task_id=1)

if success:
    status = "complete" if task["complete"] else "incomplete"
    print(f"✓ Task marked as {status}")
else:
    print(f"✗ {message}")
```

## Testing Contract

### Unit Test Requirements

Each function must have unit tests covering:

1. **Happy path**: Valid inputs, successful operation
2. **Validation errors**: Invalid inputs (empty title, bad priority)
3. **Not found errors**: Non-existent task IDs
4. **Edge cases**: Empty list, boundary conditions
5. **State verification**: Confirm tasks list and next_id updates

### Test Isolation

- Reset state (`tasks = []`, `next_id = 1`) before each test
- No dependencies between tests
- Mock logging to avoid output during tests

## Contract Versioning

**Version**: 1.0.0
**Last Updated**: 2025-12-17

**Breaking Changes** (for future reference):
- Changing return tuple structure
- Removing or renaming functions
- Changing validation rules (stricter)

**Non-Breaking Changes**:
- Adding optional parameters with defaults
- Adding new functions
- Relaxing validation rules
- Improving error messages
