# CLI Layer Contract

**Feature**: CLI Todo App with Basic CRUD Operations
**Modules**: `src/cli/menu.py`, `src/cli/display.py`
**Date**: 2025-12-17

## Overview

This document defines the public interface contract for the CLI layer. These functions handle user interaction, input parsing, and output formatting. The CLI layer calls the service layer but never directly accesses data structures.

## Module: menu.py

### display_main_menu

**Purpose**: Display the main menu with numbered options

**Signature**:
```python
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
```

**Output Format**:
```
=== Todo App Menu ===
1. Add Task
2. View Tasks
3. Mark Task Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit
```

**Behavior**:
- Always displays same options in same order
- No input handling (only display)
- Clear visual separation from other output

---

### get_menu_choice

**Purpose**: Get and validate user's menu selection

**Signature**:
```python
def get_menu_choice() -> int:
    """Prompt user for menu choice and validate input.

    Returns:
        int: Valid menu choice (1-6)

    Raises:
        None (loops until valid input received)
    """
```

**Validation**:
- Input must be numeric
- Input must be in range 1-6
- Strips whitespace before parsing
- Handles invalid input gracefully (re-prompts)

**Input Handling**:
```python
# Valid inputs
"1" → 1
"3" → 3
"  2  " → 2 (stripped)

# Invalid inputs (re-prompt)
"abc" → "Invalid input. Please enter a number."
"0" → "Invalid choice. Please enter 1-6."
"7" → "Invalid choice. Please enter 1-6."
"" → "Invalid input. Please enter a number."
```

**User Interaction**:
```
Enter your choice (1-6): abc
Invalid input. Please enter a number.
Enter your choice (1-6): 0
Invalid choice. Please enter 1-6.
Enter your choice (1-6): 3
```

---

### prompt_add_task

**Purpose**: Gather task details from user for creation

**Signature**:
```python
def prompt_add_task() -> Optional[tuple[str, str, str]]:
    """Prompt user for task details (title, description, priority).

    Returns:
        tuple: (title, description, priority) if successful
        None: if user cancels

    Raises:
        None
    """
```

**Prompts**:
1. `"Enter task title: "`
2. `"Enter task description (optional): "`
3. `"Enter priority (High/Medium/Low): "`

**Validation**:
- Title: Cannot be empty, re-prompt if empty
- Description: Optional, empty string allowed
- Priority: Must be "High", "Medium", or "Low" (case-sensitive), re-prompt if invalid

**Return Examples**:
```python
# Valid input
("Buy groceries", "Milk, bread, eggs", "High")

# Empty description (valid)
("Call dentist", "", "Low")

# User provided all valid inputs
("Review PR", "Check for security issues", "Medium")
```

**User Interaction**:
```
Enter task title:
Title cannot be empty. Please try again.
Enter task title: Buy groceries
Enter task description (optional): Milk, bread, eggs
Enter priority (High/Medium/Low): high
Invalid priority. Must be exactly 'High', 'Medium', or 'Low'.
Enter priority (High/Medium/Low): High
```

---

### prompt_task_id

**Purpose**: Get a valid task ID from user

**Signature**:
```python
def prompt_task_id(prompt_message: str = "Enter task ID: ") -> int:
    """Prompt user for a task ID and validate numeric input.

    Args:
        prompt_message: Custom prompt text (default: "Enter task ID: ")

    Returns:
        int: Positive integer task ID

    Raises:
        None (loops until valid input received)
    """
```

**Validation**:
- Input must be numeric
- Input must be positive integer (> 0)
- Strips whitespace before parsing
- Handles invalid input gracefully (re-prompts)

**Input Handling**:
```python
# Valid inputs
"1" → 1
"42" → 42
"  5  " → 5 (stripped)

# Invalid inputs (re-prompt)
"abc" → "Invalid input. Please enter a number."
"0" → "Task ID must be positive."
"-5" → "Task ID must be positive."
"" → "Invalid input. Please enter a number."
```

---

### prompt_update_task

**Purpose**: Gather partial update fields from user

