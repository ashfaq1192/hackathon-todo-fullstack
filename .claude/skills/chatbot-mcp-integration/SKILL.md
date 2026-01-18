---
name: chatbot-mcp-integration
description: Comprehensive guide for building AI-powered chatbots using the Model Context Protocol (MCP) and OpenAI Agents SDK (Swarm) with a Next.js frontend and FastAPI backend. Use when implementing conversational interfaces for task management, integrating AI agents with custom tools, setting up stateless MCP servers, or building full-stack AI applications with robust authentication.
---

# Chatbot MCP Integration

## Quick Start

This skill guides you through building a conversational AI chatbot that can execute backend operations via natural language. The architecture uses:

- **Backend**: FastAPI + MCP tools + OpenAI Swarm Agent + Gemini API (free tier)
- **Frontend**: Next.js + ChatKit or custom chat UI
- **Auth**: JWT tokens from Better Auth

### Implementation Sequence

1. **Define MCP Tools** (backend) - Stateless Python functions
2. **Create Chat Service** (backend) - Swarm Agent with tools
3. **Add Chat Endpoint** (backend) - FastAPI route with JWT auth
4. **Build Chat UI** (frontend) - React component with API client
5. **Wire Up Auth** - Pass JWT tokens to backend

---

## Step 1: Define MCP Tools

MCP tools are stateless Python functions that the AI agent can invoke. Use `FastMCP` from the official MCP SDK.

```python
# backend/src/mcp/server.py
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

mcp = FastMCP(name="todo-mcp-server")

@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
) -> str:
    """Create a new task for the user.

    Use this tool when the user wants to add, create, or make a new task.

    Args:
        user_id: The authenticated user's ID
        title: Task title (required, max 200 characters)
        description: Optional task description
        priority: 'low', 'medium', or 'high' (default: medium)

    Returns:
        JSON string with task creation result
    """
    db = get_db_session()
    try:
        # Call your CRUD function
        result = create_task(user_id=user_id, title=title, ...)
        return str(result)
    finally:
        db.close()

@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> str:
    """List tasks for the user. Use when user wants to see their tasks."""
    # ... implementation

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> str:
    """Mark a task as completed."""
    # ... implementation

def get_mcp_server() -> FastMCP:
    """Return the configured MCP server instance."""
    return mcp
```

**Key Points:**
- Docstrings are critical - the AI reads them to understand when to use each tool
- `user_id` is injected from JWT, not asked from user
- Return JSON strings for consistent parsing

---

## Step 2: Create Chat Service with Swarm Agent

The Chat Service uses OpenAI's Swarm framework with Gemini API as the LLM backend.

```python
# backend/src/services/chat_service.py
from swarm import Agent, Swarm
from src.services.gemini_client import get_gemini_client
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
# ... other tool imports

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        # Gemini client configured with OpenAI-compatible endpoint
        gemini_client = get_gemini_client()
        self.client = gemini_client.get_client()
        self.model = gemini_client.model
        # Initialize Swarm with Gemini-backed client
        self.swarm_client = Swarm(client=self.client)

    def _create_agent_for_user(self, user_id: str) -> Agent:
        """Create agent with user_id pre-bound to all tools."""
        db = self.db

        # Wrapper functions with user_id bound
        def add_task_wrapper(title: str, description: str = "", priority: str = "medium"):
            """Add a new task for the authenticated user."""
            return add_task(user_id=user_id, title=title, priority=priority, db=db)

        def list_tasks_wrapper(status: str = "all"):
            """List tasks for the authenticated user."""
            return list_tasks(user_id=user_id, status=status, db=db)

        # ... other wrapper functions

        return Agent(
            name="Todo Assistant",
            model=self.model,
            instructions="""You are a helpful todo assistant that manages tasks.

Your user_id is already bound - DO NOT ask for it. Just use the tools directly.

Available tools:
- add_task_wrapper(title, description?, priority?)
- list_tasks_wrapper(status?)
- complete_task_wrapper(task_id)
- update_task_wrapper(task_id, title?, description?, priority?)
- delete_task_wrapper(task_id)

Always confirm actions with friendly responses. Use emojis.""",
            functions=[
                add_task_wrapper,
                list_tasks_wrapper,
                complete_task_wrapper,
                update_task_wrapper,
                delete_task_wrapper,
            ]
        )

    def process_message(self, user_message: str, user_id: str) -> dict:
        """Process user message through Swarm Agent."""
        agent = self._create_agent_for_user(user_id)
        messages = [{"role": "user", "content": user_message}]

        response = self.swarm_client.run(agent=agent, messages=messages)

        assistant_message = response.messages[-1]["content"]
        return {
            "success": True,
            "message": assistant_message,
            "tool_calls": [m.get("tool_call_id") for m in response.messages if m.get("role") == "tool"],
        }
```

