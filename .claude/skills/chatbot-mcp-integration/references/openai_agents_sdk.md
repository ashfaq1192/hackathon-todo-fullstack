# OpenAI Agents SDK: Key Concepts and Usage

The OpenAI Agents SDK provides a framework for building AI agents that can interact with external tools and services. In our MCP-based chatbot, it acts as the intelligent orchestrator, understanding user intent and invoking the appropriate MCP tools.

## Core Components

### 1. Agent
-   **Role:** The central component that reasons about user requests and decides on actions.
-   **Functionality:**
    *   **Tool Calling:** The ability to understand when to use a tool and with what parameters.
    *   **Conversational Flow Management:** Maintains the dialogue, processes tool outputs, and generates natural language responses.
-   **Configuration:** Configured with a language model (e.g., GPT-4, GPT-3.5) and a list of available tools (our MCP tools).

### 2. Tools
-   **Role:** External functions or services that the Agent can call to perform specific actions.
-   **Integration:** In our setup, these are our **MCP Tools**. The Agents SDK is configured with the schemas of these MCP tools, allowing the agent to understand their capabilities.
-   **Invocation:** When the Agent decides to use a tool, it generates a `tool_call` request, which is then executed by our backend.

### 3. Orchestration Logic
-   **Role:** The glue that connects the user's message, the Agent, the MCP tools, and the database.
-   **Flow:**
    1.  User sends a message.
    2.  The orchestration logic (e.g., in `ChatService`) receives the message and retrieves conversation history.
    3.  It constructs a prompt for the Agent, including the message and available tools.
    4.  The Agent processes the prompt:
        *   If it needs to invoke a tool, it returns a `tool_call` object.
        *   If it can respond directly, it returns a `message` object.
    5.  If a `tool_call` is returned:
        *   The orchestration logic executes the corresponding MCP tool.
        *   The tool's output is fed back to the Agent as a `tool_response`.
        *   The Agent then processes the `tool_response` and generates a natural language `message`.
    6.  The final `message` (or `tool_call` result) is sent back to the user.

## Usage in Our Chatbot

In our `phase-3-chatbot/backend/src/services/chat_service.py`, the `ChatService` class encapsulates the OpenAI Agents SDK integration.

```python
# Simplified example from chat_service.py
from openai import OpenAI
from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.runs import ToolCall

class ChatService:
    def __init__(self, session: Session, user_id: str):
        self.client = OpenAI()
        self.thread = self.client.beta.threads.create() # Or retrieve existing thread
        self.tools = self._get_mcp_tools() # Load MCP tools and their schemas

    async def process_message(self, user_message: str) -> str:
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message,
        )

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id="YOUR_ASSISTANT_ID", # Pre-configured Assistant with tools
            tools=self.tools # Ensure tools are passed to the run
        )

        # Poll the run status until complete or requires action
        while run.status == "running" or run.status == "queued":
            await asyncio.sleep(0.5)
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            # Extract last assistant message
            for msg in messages.data:
                if msg.role == "assistant":
                    if isinstance(msg.content[0], MessageContentText):
                        return msg.content[0].text.value
            return "No response from assistant."
        elif run.status == "requires_action":
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                # Execute the MCP tool (e.g., via MCP server)
                tool_output_result = await self._execute_mcp_tool(tool_call)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(tool_output_result)
                })

            run = self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            # Continue polling or recursive call to process the new run
            return await self.process_message(user_message) # Or re-poll based on new run state
        else:
            return f"Run failed with status: {run.status}"

    def _get_mcp_tools(self):
        # Dynamically retrieve MCP tool schemas from your MCP server
        # This would typically involve an HTTP call to your FastAPI /api/mcp/tools endpoint
        return [
            {"type": "function", "function": {"name": "add_task", "description": "Adds a new task", "parameters": {...}}},
            # ... other tool schemas
        ]

    async def _execute_mcp_tool(self, tool_call: ToolCall):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        # Call your actual MCP tool implementation
        # This part would integrate with your FastAPI MCP server to invoke the tool
        # Example: response = await self.mcp_client.invoke_tool(tool_name, tool_args)
        # For simplicity, directly call the Python function here (less ideal for real-world)
        if tool_name == "add_task":
            from src.mcp.tools.add_task import add_task_fn
            return add_task_fn(session=self.session, user_id=self.user_id, **tool_args)
        # ... handle other tools
        return {"error": f"Tool {tool_name} not found or not executable."}
```

## Key Considerations

*   **Assistant vs. Run-time Tools:** Assistants can be pre-configured with tools, or tools can be provided at run-time with each `run` creation. Our implementation uses run-time tools (or a dynamic mix) to ensure the agent has the most up-to-date tool definitions from our MCP server.
*   **Conversation History:** The SDK manages message history within "Threads". Our backend ensures this thread history is linked to the user and their conversations in the database.
*   **Tool Output Processing:** The orchestration logic is responsible for executing the `tool_call` and feeding the `tool_output` back to the Agent for further reasoning.
*   **Error Handling:** Robust error handling is crucial for tool execution failures and unexpected agent responses.