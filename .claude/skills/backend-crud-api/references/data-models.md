# Data Models and Schemas

## Overview

Define database models and API schemas that separate persistence concerns from API contracts. Use SQLModel for database models and Pydantic for API request/response schemas.

## Decision Point 1: Model Design

Determine entity attributes and relationships:
- Choose field types, constraints, and validation rules
- Decide on timestamp management strategy (created_at, updated_at)
- Consider indexing strategy (user_id should be indexed for query performance)

## Database Model Structure

Create SQLModel database model with:
- Primary key (auto-generated ID)
- Foreign key to user (user_id, indexed)
- Required and optional fields
- Timestamps (created_at, updated_at with auto-update)
- Field validation (min/max length, patterns)

### Example Database Model

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
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)}
    )
```

### Key Considerations

- **user_id indexing**: Always index user_id for fast queries filtering by user
- **Timestamp defaults**: Use `default_factory` with UTC timestamps
- **Auto-update timestamps**: Use `sa_column_kwargs` with `onupdate` for updated_at
- **Field constraints**: Add min/max length validation at database level
- **Optional fields**: Use `| None` with `default=None` for nullable columns

## API Schemas Structure

Create Pydantic API schemas for different operations:

### 1. EntityCreate - POST Request Schema

Fields for creating new entities (required fields only):

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete Phase II",
                "description": "Implement Backend API"
            }
        }
    )
```

### 2. EntityUpdate - PUT Request Schema

Fields for full replacement (all fields required):

```python
class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    complete: bool
```

**Key difference from Create**: Include all mutable fields. PUT requires full replacement.

### 3. EntityPatch - PATCH Request Schema

Fields for partial update (all fields optional):

```python
class TaskPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    complete: bool | None = None
```

**Key difference from Update**: All fields optional. PATCH allows partial updates.

### 4. EntityResponse - Response Schema

Complete entity with all fields including ID and timestamps:

```python
class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Critical**: Set `from_attributes=True` to allow conversion from SQLModel instances.

### 5. EntityListResponse - List Response Schema

List of entities with count:

```python
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    count: int
```

## Schema Naming Conventions

Follow consistent naming patterns:
- `{Entity}Create` - POST request body
- `{Entity}Update` - PUT request body (full replacement)
- `{Entity}Patch` - PATCH request body (partial update)
- `{Entity}Response` - Single entity response
- `{Entity}ListResponse` - List response with count

## Validation Rules

### String Fields
- **title/name**: `min_length=1, max_length=200`
- **description**: `max_length=1000`
- Use `...` for required fields, `None` for optional

### Timestamps
- Always use UTC: `datetime.now(UTC)`
- Never accept timestamps from clients (security risk)
- Auto-generate on create, auto-update on modify

### Boolean Fields
- Provide explicit defaults: `Field(default=False)`
- Never use nullable booleans unless tri-state logic is needed

## File Organization

```
src/
├── models/
│   └── entity.py      # Database models (SQLModel)
└── schemas/
    └── entity.py      # API schemas (Pydantic)
```

Keep database models and API schemas in separate files for clear separation of concerns.
