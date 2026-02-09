# OpenAI ChatKit: Configuration and Customization Options

OpenAI ChatKit provides a highly customizable UI component for building conversational interfaces. Integrating it with our Next.js frontend and FastAPI backend requires careful configuration, especially regarding authentication and API endpoints.

## Core Configuration Parameters

ChatKit is typically configured on the client-side (Next.js frontend) and relies on several environment variables and endpoint configurations to communicate with your backend.

### 1. `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
-   **Purpose:** Required for ChatKit to authenticate your domain with OpenAI, especially for hosted deployments.
-   **Source:** Obtained from the OpenAI platform settings (`https://platform.openai.com/settings/organization/chatkit`).
-   **Usage:** Set as an environment variable in your Next.js project's `.env.local` or Vercel settings.

### 2. `NEXT_PUBLIC_CHATKIT_API_ENDPOINT`
-   **Purpose:** Specifies the base URL for your backend where the ChatKit-related endpoints (like session and message handling) are hosted.
-   **Source:** Your FastAPI backend's base URL (e.g., `http://localhost:8000/api` or your deployed backend URL).
-   **Usage:** Set as an environment variable. ChatKit will use this as the base for requests like `/chatkit/session` or `/chatkit/threads/{id}/messages`.

### 3. Authentication Integration (`/api/chat/session` endpoint)
-   **Purpose:** To securely establish a ChatKit session for an authenticated user. ChatKit often calls a backend endpoint to get its initial configuration or session token.
-   **Backend Endpoint:** Your FastAPI backend will expose an endpoint (e.g., `POST /api/chat/session` as scaffolded by `generate_chat_endpoint.py`) that:
    1.  Authenticates the incoming request (e.g., using a JWT from the frontend).
    2.  Extracts the `user_id` from the authenticated session.
    3.  Returns a JSON response containing necessary session information for ChatKit, ensuring user isolation.

    ```python
    # Simplified backend endpoint (see scripts/generate_chat_endpoint.py)
    from fastapi import APIRouter, Depends, Request, HTTPException

    @router.post("/session")
    async def chatkit_session_endpoint(request: Request):
        user_id = request.state.user_id # From auth middleware
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        return {
            "session_id": f"chatkit-session-{user_id}",
            "user_id": user_id,
            "//": "Add ChatKit specific config here based on user_id"
        }
    ```

### 4. Customizing the Chat Interface

ChatKit is highly customizable through its client-side JavaScript configuration and CSS.

*   **Initial Configuration (on Frontend):**
    You typically initialize ChatKit by loading its script and providing a configuration object. This might happen in a component like `frontend/components/chat/ChatInterface.tsx`.

    ```typescript
    // frontend/components/chat/ChatInterface.tsx (simplified)
    import { useEffect, useRef } from 'react';
    import { useSession } from '@/lib/auth/client'; // Your Better Auth session

    declare global {
      interface Window {
        OpenAIChatKit: any;
      }
    }

    const ChatInterface = () => {
      const { data: session } = useSession();
      const chatContainerRef = useRef<HTMLDivElement>(null);

      useEffect(() => {
        if (session && chatContainerRef.current && window.OpenAIChatKit) {
          const chatkit = new window.OpenAIChatKit({
            element: chatContainerRef.current,
            apiEndpoint: process.env.NEXT_PUBLIC_CHATKIT_API_ENDPOINT,
            // Configure how ChatKit gets its session (e.g., by calling your backend)
            getSession: async () => {
              const response = await fetch(`${process.env.NEXT_PUBLIC_CHATKIT_API_ENDPOINT}/chat/session`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('api_token')}`, // Use your stored JWT
                  'Content-Type': 'application/json',
                },
              });
              if (!response.ok) {
                throw new Error('Failed to get ChatKit session');
              }
              return response.json(); // This should return { session_id, user_id, config }
            },
            // Other customization options
            // theme: 'dark',
            // avatar: { src: '/my-avatar.png' },
            // ...
          });
          chatkit.render(); // Render the chat interface
        }
      }, [session]);

      if (!session) {
        return <p>Please log in to chat.</p>;
      }

      return <div ref={chatContainerRef} style={{ height: '600px', width: '100%' }} />;
    };

    export default ChatInterface;
    ```

*   **Styling with CSS Variables:** ChatKit often exposes CSS variables that you can override to match your application's theme.
    ```css
    /* Example in globals.css */
    :root {
      --chatkit-primary-color: #3b82f6; /* Your app's primary blue */
      --chatkit-background-color: #f9fafb;
      --chatkit-text-color: #1f2937;
      /* ... other ChatKit variables */
    }
    ```

*   **Custom Components/Overrides:** Some advanced ChatKit setups might allow for custom React components to override default UI elements. Consult the official ChatKit documentation for these advanced features.

## Security Considerations

*   **Token Handling:** Ensure JWT tokens passed to your backend (for the ChatKit session endpoint) are handled securely (e.g., `httpOnly` cookies).
*   **Domain Whitelisting:** Remember to add your deployed frontend URL to the OpenAI platform's allowlist for ChatKit to function correctly in production.
*   **Environment Variables:** Never hardcode API keys or secrets in your frontend code. Use environment variables.

## Further Reading

Refer to the official OpenAI ChatKit documentation for the most up-to-date and comprehensive configuration options.
