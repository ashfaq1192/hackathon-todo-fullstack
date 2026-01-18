# Data Model: Next.js Frontend Application

**Date**: 2025-12-24
**Feature**: 004-frontend-nextjs
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the frontend data models (TypeScript interfaces) used in the Next.js application. These models represent client-side data structures that correspond to backend API responses and form the foundation for type-safe component development.

---

## Core Entities

### 1. User

**Purpose**: Represents an authenticated user session

**Source**: Better Auth session + JWT token payload

**TypeScript Definition**:
```typescript
// types/user.ts
export interface User {
  id: string;                    // Unique user identifier (UUID from Better Auth)
  email: string;                 // User's email address
  createdAt: string;             // ISO 8601 timestamp of account creation
}

export interface UserSession {
  user: User;
  token: string;                 // JWT access token
  expiresAt: string;             // ISO 8601 timestamp of token expiration
}
```

**Fields**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | string | Yes | UUID format | Unique identifier from Better Auth |
| email | string | Yes | Valid email format | User's email address |
| createdAt | string | Yes | ISO 8601 timestamp | When account was created |

**State Transitions**:
- **Unauthenticated** → **Authenticated**: User signs up or logs in successfully
- **Authenticated** → **Unauthenticated**: User logs out or token expires

**Validation Rules**:
- Email must be valid format (validated by Better Auth)
- ID is immutable after creation
- Token must be validated on every API request

---

### 2. Task

**Purpose**: Represents a todo task item

**Source**: Backend API `/api/{user_id}/tasks` endpoints

**TypeScript Definition**:
```typescript
// types/task.ts
export interface Task {
  id: number;                    // Unique task identifier (auto-increment from backend)
  user_id: string;               // Owner's user ID (foreign key to User.id)
  title: string;                 // Task title (required)
  description: string | null;    // Task description (optional)
  complete: boolean;             // Completion status
  created_at: string;            // ISO 8601 timestamp of creation
  updated_at: string;            // ISO 8601 timestamp of last update
}
```

**Fields**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | number | Yes | Positive integer | Unique identifier (backend-generated) |
| user_id | string | Yes | UUID format | Owner's user ID |
| title | string | Yes | 1-200 characters | Task title |
| description | string \| null | No | Max 1000 characters | Task description |
| complete | boolean | Yes | true or false | Completion status |
| created_at | string | Yes | ISO 8601 timestamp | Creation timestamp |
| updated_at | string | Yes | ISO 8601 timestamp | Last update timestamp |

**State Transitions**:
- **New** → **Created**: User submits create task form
- **Incomplete** → **Complete**: User checks completion checkbox
- **Complete** → **Incomplete**: User unchecks completion checkbox
- **Exists** → **Updated**: User edits title or description
- **Exists** → **Deleted**: User confirms deletion

**Validation Rules** (Client-Side):
- Title: Required, min 1 character, max 200 characters
- Description: Optional, max 1000 characters
- Complete: Boolean only (true/false)
- ID, user_id, timestamps: Read-only (set by backend)

---

### 3. Task Creation Payload

**Purpose**: Data sent to backend when creating a new task

**TypeScript Definition**:
```typescript
// types/task.ts
export interface TaskCreate {
  title: string;                 // Required task title
  description?: string;          // Optional task description
}
```

**Zod Validation Schema**:
```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

export const createTaskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters')
    .trim(),
  description: z.string()
    .max(1000, 'Description must be less than 1000 characters')
    .trim()
    .optional()
    .or(z.literal('')),  // Allow empty string
});

export type CreateTaskInput = z.infer<typeof createTaskSchema>;
```

---

### 4. Task Update Payload

**Purpose**: Data sent to backend when updating an existing task

**TypeScript Definition**:
```typescript
// types/task.ts
export interface TaskUpdate {
  title: string;                 // Updated title
  description: string | null;    // Updated description
  complete: boolean;             // Updated completion status
}

export interface TaskPatch {
  title?: string;                // Partial update: title only
  description?: string | null;   // Partial update: description only
  complete?: boolean;            // Partial update: completion status only
}
```

**Zod Validation Schema**:
```typescript
// lib/validation/schemas.ts
export const updateTaskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters')
    .trim(),
  description: z.string()
    .max(1000, 'Description must be less than 1000 characters')
    .trim()
    .nullable(),
  complete: z.boolean(),
});

export const patchTaskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters')
    .trim()
    .optional(),
  description: z.string()
    .max(1000, 'Description must be less than 1000 characters')
    .trim()
    .nullable()
    .optional(),
  complete: z.boolean().optional(),
}).refine(data => Object.keys(data).length > 0, {
  message: 'At least one field must be provided',
});
```

---

### 5. Task List Response

**Purpose**: Response from backend when fetching tasks

**TypeScript Definition**:
```typescript
// types/task.ts
export interface TaskListResponse {
  tasks: Task[];                 // Array of task objects
  count: number;                 // Total number of tasks
}
```

**Example JSON**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user_abc123",
      "title": "Complete hackathon project",
      "description": "Finish Phase II frontend implementation",
      "complete": false,
      "created_at": "2025-12-24T10:00:00Z",
      "updated_at": "2025-12-24T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

### 6. Authentication Payloads

**Purpose**: Data sent to Better Auth for signup and login

