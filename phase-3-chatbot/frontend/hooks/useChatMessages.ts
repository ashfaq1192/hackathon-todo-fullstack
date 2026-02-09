import { useState, useCallback, useRef, useEffect } from 'react';
import type { ChatMessage, ToolCallEvent, TaskToolName } from '@/types/chat';
import { useChatWidget } from '@/hooks/useChatWidget';
import toast from 'react-hot-toast';

interface UseChatMessagesOptions {
  /** Callback when a tool call is detected (for task sync) */
  onToolCall?: (event: ToolCallEvent) => void;
  /** Callback when a new assistant message is received (for unread badge) */
  onNewMessage?: () => void;
  /** Number of retry attempts for failed network requests */
  maxRetries?: number;
}

interface UseChatMessagesReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  loadHistory: () => Promise<void>;
  cancelRequest: () => void;
}

// API endpoint
const API_ENDPOINT = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generate a unique message ID
 */
function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Handle 401 Unauthorized responses by redirecting to login
 */
const handleUnauthorized = () => {
  toast.error('Session expired. Please log in again.');
  window.location.assign('/login');
};

/**
 * Get auth token for API requests
 */
async function getAuthToken(): Promise<string> {
  const response = await fetch('/api/token');
  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized();
    }
    throw new Error('Failed to get authentication token');
  }
  const { token } = await response.json();
  return token;
}

/**
 * useChatMessages - Hook for managing chat messages and streaming
 */
