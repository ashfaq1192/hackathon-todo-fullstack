# Quickstart Guide: CLI Todo App Development

**Feature**: CLI Todo App with Basic CRUD Operations
**Date**: 2025-12-17
**For**: Developers implementing this feature

## Overview

This guide helps you quickly set up the development environment and understand the implementation workflow for the CLI Todo App. Follow these steps to go from zero to running tests.

## Prerequisites

- Python 3.13+ installed
- UV package manager installed
- Git repository cloned
- On branch `001-cli-todo-app`

## Quick Setup (5 minutes)

### 1. Create Virtual Environment

```bash
# From repository root
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Development dependencies only (no runtime dependencies needed)
uv add pytest pytest-cov ruff
```

### 3. Create Environment Configuration

```bash
# Create .env file
cat > .env << EOF
LOG_LEVEL=DEBUG
APP_NAME=evolution-todo
EOF
```

### 4. Verify Setup

```bash
# Check Python version
python --version  # Should be 3.13+

# Check UV
uv --version

# Check virtual environment
which python  # Should point to .venv/bin/python
```

## Project Structure Reference

```
/mnt/e/projects/hackathon-todo/
├── src/
│   ├── models/
│   │   └── task.py              # Task entity (implement first)
│   ├── services/
│   │   └── task_service.py      # CRUD logic (implement second)
│   ├── cli/
│   │   ├── menu.py              # Menu handling (implement third)
│   │   └── display.py           # Output formatting (implement third)
│   └── main.py                  # Entry point (implement last)
│
├── tests/
│   ├── unit/
│   │   ├── models/
│   │   │   └── test_task.py
│   │   ├── services/
│   │   │   └── test_task_service.py
│   │   └── cli/
│   │       ├── test_menu.py
│   │       └── test_display.py
│   └── integration/
│       └── test_app_flow.py
│
├── specs/001-cli-todo-app/
│   ├── spec.md                  # Requirements (read first)
│   ├── plan.md                  # This plan (read second)
│   ├── research.md              # Tech decisions (reference)
│   ├── data-model.md            # Data structures (reference)
│   ├── contracts/               # API contracts (reference)
│   └── quickstart.md            # This file
│
├── .env                         # Environment config
├── pyproject.toml               # UV project config
└── README.md                    # User-facing docs
```

## Implementation Workflow (TDD)

### Step 1: Understand Requirements

1. Read `specs/001-cli-todo-app/spec.md` - Feature requirements and acceptance criteria
2. Read `specs/001-cli-todo-app/data-model.md` - Task structure and validation rules
3. Read `specs/001-cli-todo-app/contracts/service_contract.md` - Service layer API
4. Read `specs/001-cli-todo-app/contracts/cli_contract.md` - CLI layer API

### Step 2: Create Directory Structure

```bash
# From repository root
mkdir -p src/models src/services src/cli
mkdir -p tests/unit/models tests/unit/services tests/unit/cli tests/integration

# Create __init__.py files for Python packages
touch src/__init__.py src/models/__init__.py src/services/__init__.py src/cli/__init__.py
touch tests/__init__.py tests/unit/__init__.py tests/unit/models/__init__.py
touch tests/unit/services/__init__.py tests/unit/cli/__init__.py tests/integration/__init__.py
```

### Step 3: TDD Cycle (Red-Green-Refactor)

**Order of Implementation**:

1. **Models Layer** (`src/models/task.py`)
   - Write tests first: `tests/unit/models/test_task.py`
   - Implement task validation functions
   - Run tests: `pytest tests/unit/models/`

2. **Services Layer** (`src/services/task_service.py`)
   - Write tests first: `tests/unit/services/test_task_service.py`
   - Implement CRUD functions (see service_contract.md)
   - Run tests: `pytest tests/unit/services/`

3. **CLI Layer** (`src/cli/menu.py`, `src/cli/display.py`)
   - Write tests first: `tests/unit/cli/test_menu.py`, `tests/unit/cli/test_display.py`
   - Implement input/output functions (see cli_contract.md)
   - Run tests: `pytest tests/unit/cli/`

4. **Main Entry Point** (`src/main.py`)
   - Write integration test: `tests/integration/test_app_flow.py`
   - Implement main loop
   - Run all tests: `pytest`

### Step 4: Testing Commands

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/models/test_task.py

# Run tests matching pattern
pytest -k "test_create_task"

# Run with verbose output
pytest -v

# Run with output capture disabled (see prints)
pytest -s
```

### Step 5: Code Quality Checks

```bash
# Lint code (PEP8 compliance)
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Check specific file
ruff check src/models/task.py
```

## Running the Application

### Development Mode

```bash
# From repository root, with virtual environment activated
python src/main.py
```

### Expected Behavior

```
=== Todo App Menu ===
1. Add Task
2. View Tasks
3. Mark Task Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit

Enter your choice (1-6):
```

## Key Implementation Patterns

### Pattern 1: Service Layer Function Template

```python
# src/services/task_service.py

def create_task(title: str, description: str, priority: str) -> tuple[bool, str, Optional[dict]]:
    """Create a new task with auto-generated ID."""

    # 1. Validate inputs
    title = title.strip()
    if not title:
        return (False, "Title cannot be empty", None)

    if priority not in ["High", "Medium", "Low"]:
        return (False, "Priority must be exactly 'High', 'Medium', or 'Low'", None)

    # 2. Create task
    global next_id
    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "priority": priority,
        "complete": False
    }

    # 3. Update state
    tasks.append(task)
    next_id += 1

    # 4. Log operation
    logger.info(f"Task created - ID: {task['id']}, Title: {title}")

    # 5. Return success
    return (True, "Task added successfully", task)
