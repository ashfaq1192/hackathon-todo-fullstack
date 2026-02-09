# Evolution of Todo - Phase III: AI-Powered Todo Chatbot

This document provides details for Phase III of the "Evolution of Todo" project. This phase introduces an AI-powered chatbot that allows users to manage their tasks using natural language.

## 🎯 Project Overview

Phase III represents a significant leap forward by integrating artificial intelligence into the Todo application. Users can now interact with a conversational AI to perform all task management operations. This phase demonstrates a modern, AI-native architecture using an OpenAI-compatible agent, a set of defined "tools" for the agent to use, and a conversational UI.

## 🛠️ Tech Stack

### Backend AI Integration
- **AI Framework**: OpenAI Agents SDK for orchestrating the AI agent.
- **LLM Provider**: An OpenAI-compatible API (such as Gemini) is used as the core language model.
- **MCP Tools**: The project exposes 5 function-calling tools that the AI agent can use (add, list, complete, update, delete). This is managed via the Model Context Protocol (MCP).
- **Context Management**: Conversation history is persisted in the database to maintain context across sessions.

### Frontend Chat
- **Chat UI**: The frontend uses OpenAI's ChatKit to provide a rich, conversational user interface.
- **Voice Input**: The architecture supports potential integration with the Web Speech API for voice commands.
- **Streaming**: Server-Sent Events (SSE) can be used for streaming responses from the AI agent.

## ✨ Features

- ✅ **Natural Language Task Management**: Users can manage tasks by simply talking to the chatbot (e.g., "Add a task to buy groceries").
- ✅ **Conversation History**: All conversations are saved to the database, so the chatbot remembers previous interactions.
- ✅ **MCP Tools for CRUD**: The AI agent has access to a full set of tools for all CRUD operations (Add, List, Complete, Update, Delete).
- ✅ **OpenAI ChatKit Integration**: A seamless and polished chat interface is provided on the frontend.
- ✅ **Stateless Backend Architecture**: The backend is designed to be stateless, allowing for greater scalability.
- ✅ **Secure and Authenticated**: All interactions with the chatbot are secured via JWT and are tied to the logged-in user.

### Natural Language Examples
```
- "Add a task to buy groceries"
- "Show me my pending tasks"
- "Mark task 3 as complete"
- "Delete task 5"
- "Update task 1, set description to 'Check prices'"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Next.js 16 App (React 19 + TypeScript 5)                  │ │
│  │  • OpenAI ChatKit (conversational UI)                      │ │
│  │  • Better Auth (JWT for chat API)                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI 0.115.0+ (Python 3.13+)                           │ │
│  │  • Auth Middleware (validates JWT)                         │ │
│  │  • Chat Endpoint (/api/chat)                               │ │
│  │  • MCP Server (FastMCP)                                    │ │
│  │  • OpenAI Agents SDK (orchestration)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Internal Invocation / DB Access
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MCP TOOLS / DB                             │
│  • MCP Tools (add_task, list_tasks, etc.)                       │
│  • Database (Neon PostgreSQL)                                   │
│    • Tasks, Conversations, Messages tables                      │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 20+
- `uv` Python package manager
- A free Neon account for the PostgreSQL database.
- An API key from an OpenAI-compatible service (like Gemini or OpenAI).

### Backend Setup

1.  **Navigate to the backend directory**:
    ```bash
    cd phase-3-chatbot/backend
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Configure the environment**:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file with your Neon `DATABASE_URL`, `BETTER_AUTH_SECRET`, `JWT_SECRET_KEY`, and your `OPENAI_API_KEY`.

4.  **Run database migrations**: This will create the new `Conversation` and `Message` tables required for the chatbot.
    ```bash
    python -c "from src.database import create_db_and_tables; create_db_and_tables()"
    ```

5.  **Start the backend server**:
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will be running at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd phase-3-chatbot/frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Configure the environment**:
    ```bash
    cp .env.example .env.local
    ```
    Edit the `.env.local` file with your `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`, set `NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://localhost:8000/api`, and fill in any other required authentication variables.

4.  **Start the frontend server**:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.

### Access the Chatbot

1.  Open your browser to `http://localhost:3000`.
2.  Ensure you are logged in (you can sign up or log in using the Phase II interface).
3.  Navigate to the `/chat` page.
4.  Start a conversation with the AI Chatbot!
