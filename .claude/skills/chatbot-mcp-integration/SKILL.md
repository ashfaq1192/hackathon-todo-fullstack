---
name: chatbot-mcp-integration
description: Comprehensive guide for building AI-powered chatbots using the Model Context Protocol (MCP) and OpenAI Agents SDK (Swarm) with a Next.js frontend and FastAPI backend. Use when implementing conversational interfaces for task management, integrating AI agents with custom tools, setting up stateless MCP servers, building full-stack AI applications with robust authentication, or implementing chat widget overlays with real-time task sync.
---

# Chatbot MCP Integration

## Quick Start

This skill guides you through building a conversational AI chatbot that can execute backend operations via natural language. The architecture uses:

- **Backend**: FastAPI + MCP tools + OpenAI Swarm Agent + Gemini API (free tier)
- **Frontend**: Next.js + Chat Widget Overlay or full-page chat UI
- **Auth**: JWT tokens from Better Auth

### Implementation Sequence

1. **Define MCP Tools** (backend) - Stateless Python functions
2. **Create Chat Service** (backend) - Swarm Agent with tools
3. **Add Chat Endpoint** (backend) - FastAPI route with JWT auth
4. **Build Chat UI** (frontend) - Widget overlay or full-page component
5. **Wire Up Auth** - Pass JWT tokens to backend
6. **Add Real-Time Sync** - SSE events trigger task list updates

---

## Step 1: Define MCP Tools

MCP tools are stateless Python functions that the AI agent can invoke.

```python
# backend/src/mcp/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="todo-mcp-server")

@mcp.tool()
def add_task(user_id: str, title: str, priority: str = "medium") -> str:
    """Create a new task for the user."""
    # Implementation
    return json.dumps({"success": True, "task_id": task.id})

@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> str:
    """List tasks for the user."""
    # Implementation

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> str:
    """Mark a task as completed."""
    # Implementation
```

**Key Points:**
- Docstrings are critical - the AI reads them to understand when to use each tool
- `user_id` is injected from JWT, not asked from user
- Return JSON strings for consistent parsing

---

## Step 2: Create Chat Service with Swarm Agent

```python
# backend/src/services/chat_service.py
from swarm import Agent, Swarm

class ChatService:
    def __init__(self, db: Session):
        self.swarm_client = Swarm(client=get_gemini_client())

    def _create_agent_for_user(self, user_id: str) -> Agent:
        # Bind user_id to all tool wrappers
        return Agent(
            name="Todo Assistant",
            model="gemini-2.0-flash-exp",
            instructions="You are a helpful todo assistant...",
            functions=[add_task_wrapper, list_tasks_wrapper, ...]
        )

    def process_message(self, user_message: str, user_id: str) -> dict:
        agent = self._create_agent_for_user(user_id)
        response = self.swarm_client.run(agent=agent, messages=[...])
        return {"success": True, "message": response.messages[-1]["content"]}
```

---

## Step 3: Add Chat Endpoint with JWT Auth

```python
# backend/src/api/routes/chat.py
@router.post("/{user_id}/chat")
async def process_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    chat_service = ChatService(db=session)
    return chat_service.process_message(request.message, current_user)
```

---

## Step 4: Build Chat UI

### Option A: Chat Widget Overlay (Recommended)

The chat widget overlay enables users to interact with the AI while viewing their task list.

#### Widget Architecture

```
Dashboard Page
├── TaskProvider (global task state)
│   └── ChatWidgetProvider (widget UI state)
│       ├── TodoList (uses TaskContext)
│       ├── ChatWidgetFAB (floating button)
│       └── ChatWidget (Portal-rendered overlay)
│           ├── ChatMessages
│           ├── ChatInput
│           └── useTaskSync (SSE → TaskContext sync)
```

#### Widget Modes

```typescript
type WidgetMode = 'closed' | 'open' | 'minimized';
```

#### Context Providers

**ChatWidgetContext** - Widget UI state with localStorage persistence:

```typescript
interface ChatWidgetContextValue {
  mode: WidgetMode;
  threadId: string | null;
  hasUnreadMessages: boolean;
  open: () => void;
  close: () => void;
  minimize: () => void;
  restore: () => void;
}
```

**TaskContext** - Task CRUD with optimistic updates:

```typescript
interface TaskContextValue {
  tasks: Task[];
  isLoading: boolean;
  fetchTasks: () => Promise<void>;
  addTask: (data: TaskCreate) => Promise<Task>;
  triggerRefresh: () => void;  // Debounced fetch
}
```

#### Custom Hooks

**useChatWidget** - Convenience wrapper:

```typescript
function useChatWidget() {
  const context = useChatWidgetContext();
  return {
    ...context,
    isOpen: context.mode === 'open',
    toggle: () => context.mode === 'open' ? context.minimize() : context.open(),
  };
}
```

**useTaskSync** - SSE tool_call detection:

