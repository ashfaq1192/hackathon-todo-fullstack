"use client";

/**
 * ChatKitWidget Component
 *
 * OpenAI ChatKit integration for Todo Assistant.
 * Uses @openai/chatkit-react for the chat interface connected
 * to our custom backend via the ChatKit Python SDK.
 *
 * Hackathon Compliance: PDF Page 17 requires "Frontend: OpenAI ChatKit"
 *
 * @component
 */

import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { useSession } from "@/lib/auth/client";
import { useRouter } from "next/navigation";
import Script from "next/script";
import VoiceInput from "./VoiceInput";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Task interface for parsed tasks
interface ParsedTask {
  id: number;
  title: string;
  priority: "low" | "medium" | "high";
  status: "pending" | "completed";
}

// Parse task list from assistant message
function parseTaskList(content: string): { tasks: ParsedTask[]; header: string | null; isTaskList: boolean } {
  // Pattern to match task items like: - ⏳ **[ID: 11]** PIAIC Class (medium)
  // or: - ✅ **[ID: 12]** Hello (low)
  const taskPattern = /^-\s*([⏳✅])\s*\*?\*?\[?ID:?\s*(\d+)\]?\*?\*?\s*(.+?)\s*\((\w+)\)\s*$/gm;

  const tasks: ParsedTask[] = [];
  let match;

  while ((match = taskPattern.exec(content)) !== null) {
    const [, emoji, id, title, priority] = match;
    tasks.push({
      id: parseInt(id),
      title: title.replace(/\*\*/g, '').trim(),
      priority: priority.toLowerCase() as "low" | "medium" | "high",
      status: emoji === "✅" ? "completed" : "pending",
    });
  }

  // Extract header if present
  const headerMatch = content.match(/\*\*(.+?):\*\*/);
  const header = headerMatch ? headerMatch[1] : null;

  return { tasks, header, isTaskList: tasks.length > 0 };
}

// Task card component for better visualization
function TaskCard({ task }: { task: ParsedTask }) {
  const priorityColors = {
    low: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
    high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  };

  const statusIcons = {
    pending: (
      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-amber-100 dark:bg-amber-900/30">
        <svg className="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </span>
    ),
    completed: (
      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-900/30">
        <svg className="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </span>
    ),
  };

  return (
    <div className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
      task.status === "completed"
        ? "bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700"
        : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:shadow-sm"
    }`}>
      {statusIcons[task.status]}
      <div className="flex-1 min-w-0">
        <p className={`font-medium truncate ${
          task.status === "completed"
            ? "text-gray-500 dark:text-gray-400 line-through"
            : "text-gray-900 dark:text-white"
        }`}>
          {task.title}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">ID: {task.id}</p>
      </div>
      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${priorityColors[task.priority]}`}>
        {task.priority}
      </span>
    </div>
  );
}

