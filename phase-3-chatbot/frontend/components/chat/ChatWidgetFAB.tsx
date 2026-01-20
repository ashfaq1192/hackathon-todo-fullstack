'use client';

import { useChatWidget } from '@/hooks/useChatWidget';

/**
 * Floating Action Button for the chat widget.
 * Fixed position in bottom-right corner of viewport.
 */
export function ChatWidgetFAB() {
  const { isOpen, hasUnreadMessages, open, restore, mode } = useChatWidget();

  const handleClick = () => {
    if (mode === 'minimized') {
      restore();
    } else if (mode === 'closed') {
      open();
    }
    // If open, do nothing - widget is already visible
  };

  // Don't show FAB when widget is fully open
  if (isOpen) {
    return null;
  }

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-[9998] flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg transition-all duration-200 hover:scale-110 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label={hasUnreadMessages ? 'Open chat (new messages)' : 'Open chat assistant'}
      aria-expanded={isOpen}
    >
      {/* Chat icon */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>

      {/* Unread badge */}
      {hasUnreadMessages && (
        <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-bold">
          !
        </span>
      )}
    </button>
  );
}

export default ChatWidgetFAB;
