# CRUD Database Operations

## Overview

Implement database operations that handle transactions properly, log important events, and provide clear error handling. All CRUD functions should be pure data access logic without business rules or authorization checks.

## Decision Point: Transaction Management

Determine when to commit vs rollback:
- Commit on successful operations
- Rollback on SQLAlchemy errors
- Log all database errors with context
- Re-raise exceptions for upper layers to handle

## Create Operation

Accept session, user_id, and entity fields. Create model instance, add to session, commit, refresh, and return created entity.

### Implementation Pattern

```python
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def create_task(session: Session, user_id: str, title: str, description: str | None = None) -> Task:
    """Create a new task for a user.

    Args:
        session: Database session
        user_id: User who owns the task
        title: Task title
        description: Optional task description

    Returns:
        Created task with ID and timestamps

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task {task.id} created for user {user_id}")
        return task
    except SQLAlchemyError as e:
        logger.error(f"Error creating task: {e}")
        session.rollback()
        raise
```

### Key Points

- **Refresh after commit**: Ensures timestamps and generated IDs are populated
- **Explicit rollback**: Always rollback on errors to maintain transaction integrity
- **Logging**: Log success with entity ID and user context
- **Re-raise exceptions**: Let upper layers handle error responses

## Read Operations

Query by ID or filter criteria. Return entity/list or None if not found.

### Get by ID

```python
def get_task_by_id(session: Session, task_id: int) -> Task | None:
    """Retrieve a task by ID.

    Args:
        session: Database session
        task_id: Task ID to retrieve

    Returns:
        Task if found, None otherwise
    """
    try:
        return session.get(Task, task_id)
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise
```

### Get by User (Filtered List)

```python
from sqlmodel import select

def get_tasks_by_user(session: Session, user_id: str) -> list[Task]:
    """Retrieve all tasks for a user.

    Args:
        session: Database session
        user_id: User ID to filter by

    Returns:
        List of tasks (empty list if none found)
    """
    try:
        statement = select(Task).where(Task.user_id == user_id)
        return list(session.exec(statement).all())
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {e}")
        raise
```

### Key Points

- **session.get()**: Efficient for primary key lookups
- **select().where()**: Use for filtered queries
- **Return None vs empty list**: Single entity returns None if not found, lists return empty []
- **Type safety**: Explicit `list[Task]` return type

## Update Operation

Get entity by ID, check existence, update fields from dictionary, commit and refresh.

### Implementation Pattern

```python
def update_task(session: Session, task_id: int, updates: dict) -> Task | None:
    """Update a task with provided fields.

    Args:
        session: Database session
        task_id: Task ID to update
        updates: Dictionary of fields to update

    Returns:
        Updated task if found, None if task doesn't exist

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        task = session.get(Task, task_id)
        if not task:
            return None

        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)

        # Explicitly update updated_at timestamp
        task.updated_at = datetime.now(UTC)

        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task {task_id} updated")
        return task
    except SQLAlchemyError as e:
        logger.error(f"Error updating task {task_id}: {e}")
        session.rollback()
        raise
```

### Key Points

- **Return None for not found**: Allows caller to distinguish between "not found" and "error"
- **Dictionary-based updates**: Flexible for both PUT and PATCH operations
- **hasattr check**: Prevents setting invalid attributes
- **Explicit timestamp update**: Update updated_at even if not in updates dict
- **session.add()**: Mark entity as modified before commit

### Alternative: Separate PUT and PATCH Functions

For clearer semantics, consider separate functions:

```python
def replace_task(session: Session, task_id: int, title: str, description: str | None, complete: bool) -> Task | None:
    """Full replacement (PUT) - all fields required."""
    task = session.get(Task, task_id)
    if not task:
        return None
    task.title = title
    task.description = description
    task.complete = complete
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def patch_task(session: Session, task_id: int, updates: dict) -> Task | None:
    """Partial update (PATCH) - only update provided fields."""
    task = session.get(Task, task_id)
    if not task:
        return None
    for field, value in updates.items():
        if hasattr(task, field):
            setattr(task, field, value)
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## Delete Operation

Get entity by ID, check existence, delete and commit. Return True on success, False if not found.

### Implementation Pattern

```python
def delete_task(session: Session, task_id: int) -> bool:
    """Delete a task by ID.

    Args:
        session: Database session
        task_id: Task ID to delete

    Returns:
        True if deleted, False if task doesn't exist

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        task = session.get(Task, task_id)
        if not task:
            return False

        session.delete(task)
        session.commit()
        logger.info(f"Task {task_id} deleted")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        session.rollback()
        raise
```

### Key Points

- **Boolean return**: True = deleted, False = not found
- **Explicit not found handling**: Prevents errors on non-existent entities
- **Commit after delete**: Ensure deletion is persisted

## Error Handling Strategy

### Rollback on Errors

Always rollback failed transactions:

```python
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    session.rollback()
    raise
```

### Logging Best Practices

- **Success**: Log entity ID and operation context
- **Errors**: Log error type and relevant IDs
- **Never log sensitive data**: Don't log user data or full entity contents

### Exception Propagation

- **Let exceptions bubble up**: CRUD functions should not catch and suppress SQLAlchemy errors
- **Re-raise after rollback**: Upper layers (route handlers) will convert to HTTP responses
- **Don't convert to HTTP exceptions**: Keep CRUD layer pure data access

## Database Session Management

### Session Lifecycle

```python
from sqlmodel import Session, create_engine

def get_session() -> Session:
    """FastAPI dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

### Usage in CRUD Functions

Accept session as first parameter:

```python
def create_task(session: Session, user_id: str, ...) -> Task:
    # Session is managed by caller
    pass
```

Never create sessions inside CRUD functions - always accept as parameter for testability and transaction control.

## Testing CRUD Operations

### Unit Test Pattern

```python
def test_create_task(session):
    task = create_task(session, user_id="user123", title="Test Task")
    assert task.id is not None
    assert task.user_id == "user123"
    assert task.title == "Test Task"

def test_get_task_not_found(session):
    task = get_task_by_id(session, task_id=99999)
    assert task is None

def test_update_task(session):
    task = create_task(session, user_id="user123", title="Original")
    updated = update_task(session, task.id, {"title": "Updated"})
    assert updated.title == "Updated"
```

## File Organization

```
src/database/
├── connection.py      # Engine, session management
└── crud.py           # CRUD operations
```

Keep all CRUD functions in a single `crud.py` file for discoverability, or split by entity if many entities exist:

```
src/database/
├── connection.py
├── task_crud.py
├── project_crud.py
└── comment_crud.py
```
