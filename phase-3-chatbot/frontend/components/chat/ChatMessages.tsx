'use client';

/**
 * ChatMessages Component
 *
 * Displays chat messages with intelligent rendering for:
 * - Task lists (parsed from assistant responses)
 * - Action messages (SUCCESS, ERROR, INFO)
 * - Markdown content with syntax highlighting
 *
 * Extracted from ChatInterface.tsx for reuse in ChatWidget.
 */

import { useEffect, useRef, useMemo } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  parseTaskList,
  formatActionMessage,
  type ParsedTask,
} from '@/lib/chat/messageUtils';
import type { ChatMessage } from '@/types/chat';

// ============================================================================
// Sub-components
// ============================================================================

/**
 * TaskCard - Displays a single task with status icon and priority badge
 */
function TaskCard({ task }: { task: ParsedTask }) {
  const priorityColors = {
    low: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    medium:
      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    high: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  };

  const statusIcons = {
    pending: (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/30">
        <svg
          className="h-4 w-4 text-amber-600 dark:text-amber-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </span>
    ),
    completed: (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/30">
        <svg
          className="h-4 w-4 text-emerald-600 dark:text-emerald-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </span>
    ),
  };

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border p-3 transition-all ${
        task.status === 'completed'
          ? 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50'
          : 'border-gray-200 bg-white hover:shadow-sm dark:border-gray-700 dark:bg-gray-800'
      }`}
    >
      {statusIcons[task.status]}
      <div className="min-w-0 flex-1">
        <p
          className={`truncate font-medium ${
            task.status === 'completed'
              ? 'text-gray-500 line-through dark:text-gray-400'
              : 'text-gray-900 dark:text-white'
          }`}
        >
          {task.title}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          ID: {task.id}
        </p>
      </div>
      <span
        className={`rounded-full px-2.5 py-1 text-xs font-medium ${priorityColors[task.priority]}`}
      >
        {task.priority}
      </span>
    </div>
  );
}

/**
 * FormattedTaskList - Renders a list of tasks with header
 */
function FormattedTaskList({ content }: { content: string }) {
  const { tasks, header, isTaskList } = useMemo(
    () => parseTaskList(content),
    [content]
  );

  if (!isTaskList) {
    return null;
  }

  return (
    <div className="space-y-3">
      {header && (
        <div className="mb-3 flex items-center gap-2">
          <span className="text-lg">📋</span>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {header}
          </h3>
          <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
            {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
          </span>
        </div>
      )}
      <div className="space-y-2">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}

/**
 * ActionMessage - Displays SUCCESS/ERROR/INFO messages with styled icons
 */
function ActionMessage({ type, message }: { type: string; message: string }) {
  const styles = {
    success: {
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
      border: 'border-emerald-200 dark:border-emerald-800',
      icon: (
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/30">
          <svg
            className="h-5 w-5 text-emerald-600 dark:text-emerald-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </span>
      ),
      text: 'text-emerald-800 dark:text-emerald-200',
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      icon: (
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
          <svg
            className="h-5 w-5 text-red-600 dark:text-red-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </span>
      ),
      text: 'text-red-800 dark:text-red-200',
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      icon: (
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
          <svg
            className="h-5 w-5 text-blue-600 dark:text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </span>
      ),
      text: 'text-blue-800 dark:text-blue-200',
    },
  };

  const style = styles[type as keyof typeof styles] || styles.info;

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border p-4 ${style.bg} ${style.border}`}
    >
      {style.icon}
      <p className={`font-medium ${style.text}`}>{message}</p>
    </div>
  );
}

/**
 * MessageContent - Smart message content renderer
 * Handles task lists, action messages, and markdown
 */
