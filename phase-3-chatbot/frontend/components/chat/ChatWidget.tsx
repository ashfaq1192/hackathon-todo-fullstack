'use client';

/**
 * Chat Widget Container Component
 *
 * Renders the chat widget as a fixed overlay in the bottom-right corner.
 * Integrates:
 * - ChatMessages for message display
 * - ChatInput for message input with voice support
 * - useChatMessages hook for thread/message management
 *
 * Supports open, minimized, and closed states via ChatWidgetContext.
 */

import { useRef, useEffect } from 'react';
import { useChatWidget } from '../hooks/useChatWidget';
import { useChatMessages } from '../hooks/useChatMessages';
import { useTaskSync } from '../hooks/useTaskSync'; // Import useTaskSync
import { Portal } from '../components/ui/Portal';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';

export function ChatWidget() {
  const { isOpen, close, minimize, setHasUnreadMessages, mode } = useChatWidget();
  const { handleToolCall } = useTaskSync(); // Call useTaskSync to get handleToolCall

  const chatWidgetRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLTextAreaElement>(null); // Ref for ChatInput textarea

  const { messages, isLoading, error, sendMessage } = useChatMessages({
    onToolCall: handleToolCall,
    onNewMessage: () => setHasUnreadMessages(true), // Use onNewMessage from useChatMessages
  });

  // Focus trap for accessibility
  useEffect(() => {
    if (mode === 'open' && chatWidgetRef.current) {
      // Set initial focus to the chat input
      chatInputRef.current?.focus();

      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === 'Tab') {
          event.preventDefault();
          const focusableElements = chatWidgetRef.current?.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          if (!focusableElements) return;

          const firstFocusableEl = focusableElements[0] as HTMLElement;
          const lastFocusableEl = focusableElements[focusableElements.length - 1] as HTMLElement;

          if (event.shiftKey) {
            // If Shift + Tab and focus is on first element, go to last
            if (document.activeElement === firstFocusableEl) {
              lastFocusableEl.focus();
            }
          } else {
            // If Tab and focus is on last element, go to first
            if (document.activeElement === lastFocusableEl) {
              firstFocusableEl.focus();
            }
          }
        }
      };

      document.addEventListener('keydown', handleKeyDown);

      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [mode]);

  // Escape key handler to close/minimize widget
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && mode === 'open') {
        event.preventDefault();
        minimize(); // First minimize
      } else if (event.key === 'Escape' && mode === 'minimized') {
        event.preventDefault();
        close(); // Then close
      }
    };

    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [mode, minimize, close]);

  return (
    <Portal>
      <div
        ref={chatWidgetRef}
        className={`fixed bottom-6 right-6 z-[9999] flex flex-col overflow-hidden rounded-xl bg-white shadow-2xl transition-all duration-200 ease-in-out
          w-[calc(100vw-32px)] h-[60vh] md:w-[400px] md:h-[500px] lg:w-[380px]
          ${
            mode === 'open'
              ? 'opacity-100 scale-100 translate-y-0'
              : mode === 'minimized'
                ? 'opacity-0 scale-90 translate-y-full pointer-events-none'
                : 'opacity-0 scale-95 pointer-events-none' // closed
          }`}
        role="dialog"
        aria-labelledby="chat-widget-title"
        aria-modal="true"
        aria-hidden={!isOpen}
      >
        {/* Header */}
        <div className="flex flex-shrink-0 items-center justify-between border-b border-gray-200 bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/20">
                <span className="text-lg">🤖</span>
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 animate-pulse rounded-full border-2 border-white bg-green-400"></div>
            </div>
            <h2
              id="chat-widget-title"
              className="text-base font-semibold text-white"
            >
              Todo Assistant
            </h2>
          </div>
          <div className="flex items-center gap-1">
            {/* Minimize button */}
            <button
              onClick={minimize}
              className="rounded p-1.5 text-white/80 transition-colors hover:bg-white/20 hover:text-white"
              aria-label="Minimize chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M18 12H6"
                />
              </svg>
            </button>
            {/* Close button */}
            <button
              onClick={close}
              className="rounded p-1.5 text-white/80 transition-colors hover:bg-white/20 hover:text-white"
              aria-label="Close chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="flex-shrink-0 border-b border-red-200 bg-red-50 px-4 py-2">
            <p className="text-xs text-red-600">{error}</p>
          </div>
        )}

        {/* Messages Area */}
        <ChatMessages messages={messages} isLoading={isLoading} />

        {/* Input Area */}
        <ChatInput
          onSend={sendMessage}
          isLoading={isLoading}
          showVoiceInput={true}
          placeholder="Ask me to manage your tasks..."
          inputRef={chatInputRef} // Pass ref to ChatInput
        />
      </div>
    </Portal>
  );
}

export default ChatWidget;
