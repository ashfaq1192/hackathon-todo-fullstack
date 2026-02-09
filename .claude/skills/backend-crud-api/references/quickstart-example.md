# Quick Start: Task CRUD Example

Complete example implementing tasks CRUD with all 6 steps.

## Step 1: Database Model

```python
from datetime import UTC, datetime
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, min_length=1)
    title: str = Field(max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=1000)
    complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

## Step 2: API Schemas

```python
from pydantic import BaseModel, Field, ConfigDict

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    complete: bool

class TaskPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    complete: bool | None = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    complete: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    count: int
```

## Step 3: CRUD Functions

```python
from sqlmodel import Session, select

def create_task(session: Session, user_id: str, title: str, description: str | None = None) -> Task:
    try:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except SQLAlchemyError:
        session.rollback()
        raise

def get_tasks_by_user(session: Session, user_id: str) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    return list(session.exec(statement).all())

def get_task_by_id(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)

def update_task(session: Session, task_id: int, updates: dict) -> Task | None:
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

def delete_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True
```

## Step 4: Authentication Dependencies

```python
from fastapi import Header, HTTPException

def get_current_user(authorization: str | None = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = authorization[7:]
    return extract_user_id_from_token(token)

def verify_user_id_match(current_user: str, path_user_id: str) -> None:
    if current_user != path_user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot access resources for user '{path_user_id}'"
        )
```

## Step 5: API Routes

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=TaskListResponse)
def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    tasks = get_tasks_by_user(session, user_id)
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        count=len(tasks)
    )

@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(
    user_id: str,
    task_in: TaskCreate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    new_task = create_task(session, user_id, task_in.title, task_in.description)
    return TaskResponse.model_validate(new_task)

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return TaskResponse.model_validate(task)

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task_full(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = task_update.model_dump()
    updated_task = update_task(session, task_id, updates)
    return TaskResponse.model_validate(updated_task)

@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def patch_task_partial(
    user_id: str,
    task_id: int,
    task_patch: TaskPatch,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_dict = task_patch.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    updated_task = update_task(session, task_id, update_dict)
    return TaskResponse.model_validate(updated_task)

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_by_id(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    verify_user_id_match(current_user, user_id)
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    delete_task(session, task_id)
    return None
```

## Step 6: Error Handling

```python
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

# Custom exceptions
class AuthError(Exception):
    pass

class ForbiddenError(Exception):
    pass

# Exception handlers
@app.exception_handler(AuthError)
async def auth_error_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"error": "Authentication Error", "message": str(exc), "status_code": 401}
    )

@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request, exc):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Database Error", "message": "An error occurred", "status_code": 500}
    )
```
