'use client';

/**
 * useTaskSync Hook
 *
 * Detects tool_call SSE events and triggers task list refresh.
 * Provides a debounced refresh to avoid excessive API calls when
 * multiple task operations occur in quick succession.
 *
 * Used by ChatWidget to sync dashboard task list in real-time (US3).
 */

import { useCallback, useRef } from 'react';
import { useTaskContext } from '@/contexts/TaskContext';
import type { ToolCallEvent } from '@/types/chat';

// Tool names that modify tasks
const TASK_MODIFYING_TOOLS = [
  'add_task',
  'complete_task',
  'delete_task',
  'update_task',
] as const;

// Debounce delay in milliseconds
const DEBOUNCE_DELAY = 300;

interface UseTaskSyncReturn {
  /** Handler for tool call events - triggers debounced task refresh */
  handleToolCall: (event: ToolCallEvent) => void;
  /** Force immediate task refresh (bypasses debounce) */
  forceRefresh: () => void;
}

/**
 * useTaskSync - Hook for syncing tasks when AI modifies them
 */
export function useTaskSync(): UseTaskSyncReturn {
  const { triggerRefresh } = useTaskContext();
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Debounced refresh - waits for DEBOUNCE_DELAY ms of inactivity
   * before triggering the actual refresh
   */
  const debouncedRefresh = useCallback(() => {
    // Clear any existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new timer
    debounceTimerRef.current = setTimeout(() => {
      triggerRefresh();
      debounceTimerRef.current = null;
    }, DEBOUNCE_DELAY);
  }, [triggerRefresh]);

  /**
   * Handle tool call events from SSE stream
   * Triggers task refresh for task-modifying operations
   */
  const handleToolCall = useCallback(
    (event: ToolCallEvent) => {
      // Check if this tool modifies tasks
      if (TASK_MODIFYING_TOOLS.includes(event.name as (typeof TASK_MODIFYING_TOOLS)[number])) {
        // Trigger debounced refresh
        debouncedRefresh();
      }
    },
    [debouncedRefresh]
  );

  /**
   * Force immediate refresh (bypasses debounce)
   */
  const forceRefresh = useCallback(() => {
    // Clear any pending debounced refresh
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
    // Trigger immediate refresh
    triggerRefresh();
  }, [triggerRefresh]);

  return {
    handleToolCall,
    forceRefresh,
  };
}

export default useTaskSync;
