# Model Context Protocol (MCP) Specification Overview

The Model Context Protocol (MCP) is a specification designed to standardize how AI agents discover, describe, and invoke tools or functions exposed by backend services. It provides a structured way for AI models to interact with external systems.

## Core Concepts

### 1. Tools
-   **Definition:** Specific, stateless functions or actions that an AI agent can perform.
-   **Description:** Each tool has a schema (similar to OpenAPI/JSON Schema) that describes its name, purpose, and parameters. This schema allows the AI model to understand how and when to use the tool.
-   **Invocation:** AI agents generate requests to invoke tools with specific parameters, and the MCP server executes these tools.

### 2. MCP Server
-   **Role:** A backend service that hosts and exposes MCP tools.
-   **Functionality:**
    *   **Tool Discovery:** Provides a mechanism for AI agents to list available tools and their schemas.
    *   **Tool Invocation:** Receives requests from AI agents to execute specific tools with provided arguments.
    *   **Statelessness:** MCP tools should generally be stateless, meaning they don't retain information between invocations. Any necessary state (e.g., user sessions, conversation history) should be managed by the AI agent's orchestration layer (e.g., via database).

### 3. Agent
-   **Role:** The AI model (e.g., OpenAI Agents SDK) that consumes MCP tools.
-   **Functionality:**
    *   **Natural Language Understanding:** Interprets user's natural language requests.
    *   **Tool Selection:** Based on the user's intent, decides which MCP tool (if any) is most appropriate to use.
    *   **Parameter Extraction:** Extracts necessary parameters for the selected tool from the user's message.
    *   **Tool Invocation:** Formulates and sends a request to the MCP server to invoke the tool.
    *   **Response Handling:** Processes the output from the tool and generates a natural language response back to the user.

## Key Principles in our Implementation

*   **Stateless Tools:** Our MCP tools are designed to be stateless. Any required context (like `user_id` or `Session` for database access) is injected at runtime, not maintained by the tool itself.
*   **FastAPI Integration:** We use `FastMCP` (a library that wraps FastAPI) to easily expose our Python functions as MCP tools.
*   **AI Agent Orchestration:** The OpenAI Agents SDK is responsible for the intelligence layer: interpreting user intent, selecting the right MCP tool, and formulating the tool calls.

## Example MCP Tool Structure (Python)

```python
# In src/mcp/tools/my_tool.py
from sqlmodel import Session # Example dependency

def my_tool(
    session: Session, # Injected by FastAPI dependency
    user_id: str,     # Injected by authentication middleware
    param1: str,
    param2: int | None = None
) -> dict:
    """
    Performs a specific action based on param1 and param2 for a given user.
    This description is used by the AI agent to understand the tool's purpose.
    """
    # ... tool logic ...
    return {"result": "success", "data": "some_output"}
```

<h2>Relevant Specifications</h2>

*   **OpenAPI/JSON Schema:** Used to describe the tool parameters and responses.
*   **JSON-RPC 2.0:** Often used as the underlying communication protocol for MCP servers.

<h2>Further Reading</h2>

For a deeper dive into the Model Context Protocol, refer to its official documentation (if available) and the specific implementation details in the `chatbot-mcp-integration` skill.