---

## Step 3: Add Chat Endpoint with JWT Auth

```python
# backend/src/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from src.api.dependencies import get_current_user
from src.database import get_session
from src.services.chat_service import ChatService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    success: bool
    message: str
    conversation_id: int
    tool_calls: list[str] = []

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def process_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),  # JWT validation
    session: Session = Depends(get_session),
) -> ChatResponse:
    """Process natural language message through AI assistant."""
    # CRITICAL: Validate JWT user matches URL user
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch",
        )

    chat_service = ChatService(db=session)
    result = chat_service.process_message(
        user_message=request.message,
        user_id=current_user,
    )

    return ChatResponse(
        success=result["success"],
        message=result["message"],
        conversation_id=request.conversation_id or 1,
        tool_calls=result.get("tool_calls", []),
    )
```

---

## Step 4: Build Chat UI

### Option A: Custom React Chat Component

```tsx
// frontend/components/chat/ChatInterface.tsx
"use client";

import { useState } from 'react';
import { useSession } from '@/lib/auth/client';
import { sendChatMessage } from '@/lib/api/chat';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatInterface() {
  const { data: session } = useSession();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !session?.user?.id) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(session.user.id, userMessage);
      setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] p-3 rounded-lg ${
              msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-gray-500">Thinking...</div>}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 p-2 border rounded"
          />
          <button type="submit" disabled={isLoading} className="px-4 py-2 bg-blue-500 text-white rounded">
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
```

### Chat API Client

```typescript
// frontend/lib/api/chat.ts
import { apiClient } from './client';

export interface ChatResponse {
  success: boolean;
  message: string;
  conversation_id: number;
  tool_calls: string[];
}

export async function sendChatMessage(userId: string, message: string): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(`/api/${userId}/chat`, {
    message,
  });
  return response.data;
}
```

### Option B: OpenAI ChatKit Integration

If using OpenAI ChatKit for the hackathon requirement:

```tsx
// frontend/components/chat/ChatKitContainer.tsx
"use client";

import { useEffect, useRef } from 'react';
import { getApiToken } from '@/lib/api/client';

declare global {
  interface Window { OpenAIChatKit: any; }
}

export default function ChatKitContainer({ apiEndpoint }: { apiEndpoint: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = "https://cdn.platform.openai.com/deployments/chatkit/chatkit.js";
    script.async = true;
    script.onload = () => {
      if (window.OpenAIChatKit && containerRef.current) {
        const chatkit = new window.OpenAIChatKit({
          element: containerRef.current,
          apiEndpoint,
          getSession: async () => {
            const token = getApiToken();
            const response = await fetch(`${apiEndpoint}/session`, {
              method: 'POST',
              headers: { 'Authorization': `Bearer ${token}` },
            });
            return response.json();
          },
          theme: 'light',
          title: "AI Todo Assistant",
        });
        chatkit.render();
      }
    };
    document.body.appendChild(script);
  }, [apiEndpoint]);

  return <div ref={containerRef} className="w-full h-full" />;
}
```

---

## Step 5: Gemini API Configuration (Free Tier)

Configure Gemini as an OpenAI-compatible backend for Swarm:

```python
# backend/src/services/gemini_client.py
from openai import OpenAI
from src.config import settings

class GeminiClient:
    def __init__(self):
        self.model = "gemini-2.0-flash-exp"
        self._client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    def get_client(self) -> OpenAI:
        return self._client

_gemini_client: GeminiClient | None = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
```

**Environment Variables:**
```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key
```

---

## Resilience Patterns

### Circuit Breaker

Protect against cascading failures when Gemini API is unavailable:

```python
# backend/src/middleware/circuit_breaker.py
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open" # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, func):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerError("Circuit breaker is open")

        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### Intent-Based Fallback

When Gemini API fails, detect intent locally and execute tools directly:

```python
def _detect_intent(self, message: str) -> tuple[str, dict]:
    """Detect user intent for fallback tool execution."""
    msg_lower = message.lower()

    # List tasks patterns
    if any(p in msg_lower for p in ["list task", "show task", "my task"]):
        return ("list_tasks", {"status": "all"})

    # Add task patterns
    if any(p in msg_lower for p in ["add task", "create task", "new task"]):
        title = self._extract_title(message)
        return ("add_task", {"title": title})

    # Complete task patterns
    if any(p in msg_lower for p in ["complete task", "mark done", "finish task"]):
        task_id = self._extract_task_id(message)
        return ("complete_task", {"task_id": task_id})

    return ("unknown", {})