**Signature**:
```python
def prompt_update_task() -> tuple[int, Optional[str], Optional[str], Optional[str]]:
    """Prompt user for task ID and fields to update.

    Returns:
        tuple: (task_id, title or None, description or None, priority or None)
            At least one field (title/description/priority) will be non-None

    Raises:
        None
    """
```

**Prompts**:
1. `"Enter task ID: "` (required, validated)
2. `"Enter new title (or press Enter to skip): "` (optional)
3. `"Enter new description (or press Enter to skip): "` (optional)
4. `"Enter new priority (or press Enter to skip): "` (optional)

**Partial Update Logic**:
- Empty input (just Enter) → field is None (skip update for that field)
- Non-empty input → field is updated
- At least one field must be non-None (re-prompt if all skipped)
- Title validation: if provided, cannot be only whitespace
- Priority validation: if provided, must be valid value

**Return Examples**:
```python
# Update only title
(1, "New title", None, None)

# Update title and priority
(2, "Updated task", None, "Low")

# Update all fields
(3, "New title", "New description", "High")

# Update only description (empty string is valid)
(4, None, "", None)
```

**User Interaction**:
```
Enter task ID: 1
Enter new title (or press Enter to skip): Updated Title
Enter new description (or press Enter to skip):
Enter new priority (or press Enter to skip): Low
```

---

## Module: display.py

### display_task

**Purpose**: Format and display a single task

**Signature**:
```python
def display_task(task: dict) -> None:
    """Display a single task with all fields formatted.

    Args:
        task: Task dictionary with id, title, description, priority, complete

    Returns:
        None

    Raises:
        None
    """
```

**Output Format**:
```
[ID: 1] Buy groceries
  Priority: High
  Status: Incomplete
  Description: Milk, bread, eggs
```

**Formatting Rules**:
- ID in square brackets
- Title on first line
- Priority, Status, Description indented
- Status: "Complete" or "Incomplete" based on boolean
- Empty description shown as "(no description)"

**Examples**:
```
# Task with description
[ID: 1] Buy groceries
  Priority: High
  Status: Incomplete
  Description: Milk, bread, eggs

# Task without description
[ID: 2] Call dentist
  Priority: Low
  Status: Complete
  Description: (no description)

# Completed task
[ID: 3] Review pull request
  Priority: Medium
  Status: Complete
  Description: Check for security vulnerabilities
```

---

### display_task_list

**Purpose**: Display all tasks in formatted list

**Signature**:
```python
def display_task_list(tasks: list[dict]) -> None:
    """Display all tasks in a formatted list.

    Args:
        tasks: List of task dictionaries (already sorted)

    Returns:
        None

    Raises:
        None
    """
```

**Output Format** (multiple tasks):
```
=== Your Tasks (3 total) ===

[ID: 1] High priority task
  Priority: High
  Status: Incomplete
  Description: Critical work

[ID: 3] Medium priority task
  Priority: Medium
  Status: Incomplete
  Description: Important but not urgent

[ID: 2] Completed task
  Priority: High
  Status: Complete
  Description: Already done
```

**Output Format** (empty list):
```
=== Your Tasks (0 total) ===

No tasks to display. Add a task to get started!
```

**Formatting Rules**:
- Header shows total count
- Blank line before first task
- Blank line between tasks
- Tasks displayed via `display_task()` function
- Empty list shows helpful message

---

### display_success_message

**Purpose**: Display success confirmation with visual indicator

**Signature**:
```python
def display_success_message(message: str) -> None:
    """Display a success message with visual indicator.

    Args:
        message: Success message text

    Returns:
        None

    Raises:
        None
    """
```

**Output Format**:
```
✓ Task added successfully
```

**Usage**:
- Prefix with checkmark (✓) or `[SUCCESS]` if unicode unavailable
- Green text (optional enhancement for production-ready)
- Called after successful operations

---

### display_error_message

**Purpose**: Display error message with visual indicator

