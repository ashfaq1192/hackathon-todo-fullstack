# Task Data Contract

**Version**: 1.0.0
**Date**: 2025-12-18
**Stage**: Stage 1 (Database & Models)

## Overview

This contract defines the Task data structure for database storage. Stage 2 (Backend API) will consume this contract to build API request/response schemas.

---

## Task Entity Schema

### Database Model (Internal)

```typescript
{
  "id": number,                    // Auto-generated primary key
  "user_id": string,               // Owner of the task (required, indexed)
  "title": string,                 // Task title (required, max 200 chars)
  "description": string | null,    // Optional description (max 1000 chars)
  "complete": boolean,             // Completion status (default: false)
  "created_at": string,            // ISO 8601 timestamp (UTC)
  "updated_at": string             // ISO 8601 timestamp (UTC)
}
```

### Field Specifications

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | integer | Yes (DB) | > 0, unique | Auto-generated | Primary key |
| `user_id` | string | Yes | Non-empty, max 255 | - | Better Auth user ID |
| `title` | string | Yes | 1-200 chars | - | Task title |
| `description` | string \| null | No | Max 1000 chars | null | Optional details |
| `complete` | boolean | Yes | true/false | false | Completion status |
| `created_at` | datetime | Yes (DB) | Valid UTC datetime | Auto-generated | Creation timestamp |
| `updated_at` | datetime | Yes (DB) | Valid UTC datetime | Auto-updated | Last modification |

---

## Validation Rules

### 1. user_id Validation
- **MUST** be non-empty string
- **MUST** match Better Auth user ID format (Stage 3)
- **MUST** be indexed for query performance
- **Error**: `ValidationError` if empty or None

### 2. title Validation
- **MUST** be non-empty string
- **MUST** be 1-200 characters (inclusive)
- **Error**: `ValidationError` if empty, None, or > 200 chars

### 3. description Validation
- **MAY** be null (optional field)
- **MUST** be ≤ 1000 characters if provided
- **Error**: `ValidationError` if > 1000 chars

### 4. complete Validation
- **MUST** be boolean (true or false)
- **MUST** default to `false` for new tasks
- **Error**: `ValidationError` if non-boolean value

### 5. Timestamp Validation
- **MUST** be UTC datetime
- **MUST** auto-generate `created_at` on insert
- **MUST** auto-update `updated_at` on modification
- **Format**: ISO 8601 (`YYYY-MM-DDTHH:MM:SS.sssZ`)

---

## JSON Representation

### Example Task (Complete)

```json
{
  "id": 42,
  "user_id": "user_abc123",
  "title": "Complete Phase II Stage 1",
  "description": "Set up Neon PostgreSQL database with SQLModel ORM and create Task model",
  "complete": false,
  "created_at": "2025-12-18T10:30:00.000Z",
  "updated_at": "2025-12-18T10:30:00.000Z"
}
```

### Example Task (Minimal)

```json
{
  "id": 43,
  "user_id": "user_xyz789",
  "title": "Buy groceries",
  "description": null,
  "complete": false,
  "created_at": "2025-12-18T11:45:00.000Z",
  "updated_at": "2025-12-18T11:45:00.000Z"
}
```

---

## Stage 2 Preview: API Request/Response Schemas

**Note**: These schemas will be fully defined in Stage 2 (Backend API). Preview shown for reference.

### Create Task Request (POST /api/{user_id}/tasks)

```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string | null (optional, max 1000 chars)"
}
```

**Response**: 201 Created
```json
{
  "id": 42,
  "user_id": "user_abc123",
  "title": "Task title",
  "description": "Task details",
  "complete": false,
  "created_at": "2025-12-18T10:30:00.000Z",
  "updated_at": "2025-12-18T10:30:00.000Z"
}
```

### Get Task by ID (GET /api/{user_id}/tasks/{id})

**Response**: 200 OK
```json
{
  "id": 42,
  "user_id": "user_abc123",
  "title": "Task title",
  "description": "Task details",
  "complete": false,
  "created_at": "2025-12-18T10:30:00.000Z",
  "updated_at": "2025-12-18T10:30:00.000Z"
}
```

**Error Response**: 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### List Tasks by User (GET /api/{user_id}/tasks)

**Response**: 200 OK
```json
{
  "tasks": [
    { /* Task object */ },
    { /* Task object */ }
  ],
  "count": 2
}
```

---

## Pydantic Schema (Stage 2 Use)

Stage 2 will create Pydantic schemas for API validation:

```python
from pydantic import BaseModel, Field
from datetime import datetime

class TaskCreate(BaseModel):
    """Request schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

class TaskResponse(BaseModel):
    """Response schema for task operations."""
    id: int
    user_id: str
    title: str
    description: str | None
    complete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel
```

---

## Contract Guarantees

This contract guarantees:

1. **Type Safety**: All fields have defined types (SQLModel + Pydantic)
2. **Validation**: Constraints enforced before database operations
3. **Immutability**: `id`, `created_at` cannot be modified after creation
4. **Auto-Updates**: `updated_at` automatically refreshed on modifications
5. **Multi-User Isolation**: `user_id` index enables efficient per-user queries

---

## Breaking Changes Policy

**Version**: 1.0.0 (initial release)

**Future Breaking Changes**:
- Adding required fields → Major version bump (2.0.0)
- Removing fields → Major version bump
- Changing field types → Major version bump
- Tightening constraints → Minor version bump (1.1.0)
- Loosening constraints → Patch version bump (1.0.1)

**Non-Breaking Changes**:
- Adding optional fields → Minor version bump
- Adding indexes → Patch version bump
- Documentation updates → No version change

---

## Stage 1 Scope

**In Scope**:
- Task model definition with SQLModel
- Database table creation (auto-create with `create_all()`)
- Basic validation rules
- Created/updated timestamps

**Out of Scope** (Deferred to Stage 2+):
- API endpoints and request/response schemas
- Update/Delete operations
- Pagination for task lists
- Filtering/sorting capabilities
- Task archival/soft deletes

---

## Summary

**Contract Type**: Data Model (Database Schema)
**Consumers**: Stage 2 (Backend API), Stage 4 (Frontend UI)
**Validation Engine**: SQLModel + Pydantic
**Database**: Neon Serverless PostgreSQL
**Format**: JSON (serialization), SQLModel (Python)

**Next Stage**: Stage 2 will extend this contract with API request/response schemas
