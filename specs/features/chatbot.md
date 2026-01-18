# Feature: AI-Powered Todo Chatbot

**Feature ID**: chatbot
**Status**: In Progress
**Phases**: III, IV, V
**Points**: 200 (base) + 100 (Urdu) + 200 (voice)

## Overview

Transform traditional form-based task management into a conversational AI interface. Users interact with a chatbot that understands natural language commands like "Add a task to buy groceries" and executes them using MCP (Model Context Protocol) tools.

## Phase Evolution

| Phase | Infrastructure | Key Additions |
|-------|---------------|---------------|
| III | Vercel Serverless | Core chatbot, MCP tools, ChatKit UI |
| IV | Kubernetes | Containerized AI services |
| V | Cloud-Native | Event-driven, advanced AI features |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  OpenAI ChatKit │────▶│  FastAPI Chat   │────▶│  OpenAI Agents  │
│  (Frontend)     │     │  Endpoint       │     │  SDK (Swarm)    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌───────────────────────────┴───────┐
                              │           MCP Tools               │
                              │  ┌─────────┐ ┌─────────┐         │
                              │  │add_task │ │list_task│ ...     │
                              │  └────┬────┘ └────┬────┘         │
                              └───────┼───────────┼───────────────┘
                                      │           │
                              ┌───────▼───────────▼───────┐
                              │    Neon PostgreSQL        │
                              │  (Tasks + Conversations)  │
                              └───────────────────────────┘
```

## Technology Stack

- **Frontend**: OpenAI ChatKit (conversational UI)
- **AI Framework**: OpenAI Agents SDK (Swarm)
- **LLM Backend**: Google Gemini API (free tier via OpenAI-compatible interface)
- **Protocol**: MCP (Model Context Protocol) for tool execution
- **Voice**: Web Speech API (browser-native)

## Core Capabilities

### Natural Language Task Management

| User Says | Action | Response |
|-----------|--------|----------|
| "Add a task to buy groceries" | `add_task()` | "Task created: Buy groceries (ID: 5)" |
| "Show me my pending tasks" | `list_tasks(status='pending')` | Lists pending tasks |
| "Mark task 3 as complete" | `complete_task(task_id=3)` | "Completed: Buy groceries" |
| "Change task 2 title to..." | `update_task()` | "Updated task 2: ..." |
| "Delete task 4" | `delete_task(task_id=4)` | "Deleted task 4" |

### MCP Tools

```python
# Tool Signatures (Stateless - user_id from JWT)
add_task(user_id, title, description) -> {task_id, status, title}
list_tasks(user_id, status?) -> [{task}, ...]
complete_task(user_id, task_id) -> {confirmation}
update_task(user_id, task_id, title?, description?) -> {task}
delete_task(user_id, task_id) -> {confirmation}
```

## Conversation Persistence

### Stateless Architecture
- Server holds NO conversation state in memory
- All context fetched from database per request
- Enables horizontal scaling and serverless deployment

### Context Management
- **Sliding Window**: Keep 10-15 recent messages verbatim
- **Summarization**: Older messages compressed to ~500 token summary
- **Storage**: Summary stored in `Conversation.summary` field
- **Trigger**: Regenerate summary every ~20 messages

### Database Models

```
Conversation {
  id: integer
  user_id: string
  summary: text (nullable, max 500 tokens)
  created_at: timestamp
  updated_at: timestamp
}

Message {
  id: integer
  conversation_id: integer (FK)
  user_id: string
  role: enum (user, assistant)
  content: text
  created_at: timestamp
}
```

## API Endpoint

```
POST /api/{user_id}/chat
Authorization: Bearer <jwt_token>

Request:
{
  "message": "Add a task to buy groceries"
}

Response:
{
  "response": "Task created: Buy groceries (ID: 5)",
  "conversation_id": 1
}
```

## Error Handling

### Retry Strategy
- Exponential backoff: 3 attempts (1s, 2s, 4s delays)
- Circuit breaker: Opens for 60s after 5 consecutive failures
- User message: "I'm having trouble right now. Please try again."

### Edge Cases
- Ambiguous commands: Ask for clarification
- Multiple task matches: List options and ask
- Non-task questions: Politely redirect to todo assistance
- Token expiry: Redirect to login

## Bonus Features

### Urdu Support (+100 points)
- Natural language processing for Urdu commands
- Urdu responses from AI
- Mixed English/Urdu handling
- Example: "ایک کام شامل کریں: دودھ خریدنا"

### Voice Commands (+200 points)
- Browser Web Speech API integration
- Microphone button in ChatKit UI
- Speech-to-text conversion
- Supports English and Urdu
- Graceful fallback for unclear speech

## Success Criteria

- Natural language interpreted correctly 90%+ of time
- Response time < 5 seconds under normal conditions
- Conversation history persists across sessions
- Stateless architecture verified (server restart safe)
- 50 concurrent users supported
- Demo video < 90 seconds showing all interactions

## Non-Functional Requirements

- Chat endpoint: < 5s response time
- MCP tools: < 500ms database operations
- Token management: Sliding window prevents overflow
- Scalability: No server-side session state

## Related Specifications

- Detailed chatbot spec: `specs/archive/phase-3/007-chatbot-mcp/spec.md`
- Plan: `specs/archive/phase-3/007-chatbot-mcp/plan.md`
- Tasks: `specs/archive/phase-3/007-chatbot-mcp/tasks.md`

---

*Last Updated: 2026-01-18*
