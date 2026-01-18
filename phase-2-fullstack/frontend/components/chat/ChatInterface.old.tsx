"use client";

/**
 * ChatInterface Component
 *
 * Provides conversational UI for managing todos through natural language
 * using OpenAI ChatKit. Integrates with the backend chat endpoint and
 * maintains conversation history.
 *
 * Features:
 * - Natural language task management (add, list, complete, update, delete)
 * - Persistent conversation history
 * - JWT authentication for user isolation
 * - Real-time streaming responses from AI
 *
 * @component
 */

import { useEffect, useState, useCallback } from "react";
import { useSession } from "@/lib/auth/client";
import { useRouter } from "next/navigation";
import VoiceInput from "./VoiceInput";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface ChatResponse {
  success: boolean;
  message: string;
  conversation_id: number;
  message_id: number;
  tool_calls: string[];
}

export default function ChatInterface() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login");
    }
  }, [session, isPending, router]);

  // Get API endpoint from environment
  const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  /**
   * Send message to chat endpoint
   */
  const handleSendMessage = async (message: string) => {
    if (!message.trim() || !session?.user?.id) return;

    setIsLoading(true);
    setError(null);

    // Add user message to UI
    const userMessage: ChatMessage = { role: "user", content: message };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      // Get JWT token from /api/token endpoint
      const tokenResponse = await fetch("/api/token");
      if (!tokenResponse.ok) {
        throw new Error("Failed to get authentication token");
      }
      const { token } = await tokenResponse.json();

      // Send to backend chat endpoint
      const response = await fetch(
        `${apiEndpoint}/api/${session.user.id}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            message,
            conversation_id: conversationId,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to send message");
      }

      const data: ChatResponse = await response.json();

      // Update conversation ID on first message
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.message,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      setError(err instanceof Error ? err.message : "Failed to send message");

      // Show error message in chat
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `❌ Error: ${
          err instanceof Error ? err.message : "Failed to send message"
        }`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(input);
  };

  /**
   * Handle Enter key (send message, Shift+Enter for newline)
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  /**
   * Handle voice input transcript (T054)
   * Automatically sends the transcribed text as a message
   */
  const handleVoiceTranscript = useCallback((transcript: string) => {
    if (transcript.trim()) {
      handleSendMessage(transcript);
    }
  }, []);

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 p-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Todo Assistant
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Manage your tasks through natural language. Try &quot;Show me my pending tasks&quot; or &quot;Add a task to buy groceries&quot;
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-12">
            <div className="text-6xl mb-4">💬</div>
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-2">Ask me to add, view, update, or complete tasks</p>
            <div className="mt-6 space-y-2 text-left max-w-md mx-auto bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
              <p className="font-medium text-sm">Example commands:</p>
              <ul className="text-sm space-y-1">
                <li>• &quot;Add a task to buy groceries&quot;</li>
                <li>• &quot;Show me my pending tasks&quot;</li>
                <li>• &quot;Mark task 3 as complete&quot;</li>
                <li>• &quot;Update task 2 title to &#39;Call dentist&#39;&quot;</li>
                <li>• &quot;Delete task 5&quot;</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
              }`}
            >
              <div className="text-xs font-medium mb-1 opacity-70">
                {msg.role === "user" ? "You" : "Todo Assistant"}
              </div>
              <div className="whitespace-pre-wrap break-words">
                {msg.content}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 dark:bg-gray-800">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce w-2 h-2 bg-gray-600 rounded-full"></div>
                <div className="animate-bounce w-2 h-2 bg-gray-600 rounded-full animation-delay-200"></div>
                <div className="animate-bounce w-2 h-2 bg-gray-600 rounded-full animation-delay-400"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-4">
        {error && (
          <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-200 text-sm">
            {error}
          </div>
        )}

        {/* Voice Input Controls (T053-T056: +200 bonus) */}
        <div className="mb-3">
          <VoiceInput
            onTranscript={handleVoiceTranscript}
            disabled={isLoading}
            defaultLanguage="en-US"
          />
        </div>

        <form onSubmit={handleSubmit} className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message or use voice input... (Press Enter to send, Shift+Enter for new line)"
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
