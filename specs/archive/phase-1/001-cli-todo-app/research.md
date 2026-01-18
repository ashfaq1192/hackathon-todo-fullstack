# Research: CLI Todo App Implementation

**Feature**: CLI Todo App with Basic CRUD Operations
**Date**: 2025-12-17
**Phase**: Phase 0 - Research

## Technology Stack Research

### Python 3.13+ for CLI Application

**Decision**: Use Python 3.13+ with standard library for core functionality

**Rationale**:
- Python 3.13 provides excellent built-in support for CLI applications via `input()` and `print()`
- Standard library includes all necessary tools: list data structures, string formatting, input validation
- No external dependencies needed for MVP reduces complexity and installation friction
- Python's readability aligns with clean code principles (Constitution IV)
- Cross-platform compatibility out of the box

**Alternatives Considered**:
- **Click/Typer frameworks**: Rejected for MVP - adds unnecessary dependency for simple numbered menu
- **Rich library for formatting**: Deferred to production-ready phase - stdlib `print()` sufficient for MVP
- **Python 3.11**: Rejected - constitution specifies 3.13+ for latest features and performance

### In-Memory Storage Pattern

**Decision**: Use Python list of dictionaries for in-memory task storage

**Rationale**:
- Simplest data structure meeting requirements: `[{'id': int, 'title': str, ...}, ...]`
- Direct list manipulation supports all CRUD operations efficiently
- No serialization/deserialization overhead
- Session-scoped requirement (spec.md:line 103) explicitly allows data loss on exit
- Enables easy sorting via `sorted(tasks, key=lambda t: ...)`

**Alternatives Considered**:
- **Class-based ORM (SQLAlchemy)**: Rejected - overkill for in-memory, adds dependency
- **Dataclasses**: Considered but deferred - dict provides sufficient structure for MVP
- **Global state management**: Selected - single tasks list in service layer is appropriate for single-user CLI

### Menu-Driven Interface Pattern

**Decision**: Numbered menu with `input()` and loop-based flow control

**Rationale**:
- Clarification (spec.md:line 15) confirmed numbered menu pattern (1, 2, 3, etc.)
- Standard CLI pattern familiar to users
- Simple implementation: display menu → get input → validate → execute → loop
- Built-in `input()` provides blocking I/O suitable for CLI interaction

**Alternatives Considered**:
- **Command-line arguments (argparse)**: Rejected - spec requires interactive menu, not one-shot commands
- **Text-based UI (curses)**: Rejected - unnecessarily complex for MVP menu
- **Prompt Toolkit**: Deferred - adds dependency, stdlib sufficient for numbered selection

## Best Practices Research

### Task Sorting Algorithm

**Decision**: Multi-level sort by (completion status, priority, ID)

**Rationale**:
- Clarification (spec.md:line 14) specifies: priority (High→Medium→Low), incomplete before completed, then ID ascending
- Python's `sorted()` with tuple keys handles multi-level sorting elegantly
- Priority mapping: `{"High": 0, "Medium": 1, "Low": 2}` for numeric comparison
- Stable sort ensures consistent ordering

**Implementation Pattern**:
```python
priority_order = {"High": 0, "Medium": 1, "Low": 2}
sorted_tasks = sorted(
    tasks,
    key=lambda t: (t["complete"], priority_order[t["priority"]], t["id"])
)
```

### ID Generation Strategy

**Decision**: Counter-based auto-increment with no reuse

**Rationale**:
- Clarification (spec.md:line 13) confirmed IDs never reused after deletion
- Simple counter variable incremented on each task creation
- Avoids collision risk from reusing deleted IDs
- Aligns with database auto-increment patterns for future migration to Phase II

**Implementation Pattern**:
```python
next_id = 1  # Module-level counter
def create_task(...):
    global next_id
    task = {"id": next_id, ...}
    next_id += 1
    return task
```

### Input Validation Patterns

**Decision**: Validation at service layer with descriptive error messages

**Rationale**:
- Edge cases (spec.md:lines 88-102) define specific validation rules
- Service layer validation separates business logic from UI
- Return tuple `(success: bool, message: str, data: Optional[dict])` for clear error handling
- CLI layer displays validation messages without knowledge of business rules

**Key Validations**:
- Title: non-empty after `str.strip()`
- Priority: exact match to `["High", "Medium", "Low"]` (case-sensitive)
- Task ID: positive integer, existence check in tasks list
- Menu choice: numeric, within valid range

### Partial Update Pattern

**Decision**: Accept optional parameters, only update provided fields

**Rationale**:
- Clarification (spec.md:line 16) confirmed partial updates allowed
- Function signature: `update_task(task_id, title=None, description=None, priority=None)`
- Only non-None arguments overwrite existing task fields
- Validation applied only to provided fields

**Implementation Pattern**:
```python
def update_task(task_id, title=None, description=None, priority=None):
    task = find_task_by_id(task_id)
    if title is not None:
        if not title.strip():
            return (False, "Title cannot be empty", None)
        task["title"] = title.strip()
    if description is not None:
        task["description"] = description
    if priority is not None:
        if priority not in ["High", "Medium", "Low"]:
            return (False, "Invalid priority", None)
        task["priority"] = priority
    return (True, "Task updated", task)
```

## Testing Strategy Research

### TDD Approach for CLI Application

**Decision**: Test-first development with pytest, 70% coverage for MVP

