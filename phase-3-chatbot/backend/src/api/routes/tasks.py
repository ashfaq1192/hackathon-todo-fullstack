"""
Task API routes for CRUD operations.

This module implements RESTful endpoints for task management:
- GET /api/{user_id}/tasks - List all tasks for a user (with search/filter/sort)
- POST /api/{user_id}/tasks - Create a new task
- GET /api/{user_id}/tasks/{task_id} - Get a specific task
- PUT /api/{user_id}/tasks/{task_id} - Update entire task
- PATCH /api/{user_id}/tasks/{task_id} - Partially update task
- DELETE /api/{user_id}/tasks/{task_id} - Delete a task
"""

import logging

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlmodel import Session

from src.api.dependencies import get_current_user, verify_user_id_match
from src.database import get_session
from src.database.crud import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks_by_user,
    get_tasks_filtered,
    update_task,
)
from src.models.task import TaskPriority
from src.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskPatch,
    TaskResponse,
    TaskUpdate,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create APIRouter instance (T049)
router = APIRouter()


# User Story 1: List User's Tasks (T050-T053) - with search/filter/sort
@router.get(
    "/{user_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all tasks for a user",
    description="Retrieve tasks with optional search, filtering, and sorting",
    responses={
        200: {"description": "Successfully retrieved task list"},
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User ID mismatch"},
    },
)
def list_tasks(
    user_id: str,
    search: str | None = Query(None, description="Search keyword in title/description"),
    task_status: str | None = Query(None, alias="status", description="Filter: all/pending/completed"),
    priority: str | None = Query(None, description="Filter by priority: low/medium/high"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    sort_by: str = Query("created_at", description="Sort: created_at/due_date/priority/title"),
    sort_order: str = Query("desc", description="Sort order: asc/desc"),
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskListResponse:
    """
    List all tasks for a specific user with optional search, filtering, and sorting.

    Args:
        user_id: User ID from path parameter
        search: Optional keyword search in title/description
        task_status: Optional status filter (all/pending/completed)
        priority: Optional priority filter (low/medium/high)
        tags: Optional tag filter
        sort_by: Sort field (created_at/due_date/priority/title)
        sort_order: Sort direction (asc/desc)
        current_user: Authenticated user ID from JWT token
        session: Database session

    Returns:
        TaskListResponse containing list of tasks and count
    """
    # T051: Verify user_id matches authenticated user
    verify_user_id_match(current_user, user_id)

    # Use filtered query if any filter/search/sort params provided
    has_filters = any([search, task_status, priority, tags, sort_by != "created_at", sort_order != "desc"])

    if has_filters:
        tasks = get_tasks_filtered(
            session,
            user_id,
            search=search,
            status=task_status,
            priority=priority,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    else:
        tasks = get_tasks_by_user(session, user_id)

    logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")

    # T053: Return TaskListResponse with tasks and count
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        count=len(tasks),
    )


# User Story 2: Create a New Task (T054-T058)
@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task for a user",
    description="Create a new task for the authenticated user",
    responses={
        201: {"description": "Task created successfully"},
        400: {"description": "Bad Request - Invalid input data"},
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User ID mismatch"},
        409: {"description": "Conflict - Task with the same title already exists"},
    },
)
def create_new_task(
    user_id: str,
    task_in: TaskCreate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Create a new task for a specific user.

    Args:
        user_id: User ID from path parameter
        task_in: Task creation data from request body
        current_user: Authenticated user ID from JWT token
        session: Database session

    Returns:
        The newly created task
    """
    # T055: Verify user_id matches authenticated user
    verify_user_id_match(current_user, user_id)

    # T056: Create the new task with all fields
    extra_fields = {}
    if task_in.priority:
        extra_fields["priority"] = task_in.priority
    if task_in.due_date:
        extra_fields["due_date"] = task_in.due_date
    if task_in.recurring:
        extra_fields["recurring"] = task_in.recurring
    if task_in.recurring_end_date:
        extra_fields["recurring_end_date"] = task_in.recurring_end_date
    if task_in.tags:
        extra_fields["tags"] = task_in.tags

    new_task = create_task(
        session,
        user_id=user_id,
        title=task_in.title,
        description=task_in.description,
        **extra_fields,
    )
    logger.info(f"Created task '{new_task.title}' for user {user_id}")

    # T057: Return the created task
    return TaskResponse.model_validate(new_task)


# User Story 3: Get a Specific Task (T059-T063)
@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific task",
    description="Retrieve a single task by its ID for the authenticated user",
    responses={
        200: {"description": "Successfully retrieved task"},
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User does not have access to this task"},
        404: {"description": "Not Found - Task not found"},
    },
)
def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Retrieve a single task by its ID.
    """
    # T060: Verify user_id matches authenticated user
    verify_user_id_match(current_user, user_id)

    # T061: Retrieve the task from the database
    task = get_task_by_id(session, task_id)

    # T062: Check if task exists and belongs to the user
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this task")

    logger.info(f"Retrieved task {task_id} for user {user_id}")

    # T063: Return the task
    return TaskResponse.model_validate(task)


# User Story 4: Update a Task (PUT)
@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a specific task",
    description="Fully update a task's details by its ID.",
    responses={
        200: {"description": "Task updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
    },
)
def update_existing_task(
    user_id: str,
    task_id: int,
    task_in: TaskUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Update an existing task.
    """
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this task")

    updated_task = update_task(session, task_id, task_in.model_dump())
    if not updated_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found after update")

    logger.info(f"Updated task {task_id} for user {user_id}")
    return TaskResponse.model_validate(updated_task)


# User Story 5: Partially Update a Task (PATCH)
@router.patch(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a task",
    description="Partially update a task's details by its ID.",
    responses={
        200: {"description": "Task updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
    },
)
def partially_update_task(
    user_id: str,
    task_id: int,
    task_in: TaskPatch,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Partially update an existing task.
    """
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this task")

    update_data = task_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updated_task = update_task(session, task_id, update_data)
    if not updated_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found after update")

    logger.info(f"Partially updated task {task_id} for user {user_id}")
    return TaskResponse.model_validate(updated_task)


# User Story 6: Delete a Task
@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by its ID.",
    responses={
        204: {"description": "Task deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
    },
)
def delete_task_by_id(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a task by its ID.
    """
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this task")

    if not delete_task(session, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    logger.info(f"Deleted task {task_id} for user {user_id}")
    return None
