/**
 * Chat Types
 *
 * Type definitions for chat messages and SSE events.
 */

/** Message sender role */
export type MessageRole = 'user' | 'assistant' | 'system';

/** Chat message representation */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

/** MCP tool names for task operations */
export type TaskToolName =
  | 'add_task'
  | 'list_tasks'
  | 'complete_task'
  | 'delete_task'
  | 'update_task';

/** Tool call event parsed from SSE stream */
export interface ToolCallEvent {
  name: TaskToolName;
  result: {
    task_id?: number;
    status: 'success' | 'error';
    message?: string;
  };
}

/** SSE event types from backend */
export type SSEEventType = 'start' | 'delta' | 'tool_call' | 'done' | 'error';

/** Parsed SSE event */
export interface SSEEvent {
  type: SSEEventType;
  data?: string | ToolCallEvent;
}

/** Return type for useChatMessages hook */
export interface UseChatMessagesReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  loadHistory: (threadId: string) => Promise<void>;
  onToolCall: (callback: (event: ToolCallEvent) => void) => void;
}

/** Return type for useTaskSync hook */
export interface UseTaskSyncReturn {
  isSyncing: boolean;
  lastSyncTime: Date | null;
  forceSync: () => Promise<void>;
}
