# Chat API Documentation

This document provides quick reference for the Todo Chatbot API endpoints.

For full OpenAPI specification, see: `specs/features/007-chatbot-mcp/contracts/chat-api.yaml`

## Base URL

- **Production**: `https://your-backend.vercel.app`
- **Development**: `http://localhost:8000`

## Authentication

All endpoints require JWT token in Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### POST `/api/{user_id}/chat`

Send a message to the AI chatbot for task management.

**Request:**
```json
{
  "message": "Add a task to buy groceries"
}
```

**Response:**
```json
{
  "success": true,
  "message": "I've added 'Buy groceries' to your tasks.",
  "conversation_id": 123,
  "tool_calls": ["add_task"]
}
```

**Error Response (429 - Rate Limited):**
```json
{
  "detail": "Rate limit exceeded. Please wait 45 seconds before retrying.",
  "retry_after": 45
}
```

### POST `/api/chatkit/session`

Create a ChatKit session for frontend widget.

**Response:**
```json
{
  "client_secret": "ck_abc123...",
  "session_id": "sess_xyz789...",
  "expires_at": "2024-01-15T12:00:00Z"
}
```

### POST `/api/chatkit/threads`

Create a new conversation thread.

**Request:**
```json
{
  "metadata": {
    "title": "Chat Session"
  }
}
```

**Response:**
```json
{
  "id": "thread_42",
  "metadata": {"title": "Chat Session"},
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### POST `/api/chatkit/threads/{thread_id}/messages`

Send a message and receive streaming response.

**Request:**
```json
{
  "content": "Show me my tasks"
}
```

**Response (Server-Sent Events):**
```
event: start
data: {"thread_id": "thread_42"}

event: delta
data: {"content": "Here are your tasks:\n"}

event: delta
data: {"content": "1. Buy groceries"}

event: done
data: {"thread_id": "thread_42"}
```

## Natural Language Commands

The chatbot understands various natural language commands:

| Intent | Example Commands |
|--------|-----------------|
| Add task | "Add a task to buy groceries", "Create a new high priority task: Doctor appointment" |
| List tasks | "Show my tasks", "What are my pending tasks?", "List all tasks" |
| Complete task | "Mark task 3 as complete", "I finished task 5" |
| Update task | "Change task 2 title to 'Call dentist'", "Set task 1 priority to high" |
| Delete task | "Delete task 4", "Remove task 6" |

### Urdu Language Support

The chatbot also supports Urdu commands:

| Intent | Urdu Command |
|--------|--------------|
| Add task | "ایک کام شامل کریں: دودھ خریدنا" |
| List tasks | "میرے کام دکھائیں" |
| Complete task | "کام 1 مکمل کریں" |
| Delete task | "کام 2 حذف کریں" |

## Rate Limiting

- **Limit**: 15 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Window duration in seconds
  - `Retry-After`: Seconds until rate limit resets (on 429 response)

## MCP Tools

The chatbot uses 5 MCP (Model Context Protocol) tools:

1. **add_task** - Create new tasks
2. **list_tasks** - List user's tasks (all, pending, or completed)
3. **complete_task** - Mark a task as complete
4. **update_task** - Update task title, description, or priority
5. **delete_task** - Delete a task

For tool schemas, see: `specs/features/007-chatbot-mcp/contracts/mcp-tools.yaml`