```

---

## File Organization

```
backend/
├── src/
│   ├── main.py                    # FastAPI app, routers
│   ├── config.py                  # Environment variables
│   ├── database/
│   │   ├── connection.py          # Database session
│   │   └── crud.py                # CRUD operations
│   ├── models/
│   │   ├── task.py                # Task model
│   │   ├── conversation.py        # Conversation model
│   │   └── message.py             # Message model
│   ├── services/
│   │   ├── chat_service.py        # Swarm Agent orchestration
│   │   ├── gemini_client.py       # Gemini API client
│   │   └── context_service.py     # Conversation context
│   ├── mcp/
│   │   ├── server.py              # FastMCP server
│   │   └── tools/                 # Individual MCP tools
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── update_task.py
│   │       └── delete_task.py
│   ├── middleware/
│   │   └── circuit_breaker.py     # Resilience patterns
│   └── api/routes/
│       ├── chat.py                # Chat endpoint
│       └── tasks.py               # REST API (optional)
└── tests/
    ├── unit/mcp/                  # Tool unit tests
    └── integration/               # API integration tests

frontend/
├── app/
│   └── chat/page.tsx              # Chat page
├── components/chat/
│   └── ChatInterface.tsx          # Chat UI component
├── lib/api/
│   ├── client.ts                  # API client with auth
│   └── chat.ts                    # Chat API functions
└── types/chat.ts                  # TypeScript types
```

---

## Testing

### Unit Test for MCP Tool

```python
# backend/tests/unit/mcp/test_add_task.py
import pytest
from src.mcp.tools.add_task import add_task

def test_add_task_success(db_session, test_user_id):
    result = add_task(
        user_id=test_user_id,
        title="Test Task",
        priority="high",
        db=db_session,
    )
    assert result["success"] is True
    assert "task_id" in result
    assert result["message"] == "Task 'Test Task' created successfully!"

def test_add_task_invalid_priority(db_session, test_user_id):
    result = add_task(
        user_id=test_user_id,
        title="Test",
        priority="invalid",
        db=db_session,
    )
    assert result["success"] is False
```

### Integration Test for Chat Endpoint

```python
# backend/tests/integration/test_chat.py
import pytest
from fastapi.testclient import TestClient

def test_chat_add_task(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/test-user-id/chat",
        json={"message": "Add a task to buy groceries"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "groceries" in data["message"].lower() or "created" in data["message"].lower()
```

---

## Common Issues

### 1. Gemini 400 Error on Tool Results

**Problem:** Gemini API rejects tool result format.

**Solution:** Use intent-based fallback and capture tool results:
```python
# Capture last tool result for fallback
_last_tool_result: dict | None = None

def add_task_wrapper(...):
    global _last_tool_result
    result = add_task(...)
    _last_tool_result = result  # Capture for fallback
    return result
```

### 2. Rate Limiting (429 Errors)

**Problem:** Gemini free tier has rate limits (15 req/min).

**Solution:** Use circuit breaker + local intent detection:
```python
if "429" in error_str or "rate" in error_str.lower():
    intent, params = self._detect_intent(user_message)
    if intent != "unknown":
        return self._execute_fallback_tool(intent, params, user_id)
```

### 3. JWT Token Not Passed to Backend

**Problem:** Chat requests fail with 401.

**Solution:** Ensure API client includes Authorization header:
```typescript
// lib/api/client.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Resources

This skill bundles the following resources:

### references/
- `mcp_spec.md` - Model Context Protocol specification overview
- `openai_agents_sdk.md` - OpenAI Agents SDK (Swarm) documentation
- `chatkit_config.md` - OpenAI ChatKit configuration guide
- `api_reference.md` - Chat API contracts and schemas

### assets/
- `fastapi_mcp_template/` - Complete FastAPI MCP server boilerplate
- `nextjs_chatkit_template/` - Next.js frontend with ChatKit integration

### scripts/
- `create_mcp_tool.py` - Scaffold new MCP tools
- `generate_chat_endpoint.py` - Generate FastAPI chat endpoint

---

## Success Criteria

- [ ] MCP tools registered and discoverable by Swarm Agent
- [ ] Chat endpoint accepts messages and returns AI responses
- [ ] JWT authentication validates user on every request
- [ ] Tools execute with correct user_id isolation
- [ ] Fallback works when Gemini API fails
- [ ] Frontend sends messages and displays responses
- [ ] Conversation context maintained across messages