```

### Pattern 2: CLI Input Validation Loop

```python
# src/cli/menu.py

def get_menu_choice() -> int:
    """Prompt user for menu choice and validate."""

    while True:
        try:
            choice = input("Enter your choice (1-6): ").strip()
            choice_int = int(choice)

            if 1 <= choice_int <= 6:
                return choice_int
            else:
                print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
```

### Pattern 3: Test with Mock Input

```python
# tests/unit/cli/test_menu.py

from unittest.mock import patch
from src.cli.menu import get_menu_choice

@patch('builtins.input', side_effect=['abc', '0', '3'])
def test_get_menu_choice_with_invalid_then_valid(mock_input):
    """Test input validation loop."""
    # First two inputs are invalid, third is valid
    choice = get_menu_choice()
    assert choice == 3
    assert mock_input.call_count == 3
```

### Pattern 4: Integration Test Example

```python
# tests/integration/test_app_flow.py

from unittest.mock import patch
from src.services.task_service import create_task, get_all_tasks

def test_add_and_view_task_flow():
    """Test complete add and view workflow."""

    # 1. Create task
    success, message, task = create_task("Test Task", "Description", "High")
    assert success is True
    assert task["id"] == 1

    # 2. View tasks
    success, message, task_list = get_all_tasks()
    assert success is True
    assert len(task_list) == 1
    assert task_list[0]["title"] == "Test Task"
```

## Common Development Tasks

### Add New Test

```bash
# Create test file following naming convention
touch tests/unit/services/test_new_feature.py

# Write test
cat > tests/unit/services/test_new_feature.py << 'EOF'
import pytest
from src.services.task_service import new_function

def test_new_function():
    """Test description."""
    result = new_function()
    assert result is not None
EOF

# Run test
pytest tests/unit/services/test_new_feature.py
```

### Check Coverage for Specific Module

```bash
# Coverage for services only
pytest --cov=src/services --cov-report=term-missing tests/unit/services/

# Coverage for entire src with HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View in browser
```

### Debug Test Failure

```bash
# Run with verbose output and no capture (see prints)
pytest -vvs tests/unit/services/test_task_service.py::test_create_task

# Run with debugger on failure
pytest --pdb tests/unit/services/test_task_service.py
```

## Troubleshooting

### Issue: Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should be .venv/bin/python

# Ensure PYTHONPATH includes repository root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with python -m
python -m pytest tests/
```

### Issue: Tests Not Found

```bash
# Ensure __init__.py files exist in all directories
find . -name __init__.py

# If missing, create them
touch tests/__init__.py tests/unit/__init__.py
```

### Issue: Coverage Too Low

```bash
# Identify uncovered lines
pytest --cov=src --cov-report=term-missing

# Output shows line numbers that need tests:
# src/services/task_service.py   85%   25-27, 45
# Write tests to cover lines 25-27 and 45
```

### Issue: PEP8 Violations

```bash
# Check what's wrong
ruff check src/

# Auto-fix some issues
ruff check --fix src/

# Format code
ruff format src/
```

## Definition of Done Checklist

### MVP Checklist (70% Coverage)

- [ ] All 5 CRUD operations implemented (Add, View, Mark, Update, Delete)
- [ ] In-memory storage working with list of dicts
- [ ] Menu-driven CLI with user prompts
- [ ] Input validation for all edge cases
- [ ] Error handling with user-friendly messages
- [ ] Test coverage ≥70% (`pytest --cov=src --cov-report=term-missing`)
- [ ] All tests passing (`pytest` exits with 0)
- [ ] PEP8 compliant (`ruff check src/` has no errors)
- [ ] README.md with setup instructions
- [ ] CLAUDE.md with session documentation

### Production-Ready Checklist (80% Coverage)

All MVP items PLUS:

- [ ] Test coverage ≥80%
- [ ] Comprehensive edge case coverage
- [ ] All functions have Google-style docstrings
- [ ] Logging implemented for all CRUD operations
- [ ] Enhanced error messages with context
- [ ] Integration tests for all workflows

## Next Steps After Implementation

1. **Verify MVP Criteria**: Run checklist above
2. **Document Session**: Update CLAUDE.md with prompts and iterations
3. **Create README.md**: User-facing setup and usage guide
4. **Run `/sp.tasks`**: Generate task breakdown for implementation
5. **Run `/sp.implement`**: Execute implementation via Claude Code

## Reference Documentation

- **Feature Spec**: `specs/001-cli-todo-app/spec.md`
- **Data Model**: `specs/001-cli-todo-app/data-model.md`
- **Service Contract**: `specs/001-cli-todo-app/contracts/service_contract.md`
- **CLI Contract**: `specs/001-cli-todo-app/contracts/cli_contract.md`
- **Research Decisions**: `specs/001-cli-todo-app/research.md`
- **Constitution**: `.specify/memory/constitution.md`

## Quick Reference Commands

```bash
# Setup
uv venv && source .venv/bin/activate
uv add pytest pytest-cov ruff

# Development
pytest --cov=src --cov-report=term-missing  # Test with coverage
ruff check src/ tests/                      # Lint code
python src/main.py                          # Run app

# Specific tests
pytest tests/unit/models/                   # Test models only
pytest -k "test_create"                     # Test matching pattern
pytest -vvs                                 # Verbose with output

# Code quality
ruff check --fix src/                       # Auto-fix linting
ruff format src/                            # Format code
```

## Support

- **Architecture Questions**: Refer to `plan.md` and `research.md`
- **API Questions**: Refer to `contracts/service_contract.md` and `contracts/cli_contract.md`
- **Requirements Questions**: Refer to `spec.md`
- **Constitution Compliance**: Refer to `.specify/memory/constitution.md`
