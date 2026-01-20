# Data Model: Chat Widget Overlay

**Feature**: 001-chat-widget-overlay
**Date**: 2026-01-20

## Overview

This feature introduces new frontend state models for the chat widget overlay. No database schema changes are required - all models are TypeScript interfaces for React state management.

---

## 1. Widget State Types

### WidgetState

Tracks the visibility and mode of the chat widget.

```typescript
// File: types/chat-widget.ts

export type WidgetMode = 'closed' | 'open' | 'minimized';

export interface WidgetState {
  mode: WidgetMode;
  threadId: string | null;
  hasUnreadMessages: boolean;
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| mode | `'closed' \| 'open' \| 'minimized'` | Current visibility state |
| threadId | `string \| null` | Active conversation thread ID |
| hasUnreadMessages | `boolean` | Badge indicator for minimized state |

**State Transitions**:
```
closed → open (click FAB)
open → minimized (click minimize)
open → closed (click close)
minimized → open (click FAB)
minimized → closed (click close on FAB long-press or context menu)
```

---

### WidgetPersistedState

Subset of WidgetState that persists to localStorage.

```typescript
export interface WidgetPersistedState {
  mode: WidgetMode;
  threadId: string | null;
}
```

**Storage**:
- Key: `chat-widget-state`
- Format: JSON string
- Persistence: Browser session (survives refresh, not incognito)

---

## 2. Chat Message Types

### ChatMessage

Represents a single message in the conversation.

```typescript
// File: types/chat.ts

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| id | `string` | Unique message identifier |
| role | `MessageRole` | Who sent the message |
| content | `string` | Message text content |
| timestamp | `Date` | When message was created |
| isStreaming | `boolean?` | True while SSE is streaming content |

---

### ToolCallEvent

Parsed from SSE stream when AI invokes MCP tools.

```typescript
export type TaskToolName =
  | 'add_task'
  | 'list_tasks'
  | 'complete_task'
  | 'delete_task'
  | 'update_task';

export interface ToolCallEvent {
  name: TaskToolName;
  result: {
    task_id?: number;
    status: 'success' | 'error';
    message?: string;
  };
}
```

**Usage**: When `useTaskSync` detects a tool_call event with task-related name, it triggers a task list refresh.

---

## 3. Context Types

### TaskContextValue

Shared task state for dashboard and widget synchronization.

```typescript
// File: contexts/TaskContext.tsx

export interface TaskContextValue {
  // State
  tasks: Task[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchTasks: () => Promise<void>;
  addTask: (task: TaskCreate) => Promise<Task>;
  updateTask: (taskId: number, updates: TaskPatch) => Promise<Task>;
  deleteTask: (taskId: number) => Promise<void>;

  // Sync
  triggerRefresh: () => void;
}
```

**Consumers**:
- `TodoList` - Reads `tasks`, `isLoading`
- `AddTodoForm` - Calls `addTask`
- `useChatMessages` hook - Calls `triggerRefresh` after tool_call events

---

### ChatWidgetContextValue

Widget visibility state and controls.

```typescript
// File: contexts/ChatWidgetContext.tsx

export interface ChatWidgetContextValue {
  // State
  mode: WidgetMode;
  threadId: string | null;
  hasUnreadMessages: boolean;

  // Actions
  open: () => void;
  close: () => void;
  minimize: () => void;
  restore: () => void;
  setThreadId: (id: string) => void;
  markMessagesRead: () => void;
}
```

**Consumers**:
- `ChatWidgetFAB` - Calls `open`, reads `mode`, `hasUnreadMessages`
- `ChatWidget` - Calls `close`, `minimize`, reads `mode`
- `useChatMessages` - Calls `setThreadId`

---

## 4. Hook Return Types

### UseChatMessagesReturn

Return type for the chat messages hook.

```typescript
// File: hooks/useChatMessages.ts

export interface UseChatMessagesReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  onToolCall: (callback: (event: ToolCallEvent) => void) => void;
}
```

---

### UseTaskSyncReturn

Return type for the task synchronization hook.

```typescript
// File: hooks/useTaskSync.ts

export interface UseTaskSyncReturn {
  isSyncing: boolean;
  lastSyncTime: Date | null;
  forceSync: () => Promise<void>;
}
```

---

## 5. Existing Types (Unchanged)

The following existing types from `types/task.ts` remain unchanged:

```typescript
// Already exists - no modifications needed

export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  complete: boolean;
  priority: TaskPriority;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
}

export interface TaskPatch {
  title?: string;
  description?: string | null;
  complete?: boolean;
  priority?: TaskPriority;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}
```

---

## 6. Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend State                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TaskContext ◄──────────────── useChatMessages               │
│  ├─ tasks[]                     (triggers refresh on        │
│  ├─ fetchTasks()                tool_call events)           │
│  └─ triggerRefresh()                                        │
│       │                                                      │
│       ▼                                                      │
│  TodoList                       ChatWidget                   │
│  (reactive updates)             ├─ ChatMessages              │
│                                 ├─ ChatInput                 │
│                                 └─ VoiceInput                │
│                                                              │
│  ChatWidgetContext ◄─────────── ChatWidgetFAB                │
│  ├─ mode                        (toggle open/close)          │
│  ├─ open()                                                   │
│  └─ minimize()                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Unchanged)                       │
├─────────────────────────────────────────────────────────────┤
│  GET /api/{user_id}/tasks  ──►  Task[]                      │
│  POST /api/chatkit/threads/{id}/messages  ──►  SSE Stream   │
│       │                                                      │
│       └─► event: tool_call                                  │
│           data: {name: "add_task", result: {...}}           │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Validation Rules

### WidgetState
- `mode` must be one of: 'closed', 'open', 'minimized'
- `threadId` can be null (no active conversation) or valid UUID string
- `hasUnreadMessages` defaults to false

### ChatMessage
- `id` must be non-empty string
- `role` must be one of: 'user', 'assistant', 'system'
- `content` can be empty string (for streaming start)
- `timestamp` must be valid Date

### ToolCallEvent
- `name` must be recognized task tool name
- `result.status` must be 'success' or 'error'
- `result.task_id` required for single-task operations

---

## 8. State Initialization

### TaskContext Initial State
```typescript
const initialTaskState = {
  tasks: [],
  isLoading: true,
  error: null
};
```

### ChatWidgetContext Initial State
```typescript
const getInitialWidgetState = (): WidgetState => {
  // Try to restore from localStorage
  const stored = localStorage.getItem('chat-widget-state');
  if (stored) {
    try {
      const parsed = JSON.parse(stored) as WidgetPersistedState;
      return {
        mode: parsed.mode,
        threadId: parsed.threadId,
        hasUnreadMessages: false // Reset on page load
      };
    } catch {
      // Invalid JSON, use defaults
    }
  }

  return {
    mode: 'closed',
    threadId: null,
    hasUnreadMessages: false
  };
};
```

---

## Summary

| Type | Location | Purpose |
|------|----------|---------|
| WidgetState | `types/chat-widget.ts` | Widget visibility tracking |
| WidgetPersistedState | `types/chat-widget.ts` | localStorage persistence |
| ChatMessage | `types/chat.ts` | Message representation |
| ToolCallEvent | `types/chat.ts` | SSE event parsing |
| TaskContextValue | `contexts/TaskContext.tsx` | Task state sharing |
| ChatWidgetContextValue | `contexts/ChatWidgetContext.tsx` | Widget state sharing |

No database changes required. All models are frontend-only.