export function useChatMessages(
  options: UseChatMessagesOptions = {}
): UseChatMessagesReturn {
  const { onToolCall, onNewMessage, maxRetries = 1 } = options; // Default to 1 retry
  const { threadId, setThreadId } = useChatWidget();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track if history has been loaded
  const historyLoadedRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null); // Ref to store AbortController

  /**
   * Create a new chat thread
   */
  const createThread = useCallback(async (retries = 0): Promise<string> => {
    try {
      const token = await getAuthToken();

      const response = await fetch(`${API_ENDPOINT}/api/chatkit/threads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ metadata: { title: 'Chat Widget Session' } }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          handleUnauthorized();
          throw new Error('Unauthorized');
        }
        if (response.status >= 500 && retries < maxRetries) {
          toast.error('Network error, retrying...');
          await new Promise((resolve) => setTimeout(resolve, 1000 * (retries + 1))); // Exponential backoff
          return createThread(retries + 1);
        }
        throw new Error('Failed to create chat thread');
      }

      const data = await response.json();
      return data.id;
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was intentionally aborted, no error toast needed
        throw err;
      }
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      toast.error(`Error creating chat: ${errorMsg}`);
      throw err;
    }
  }, [maxRetries]);

  /**
   * Load message history from existing thread
   */
  const loadHistory = useCallback(async () => {
    if (!threadId || historyLoadedRef.current) return;

    try {
      const token = await getAuthToken();

      const response = await fetch(
        `${API_ENDPOINT}/api/chatkit/threads/${threadId}/messages`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        // Thread might not exist anymore - that's OK, start fresh
        if (response.status === 404) {
          setThreadId('');
          return;
        }
        if (response.status === 401) {
          handleUnauthorized();
          return;
        }
        throw new Error('Failed to load message history');
      }

      const data = await response.json();

      // Convert API messages to our format
      if (data.messages && Array.isArray(data.messages)) {
        const loadedMessages: ChatMessage[] = data.messages.map(
          (msg: { id?: string; role: string; content: string; created_at?: string }) => ({
            id: msg.id || generateMessageId(),
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: msg.created_at ? new Date(msg.created_at) : new Date(),
            isStreaming: false,
          })
        );

        setMessages(loadedMessages);
        historyLoadedRef.current = true;
      }
    } catch (err) {
      console.error('Failed to load history:', err);
      // Don't set error state - just start fresh
    }
  }, [threadId, setThreadId]);

  /**
   * Send a message and handle SSE streaming response
   */
  const sendMessage = useCallback(
    async (content: string, retries = 0) => {
      if (!content.trim() || isLoading) return;

      // Abort any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setIsLoading(true);
      setError(null);

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
        isStreaming: false,
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        // Create thread if needed
        let currentThreadId = threadId;
        if (!currentThreadId) {
          currentThreadId = await createThread();
          setThreadId(currentThreadId);
        }

        // Get auth token
        const token = await getAuthToken();

        // Send message with streaming
        const response = await fetch(
          `${API_ENDPOINT}/api/chatkit/threads/${currentThreadId}/messages`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
              Accept: 'text/event-stream',
            },
            body: JSON.stringify({ content: content.trim() }),
            signal: controller.signal, // Pass the AbortController's signal
          }
        );

        if (!response.ok) {
          if (response.status === 401) {
            handleUnauthorized();
            throw new Error('Unauthorized');
          }
          if (response.status >= 500 && retries < maxRetries) {
            toast.error('Network error, retrying...');
            await new Promise((resolve) => setTimeout(resolve, 1000 * (retries + 1))); // Exponential backoff
            return sendMessage(content, retries + 1);
          }
          throw new Error('Failed to send message');
        }

        // Process SSE stream
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let assistantContent = '';

        if (reader) {
          // Add placeholder for assistant message
          const assistantMessageId = generateMessageId();
          setMessages((prev) => [
            ...prev,
            {
              id: assistantMessageId,
              role: 'assistant',
              content: '',
              timestamp: new Date(),
              isStreaming: true,
            },
          ]);

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));

                  // Handle content delta
                  if (data.content) {
                    assistantContent += data.content;
                    setMessages((prev) => {
                      const updated = [...prev];
                      const lastIdx = updated.length - 1;
                      if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
                        updated[lastIdx] = {
                          ...updated[lastIdx],
                          content: assistantContent,
                        };
                      }
                      return updated;
                    });
                  }

                  // Handle tool call events (T030, T035)
                  if (data.type === 'tool_call' && data.name && onToolCall) {
                    const toolCallEvent: ToolCallEvent = {
                      name: data.name as TaskToolName,
                      result: {
                        task_id: data.result?.task_id,
                        status: data.result?.status || 'success',
                        message: data.result?.message,
                      },
                    };
                    onToolCall(toolCallEvent);
                  }

                  // Alternative: Check for tool call in structured format
                  if (data.tool_calls && Array.isArray(data.tool_calls) && onToolCall) {
                    for (const toolCall of data.tool_calls) {
                      if (toolCall.name) {
                        const toolCallEvent: ToolCallEvent = {
                          name: toolCall.name as TaskToolName,
                          result: {
                            task_id: toolCall.result?.task_id,
                            status: toolCall.result?.status || 'success',
                            message: toolCall.result?.message,
                          },
                        };
                        onToolCall(toolCallEvent);
                      }
                    }
                  }
                } catch {
                  // Ignore parse errors for non-JSON lines
                }
              }
            }
          }

          // Mark streaming as complete
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
              updated[lastIdx] = {
                ...updated[lastIdx],
                isStreaming: false,
              };
            }
            return updated;
          });
          // Notify onNewMessage after a complete assistant message
          if (assistantContent.length > 0 && onNewMessage) {
            onNewMessage();
          }
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          console.log('Request aborted by user');
          // Update the last message to indicate it was cancelled
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant' && updated[lastIdx].isStreaming) {
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + '\n\n*(Response cancelled)*',
                isStreaming: false,
              };
            }
            return updated;
          });
          return; // Do not show error toast or add new error message
        }
        const errorMsg = err instanceof Error ? err.message : 'Failed to send message';
        setError(errorMsg);
        toast.error(`Chat error: ${errorMsg}`); // Show toast for chat errors

        // Add error message
        setMessages((prev) => [
          ...prev,
          {
            id: generateMessageId(),
            role: 'assistant',
            content: `Error: ${errorMsg}`,
            timestamp: new Date(),
            isStreaming: false,
          },
        ]);
        if (onNewMessage) {
          // Notify onNewMessage even if it's an error message
          onNewMessage();
        }
      } finally {
        setIsLoading(false);
        abortControllerRef.current = null; // Clear the controller after request is done or aborted
      }
    },
    [isLoading, threadId, createThread, setThreadId, onToolCall, onNewMessage, maxRetries]
  );

  /**
   * Cancel any ongoing message request
   */
  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      toast('Chat response cancelled.', { icon: 'ℹ️' });
    }
  }, []);

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    historyLoadedRef.current = false;
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); // Abort any ongoing request
      abortControllerRef.current = null;
    }
  }, []);

  // Load history when threadId changes and is set
  useEffect(() => {
    if (threadId && !historyLoadedRef.current) {
      loadHistory();
    }
  }, [threadId, loadHistory]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    loadHistory,
    cancelRequest,
  };
}

export default useChatMessages;