**Rationale**:
- Constitution Testing Requirements mandate TDD and 70% coverage minimum
- pytest provides simple, readable test syntax
- Unit tests for models and services; integration tests for full workflows
- Mock `input()` and capture `print()` output for CLI testing

**Test Structure**:
- `tests/unit/models/test_task.py`: Task validation logic
- `tests/unit/services/test_task_service.py`: CRUD operations, sorting, ID generation
- `tests/unit/cli/test_menu.py`: Menu input parsing, validation
- `tests/unit/cli/test_display.py`: Task list formatting
- `tests/integration/test_app_flow.py`: End-to-end workflows (add → view → update → delete)

**Testing Tools**:
- `pytest`: Test runner and framework
- `pytest-cov`: Coverage reporting
- `unittest.mock`: Mock user input and capture output
- `pytest-mock`: Cleaner mocking syntax

### Mock Input Pattern for CLI Testing

**Decision**: Use `unittest.mock.patch` to mock `builtins.input`

**Implementation Pattern**:
```python
from unittest.mock import patch

@patch('builtins.input', side_effect=['1', 'Test Task', 'Description', 'High'])
def test_add_task_flow(mock_input):
    # Test code that calls input() multiple times
    # mock_input will return '1', then 'Test Task', then 'Description', then 'High'
    pass
```

## Logging Strategy Research

**Decision**: Python standard logging module with INFO level for CRUD operations

**Rationale**:
- Constitution Logging Standards require stdlib logging with specific format
- INFO level logs all CRUD operations for audit trail
- DEBUG level for development troubleshooting
- Configuration via `.env` file (`LOG_LEVEL=DEBUG` for development, `INFO` for production)

**Log Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Log Events**:
- Task created: `INFO: Task created - ID: {id}, Title: {title}`
- Task updated: `INFO: Task updated - ID: {id}, Fields: {changed_fields}`
- Task deleted: `INFO: Task deleted - ID: {id}`
- Task completed: `INFO: Task completion toggled - ID: {id}, Complete: {status}`

## Architecture Decisions

### Layered Architecture for Separation of Concerns

**Decision**: Three-layer architecture (Models, Services, CLI)

**Rationale**:
- **Models layer**: Task entity definition and validation rules
- **Services layer**: Business logic, CRUD operations, task storage management
- **CLI layer**: User interface, menu display, input handling, output formatting
- Clear separation enables independent testing and future migration to web (Phase II)

**Data Flow**:
```
User Input → CLI (menu.py) → Services (task_service.py) → Models (task.py) → Services → CLI → User Output
```

### Single Module State Management

**Decision**: Module-level variables in `task_service.py` for tasks list and ID counter

**Rationale**:
- Single-user, session-scoped application doesn't need complex state management
- Module-level `tasks = []` and `next_id = 1` provide simple global state
- Encapsulated within service layer - CLI doesn't access state directly
- Suitable for Phase I; will refactor to class-based or database in Phase II

## Environment Configuration Research

**Decision**: Use `.env` file with python-decouple or manual parsing

**Rationale**:
- Constitution requires `.env` for configuration
- Minimal config needs for Phase I: `LOG_LEVEL`, `APP_NAME`
- For MVP: can use simple `os.getenv()` with defaults
- For production-ready: add `python-decouple` dependency for type-safe config

**Configuration Variables**:
- `LOG_LEVEL`: Default `INFO`, override with `DEBUG` for development
- `APP_NAME`: Default `evolution-todo`, used in logging and display

## Dependencies Summary

### MVP Dependencies (Minimal)
- Python 3.13+ (stdlib only for application code)
- pytest (testing)
- pytest-cov (coverage reporting)
- ruff (linting - PEP8 compliance)

### Production-Ready Dependencies (Optional Enhancements)
- rich (colored/formatted CLI output)
- python-decouple (typed environment config)
- pytest-mock (cleaner test mocking)

### UV Package Management

**Decision**: Use UV for dependency management per constitution

**Commands**:
- `uv venv` - Create virtual environment
- `uv add pytest pytest-cov ruff` - Add development dependencies
- `uv pip compile` - Generate lock file
- `uv sync` - Install from lock file

## Risk Analysis

### Identified Risks

1. **Input Validation Complexity**: Multiple edge cases (empty strings, whitespace, case sensitivity)
   - **Mitigation**: Comprehensive unit tests for validation, early validation at service layer

2. **State Management**: Global state could cause issues if multiple instances needed
   - **Mitigation**: Acceptable for Phase I single-user CLI; document for Phase II refactoring

3. **Testing CLI Input/Output**: Mocking `input()` and capturing `print()` can be fragile
   - **Mitigation**: Separate business logic (services) from I/O (CLI) for easier testing

4. **ID Counter Reset**: Counter resets on app restart (expected behavior)
   - **Mitigation**: Documented as expected; no persistence required per spec

### Non-Risks (Explicitly Out of Scope)

- **Persistence**: In-memory only, data loss on exit is expected per spec
- **Concurrency**: Single-user, blocking I/O acceptable
- **Performance**: Dozens of tasks expected, no optimization needed
- **Security**: No authentication, no sensitive data in Phase I

## Research Conclusion

All technology choices align with:
- ✅ Constitution requirements (Python 3.13+, UV, TDD, PEP8, logging)
- ✅ Spec requirements (numbered menu, in-memory storage, CRUD operations)
- ✅ Clarifications (sorting, ID non-reuse, partial updates, toggle completion)

No unresolved questions or NEEDS CLARIFICATION items remain. Ready to proceed to Phase 1 design.
