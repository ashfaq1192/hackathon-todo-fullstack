"""
CRUD (Create, Read, Update, Delete) operations for the Task model.
"""

import asyncio
import logging

from sqlalchemy import case, func
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from src.models.task import Task, TaskPriority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _fire_and_forget(coro):
    """Schedule an async coroutine from sync code without blocking.

    Used to publish Dapr events after CRUD operations.
    If no event loop is running (e.g., in tests), the coroutine is silently skipped.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        # No running event loop (tests, CLI usage)
        pass


def create_task(session: Session, user_id: str, title: str, description: str | None = None, **kwargs) -> Task:
    """
    Create a new task and save it to the database.

    Args:
        session: The database session.
        user_id: The ID of the user creating the task.
        title: The title of the task.
        description: The description of the task (optional).
        **kwargs: Additional fields (priority, due_date, recurring, recurring_end_date, tags).

    Returns:
        The created task object.

    Raises:
        SQLAlchemyError: If a database error occurs.
    """
    try:
        task = Task(user_id=user_id, title=title, description=description, **kwargs)
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task {task.id} created for user {user_id}.")

        # Publish event (async, non-blocking)
        from src.services.event_publisher import publish_task_created
        _fire_and_forget(publish_task_created(task, user_id))

        # Schedule reminder if task has a due date
        if task.due_date:
            from src.services.reminder_service import schedule_reminder
            _fire_and_forget(schedule_reminder(task.id, task.title, task.due_date, user_id))

        return task
    except SQLAlchemyError as e:
        logger.error(f"Error creating task for user {user_id}: {e}")
        session.rollback()
        raise


def get_task_by_id(session: Session, task_id: int) -> Task | None:
    """
    Retrieve a single task by its ID.

    Args:
        session: The database session.
        task_id: The ID of the task to retrieve.

    Returns:
        The task object if found, otherwise None.

    Raises:
        SQLAlchemyError: If a database error occurs.
    """
    try:
        task = session.get(Task, task_id)
        return task
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise


def get_tasks_by_user(session: Session, user_id: str) -> list[Task]:
    """
    Retrieve all tasks for a specific user.

    Args:
        session: The database session.
        user_id: The ID of the user whose tasks to retrieve.

    Returns:
        A list of task objects.

    Raises:
        SQLAlchemyError: If a database error occurs.
    """
    try:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        return tasks
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {e}")
        raise


def get_tasks_filtered(
    session: Session,
    user_id: str,
    search: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[Task]:
    """
    Retrieve tasks with search, filter, and sort capabilities.

    Args:
        session: The database session.
        user_id: The ID of the user.
        search: Keyword search in title/description (ILIKE).
        status: Filter by completion status (all/pending/completed).
        priority: Filter by priority level.
        tags: Filter by tags (tasks matching any of the provided tags).
        sort_by: Sort field (created_at/due_date/priority/title).
        sort_order: Sort direction (asc/desc).

    Returns:
        A list of filtered and sorted task objects.
    """
    try:
        statement = select(Task).where(Task.user_id == user_id)

        # Search filter - ILIKE on title and description
        if search:
            search_pattern = f"%{search}%"
            statement = statement.where(
                (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern))
            )

        # Status filter
        if status == "pending":
            statement = statement.where(Task.complete == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.complete == True)  # noqa: E712

        # Priority filter
        if priority:
            try:
                priority_enum = TaskPriority(priority)
                statement = statement.where(Task.priority == priority_enum)
            except ValueError:
                pass  # Ignore invalid priority values

        # Tags filter - tasks containing any of the provided tags
        if tags:
            from sqlalchemy import text as sa_text, bindparam
            from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
            from sqlalchemy import String, cast, column, type_coerce
            # Use raw PostgreSQL overlap operator (&&) since TypeDecorator
            # doesn't expose ARRAY methods directly
            statement = statement.where(
                cast(Task.tags, PG_ARRAY(String)).overlap(tags)
            )

        # Sorting
        sort_column = {
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "title": Task.title,
        }.get(sort_by, Task.created_at)

        # Special handling for priority sorting (high > medium > low)
        if sort_by == "priority":
            priority_order = case(
                (Task.priority == TaskPriority.high, 3),
                (Task.priority == TaskPriority.medium, 2),
                (Task.priority == TaskPriority.low, 1),
                else_=0,
            )
            if sort_order == "asc":
                statement = statement.order_by(priority_order.asc())
            else:
                statement = statement.order_by(priority_order.desc())
        else:
            if sort_order == "asc":
                statement = statement.order_by(sort_column.asc())
            else:
                statement = statement.order_by(sort_column.desc())

        tasks = session.exec(statement).all()
        return tasks
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving filtered tasks for user {user_id}: {e}")
        raise


def update_task(session: Session, task_id: int, updates: dict) -> Task | None:
    """
    Update a task with the provided field updates.

    Args:
        session: The database session.
        task_id: The ID of the task to update.
        updates: Dictionary of field names and values to update.

    Returns:
        The updated task object if found, otherwise None.

    Raises:
        SQLAlchemyError: If a database error occurs.

    Example:
        update_task(session, 1, {"title": "New Title", "complete": True})
    """
    try:
        task = session.get(Task, task_id)
        if task is None:
            logger.warning(f"Task {task_id} not found for update.")
            return None

        # Update only the provided fields
        updated_fields = []
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)
                updated_fields.append(field)
            else:
                logger.warning(f"Ignoring unknown field '{field}' in update for task {task_id}")

        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task {task_id} updated successfully.")

        # Publish event (async, non-blocking)
        from src.services.event_publisher import publish_task_updated, publish_task_completed
        if "complete" in updated_fields and task.complete:
            _fire_and_forget(publish_task_completed(task, task.user_id))
        else:
            _fire_and_forget(publish_task_updated(task, task.user_id, updated_fields))

        # Reschedule reminder if due_date was updated
        if "due_date" in updated_fields and task.due_date:
            from src.services.reminder_service import schedule_reminder
            _fire_and_forget(schedule_reminder(task.id, task.title, task.due_date, task.user_id))
        elif "due_date" in updated_fields and not task.due_date:
            from src.services.reminder_service import cancel_reminder
            _fire_and_forget(cancel_reminder(task.id))

        return task
    except SQLAlchemyError as e:
        logger.error(f"Error updating task {task_id}: {e}")
        session.rollback()
        raise


def delete_task(session: Session, task_id: int) -> bool:
    """
    Delete a task by its ID.

    Args:
        session: The database session.
        task_id: The ID of the task to delete.

    Returns:
        True if the task was deleted, False if the task was not found.

    Raises:
        SQLAlchemyError: If a database error occurs.

    Example:
        if delete_task(session, 1):
            print("Task deleted successfully")
    """
    try:
        task = session.get(Task, task_id)
        if task is None:
            logger.warning(f"Task {task_id} not found for deletion.")
            return False

        # Capture info before deletion for event publishing
        task_title = task.title
        user_id = task.user_id

        session.delete(task)
        session.commit()
        logger.info(f"Task {task_id} deleted successfully.")

        # Publish event and cancel reminder (async, non-blocking)
        from src.services.event_publisher import publish_task_deleted
        from src.services.reminder_service import cancel_reminder
        _fire_and_forget(publish_task_deleted(task_id, task_title, user_id))
        _fire_and_forget(cancel_reminder(task_id))

        return True
    except SQLAlchemyError as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        session.rollback()
        raise
