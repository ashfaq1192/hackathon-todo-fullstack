'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useChatWidget } from './useChatWidget';
import { useChatMessages } from './useChatMessages';
import { useTaskContext } from '../contexts/TaskContext';
import type { ToolCallEvent } from '../types/chat';

/**
 * useTaskSync Hook
 *
 * This hook integrates with the chat widget to listen for specific
 * tool_call events from the AI assistant that indicate a modification
 * to the user's task list (add, complete, delete, update).
 *
 * Upon detecting such an event, it triggers a refresh of the task list
 * in the TaskContext, ensuring the dashboard view is always up-to-date
 * with changes made through the chat interface.
 */
export function useTaskSync() {
  const { triggerRefresh } = useTaskContext();
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Debounced refresh function
  const debouncedRefresh = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    refreshTimeoutRef.current = setTimeout(() => {
      triggerRefresh();
    }, 300); // 300ms debounce
  }, [triggerRefresh]);

  // Callback to be passed to useChatMessages
  const handleToolCall = useCallback(
    (event: ToolCallEvent) => {
      // Tool names that affect task list
      const taskModifyingTools = [
        'add_task',
        'complete_task',
        'delete_task',
        'update_task',
        'list_tasks', // Including list_tasks as it might involve filtering/sorting that affects display
      ];

      if (taskModifyingTools.includes(event.name)) {
        // Trigger debounced task list refresh
        debouncedRefresh();
      }
    },
    [debouncedRefresh]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, []);

  return { handleToolCall };
}
