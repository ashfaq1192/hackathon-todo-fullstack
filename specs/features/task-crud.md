# Feature: Task CRUD Operations

**Feature ID**: task-crud
**Status**: Active across all phases
**Phases**: I, II, III, IV, V

## Overview

Core task management operations that form the foundation of the todo application. These capabilities evolve across phases while maintaining backward compatibility.

## Phase Evolution

| Phase | Interface | Storage | Key Capabilities |
|-------|-----------|---------|------------------|
| I | CLI Menu | In-Memory | Basic CRUD, priority levels |
| II | REST API | PostgreSQL | Multi-user, persistence, auth |
| III | Natural Language | PostgreSQL | AI-powered, conversational |
| IV | Same as III | K8s PostgreSQL | Containerized deployment |
| V | Same as III | Cloud PostgreSQL | Event-driven, advanced features |

## Core Operations

### 1. Add Task
- **Phase I**: Menu-driven, requires title + priority (High/Medium/Low)
- **Phase II+**: REST API `POST /api/{user_id}/tasks` with JWT auth
- **Phase III+**: Natural language "Add a task to buy groceries"

### 2. View Tasks
- **Phase I**: List sorted by priority, incomplete first
- **Phase II+**: REST API `GET /api/{user_id}/tasks` with user isolation
- **Phase III+**: "Show me my pending tasks"

### 3. Mark Complete
- **Phase I**: Toggle by task ID
- **Phase II+**: PATCH endpoint with `{complete: true/false}`
- **Phase III+**: "Mark task 3 as complete"

### 4. Update Task
- **Phase I**: Partial updates (title, description, or priority)
- **Phase II+**: PUT (full) or PATCH (partial) endpoints
- **Phase III+**: "Change task 2 title to..."

### 5. Delete Task
- **Phase I**: Remove by task ID
- **Phase II+**: DELETE endpoint with 204 response
- **Phase III+**: "Delete task 4"

## Task Entity

```
Task {
  id: integer (auto-increment, never reused)
  user_id: string (Phase II+, indexed)
  title: string (required, max 200 chars)
  description: string (optional, max 1000 chars)
  priority: enum (High/Medium/Low) - Phase I only
  complete: boolean (default: false)
  created_at: timestamp
  updated_at: timestamp
}
```

## Validation Rules

- Title: Required, non-empty after trimming, max 200 characters
- Description: Optional, max 1000 characters
- Priority (Phase I): Must be exactly "High", "Medium", or "Low"
- Task IDs: Auto-generated, never reused after deletion

## API Endpoints (Phase II+)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all user tasks |
| POST | `/api/{user_id}/tasks` | Create new task |
| GET | `/api/{user_id}/tasks/{id}` | Get single task |
| PUT | `/api/{user_id}/tasks/{id}` | Full update |
| PATCH | `/api/{user_id}/tasks/{id}` | Partial update |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |

## MCP Tools (Phase III+)

| Tool | Parameters | Returns |
|------|------------|---------|
| `add_task` | user_id, title, description | task_id, status, title |
| `list_tasks` | user_id, status | array of tasks |
| `complete_task` | user_id, task_id | confirmation |
| `update_task` | user_id, task_id, title?, description? | updated task |
| `delete_task` | user_id, task_id | confirmation |

## Success Criteria

- Phase I: Menu-driven CRUD in < 15 seconds per operation
- Phase II: API response < 200ms, 70%+ test coverage
- Phase III: Natural language interpreted correctly 90%+ of time
- Phase IV: Containerized deployment maintains performance
- Phase V: Advanced features (priorities, tags, search) added

## Related Specifications

- Detailed Phase I spec: `specs/archive/phase-1/001-cli-todo-app/spec.md`
- Detailed Phase II backend: `specs/archive/phase-2/003-backend-api/spec.md`
- Detailed Phase III chatbot: `specs/archive/phase-3/007-chatbot-mcp/spec.md`

---

*Last Updated: 2026-01-18*