function MessageContent({
  content,
  isUser,
}: {
  content: string;
  isUser: boolean;
}) {
  // Check for task list format
  const { isTaskList } = useMemo(() => parseTaskList(content), [content]);

  // Check for action message format
  const actionInfo = useMemo(() => formatActionMessage(content), [content]);

  // Render task list with custom formatting
  if (!isUser && isTaskList) {
    return <FormattedTaskList content={content} />;
  }

  // Render action messages with custom styling
  if (!isUser && actionInfo?.isAction) {
    return <ActionMessage type={actionInfo.type} message={actionInfo.message} />;
  }

  // Default: render with ReactMarkdown
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({
          inline,
          className,
          children,
          ...props
        }: {
          inline?: boolean;
          className?: string;
          children?: React.ReactNode;
        }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code
              className={`${className} rounded bg-gray-100 px-1.5 py-0.5 text-sm dark:bg-gray-700`}
              {...props}
            >
              {children}
            </code>
          );
        },
        strong({ children }) {
          return (
            <strong className="font-semibold text-gray-900 dark:text-white">
              {children}
            </strong>
          );
        },
        p({ children }) {
          return <p className="mb-2 last:mb-0">{children}</p>;
        },
        ul({ children }) {
          return (
            <ul className="my-2 list-inside list-disc space-y-1">{children}</ul>
          );
        },
        li({ children }) {
          return (
            <li className="text-gray-700 dark:text-gray-300">{children}</li>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// ============================================================================
// Main Component
// ============================================================================

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

/**
 * ChatMessages - Main message list component with auto-scroll
 */
export function ChatMessages({ messages, isLoading = false }: ChatMessagesProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    const scrollToBottom = () => {
      if (containerRef.current) {
        containerRef.current.scrollTop = containerRef.current.scrollHeight;
      }
    };

    // Multiple attempts with increasing delays to ensure DOM is ready
    const timers = [
      setTimeout(scrollToBottom, 0),
      setTimeout(scrollToBottom, 50),
      setTimeout(scrollToBottom, 150),
    ];

    return () => timers.forEach(clearTimeout);
  }, [messages]);

  // Also scroll when loading state changes
  useEffect(() => {
    if (containerRef.current) {
      const timer = setTimeout(() => {
        if (containerRef.current) {
          containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 space-y-3 overflow-y-auto bg-gray-50 p-4"
    >
      {messages.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {isLoading &&
            messages[messages.length - 1]?.role !== 'assistant' && (
              <LoadingIndicator />
            )}
        </>
      )}
    </div>
  );
}

/**
 * EmptyState - Shown when no messages exist
 */
function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg">
        <span className="text-2xl">💬</span>
      </div>
      <h3 className="mb-1 text-base font-semibold text-gray-800">
        Start a conversation
      </h3>
      <p className="mb-4 text-sm text-gray-500">
        Ask me to add, view, or manage tasks
      </p>
      <div className="w-full max-w-[280px] rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
        <p className="mb-2 flex items-center gap-1.5 text-sm font-medium text-gray-700">
          <span>✨</span> Try saying:
        </p>
        <ul className="space-y-1.5 text-left text-xs text-gray-600">
          <li className="flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded bg-green-100 text-[10px]">
              ➕
            </span>
            &quot;Add a task to buy groceries&quot;
          </li>
          <li className="flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded bg-blue-100 text-[10px]">
              📋
            </span>
            &quot;Show my pending tasks&quot;
          </li>
          <li className="flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded bg-emerald-100 text-[10px]">
              ✅
            </span>
            &quot;Complete task 3&quot;
          </li>
        </ul>
      </div>
    </div>
  );
}

/**
 * MessageBubble - Individual message display
 */
function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 shadow-sm ${
          isUser
            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
            : 'border border-gray-100 bg-white text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white'
        }`}
      >
        <div
          className={`mb-1 flex items-center gap-1.5 text-[10px] font-semibold ${
            isUser
              ? 'text-white/80'
              : 'text-indigo-600 dark:text-indigo-400'
          }`}
        >
          {isUser ? (
            <>
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-white/20 text-[8px]">
                👤
              </span>
              You
            </>
          ) : (
            <>
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-indigo-100 text-[8px] dark:bg-indigo-900/50">
                🤖
              </span>
              Assistant
            </>
          )}
        </div>
        <div className="text-sm leading-relaxed">
          {message.content ? (
            <MessageContent content={message.content} isUser={isUser} />
          ) : message.isStreaming ? (
            <span className="italic text-gray-400">Thinking...</span>
          ) : null}
        </div>
      </div>
    </div>
  );
}

/**
 * LoadingIndicator - Animated dots while waiting for response
 */
function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] rounded-2xl border border-gray-100 bg-white px-4 py-3 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex items-center space-x-1.5">
          <div className="h-2 w-2 animate-bounce rounded-full bg-indigo-500"></div>
          <div
            className="h-2 w-2 animate-bounce rounded-full bg-purple-500"
            style={{ animationDelay: '0.2s' }}
          ></div>
          <div
            className="h-2 w-2 animate-bounce rounded-full bg-pink-500"
            style={{ animationDelay: '0.4s' }}
          ></div>
        </div>
      </div>
    </div>
  );
}

export default ChatMessages;
