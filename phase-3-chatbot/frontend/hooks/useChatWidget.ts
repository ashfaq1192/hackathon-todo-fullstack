'use client';

import { useChatWidgetContext } from '../contexts/ChatWidgetContext';
import type { ChatWidgetContextValue } from '../types/chat-widget';

/**
 * Hook for managing chat widget state.
 * Wraps ChatWidgetContext with additional convenience methods.
 */
export function useChatWidget(): ChatWidgetContextValue & {
  isOpen: boolean;
  isMinimized: boolean;
  isClosed: boolean;
  toggle: () => void;
} {
  const context = useChatWidgetContext();

  const isOpen = context.mode === 'open';
  const isMinimized = context.mode === 'minimized';
  const isClosed = context.mode === 'closed';

  const toggle = () => {
    if (isOpen) {
      context.minimize();
    } else {
      context.open();
    }
  };

  return {
    ...context,
    isOpen,
    isMinimized,
    isClosed,
    toggle,
  };
}

export default useChatWidget;
