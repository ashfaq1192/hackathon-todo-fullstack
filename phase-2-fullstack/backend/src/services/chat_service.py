"""Chat service with OpenAI Swarm Agent and Gemini backend.

This service implements the HYBRID architecture:
- OpenAI Agents SDK (Swarm framework) for agent orchestration
- Google Gemini API (free tier) as the LLM backend
- MCP tools registered as Python functions with Swarm Agent
- Stateless design with database-backed conversation state
- Circuit breaker and retry logic for resilience (T061)
- Intent-based fallback when Gemini function calling fails
"""

import json
import logging
import re
from functools import partial
from typing import Any

from sqlmodel import Session
from swarm import Agent, Swarm

from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.update_task import update_task
from src.mcp.tools.delete_task import delete_task
from src.services.context_service import ContextService
from src.services.gemini_client import get_gemini_client
from src.middleware.circuit_breaker import get_circuit_breaker, CircuitBreakerError
from src.utils.retry import with_exponential_backoff_sync, RetryableError

logger = logging.getLogger(__name__)

# Thread-local storage for capturing tool results
# This allows us to retrieve tool results when Gemini fails to process them
_last_tool_result: dict | None = None


class ChatService:
    """Service for processing chat messages with Swarm Agent.

    This service:
    - Initializes Swarm Agent with MCP tools
    - Processes user messages through Gemini-backed Swarm client
    - Manages conversation context with sliding window
    - Returns assistant responses and handles tool calls
    """

    def __init__(self, db: Session):
        """Initialize chat service with database session.

        Args:
            db: SQLModel database session for MCP tools
        """
        self.db = db
        self.context_service = ContextService(db)

        # Get Gemini client configured with OpenAI-compatible endpoint
        gemini_client = get_gemini_client()
        self.client = gemini_client.get_client()
        self.model = gemini_client.model

        # Initialize Swarm with Gemini-backed AsyncOpenAI client
        self.swarm_client = Swarm(client=self.client)

    def _create_agent_for_user(self, user_id: str) -> Agent:
        """Create a Swarm Agent with user-specific wrapper functions.

        The user_id is bound into the wrapper functions so the agent
        doesn't need to ask for it or guess it.

        Args:
            user_id: Authenticated user ID from JWT token

        Returns:
            Agent: Configured Swarm Agent with user-bound tools
        """
        global _last_tool_result
        db = self.db

        # Create wrapper functions with user_id pre-bound
        # These wrappers also capture tool results for fallback when Gemini fails
        def add_task_wrapper(title: str, description: str = "", priority: str = "medium"):
            """Add a new task for the authenticated user."""
            global _last_tool_result
            kwargs = {"user_id": user_id, "title": title, "priority": priority, "db": db}
            if description:
                kwargs["description"] = description
            result = add_task(**kwargs)
            _last_tool_result = result
            return result

        def list_tasks_wrapper(status: str = "all"):
            """List tasks for the authenticated user. Returns task list with IDs."""
            global _last_tool_result
            result = list_tasks(user_id=user_id, status=status, db=db)
            _last_tool_result = result
            return result

        def complete_task_wrapper(task_id: int):
            """Mark a task as complete for the authenticated user."""
            global _last_tool_result
            result = complete_task(user_id=user_id, task_id=task_id, db=db)
            _last_tool_result = result
            return result

        def update_task_wrapper(task_id: int, title: str = "", description: str = "", priority: str = ""):
            """Update a task for the authenticated user."""
            global _last_tool_result
            kwargs = {"user_id": user_id, "task_id": task_id, "db": db}
            if title:
                kwargs["title"] = title
            if description:
                kwargs["description"] = description
            if priority:
                kwargs["priority"] = priority
            result = update_task(**kwargs)
            _last_tool_result = result
            return result

        def delete_task_wrapper(task_id: int):
            """Delete a task for the authenticated user."""
            global _last_tool_result
            result = delete_task(user_id=user_id, task_id=task_id, db=db)
            _last_tool_result = result
            return result

        # Create Swarm Agent with MCP tools (user_id pre-bound)
        # T049-T050: Enhanced multilingual support for English and Urdu
        return Agent(
            name="Todo Assistant",
            model=self.model,
            instructions=f"""You are a helpful todo assistant that manages tasks via natural language.

**IMPORTANT**: You are serving the authenticated user. Their user_id is already known and bound to all tools.
DO NOT ask for user_id - it is automatically handled. Just use the tools directly.

**Your Role**:
- Help users add, view, update, complete, and delete tasks
- **IMPORTANT**: Auto-detect the user's language (English or Urdu) and respond in the SAME language
- Use the provided tools to perform task operations
- Always confirm actions clearly with friendly, concise responses
- Use emojis appropriately to make interactions engaging (✅ ❌ 📝 🗑️ etc.)

**CRITICAL - Task ID Handling**:
- Tasks have unique database IDs (like 15, 27, 42, etc.)
- When user says "task #1" or "task 1", they might mean the FIRST task in their list, NOT database ID 1
- ALWAYS call list_tasks_wrapper() FIRST to see the actual task IDs before completing/updating/deleting
- Show users their tasks with IDs so they know which ID to use
- Example: If user says "complete task 1", first list tasks to find the correct ID

**Multi-Language Support (Phase III - Urdu +100 Bonus)**:
- Detect if user writes in Urdu script (e.g., "ایک کام شامل کریں")
- Respond fully in Urdu when user writes in Urdu
- Common Urdu task commands to recognize:
  - "کام شامل کریں" / "نیا کام بنائیں" = Add task
  - "کام دکھائیں" / "میرے کام" = Show tasks
  - "کام مکمل کریں" = Complete task
  - "کام تبدیل کریں" / "کام اپڈیٹ کریں" = Update task
  - "کام حذف کریں" / "کام ہٹائیں" = Delete task
- Example Urdu responses:
  - "✅ کام 'دودھ خریدنا' کامیابی سے شامل ہو گیا!"
  - "📋 آپ کے کام:"
  - "✅ کام مکمل ہو گیا!"

**Tool Usage** (user_id is automatically provided - just call with required params):
- add_task_wrapper(title, description?, priority?): Create new tasks
- list_tasks_wrapper(status?): Show tasks (status: all/pending/completed) - CALL THIS FIRST to get task IDs
- complete_task_wrapper(task_id): Mark task as complete (use actual database ID from list)
- update_task_wrapper(task_id, title?, description?, priority?): Update task
- delete_task_wrapper(task_id): Delete task

**Response Style**:
- Be concise and friendly
- Match the user's language in your response
- When listing tasks, format them clearly in markdown with IDs visible:
  📋 **Your Tasks:**
  - ⏳ [ID: 15] Buy groceries (medium)
  - ✅ [ID: 27] Call mom (high) - Completed
- Confirm what you did after using a tool
- If something fails, explain why and suggest alternatives
- NEVER reveal internal error messages or database details""",
            functions=[
                add_task_wrapper,       # Phase 3, User Story 1 (T015)
                list_tasks_wrapper,     # Phase 4, User Story 2 (T021)
                complete_task_wrapper,  # Phase 5, User Story 3 (T025)
                update_task_wrapper,    # Phase 6, User Story 4 (T029)
                delete_task_wrapper,    # Phase 7, User Story 5 (T033)
            ]
        )

    def process_message(
        self,
        user_message: str,
        conversation_id: int | None,
        user_id: str,
    ) -> dict[str, Any]:
        """Process user message through Swarm Agent.

        Args:
            user_message: User's natural language input
            conversation_id: Optional conversation ID for context retrieval
            user_id: Authenticated user ID from JWT token

        Returns:
            dict: Response with assistant message and metadata
                {
                    "success": bool,
                    "message": str,  # Assistant's response
                    "conversation_id": int,
                    "tool_calls": list,  # Tools that were executed
                }
        """
        # FAST PATH: Handle greetings and simple messages without calling Gemini API
        greeting_response = self._handle_simple_message(user_message)
        if greeting_response:
            return {
                "success": True,
                "message": greeting_response,
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

        # FAST PATH: Detect task-related intent and execute directly
        # This bypasses Gemini entirely for known task operations
        intent, params = self._detect_intent(user_message)
        if intent != "unknown":
            logger.info(f"Direct intent execution: {intent} with params {params}")
            fallback_result = self._execute_fallback_tool(intent, params, user_id)
            if fallback_result:
                return self._format_tool_result(fallback_result, conversation_id)

        # Get conversation context if conversation_id provided
        messages = []
        if conversation_id:
            messages = self.context_service.get_context_messages(
                conversation_id=conversation_id, include_summary=True
            )

        # Append user message
        messages.append({"role": "user", "content": user_message})

        # Create agent with user_id pre-bound to all tools
        # This ensures the agent uses the correct user for all operations
        todo_agent = self._create_agent_for_user(user_id)

        try:
            # T061: Use circuit breaker for Gemini API resilience
            circuit_breaker = get_circuit_breaker()

            # Define the Swarm call to be wrapped by circuit breaker
            def run_swarm():
                return self.swarm_client.run(
                    agent=todo_agent, messages=messages
                )

            # Execute with circuit breaker protection
            try:
                response = circuit_breaker.call(run_swarm)

                # Check if list_tasks was called and format the output
                list_tasks_result = None
                for msg in response.messages:
                    tool_name = msg.get("name", "") if isinstance(msg, dict) else ""
                    if msg.get("role") == "tool" and tool_name == "list_tasks_wrapper":
                        try:
                            # The content of the tool message is a JSON string
                            content = msg.get("content")
                            if isinstance(content, str):
                                list_tasks_result = json.loads(content)
                            elif isinstance(content, dict):
                                list_tasks_result = content
                        except (json.JSONDecodeError, TypeError):
                            pass  # Ignore if content is not a valid JSON string

                if list_tasks_result:
                    formatted_response = self._format_tool_result(list_tasks_result, conversation_id)
                    assistant_message = formatted_response["message"]
                else:
                    # Extract assistant message if list_tasks was not called or failed to parse
                    assistant_message = response.messages[-1]["content"] if response.messages else ""

                # Track which tools were called
                tool_calls = []
                for msg in response.messages:
                    if msg.get("role") == "tool":
                        tool_calls.append(msg.get("tool_call_id", "unknown"))

                logger.info(f"Chat processed successfully. Tools called: {tool_calls}")

                return {
                    "success": True,
                    "message": assistant_message,
                    "conversation_id": conversation_id,
                    "tool_calls": tool_calls,
                }

            except CircuitBreakerError as cb_error:
                logger.warning(f"Circuit breaker open: {cb_error}")
                return {
                    "success": False,
                    "message": "The AI service is temporarily unavailable due to high load. Please try again in a minute.",
                    "conversation_id": conversation_id,
                    "error": "circuit_breaker_open",
                }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error processing message: {error_str}")

            # Handle rate limit errors
            if "429" in error_str or "rate" in error_str.lower() or "quota" in error_str.lower():
                logger.warning("Gemini API rate limit hit - using fallback")
                # Check if tool was executed before rate limit
                if _last_tool_result and isinstance(_last_tool_result, dict):
                    return self._format_tool_result(_last_tool_result, conversation_id)

                # Try intent-based fallback
                intent, params = self._detect_intent(user_message)
                if intent != "unknown":
                    fallback_result = self._execute_fallback_tool(intent, params, user_id)
                    if fallback_result:
                        return self._format_tool_result(fallback_result, conversation_id)

                return {
                    "success": False,
                    "message": "The AI service is temporarily busy. Please wait a moment and try again.",
                    "conversation_id": conversation_id,
                    "error": "rate_limit",
                }

            # Handle Gemini tool result compatibility error (400 errors)
            # When Gemini rejects the tool result format, we can still return the tool output
            if "400" in error_str:
                logger.warning("Gemini tool result compatibility issue - using captured tool result or fallback")

                # First check if we have a captured tool result
                if _last_tool_result and isinstance(_last_tool_result, dict):
                    return self._format_tool_result(_last_tool_result, conversation_id)

                # Fallback: detect intent and execute tool directly
                logger.info(f"No captured tool result, using intent-based fallback for: {user_message}")
                intent, params = self._detect_intent(user_message)
                logger.info(f"Detected intent: {intent}, params: {params}")

                if intent != "unknown":
                    fallback_result = self._execute_fallback_tool(intent, params, user_id)
                    if fallback_result:
                        return self._format_tool_result(fallback_result, conversation_id)

                # If no intent detected, provide helpful message
                return {
                    "success": True,
                    "message": "I'm having trouble understanding your request. Try one of these:\n"
                              "- 📋 'Show my tasks' or 'List tasks'\n"
                              "- ➕ 'Add task: Buy groceries'\n"
                              "- ✅ 'Complete task #1'\n"
                              "- 🗑️ 'Delete task #2'",
                    "conversation_id": conversation_id,
                    "tool_calls": [],
                }

            return {
                "success": False,
                "message": "Sorry, I encountered an error processing your request. Please try again.",
                "conversation_id": conversation_id,
                "error": error_str,
            }

    def _format_tool_result(self, tool_result: dict, conversation_id: int | None) -> dict:
        """Format a tool result for response.

        Args:
            tool_result: The captured tool result dictionary
            conversation_id: Conversation ID

        Returns:
            dict: Formatted response with tool result message
        """
        tool_message = tool_result.get("message", "")

        # Format task list nicely if present
        if "tasks" in tool_result and tool_result.get("tasks"):
            tasks = tool_result["tasks"]
            lines = ["📋 **Your Tasks:**\n"]
            for task in tasks:
                status_emoji = "✅" if task.get("complete") else "⏳"
                priority = task.get("priority", "medium")
                title = task.get("title", "Untitled")
                task_id = task.get("id", "?")
                completed_text = " - Completed" if task.get("complete") else ""
                lines.append(f"- {status_emoji} **[ID: {task_id}]** {title} ({priority}){completed_text}")
            tool_message = "\n".join(lines)

        if tool_message:
            return {
                "success": True,
                "message": tool_message,
                "conversation_id": conversation_id,
                "tool_calls": ["(tool executed)"],
            }

        return {
            "success": True,
            "message": "Your request has been processed. Please check your task list for updates.",
            "conversation_id": conversation_id,
            "tool_calls": ["(tool executed)"],
        }

    def _handle_simple_message(self, message: str) -> str | None:
        """Handle simple messages like greetings without calling Gemini API.

        This provides instant responses for common greetings and help requests,
        avoiding the latency and potential failures of the Gemini API call.

        Args:
            message: User's message

        Returns:
            str or None: Response string if message is handled, None otherwise
        """
        msg_lower = message.lower().strip()

        # Greetings (English) - exact match or word boundary to avoid false positives
        greetings_exact = ["hi", "hello", "hey", "hii", "hiii", "yo", "sup", "hola", "howdy"]
        if msg_lower in greetings_exact or msg_lower.startswith(("hi ", "hello ", "hey ")):
            return "Hello! How can I help you with your tasks today? 📝\n\nYou can say things like:\n- 📋 'Show my tasks'\n- ➕ 'Add task: Buy groceries'\n- ✅ 'Complete task #1'\n- 🗑️ 'Delete task #2'"

        # Urdu greetings
        urdu_greetings = ["سلام", "السلام علیکم", "ہیلو", "کیسے ہو"]
        for greeting in urdu_greetings:
            if greeting in message:
                return "السلام علیکم! 📝 میں آپ کے کاموں میں کیسے مدد کر سکتا ہوں؟\n\nآپ کہہ سکتے ہیں:\n- 📋 'میرے کام دکھائیں'\n- ➕ 'کام شامل کریں: دودھ خریدنا'\n- ✅ 'کام 1 مکمل کریں'"

        # Help requests
        help_patterns = ["help", "what can you do", "how do i", "what do you do", "?"]
        for pattern in help_patterns:
            if pattern in msg_lower:
                return "I'm your Todo Assistant! 📝 I can help you manage your tasks.\n\n**Available Commands:**\n- 📋 **List tasks**: 'Show my tasks', 'List pending tasks'\n- ➕ **Add task**: 'Add task: Buy groceries'\n- ✅ **Complete task**: 'Complete task #1', 'Mark task 3 as done'\n- ✏️ **Update task**: 'Update task #2 title to New Title'\n- 🗑️ **Delete task**: 'Delete task #4'\n\nJust tell me what you'd like to do!"

        # Thanks - use word boundary matching to avoid false positives (e.g., "ty" in "priority")
        thanks_patterns = [r"\bthanks\b", r"\bthank you\b", r"\bthx\b", r"\bty\b", r"\bappreciate\b"]
        for pattern in thanks_patterns:
            if re.search(pattern, msg_lower):
                return "You're welcome! 😊 Let me know if you need anything else with your tasks."

        # Goodbye - use word boundary matching
        bye_patterns = [r"\bbye\b", r"\bgoodbye\b", r"\bsee you\b", r"\bexit\b", r"\bquit\b"]
        for pattern in bye_patterns:
            if re.search(pattern, msg_lower):
                return "Goodbye! 👋 Have a productive day!"

        return None

    def _detect_intent(self, message: str) -> tuple[str, dict]:
        """Detect user intent from message for fallback tool execution.

        This method parses the user's natural language message to determine
        which tool to call when Gemini's function calling fails.

        Args:
            message: User's natural language message

        Returns:
            tuple: (intent_name, extracted_params)
                intent_name: 'list_tasks', 'complete_task', 'add_task',
                            'update_task', 'delete_task', or 'unknown'
                extracted_params: Dict of parameters extracted from message
        """
        msg_lower = message.lower().strip()

        # List tasks patterns (English and Urdu)
        list_patterns = [
            r"list.*task", r"show.*task", r"my task", r"view.*task",
            r"get.*task", r"what.*task", r"pending task", r"all task",
            r"task list", r"tasks?$", r"give.*task",
            # Urdu patterns
            r"کام دکھائیں", r"میرے کام", r"کاموں کی فہرست",
        ]
        for pattern in list_patterns:
            if re.search(pattern, msg_lower):
                # Check for status filter
                status = "all"
                if "pending" in msg_lower or "active" in msg_lower:
                    status = "pending"
                elif "completed" in msg_lower or "done" in msg_lower or "finished" in msg_lower:
                    status = "completed"
                return ("list_tasks", {"status": status})

        # Complete task patterns
        complete_patterns = [
            r"complete.*task", r"mark.*complete", r"mark.*done",
            r"finish.*task", r"done.*task", r"check.*off",
            r"task.*complete", r"task.*done", r"task.*finish",
            # Urdu
            r"کام مکمل", r"ختم کریں",
        ]
        for pattern in complete_patterns:
            if re.search(pattern, msg_lower):
                task_id = self._extract_task_id(message)
                if task_id:
                    return ("complete_task", {"task_id": task_id})
                return ("complete_task", {"task_id": None})

        # Delete task patterns
        delete_patterns = [
            r"delete.*task", r"remove.*task", r"cancel.*task",
            r"task.*delete", r"task.*remove",
            # Urdu
            r"کام حذف", r"کام ہٹائیں",
        ]
        for pattern in delete_patterns:
            if re.search(pattern, msg_lower):
                task_id = self._extract_task_id(message)
                if task_id:
                    return ("delete_task", {"task_id": task_id})
                return ("delete_task", {"task_id": None})

        # Add task patterns
        add_patterns = [
            r"add.*task", r"create.*task", r"new task", r"make.*task",
            r"task.*add", r"remind.*to",
            # Urdu
            r"کام شامل", r"نیا کام",
        ]
        for pattern in add_patterns:
            if re.search(pattern, msg_lower):
                # Extract title and priority from message
                title, priority = self._extract_add_task_params(message)
                params = {"title": title}
                if priority:
                    params["priority"] = priority
                return ("add_task", params)

        # Update task patterns - Enhanced to extract new values
        update_patterns = [
            r"update.*task", r"edit.*task", r"change.*task", r"modify.*task",
            r"rename.*task", r"change.*title", r"update.*title",
            # Urdu
            r"کام تبدیل", r"کام اپڈیٹ",
        ]
        for pattern in update_patterns:
            if re.search(pattern, msg_lower):
                task_id = self._extract_task_id(message)
                # Extract what to update (title, description, priority)
                update_params = self._extract_update_params(message)
                return ("update_task", {"task_id": task_id, **update_params})

        return ("unknown", {})

    def _extract_task_id(self, message: str) -> int | None:
        """Extract task ID from message.

        Handles formats like:
        - "task #1", "task 1", "task number 1"
        - "#1", "ID 1", "ID: 1"
        - "first task", "1st task" (ordinal references)

        Args:
            message: User's message

        Returns:
            int or None: Extracted task ID or None if not found
        """
        msg_lower = message.lower()

        # Direct ID patterns: task #1, task 1, #1, ID 1, ID: 1
        patterns = [
            r"task\s*#?\s*(\d+)",
            r"#(\d+)",
            r"id[:\s]*(\d+)",
            r"number\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                return int(match.group(1))

        # Ordinal patterns: first task, 1st task, second task, etc.
        ordinals = {
            "first": 1, "1st": 1,
            "second": 2, "2nd": 2,
            "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4,
            "fifth": 5, "5th": 5,
        }
        for word, num in ordinals.items():
            if word in msg_lower:
                # This is a positional reference, not a database ID
                # We'll need to resolve it to actual task ID
                return num  # Return ordinal number to be resolved later

        return None

    def _extract_add_task_params(self, message: str) -> tuple[str, str | None]:
        """Extract task title and priority from add task message.

        Handles patterns like:
        - "add a new task with title 'Call to Mom' with priority High"
        - "add task: Buy groceries"
        - "create a task called 'Finish report' priority low"
        - "add task Buy milk"

        Args:
            message: User's message

        Returns:
            tuple: (title, priority) where priority may be None
        """
        msg_lower = message.lower()
        title = None
        priority = None

        # Extract priority first (high, medium, low)
        priority_match = re.search(r'\b(?:priority\s+)?(high|medium|low)\b', msg_lower)
        if priority_match:
            priority = priority_match.group(1)

        # Try to extract title from various patterns

        # Pattern 1: "with title 'X'" or "title 'X'" or "titled 'X'" or "called 'X'"
        title_patterns = [
            r"(?:with\s+)?title\s+[\"']([^\"']+)[\"']",
            r"(?:with\s+)?title\s+[\"']?([^\"']+?)[\"']?\s*(?:with\s+priority|priority|$)",
            r"titled\s+[\"']([^\"']+)[\"']",
            r"called\s+[\"']([^\"']+)[\"']",
        ]
        for pattern in title_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                break

        # Pattern 2: Quoted text anywhere (fallback)
        if not title:
            quoted_match = re.search(r'[\"\'](.*?)["\']', message)
            if quoted_match:
                title = quoted_match.group(1).strip()

        # Pattern 3: After colon - "add task: Buy groceries"
        if not title:
            colon_match = re.search(r'task\s*:\s*(.+?)(?:\s+(?:with\s+)?priority|\s*$)', message, re.IGNORECASE)
            if colon_match:
                title = colon_match.group(1).strip().strip('"\'')

        # Pattern 4: Simple extraction - remove common prefixes
        if not title:
            prefixes = [
                r"add\s+(?:a\s+)?(?:new\s+)?task\s+(?:to\s+)?",
                r"create\s+(?:a\s+)?(?:new\s+)?task\s+(?:to\s+)?",
                r"new\s+task\s*:?\s*",
                r"remind\s+me\s+to\s+",
            ]
            title = message
            for prefix in prefixes:
                title = re.sub(prefix, "", title, flags=re.IGNORECASE)
            # Remove priority part from title
            title = re.sub(r'\s*(?:with\s+)?priority\s+(?:high|medium|low)\s*', '', title, flags=re.IGNORECASE)
            title = title.strip().strip('"\'')

        return (title if title else "New Task", priority)

    def _extract_task_title(self, message: str) -> str:
        """Extract task title from add task message (legacy method).

        Args:
            message: User's message

        Returns:
            str: Extracted task title
        """
        title, _ = self._extract_add_task_params(message)
        return title

    def _extract_update_params(self, message: str) -> dict:
        """Extract update parameters (title, description, priority) from message.

        Handles patterns like:
        - "Update task #31 title to 'New Title'"
        - "Change title to New Title"
        - "Rename task 5 from 'Old' to 'New'"
        - "Update task 2 priority to high"
        - "Change description of task 3 to 'New description'"

        Args:
            message: User's message

        Returns:
            dict: Extracted parameters {title, description, priority}
        """
        params = {}
        msg_lower = message.lower()

        # Extract new title - various patterns
        title_patterns = [
            # "title to 'New Title'" or "title to New Title"
            r"title\s+(?:to|as|=)\s*[\"']?([^\"'\n]+?)[\"']?\s*$",
            # "rename ... to 'New Title'" or "change ... to 'New Title'"
            r"(?:rename|change)\s+.*?\s+to\s+[\"']([^\"']+)[\"']",
            # "from 'Old' to 'New'"
            r"from\s+[\"'][^\"']+[\"']\s+to\s+[\"']([^\"']+)[\"']",
            # Fallback: capture quoted string after "to"
            r"\bto\s+[\"']([^\"']+)[\"']",
            # Fallback: "title as 'Something'"
            r"title\s+as\s+[\"']?([^\"'\n]+?)[\"']?\s*$",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params["title"] = match.group(1).strip()
                break

        # If we detect "title" keyword but didn't extract, try simpler extraction
        if not params.get("title") and ("title" in msg_lower or "rename" in msg_lower):
            # Look for quoted string anywhere in message
            quoted_match = re.search(r'[\"\'](.*?)[\"\']', message)
            if quoted_match:
                params["title"] = quoted_match.group(1).strip()

        # Extract priority
        priority_patterns = [
            r"priority\s+(?:to|as|=)\s*(low|medium|high)",
            r"set\s+priority\s+(?:to\s+)?(low|medium|high)",
            r"(low|medium|high)\s+priority",
        ]
        for pattern in priority_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                params["priority"] = match.group(1)
                break

        # Extract description
        desc_patterns = [
            r"description\s+(?:to|as|=)\s*[\"']?([^\"'\n]+?)[\"']?\s*$",
            r"desc\s+(?:to|as|=)\s*[\"']?([^\"'\n]+?)[\"']?\s*$",
        ]
        for pattern in desc_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params["description"] = match.group(1).strip()
                break

        return params

    def _execute_fallback_tool(
        self, intent: str, params: dict, user_id: str
    ) -> dict | None:
        """Execute tool directly based on detected intent.

        This is the fallback mechanism when Gemini's function calling fails.

        Args:
            intent: Detected intent name
            params: Extracted parameters
            user_id: Authenticated user ID

        Returns:
            dict or None: Tool result or None if execution failed
        """
        try:
            if intent == "list_tasks":
                status = params.get("status", "all")
                result = list_tasks(user_id=user_id, status=status, db=self.db)
                logger.info(f"Fallback list_tasks executed: {result.get('count', 0)} tasks")
                return result

            elif intent == "complete_task":
                task_id = params.get("task_id")
                if task_id is None:
                    return {
                        "success": False,
                        "message": "I couldn't determine which task to complete. Please specify the task ID, like 'complete task #1' or 'mark task 5 as done'.",
                    }

                # Check if this is a positional reference (small number might be ordinal)
                # First, get the task list to resolve positional references
                tasks_result = list_tasks(user_id=user_id, status="all", db=self.db)
                if tasks_result.get("success") and tasks_result.get("tasks"):
                    tasks = tasks_result["tasks"]

                    # If task_id is small (1-5), it might be a positional reference
                    # Check if it exists as actual task ID first
                    task_ids = [t["id"] for t in tasks]
                    if task_id in task_ids:
                        # Direct ID match - use it
                        result = complete_task(user_id=user_id, task_id=task_id, db=self.db)
                    elif task_id <= len(tasks):
                        # Treat as positional (1st, 2nd, etc.)
                        actual_task = tasks[task_id - 1]
                        actual_id = actual_task["id"]
                        result = complete_task(user_id=user_id, task_id=actual_id, db=self.db)
                        # Update message to clarify
                        if result.get("success"):
                            result["message"] = f"✅ Task '{actual_task['title']}' (ID: {actual_id}) marked as complete!"
                    else:
                        return {
                            "success": False,
                            "message": f"Task #{task_id} not found. You have {len(tasks)} tasks. Use 'list my tasks' to see them with their IDs.",
                        }
                else:
                    # Try direct ID
                    result = complete_task(user_id=user_id, task_id=task_id, db=self.db)

                logger.info(f"Fallback complete_task executed: task_id={task_id}")
                return result

            elif intent == "delete_task":
                task_id = params.get("task_id")
                if task_id is None:
                    return {
                        "success": False,
                        "message": "I couldn't determine which task to delete. Please specify the task ID, like 'delete task #1'.",
                    }
                result = delete_task(user_id=user_id, task_id=task_id, db=self.db)
                logger.info(f"Fallback delete_task executed: task_id={task_id}")
                return result

            elif intent == "add_task":
                title = params.get("title", "New Task")
                priority = params.get("priority", "medium")
                result = add_task(user_id=user_id, title=title, priority=priority, db=self.db)
                logger.info(f"Fallback add_task executed: title={title}, priority={priority}")
                return result

            elif intent == "update_task":
                task_id = params.get("task_id")
                if task_id is None:
                    return {
                        "success": False,
                        "message": "I couldn't determine which task to update. Please specify the task ID, like 'update task #1 title to New Title'.",
                    }

                # Check if we have any update values
                new_title = params.get("title")
                new_description = params.get("description")
                new_priority = params.get("priority")

                if not new_title and not new_description and not new_priority:
                    return {
                        "success": False,
                        "message": f"To update task #{task_id}, please tell me what you'd like to change. For example:\n"
                                  f"- 'Update task #{task_id} title to New Title'\n"
                                  f"- 'Change task #{task_id} priority to high'\n"
                                  f"- 'Set task #{task_id} description to New description'",
                    }

                # Perform the actual update
                update_kwargs = {"user_id": user_id, "task_id": task_id, "db": self.db}
                if new_title:
                    update_kwargs["title"] = new_title
                if new_description:
                    update_kwargs["description"] = new_description
                if new_priority:
                    update_kwargs["priority"] = new_priority

                result = update_task(**update_kwargs)
                logger.info(f"Fallback update_task executed: task_id={task_id}, title={new_title}, desc={new_description}, priority={new_priority}")

                # Enhance the success message
                if result.get("success"):
                    changes = []
                    if new_title:
                        changes.append(f"title to '{new_title}'")
                    if new_description:
                        changes.append(f"description to '{new_description}'")
                    if new_priority:
                        changes.append(f"priority to '{new_priority}'")
                    result["message"] = f"✅ Task #{task_id} updated! Changed {', '.join(changes)}."

                return result

            return None

        except Exception as e:
            logger.error(f"Fallback tool execution failed: {e}")
            return None


def get_chat_service(db: Session) -> ChatService:
    """Factory function to create ChatService instance.

    Args:
        db: SQLModel database session

    Returns:
        ChatService: Initialized chat service
    """
    return ChatService(db)
