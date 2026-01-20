'use client';

/**
 * ChatInput Component
 *
 * Input area for the chat widget with:
 * - Text input with Enter key submit
 * - Send button with loading state
 * - Voice input integration (optional)
 *
 * Extracted from ChatInterface.tsx for reuse in ChatWidget.
 */

import { useState, useCallback, type FormEvent, type KeyboardEvent, type RefObject } from 'react';
import VoiceInput from './VoiceInput';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
  showVoiceInput?: boolean;
  placeholder?: string;
  inputRef?: RefObject<HTMLTextAreaElement | null>;
}

/**
 * ChatInput - Text input with send button and optional voice input
 */
export function ChatInput({
  onSend,
  isLoading = false,
  disabled = false,
  showVoiceInput = true,
  placeholder = 'Type a message...',
  inputRef,
}: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (!input.trim() || isLoading || disabled) return;
      onSend(input.trim());
      setInput('');
    },
    [input, isLoading, disabled, onSend]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!input.trim() || isLoading || disabled) return;
        onSend(input.trim());
        setInput('');
      }
    },
    [input, isLoading, disabled, onSend]
  );

  const handleVoiceTranscript = useCallback(
    (text: string) => {
      if (text.trim() && !isLoading && !disabled) {
        onSend(text.trim());
      }
    },
    [isLoading, disabled, onSend]
  );

  const isDisabled = disabled || isLoading;
  const canSend = input.trim().length > 0 && !isDisabled;

  return (
    <div className="flex-shrink-0 border-t border-gray-200 bg-white p-3">
      {/* Voice Input (optional) - hidden on very small screens */}
      {showVoiceInput && (
        <div className="mb-2 hidden sm:block">
          <VoiceInput onTranscript={handleVoiceTranscript} disabled={isDisabled} />
        </div>
      )}

      {/* Text Input Form */}
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          /* text-base (16px) prevents iOS zoom on focus */
          className="max-h-24 min-h-[44px] flex-1 resize-none rounded-lg border border-gray-300 bg-gray-50 px-3 py-2.5 text-base text-gray-800 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-900 dark:text-white sm:text-sm sm:min-h-[40px] sm:py-2"
          rows={1}
          disabled={isDisabled}
          aria-label="Message input"
          /* Prevent auto-zoom on iOS */
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="sentences"
        />
        <button
          type="submit"
          disabled={!canSend}
          /* Larger touch target on mobile (44px minimum) */
          className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 sm:h-10 sm:w-auto sm:px-4 sm:text-sm sm:font-medium"
          aria-label="Send message"
        >
          {isLoading ? (
            <svg
              className="h-5 w-5 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          )}
        </button>
      </form>

      {/* Hint text - hidden on mobile to save space */}
      <p className="mt-1.5 hidden text-center text-[10px] text-gray-400 sm:block">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}

export default ChatInput;