**TypeScript Definition**:
```typescript
// types/auth.ts
export interface SignupPayload {
  email: string;                 // User's email
  password: string;              // User's password (min 8 chars)
}

export interface LoginPayload {
  email: string;                 // User's email
  password: string;              // User's password
}

export interface AuthResponse {
  user: User;                    // User object
  token: string;                 // JWT access token
  expiresAt: string;             // Token expiration timestamp
}
```

**Zod Validation Schema**:
```typescript
// lib/validation/schemas.ts
export const signupSchema = z.object({
  email: z.string()
    .email('Invalid email address')
    .trim()
    .toLowerCase(),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .max(100, 'Password must be less than 100 characters'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export const loginSchema = z.object({
  email: z.string()
    .email('Invalid email address')
    .trim()
    .toLowerCase(),
  password: z.string()
    .min(1, 'Password is required'),
});
```

---

## Supporting Types

### 7. API Error Response

**Purpose**: Standardized error response from backend

**TypeScript Definition**:
```typescript
// types/api.ts
export interface APIError {
  detail: string;                // Human-readable error message
  code?: string;                 // Optional error code
  field?: string;                // Optional field that caused error
}

export interface ValidationError {
  field: string;                 // Field name that failed validation
  message: string;               // Validation error message
}
```

---

### 8. Component State Types

**Purpose**: UI state management types

**TypeScript Definition**:
```typescript
// types/ui.ts
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface FormState<T> {
  data: T;                       // Form data
  loading: LoadingState;         // Current loading state
  error: string | null;          // Error message if any
}

export interface TaskItemState {
  task: Task;
  isEditing: boolean;            // Whether task is in edit mode
  isDeleting: boolean;           // Whether delete confirmation is shown
  optimisticUpdate: boolean;     // Whether UI updated optimistically
}
```

---

## Data Flow Diagrams

### Create Task Flow
```
User → CreateTaskForm
       ↓ (validates with createTaskSchema)
       ↓
       API Client (POST /api/{user_id}/tasks)
       ↓
       Backend API
       ↓ (returns Task)
       ↓
       Update TaskList state
       ↓
       Re-render TaskList with new task
```

### Toggle Complete Flow
```
User → TaskItem (clicks checkbox)
       ↓ (optimistic update)
       ↓
       API Client (PATCH /api/{user_id}/tasks/{id})
       ↓
       Backend API
       ↓ (returns updated Task or error)
       ↓
       Confirm update OR revert to original state
       ↓
       Re-render TaskItem with final state
```

### Authentication Flow
```
User → LoginForm
       ↓ (validates with loginSchema)
       ↓
       Better Auth API (POST /api/auth/signin)
       ↓
       Better Auth validates credentials
       ↓ (returns AuthResponse with JWT)
       ↓
       Store JWT in httpOnly cookie
       ↓
       Redirect to /dashboard
       ↓
       Dashboard fetches tasks with JWT in header
```

---

## Relationships

```
User (1) ----< has many >---- (N) Task
  ↑                              ↑
  |                              |
  |                              |
Better Auth Session       Backend API Database
(httpOnly cookie)         (user_id foreign key)
```

**Key Relationships**:
- One User has many Tasks (1:N)
- Tasks are filtered by user_id on all API requests
- JWT token contains user_id claim for authentication
- Better Auth manages User accounts separately from Tasks

---

## Type Safety Guarantees

### Zod Schema Validation
All user inputs are validated at runtime using Zod schemas:
- **Signup/Login**: Email format, password length
- **Create Task**: Title required, max lengths enforced
- **Update Task**: Same validation as create, plus optional fields

### TypeScript Compile-Time Checks
- All API responses typed with interfaces
- Component props strictly typed
- Form data typed with Zod inference: `z.infer<typeof schema>`
- No `any` types allowed (strict mode enabled)

### Runtime Type Validation
```typescript
// Example: Validate API response
import { z } from 'zod';

const taskSchema = z.object({
  id: z.number(),
  user_id: z.string(),
  title: z.string(),
  description: z.string().nullable(),
  complete: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

const validateTaskResponse = (data: unknown): Task => {
  return taskSchema.parse(data);  // Throws if invalid
};
```

---

## Migration from Backend Models

The frontend Task model matches the backend SQLModel Task exactly:

**Backend (Python SQLModel)**:
```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None, max_length=1000)
    complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Frontend (TypeScript)**:
```typescript
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  complete: boolean;
  created_at: string;  // ISO 8601 string (serialized from datetime)
  updated_at: string;  // ISO 8601 string (serialized from datetime)
}
```

**Differences**:
- Timestamps are strings (ISO 8601) in frontend, datetime objects in backend
- Null vs undefined: Frontend uses `| null` for optional fields, backend uses `None`
- Snake_case preserved (user_id, created_at) for consistency with backend API

---

## Summary

- **3 core entities**: User, Task, API Client state
- **6 payload types**: Create, Update, Patch, Signup, Login, Error
- **3 UI state types**: LoadingState, FormState, TaskItemState
- **100% type safety**: Zod runtime validation + TypeScript compile-time checks
- **1:1 backend mapping**: Frontend Task model matches backend SQLModel exactly

All models are ready for implementation in Phase 2 (tasks generation).

---

**Next**: Phase 1 - Generate API contracts
