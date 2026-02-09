'use client';

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useMemo,
  ReactNode,
} from 'react';
import type {
  WidgetMode,
  ChatWidgetContextValue,
  WidgetPersistedState,
} from '../types/chat-widget';
import { WIDGET_STORAGE_KEY } from '../types/chat-widget';

const ChatWidgetContext = createContext<ChatWidgetContextValue | null>(null);

interface ChatWidgetProviderProps {
  children: ReactNode;
}

/** Load persisted state from localStorage */
function loadPersistedState(): WidgetPersistedState | null {
  if (typeof window === 'undefined') return null;

  try {
    const stored = localStorage.getItem(WIDGET_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored) as WidgetPersistedState;
    }
  } catch (error) {
    console.warn('Failed to load widget state from localStorage:', error);
  }
  return null;
}

/** Save state to localStorage */
function savePersistedState(state: WidgetPersistedState): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(WIDGET_STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn('Failed to save widget state to localStorage:', error);
  }
}

export function ChatWidgetProvider({ children }: ChatWidgetProviderProps) {
  const [mode, setMode] = useState<WidgetMode>('closed');
  const [threadId, setThreadIdState] = useState<string | null>(null);
  const [hasUnreadMessages, setHasUnreadMessages] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load persisted state on mount (client-side only)
  useEffect(() => {
    const persisted = loadPersistedState();
    if (persisted) {
      setMode(persisted.mode);
      setThreadIdState(persisted.threadId);
    }
    setIsInitialized(true);
  }, []);

  // Save state to localStorage when it changes
  useEffect(() => {
    if (!isInitialized) return;

    savePersistedState({
      mode,
      threadId,
    });
  }, [mode, threadId, isInitialized]);

  const open = useCallback(() => {
    setMode('open');
    setHasUnreadMessages(false);
  }, []);

  const close = useCallback(() => {
    setMode('closed');
  }, []);

  const minimize = useCallback(() => {
    setMode('minimized');
  }, []);

  const restore = useCallback(() => {
    setMode('open');
    setHasUnreadMessages(false);
  }, []);

  const setThreadId = useCallback((id: string) => {
    setThreadIdState(id);
  }, []);

  const markMessagesRead = useCallback(() => {
    setHasUnreadMessages(false);
  }, []);

  const value = useMemo<ChatWidgetContextValue>(
    () => ({
      mode,
      threadId,
      hasUnreadMessages,
      open,
      close,
      minimize,
      restore,
      setThreadId,
      markMessagesRead,
      setHasUnreadMessages,
    }),
    [
      mode,
      threadId,
      hasUnreadMessages,
      open,
      close,
      minimize,
      restore,
      setThreadId,
      markMessagesRead,
    ]
  );

  return (
    <ChatWidgetContext.Provider value={value}>
      {children}
    </ChatWidgetContext.Provider>
  );
}

export function useChatWidgetContext(): ChatWidgetContextValue {
  const context = useContext(ChatWidgetContext);
  if (!context) {
    throw new Error(
      'useChatWidgetContext must be used within a ChatWidgetProvider'
    );
  }
  return context;
}

export default ChatWidgetContext;
