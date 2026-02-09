/**
 * Chat Widget State Types
 *
 * Type definitions for the chat widget overlay feature.
 */

/** Widget visibility mode */
export type WidgetMode = 'closed' | 'open' | 'minimized';

/** Full widget state including transient properties */
export interface WidgetState {
  mode: WidgetMode;
  threadId: string | null;
  hasUnreadMessages: boolean;
}

/** Subset of WidgetState that persists to localStorage */
export interface WidgetPersistedState {
  mode: WidgetMode;
  threadId: string | null;
}

/** Context value for ChatWidgetContext */
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
  setHasUnreadMessages: (hasUnread: boolean) => void;
}

/** localStorage key for persisted widget state */
export const WIDGET_STORAGE_KEY = 'chat-widget-state';
