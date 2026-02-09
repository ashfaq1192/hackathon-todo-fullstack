"use client";

import { useEffect, useRef, useState } from 'react';
import { useSession } from '@/lib/auth/client'; // From Better Auth client
import { getApiToken } from '@/lib/api/client'; // Assuming this helper exists to get JWT
import toast from 'react-hot-toast'; // Assuming a toast notification library

declare global {
  interface Window {
    OpenAIChatKit: any;
  }
}

interface ChatKitContainerProps {
  apiEndpoint: string;
}

// Minimal ChatKit Container component
function ChatKitContainer({ apiEndpoint }: ChatKitContainerProps) {
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingChatKit, setLoadingChatKit] = useState<boolean>(true);

  useEffect(() => {
    const loadChatKit = async () => {
      try {
        if (!window.OpenAIChatKit && chatContainerRef.current) {
          // Dynamically load the ChatKit script
          const script = document.createElement('script');
          script.src = "https://cdn.platform.openai.com/deployments/chatkit/chatkit.js";
          script.async = true;
          script.onload = async () => {
            if (window.OpenAIChatKit) {
              await initializeChatKit();
            } else {
              setError("OpenAIChatKit not found after script load.");
            }
          };
          script.onerror = () => {
            setError("Failed to load ChatKit script.");
          };
          document.body.appendChild(script);
        } else if (window.OpenAIChatKit) {
          await initializeChatKit();
        }
      } catch (err) {
        setError(`Failed to load ChatKit: ${err}`);
      } finally {
        setLoadingChatKit(false);
      }
    };

    const initializeChatKit = async () => {
      if (!chatContainerRef.current) return;

      try {
        const chatkit = new window.OpenAIChatKit({
          element: chatContainerRef.current,
          // Your backend chat endpoint
          apiEndpoint: apiEndpoint,
          // Custom function to get session, used by ChatKit to authenticate
          getSession: async () => {
            const token = getApiToken(); // Retrieve your JWT
            if (!token) {
              throw new Error("No authentication token found for ChatKit session.");
            }
            
            // Call your backend's /api/chat/session endpoint
            const response = await fetch(`${apiEndpoint}/session`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            });

            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(`Failed to get ChatKit session: ${errorData.detail || response.statusText}`);
            }
            return response.json(); // Should return { session_id, user_id, config }
          },
          // Customize UI
          theme: 'light',
          showBranding: false, // Optional: Hide OpenAI branding
          title: "AI Todo Assistant",
          subtitle: "Manage your tasks with natural language",
          // Add other ChatKit configurations as needed
        });
        chatkit.render();
      } catch (e: any) {
        setError(`Failed to initialize ChatKit: ${e.message || e}`);
        toast.error(`Chatbot Error: ${e.message || e}`);
      }
    };

    if (!error) { // Only try to load if no error occurred previously
      loadChatKit();
    }

    // Cleanup function
    return () => {
      // Potentially destroy ChatKit instance or remove script if necessary
      if (window.OpenAIChatKit && chatContainerRef.current) {
        // window.OpenAIChatKit.destroy(); // If ChatKit has a destroy method
      }
    };
  }, [apiEndpoint, error]);

  if (error) {
    return <div className="text-red-500 p-4">Error loading chatbot: {error}</div>;
  }

  if (loadingChatKit) {
    return <div className="flex justify-center items-center h-full"><p>Loading Chatbot...</p></div>;
  }

  return <div ref={chatContainerRef} className="w-full h-full" />;
}


export default function ChatInterface() {
  const { data: session, isPending } = useSession(); // Get session from Better Auth

  // Ensure ChatKit API endpoint is configured
  const chatkitApiEndpoint = process.env.NEXT_PUBLIC_CHATKIT_API_ENDPOINT;

  if (isPending) {
    return (
      <div className="flex justify-center items-center h-full">
        <p>Authenticating for chatbot...</p>
      </div>
    );
  }

  if (!session || !chatkitApiEndpoint) {
    return (
      <div className="flex justify-center items-center h-full text-red-500">
        <p>Chatbot not available. Please ensure you are logged in and ChatKit is configured.</p>
      </div>
    );
  }

  return <ChatKitContainer apiEndpoint={chatkitApiEndpoint} />;
}
