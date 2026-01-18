# API Contract: Frontend ↔ Backend Integration

**Date**: 2025-12-24
**Feature**: 004-frontend-nextjs
**Backend API**: FastAPI (completed in Stage 2: 003-backend-api)
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the API contract between the Next.js frontend and FastAPI backend. It specifies all HTTP endpoints, request/response formats, authentication requirements, and error handling patterns.

---

## Base Configuration

### Endpoints

**Development**:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

**Production**:
- Frontend: `https://hackathon-todo.vercel.app` (Vercel deployment)
- Backend API: `https://api.hackathon-todo.com` (to be determined)

### Environment Variables

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000              # Backend API base URL
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000      # Better Auth URL
BETTER_AUTH_SECRET=your-secret-key-min-32-chars        # JWT signing secret (server-side only)
BETTER_AUTH_URL=http://localhost:3000                  # Better Auth callback URL
```

---

## Authentication

### JWT Token Flow

**Token Acquisition**:
1. User signs up or logs in via Better Auth
2. Better Auth returns JWT token in response
3. Frontend stores JWT in httpOnly cookie
4. Frontend includes JWT in `Authorization` header for all backend API requests

**Request Header**:
```http
Authorization: Bearer <JWT_TOKEN>
```

**JWT Payload Structure**:
```json
{
  "sub": "user_abc123",
  "user_id": "user_abc123",
  "email": "user@example.com",
  "exp": 1703088000,
  "iat": 1703084400
}
```

**Token Validation** (Backend):
- Backend validates JWT signature using `BETTER_AUTH_SECRET`
- Backend extracts `user_id` from JWT payload
- Backend filters all database queries by `user_id`
- Backend returns `401 Unauthorized` if token is missing or invalid

---

## API Endpoints

### 1. List Tasks

**Endpoint**: `GET /api/{user_id}/tasks`

**Description**: Retrieve all tasks for the authenticated user

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's unique identifier (from JWT) |

**Query Parameters**: None

**Request Headers**:
```http
GET /api/user_abc123/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Success Response (200 OK)**:
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
    },
    {
      "id": 2,
      "user_id": "user_abc123",
      "title": "Review documentation",
      "description": null,
      "complete": true,
      "created_at": "2025-12-23T15:30:00Z",
      "updated_at": "2025-12-24T09:00:00Z"
    }
  ],
  "count": 2
}
```

**Error Responses**:
```json
// 401 Unauthorized - Missing or invalid JWT
{
  "detail": "Unauthorized"
}

// 403 Forbidden - user_id in URL doesn't match JWT
{
  "detail": "Access denied"
}
```

---

### 2. Create Task

**Endpoint**: `POST /api/{user_id}/tasks`

**Description**: Create a new task for the authenticated user

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's unique identifier (from JWT) |

**Request Body**:
```json
{
  "title": "New task title",
  "description": "Optional task description"
}
```

**Request Body Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| title | string | Yes | 1-200 characters | Task title |
| description | string | No | Max 1000 characters | Task description |

**Request Example**:
```http
POST /api/user_abc123/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Success Response (201 Created)**:
```json
{
  "id": 3,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "complete": false,
  "created_at": "2025-12-24T11:00:00Z",
  "updated_at": "2025-12-24T11:00:00Z"
}
```

**Error Responses**:
```json
// 400 Bad Request - Validation error
{
  "detail": "Title is required"
}

// 422 Unprocessable Entity - Invalid data type
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 3. Get Single Task

**Endpoint**: `GET /api/{user_id}/tasks/{id}`

**Description**: Retrieve a specific task by ID

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's unique identifier (from JWT) |
| id | integer | Yes | Task ID |

**Request Example**:
```http
GET /api/user_abc123/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Success Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete hackathon project",
  "description": "Finish Phase II frontend implementation",
  "complete": false,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:00:00Z"
}
```

**Error Responses**:
```json
// 404 Not Found - Task doesn't exist or doesn't belong to user
{
  "detail": "Task not found"
}
```

---

### 4. Update Task (Full Update)

**Endpoint**: `PUT /api/{user_id}/tasks/{id}`

**Description**: Replace all task fields with new values

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's unique identifier (from JWT) |
| id | integer | Yes | Task ID |

**Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "complete": true
}
```

**Request Body Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| title | string | Yes | 1-200 characters | Task title |
| description | string \| null | Yes | Max 1000 characters | Task description |
| complete | boolean | Yes | true/false | Completion status |

**Success Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Updated task title",
  "description": "Updated description",
  "complete": true,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T12:00:00Z"
}
```

**Error Responses**:
```json
// 404 Not Found
{
  "detail": "Task not found"
}

// 400 Bad Request - Validation error
{
  "detail": "Title cannot be empty"
}
```

---

### 5. Partial Update Task

**Endpoint**: `PATCH /api/{user_id}/tasks/{id}`

**Description**: Update specific task fields (partial update)

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's unique identifier (from JWT) |
| id | integer | Yes | Task ID |

**Request Body** (all fields optional, at least one required):
```json
{
  "complete": true
}
```

**Request Body Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| title | string | No | 1-200 characters | Task title |
| description | string \| null | No | Max 1000 characters | Task description |
| complete | boolean | No | true/false | Completion status |

**Use Case**: Toggle completion checkbox
```http
PATCH /api/user_abc123/tasks/1 HTTP/1.1
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "complete": true
}
```

**Success Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete hackathon project",
  "description": "Finish Phase II frontend implementation",
  "complete": true,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T12:05:00Z"
}
```

