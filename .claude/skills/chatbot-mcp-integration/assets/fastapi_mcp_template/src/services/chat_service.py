import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List # Added List import

from openai import OpenAI
from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.runs import ToolCall
from sqlmodel import Session, select

from src.config import settings
from src.models.conversation import Conversation
from src.models.message import Message
from src.mcp.server import get_mcp_server


class ChatService:
    """
    Manages the conversation flow, AI agent orchestration, and MCP tool invocation.
    """
    def __init__(self, session: Session, user_id: str):
        self.session = session
        self.user_id = user_id
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.mcp_server = get_mcp_server()
        self.thread_id = None # To be loaded/created per conversation

        # TODO: Configure your OpenAI Assistant ID
        self.assistant_id = "asst_YOUR_ASSISTANT_ID" # Replace with your Assistant ID

    async def _get_or_create_conversation(self) -> Conversation:
        """
        Retrieves the last active conversation for the user or creates a new one.
        """
        # For simplicity, always create a new conversation for now
        # In a real app, you'd retrieve based on user_id and perhaps a "last_active" timestamp
        conversation = Conversation(user_id=self.user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    async def _get_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Retrieves messages for a given conversation from the database.
        """
        messages = self.session.exec(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        ).all()
        return [{"role": m.role, "content": m.content} for m in messages]
    
    async def _save_message(self, conversation_id: int, role: str, content: str):
        """
        Saves a message to the database.
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=self.user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

    async def _execute_mcp_tool(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        Executes an MCP tool requested by the AI agent.
        """
        tool_name = tool_call.function.name
        tool_args_str = tool_call.function.arguments
        tool_args = json.loads(tool_args_str)
        
        # Dynamically get the tool function from the MCP server
        # This approach ensures that the tool is registered and validated by FastMCP
        tool_func = self.mcp_server.get_tool_function(tool_name)

        if not tool_func:
            return {"error": f"MCP Tool '{tool_name}' not found."}
        
        # Pass session and user_id to the tool, along with its specific arguments
        try:
            result = await tool_func(session=self.session, user_id=self.user_id, **tool_args)
            return result
        except Exception as e:
            # Log the exception for debugging
            print(f"Error executing MCP tool '{tool_name}': {e}")
            return {"error": f"Failed to execute tool '{tool_name}': {str(e)}"}


    async def process_message(self, user_message: str) -> str:
        """
        Processes a user's message through the OpenAI Agent and MCP tools.
        """
        conversation = await self._get_or_create_conversation()
        self.thread_id = conversation.id # Use conversation ID as thread ID

        await self._save_message(self.thread_id, "user", user_message)
        
        # Retrieve MCP tool schemas
        mcp_tools_schemas = [tool.model_dump(mode="json") for tool in self.mcp_server.get_tools_schemas()]

        # Add message to the OpenAI thread
        self.openai_client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=user_message,
        )

        # Create a run for the assistant
        run = self.openai_client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            tools=mcp_tools_schemas # Pass tools dynamically
        )

        # Polling loop for the run status
        while run.status == "running" or run.status == "queued":
            await asyncio.sleep(0.5) # Wait a bit before polling again
            run = self.openai_client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id) # Corrected thread_id here

        # Handle different run statuses
        if run.status == "completed":
            messages_page = self.openai_client.beta.threads.messages.list(thread_id=self.thread_id)
            assistant_message = ""
            # Iterate through messages to find the last assistant response
            for msg in messages_page.data:
                if msg.role == "assistant":
                    if isinstance(msg.content[0], MessageContentText):
                        assistant_message = msg.content[0].text.value
                        break
            
            await self._save_message(self.thread_id, "assistant", assistant_message)
            return assistant_message

        elif run.status == "requires_action":
            tool_outputs = []
            if run.required_action and run.required_action.type == "submit_tool_outputs":
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    # Execute the MCP tool and capture its output
                    tool_output_result = await self._execute_mcp_tool(tool_call)
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(tool_output_result)
                    })
            
            # Submit the tool outputs back to the assistant
            run = self.openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            
            # After submitting tool outputs, re-poll the run or recurse to get final response
            # For simplicity, we'll re-poll. In a more complex scenario, you might have a new run state.
            while run.status == "running" or run.status == "queued":
                await asyncio.sleep(0.5)
                run = self.openai_client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run.id)

            if run.status == "completed":
                messages_page = self.openai_client.beta.threads.messages.list(thread_id=self.thread_id)
                assistant_message = ""
                for msg in messages_page.data:
                    if msg.role == "assistant":
                        if isinstance(msg.content[0], MessageContentText):
                            assistant_message = msg.content[0].text.value
                            break
                await self._save_message(self.thread_id, "assistant", assistant_message)
                return assistant_message
            else:
                await self._save_message(self.thread_id, "assistant", f"Error during tool execution: {run.status}")
                return f"Error during tool execution: {run.status}"
        else:
            await self._save_message(self.thread_id, "assistant", f"Assistant run failed with status: {run.status}")
            return f"Assistant run failed with status: {run.status}"


# Global instance of ChatService (dependency injection friendly)
_chat_service_instance: Dict[str, ChatService] = {}

def get_chat_service(session: Session, user_id: str) -> ChatService:
    """
    Dependency to provide a ChatService instance per user.
    """
    # Create a new instance for each request/session
    # In a more complex app, you might cache or manage instances differently
    return ChatService(session, user_id)