```typescript
const TASK_TOOLS = ['add_task', 'complete_task', 'delete_task', 'update_task'];

function useTaskSync() {
  const { triggerRefresh } = useTaskContext();
  
  const handleToolCall = (event: ToolCallEvent) => {
    if (TASK_TOOLS.includes(event.tool_name)) {
      // Debounce 300ms to batch rapid operations
      setTimeout(triggerRefresh, 300);
    }
  };
  return { handleToolCall };
}
```

**useChatMessages** - Message + SSE management:

```typescript
function useChatMessages(options: { onToolCall?: (e: ToolCallEvent) => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const sendMessage = async (text: string) => {
    // POST to backend, parse SSE, call onToolCall
  };
  return { messages, sendMessage };
}
```

#### Widget Components

**ChatWidgetFAB** - Floating action button:

```tsx
export function ChatWidgetFAB() {
  const { isOpen, hasUnreadMessages, open } = useChatWidget();
  if (isOpen) return null;
  return (
    <button onClick={open} className="fixed bottom-6 right-6 z-[9998]">
      <ChatIcon />
      {hasUnreadMessages && <UnreadBadge />}
    </button>
  );
}
```

**ChatWidget** - Main overlay:

```tsx
export function ChatWidget() {
  const { isOpen, close, minimize } = useChatWidget();
  const { handleToolCall } = useTaskSync();
  const { messages, sendMessage } = useChatMessages({ onToolCall: handleToolCall });

  if (!isOpen) return null;
  return createPortal(
    <div role="dialog" className="fixed bottom-20 right-4 w-[380px] h-[500px]">
      <ChatMessages messages={messages} />
      <ChatInput onSend={sendMessage} />
    </div>,
    document.body
  );
}
```

#### Real-Time Task Sync Flow

```
User: "Add task buy groceries"
  ▼
ChatInput.onSend() → POST /api/{user_id}/chat
  ▼
Backend AI calls add_task MCP tool
  ▼
SSE Stream sends tool_call event
  ▼
useTaskSync.handleToolCall() detects 'add_task'
  ▼
TaskContext.triggerRefresh() (debounced)
  ▼
GET /api/{user_id}/tasks
  ▼
TodoList re-renders with new task (< 2 seconds)
```

### Option B: Full-Page Chat

```tsx
// app/chat/page.tsx
export default function ChatPage() {
  return <ChatInterface />;  // Original full-page component
}
```

---

## Step 5: Gemini API Configuration

```python
# backend/src/services/gemini_client.py
from openai import OpenAI

class GeminiClient:
    def __init__(self):
        self.model = "gemini-2.0-flash-exp"
        self._client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
```

---

## Resilience Patterns

### Circuit Breaker

Protect against cascading failures when Gemini API is unavailable.

### Intent-Based Fallback

When Gemini fails, detect intent locally:

```python
def _detect_intent(self, message: str) -> tuple[str, dict]:
    msg_lower = message.lower()
    if "add task" in msg_lower:
        return ("add_task", {"title": extract_title(message)})
    return ("unknown", {})
```

---

## File Organization

```
frontend/
├── app/
│   ├── dashboard/
│   │   ├── page.tsx           # ChatWidget + ChatWidgetFAB
│   │   └── layout.tsx         # TaskProvider + ChatWidgetProvider
│   └── chat/page.tsx          # Full-page chat (preserved)
├── components/chat/
│   ├── ChatWidget.tsx         # Overlay container
│   ├── ChatWidgetFAB.tsx      # Floating button
│   ├── ChatMessages.tsx       # Message display
│   ├── ChatInput.tsx          # Input + send
│   └── ChatInterface.tsx      # Full-page (original)
├── contexts/
│   ├── ChatWidgetContext.tsx  # Widget UI state
│   └── TaskContext.tsx        # Task CRUD state
├── hooks/
│   ├── useChatWidget.ts       # Widget state wrapper
│   ├── useChatMessages.ts     # Message + SSE
│   └── useTaskSync.ts         # Task sync
└── types/
    ├── chat-widget.ts         # WidgetMode, WidgetState
    └── task.ts                # Task, TaskCreate
```

---

## Common Issues

### 1. Task list not updating after AI action

**Cause:** useTaskSync not receiving tool_call events

**Fix:** Ensure SSE parsing extracts tool_name:
```typescript
if (event.type === 'tool_call') {
  onToolCall?.({ tool_name: event.tool_name, ... });
}
```

### 2. Widget state lost on refresh

**Cause:** localStorage not persisting

**Fix:** Check ChatWidgetContext persists to `'chat-widget-state'`

### 3. Unread badge not showing

**Cause:** onNewMessage callback not called

**Fix:** Call `setHasUnreadMessages(true)` when widget is minimized and new message arrives

---

## Success Criteria

- [ ] MCP tools registered and discoverable by Swarm Agent
- [ ] Chat endpoint accepts messages and returns AI responses
- [ ] JWT authentication validates user on every request
- [ ] Tools execute with correct user_id isolation
- [ ] Fallback works when Gemini API fails
- [ ] Chat widget opens/closes/minimizes correctly
- [ ] Task list updates within 2 seconds of AI tool execution
- [ ] Widget state persists across page refreshes
- [ ] Unread badge shows when minimized and new messages arrive