// Formatted task list component
function FormattedTaskList({ content }: { content: string }) {
  const { tasks, header, isTaskList } = useMemo(() => parseTaskList(content), [content]);

  if (!isTaskList) {
    return null;
  }

  return (
    <div className="space-y-3">
      {header && (
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg">📋</span>
          <h3 className="font-semibold text-gray-900 dark:text-white">{header}</h3>
          <span className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full text-xs font-medium">
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

// Success/action message formatter
function formatActionMessage(content: string): { isAction: boolean; type: string; message: string } | null {
  // Match patterns like: SUCCESS: Task 'add a of buying a new car' created with ID 30. Priority: medium
  const successPattern = /^SUCCESS:\s*(.+)$/i;
  const errorPattern = /^ERROR:\s*(.+)$/i;
  const infoPattern = /^INFO:\s*(.+)$/i;

  let match;
  if ((match = successPattern.exec(content))) {
    return { isAction: true, type: "success", message: match[1] };
  }
  if ((match = errorPattern.exec(content))) {
    return { isAction: true, type: "error", message: match[1] };
  }
  if ((match = infoPattern.exec(content))) {
    return { isAction: true, type: "info", message: match[1] };
  }

  return null;
}

// Action message component
function ActionMessage({ type, message }: { type: string; message: string }) {
  const styles = {
    success: {
      bg: "bg-emerald-50 dark:bg-emerald-900/20",
      border: "border-emerald-200 dark:border-emerald-800",
      icon: (
        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30">
          <svg className="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </span>
      ),
      text: "text-emerald-800 dark:text-emerald-200",
    },
    error: {
      bg: "bg-red-50 dark:bg-red-900/20",
      border: "border-red-200 dark:border-red-800",
      icon: (
        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30">
          <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </span>
      ),
      text: "text-red-800 dark:text-red-200",
    },
    info: {
      bg: "bg-blue-50 dark:bg-blue-900/20",
      border: "border-blue-200 dark:border-blue-800",
      icon: (
        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30">
          <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
      ),
      text: "text-blue-800 dark:text-blue-200",
    },
  };

  const style = styles[type as keyof typeof styles] || styles.info;

  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl border ${style.bg} ${style.border}`}>
      {style.icon}
      <p className={`font-medium ${style.text}`}>{message}</p>
    </div>
  );
}

// Smart message content renderer
function MessageContent({ content, isUser }: { content: string; isUser: boolean }) {
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
        code({ node, inline, className, children, ...props }: { node?: unknown; inline?: boolean; className?: string; children?: React.ReactNode }) {
          const match = /language-(\w+)/.exec(className || "");
          return !inline && match ? (
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code className={`${className} bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm`} {...props}>
              {children}
            </code>
          );
        },
        strong({ children }) {
          return <strong className="font-semibold text-gray-900 dark:text-white">{children}</strong>;
        },
        p({ children }) {
          return <p className="mb-2 last:mb-0">{children}</p>;
        },
        ul({ children }) {
          return <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>;
        },
        li({ children }) {
          return <li className="text-gray-700 dark:text-gray-300">{children}</li>;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// Define types for ChatKit
interface ChatKitControl {
  sendMessage: (message: string) => void;
  reset: () => void;
}

interface ChatKitConfig {
  api: {
    getClientSecret: (existing?: string | null) => Promise<string>;
    baseUrl?: string;
  };
  events?: {
    onMessage?: (message: { role: string; content: string }) => void;
    onError?: (error: Error) => void;
  };
}

export default function ChatInterface() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [isReady, setIsReady] = useState(false);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // API endpoint
  const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Redirect if not authenticated
  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login");
    }
  }, [session, isPending, router]);

  // Get ChatKit client secret from our backend
  const getClientSecret = useCallback(async (): Promise<string> => {
    if (!session?.user?.id) {
      throw new Error("Not authenticated");
    }

    try {
      // Get JWT token
      const tokenResponse = await fetch("/api/token");
      if (!tokenResponse.ok) {
        throw new Error("Failed to get authentication token");
      }
      const { token } = await tokenResponse.json();

      // Get ChatKit session from our backend
      const response = await fetch(`${apiEndpoint}/api/chatkit/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ user_id: session.user.id }),
      });

      if (!response.ok) {
        throw new Error("Failed to create ChatKit session");
      }

      const data = await response.json();
      setClientSecret(data.client_secret);
      return data.client_secret;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      setError(errorMsg);
      throw err;
    }
  }, [session, apiEndpoint]);

  // Initialize ChatKit when script loads
  useEffect(() => {
    if (typeof window !== "undefined" && session) {
      setIsReady(true);
    }
  }, [session]);

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div role="progressbar" className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* ChatKit Script */}
      <Script
        src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
        strategy="afterInteractive"
        onLoad={() => setIsReady(true)}
        onError={() => setError("Failed to load ChatKit")}
      />

      {/* Header - Modern Gradient Design */}
      <div className="flex-shrink-0 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 p-6 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <span className="text-2xl">🤖</span>
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-white">
                Todo Assistant
              </h1>
              <span className="text-xs bg-white/20 backdrop-blur-sm text-white px-2.5 py-1 rounded-full font-medium">
                AI Powered
              </span>
            </div>
            <p className="text-sm text-white/80 mt-0.5">
              Manage your tasks through natural language
            </p>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="m-4 p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-r-lg shadow-sm">
          <div className="flex items-center gap-2">
            <span className="text-red-500">⚠️</span>
            <p className="text-red-800 dark:text-red-200 font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* ChatKit Container */}
      <div className="flex-1 min-h-0">
        {isReady ? (
          <ChatKitContainer
            apiEndpoint={apiEndpoint}
            getClientSecret={getClientSecret}
            userId={session.user?.id || ""}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">
                Loading ChatKit...
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * ChatKit Container Component
 *
 * Renders the OpenAI ChatKit web component with our custom backend.
 */
function ChatKitContainer({
  apiEndpoint,
  getClientSecret,
  userId,
}: {
  apiEndpoint: string;
  getClientSecret: () => Promise<string>;
  userId: string;
}) {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);

  // Auto-scroll to bottom using direct DOM manipulation
  const scrollToBottom = useCallback(() => {
    const container = document.getElementById("chat-messages-container");
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, []);

  // Scroll when messages array changes
  useEffect(() => {
    // Multiple attempts with increasing delays to ensure DOM is ready
    const timers = [
      setTimeout(scrollToBottom, 0),
      setTimeout(scrollToBottom, 50),
      setTimeout(scrollToBottom, 150),
      setTimeout(scrollToBottom, 300),
    ];
    return () => timers.forEach(clearTimeout);
  }, [messages, scrollToBottom]);

  // Also scroll when loading state changes
  useEffect(() => {
    setTimeout(scrollToBottom, 50);
  }, [isLoading, scrollToBottom]);

  // Create a new thread
  const createThread = async (): Promise<string> => {
    const tokenResponse = await fetch("/api/token");
    const { token } = await tokenResponse.json();

    const response = await fetch(`${apiEndpoint}/api/chatkit/threads`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ metadata: { title: "Chat Session" } }),
    });

    const data = await response.json();
    return data.id;
  };

  // Send message to backend
  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setInput("");

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content }]);

    try {
      // Create thread if needed
      let currentThreadId = threadId;
      if (!currentThreadId) {
        currentThreadId = await createThread();
        setThreadId(currentThreadId);
      }

      // Get token
      const tokenResponse = await fetch("/api/token");
      const { token } = await tokenResponse.json();

      // Send message with streaming
      const response = await fetch(
        `${apiEndpoint}/api/chatkit/threads/${currentThreadId}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            Accept: "text/event-stream",
          },
          body: JSON.stringify({ content }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      // Process SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";

      if (reader) {
        // Add placeholder for assistant message
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                  assistantMessage += data.content;
                  // Update the last message
                  setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1] = {
                      role: "assistant",
                      content: assistantMessage,
                    };
                    return updated;
                  });
                }
              } catch {
                // Ignore parse errors for non-JSON lines
              }
            }
          }
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errorMsg}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div
        id="chat-messages-container"
        className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-slate-50/50 to-white dark:from-gray-900 dark:to-gray-800"
      >
        {messages.length === 0 ? (
          <div className="text-center mt-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg mb-6">
              <span className="text-4xl">💬</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">Start a conversation</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">Ask me to add, view, update, or complete tasks</p>
            <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 p-6">
              <p className="font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                <span className="text-lg">✨</span> Example commands:
              </p>
              <ul className="space-y-3 text-left">
                <li className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
                  <span className="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">➕</span>
                  <span>&quot;Add a task to buy groceries&quot;</span>
                </li>
                <li className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
                  <span className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">📋</span>
                  <span>&quot;Show me my pending tasks&quot;</span>
                </li>
                <li className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
                  <span className="flex-shrink-0 w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">✅</span>
                  <span>&quot;Mark task 3 as complete&quot;</span>
                </li>
                <li className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
                  <span className="flex-shrink-0 w-8 h-8 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center">✏️</span>
                  <span>&quot;Update task 2 title&quot;</span>
                </li>
                <li className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
                  <span className="flex-shrink-0 w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">🗑️</span>
                  <span>&quot;Delete task 5&quot;</span>
                </li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${msg.role === "user"
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white"
                  : "bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-100 dark:border-gray-700"}`}
              >
                <div className={`text-xs font-semibold mb-1.5 flex items-center gap-1.5 ${msg.role === "user" ? "text-white/80" : "text-indigo-600 dark:text-indigo-400"}`}>
                  {msg.role === "user" ? (
                    <>
                      <span className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center text-xs">👤</span>
                      You
                    </>
                  ) : (
                    <>
                      <span className="w-5 h-5 bg-indigo-100 dark:bg-indigo-900/50 rounded-full flex items-center justify-center text-xs">🤖</span>
                      Todo Assistant
                    </>
                  )}
                </div>
                <div className="leading-relaxed">
                  {msg.content ? (
                    <MessageContent content={msg.content} isUser={msg.role === "user"} />
                  ) : (
                    <span className="italic text-gray-400">Thinking...</span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl px-5 py-4 bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce w-2.5 h-2.5 bg-indigo-500 rounded-full"></div>
                <div className="animate-bounce w-2.5 h-2.5 bg-purple-500 rounded-full" style={{ animationDelay: "0.2s" }}></div>
                <div className="animate-bounce w-2.5 h-2.5 bg-pink-500 rounded-full" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Input Area - Modern Design */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4 shadow-lg">
        {/* Voice Input (T054) - Phase III User Story 8 (+200 bonus) */}
        <div className="mb-3">
          <VoiceInput
            onTranscript={(text) => {
              // Send voice transcript directly to chat
              sendMessage(text);
            }}
            disabled={isLoading}
          />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage(input);
          }}
          className="flex space-x-3"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage(input);
              }
            }}
            placeholder="Type your message or use voice input... (Press Enter to send)"
            className="flex-1 px-5 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:text-white resize-none text-gray-800 placeholder-gray-400"
            rows={2}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md hover:shadow-lg transition-all duration-200"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Send
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