**Signature**:
```python
def display_error_message(message: str) -> None:
    """Display an error message with visual indicator.

    Args:
        message: Error message text

    Returns:
        None

    Raises:
        None
    """
```

**Output Format**:
```
✗ Task not found
```

**Usage**:
- Prefix with cross (✗) or `[ERROR]` if unicode unavailable
- Red text (optional enhancement for production-ready)
- Called after validation failures or errors

---

## User Interaction Flows

### Flow 1: Add Task

```
=== Todo App Menu ===
1. Add Task
2. View Tasks
3. Mark Task Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit

Enter your choice (1-6): 1

Enter task title: Buy groceries
Enter task description (optional): Milk, bread, eggs
Enter priority (High/Medium/Low): High

✓ Task added successfully
```

### Flow 2: View Tasks

```
Enter your choice (1-6): 2

=== Your Tasks (2 total) ===

[ID: 1] Buy groceries
  Priority: High
  Status: Incomplete
  Description: Milk, bread, eggs

[ID: 2] Call dentist
  Priority: Low
  Status: Complete
  Description: (no description)
```

### Flow 3: Mark Task Complete

```
Enter your choice (1-6): 3

Enter task ID: 1

✓ Task marked as complete
```

### Flow 4: Update Task (Partial)

```
Enter your choice (1-6): 4

Enter task ID: 1
Enter new title (or press Enter to skip): Buy organic groceries
Enter new description (or press Enter to skip):
Enter new priority (or press Enter to skip):

✓ Task updated successfully
```

### Flow 5: Delete Task

```
Enter your choice (1-6): 5

Enter task ID: 2

✓ Task deleted successfully
```

### Flow 6: Exit

```
Enter your choice (1-6): 6

Thank you for using Todo App. Goodbye!
```

## Error Handling Examples

### Invalid Menu Choice

```
Enter your choice (1-6): 9
Invalid choice. Please enter 1-6.
Enter your choice (1-6): abc
Invalid input. Please enter a number.
Enter your choice (1-6): 1
```

### Empty Title

```
Enter task title:
Title cannot be empty. Please try again.
Enter task title:
Title cannot be empty. Please try again.
Enter task title: Buy milk
```

### Invalid Priority

```
Enter priority (High/Medium/Low): high
Invalid priority. Must be exactly 'High', 'Medium', or 'Low'.
Enter priority (High/Medium/Low): MEDIUM
Invalid priority. Must be exactly 'High', 'Medium', or 'Low'.
Enter priority (High/Medium/Low): Medium
```

### Task Not Found

```
Enter task ID: 999

✗ Task not found
```

## Design Principles

### Separation of Concerns

- **menu.py**: Input gathering and validation (no business logic)
- **display.py**: Output formatting (no input handling)
- **service layer**: Business logic (never touches CLI)

### User-Friendly Interaction

- Clear prompts with examples
- Descriptive error messages
- Re-prompt on invalid input (never crash)
- Visual feedback (✓/✗ indicators)

### Input Validation Strategy

- **CLI validates format**: numeric, non-empty, range
- **Service validates business rules**: priority values, task existence, title content

### No Direct State Access

- CLI never accesses `tasks` list or `next_id` directly
- All data flows through service layer function calls
- CLI receives data as return values only

## Testing Contract

### Mock Requirements

- Mock `input()` with `unittest.mock.patch('builtins.input')`
- Capture `print()` output with `unittest.mock.patch('builtins.print')` or `io.StringIO`
- Test input validation loops (invalid → valid sequences)
- Test display formatting (verify output strings)

### Unit Test Coverage

Each function must have tests for:
- Valid input paths
- Invalid input handling (re-prompt loops)
- Edge cases (empty lists, long strings)
- Output format verification

## Contract Versioning

**Version**: 1.0.0
**Last Updated**: 2025-12-17

**Breaking Changes** (for future reference):
- Changing function signatures
- Changing output formats (if other systems parse)
- Removing functions

**Non-Breaking Changes**:
- Adding optional parameters with defaults
- Improving error messages
- Adding visual enhancements (colors, formatting)