---

### 6. Delete Task

**Endpoint**: `DELETE /api/{user_id}/tasks/{id}`

**Description**: Permanently delete a task

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User's unique identifier (from JWT) |
| id | integer | Yes | Task ID |

**Request Example**:
```http
DELETE /api/user_abc123/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <JWT_TOKEN>
```

**Success Response (204 No Content)**:
```http
HTTP/1.1 204 No Content
```

**Error Responses**:
```json
// 404 Not Found
{
  "detail": "Task not found"
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow this structure:
```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Status Code | Meaning | Frontend Action |
|-------------|---------|-----------------|
| 200 OK | Request successful | Process response data |
| 201 Created | Resource created | Add to UI state |
| 204 No Content | Delete successful | Remove from UI state |
| 400 Bad Request | Validation error | Show error message to user |
| 401 Unauthorized | Missing/invalid JWT | Redirect to login |
| 403 Forbidden | Access denied | Show "Access denied" message |
| 404 Not Found | Resource not found | Show "Not found" message |
| 422 Unprocessable Entity | Invalid request data | Show validation errors |
| 500 Internal Server Error | Server error | Show "Server error, please try again" |
| 503 Service Unavailable | Server unavailable | Retry with exponential backoff |

### Retry Strategy (NFR-011)

**Network Errors Only** (not HTTP error status codes):
- **Condition**: `fetch()` throws "Failed to fetch" error
- **Retry Count**: 3 attempts
- **Delays**: 1s, 2s, 4s (exponential backoff)
- **After 3 failures**: Show error banner "Unable to connect to server"

**Example Implementation**:
```typescript
async function requestWithRetry(url: string, options: RequestInit) {
  const maxRetries = 3;
  const retryDelays = [1000, 2000, 4000];

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      // Don't retry on HTTP errors (4xx, 5xx)
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
      }

      return response;
    } catch (error) {
      // Only retry on network errors
      if (attempt < maxRetries && error.message === 'Failed to fetch') {
        await new Promise(resolve => setTimeout(resolve, retryDelays[attempt]));
        continue;
      }
      throw error;
    }
  }
}
```

---

## CORS Configuration

**Backend CORS Settings** (FastAPI):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Development frontend
        "https://hackathon-todo.vercel.app"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Frontend Fetch Configuration**:
```typescript
fetch(url, {
  method: 'POST',
  credentials: 'include',  // Send cookies with request
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify(data),
});
```

---

## Request/Response Examples

### Complete User Journey: Create and Complete a Task

#### 1. Login (Better Auth)
```http
POST http://localhost:3000/api/auth/signin HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2025-12-31T10:00:00Z"
}
```

#### 2. Fetch Tasks
```http
GET http://localhost:8000/api/user_abc123/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "tasks": [],
  "count": 0
}
```

#### 3. Create Task
```http
POST http://localhost:8000/api/user_abc123/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Write documentation",
  "description": "Complete API contract documentation"
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Write documentation",
  "description": "Complete API contract documentation",
  "complete": false,
  "created_at": "2025-12-24T13:00:00Z",
  "updated_at": "2025-12-24T13:00:00Z"
}
```

#### 4. Toggle Complete
```http
PATCH http://localhost:8000/api/user_abc123/tasks/1 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "complete": true
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Write documentation",
  "description": "Complete API contract documentation",
  "complete": true,
  "created_at": "2025-12-24T13:00:00Z",
  "updated_at": "2025-12-24T13:05:00Z"
}
```

---

## Testing Contract Compliance

### Frontend Integration Tests (Playwright)

**Test Scenarios**:
1. ✅ Create task returns 201 with task object
2. ✅ Fetch tasks returns 200 with tasks array
3. ✅ Update task returns 200 with updated task
4. ✅ Delete task returns 204
5. ✅ Unauthorized request (no JWT) returns 401
6. ✅ Access denied (wrong user_id) returns 403
7. ✅ Invalid data (empty title) returns 400
8. ✅ Not found (invalid ID) returns 404

**Example Test**:
```typescript
test('should create task successfully', async ({ request }) => {
  const response = await request.post('/api/user_abc123/tasks', {
    headers: {
      'Authorization': `Bearer ${validToken}`,
    },
    data: {
      title: 'Test Task',
      description: 'Test Description',
    },
  });

  expect(response.status()).toBe(201);
  const task = await response.json();
  expect(task).toHaveProperty('id');
  expect(task.title).toBe('Test Task');
  expect(task.complete).toBe(false);
});
```

---

## Contract Versioning

**Current Version**: v1

**Version Header** (future):
```http
Accept: application/vnd.hackathon-todo.v1+json
```

**Breaking Changes Policy**:
- Breaking changes require new version (v2)
- Non-breaking changes (new optional fields) can be added to v1
- Deprecation warnings before removal (minimum 30 days)

---

## Summary

- **6 API endpoints**: List, Create, Get, Update (PUT), Patch, Delete
- **Authentication**: JWT in Authorization header (httpOnly cookies)
- **Error Handling**: Standard HTTP status codes + retry logic for network errors
- **CORS**: Configured for localhost (dev) and Vercel (prod)
- **Data Format**: JSON request/response bodies
- **Validation**: Backend validates all inputs, returns 400/422 on errors
- **Security**: User data isolation via user_id filtering, JWT validation on all requests

All contracts are ready for implementation in Phase 2 (tasks generation).

---

**Next**: Phase 1 - Generate quickstart.md
