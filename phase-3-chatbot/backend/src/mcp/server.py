"""Official MCP Server for Todo Task Management.

This module implements an MCP (Model Context Protocol) server using the official
MCP SDK (github.com/modelcontextprotocol/python-sdk). It exposes 5 tools for
natural language task management:

- add_task: Create new tasks
- list_tasks: View user's tasks
- complete_task: Mark tasks as done
- update_task: Modify task details
- delete_task: Remove tasks

The server follows MCP specification and can be used with any MCP-compatible client
including OpenAI Agents SDK, Claude Desktop, and other MCP clients.

Hackathon Compliance: PDF Page 17 requires "Build MCP server with Official MCP SDK"
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from src.database import get_session
from src.mcp.tools.add_task import add_task as add_task_fn
from src.mcp.tools.list_tasks import list_tasks as list_tasks_fn
from src.mcp.tools.complete_task import complete_task as complete_task_fn
from src.mcp.tools.update_task import update_task as update_task_fn
from src.mcp.tools.delete_task import delete_task as delete_task_fn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance (high-level MCP SDK interface)
mcp = FastMCP(
    name="todo-mcp-server",
)


def get_db_session() -> Session:
    """Get database session for tool execution."""
    return next(get_session())


@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
) -> str:
    """Create a new task for the user.

    Use this tool when the user wants to add, create, or make a new task.

    Args:
        user_id: The authenticated user's ID
        title: Task title (required, max 200 characters)
        description: Optional task description (max 1000 characters)
        priority: Priority level - 'low', 'medium', or 'high' (default: medium)

    Returns:
        JSON string with task creation result including task_id and confirmation
    """
    db = get_db_session()
    try:
        result = add_task_fn(
            user_id=user_id,
            title=title,
            description=description if description else None,
            priority=priority,
            db=db,
        )
        return str(result)
    finally:
        db.close()


@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
) -> str:
    """List tasks for the user.

    Use this tool when the user wants to see, view, show, or list their tasks.

    Args:
        user_id: The authenticated user's ID
        status: Filter tasks by status - 'all', 'pending', or 'completed' (default: all)

    Returns:
        JSON string with list of tasks matching the criteria
    """
    db = get_db_session()
    try:
        result = list_tasks_fn(
            user_id=user_id,
            status=status,
            db=db,
        )
        return str(result)
    finally:
        db.close()


@mcp.tool()
def complete_task(
    user_id: str,
    task_id: int,
) -> str:
    """Mark a task as completed.

    Use this tool when the user wants to complete, finish, mark done, or check off a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task to complete

    Returns:
        JSON string with completion result and confirmation
    """
    db = get_db_session()
    try:
        result = complete_task_fn(
            user_id=user_id,
            task_id=task_id,
            db=db,
        )
        return str(result)
    finally:
        db.close()


@mcp.tool()
def update_task(
    user_id: str,
    task_id: int,
    title: str = "",
    description: str = "",
    priority: str = "",
) -> str:
    """Update an existing task.

    Use this tool when the user wants to update, edit, change, or modify a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task to update
        title: New title (optional, leave empty to keep current)
        description: New description (optional, leave empty to keep current)
        priority: New priority - 'low', 'medium', or 'high' (optional)

    Returns:
        JSON string with update result and confirmation
    """
    db = get_db_session()
    try:
        # Build kwargs with only non-empty values
        kwargs: dict[str, Any] = {"user_id": user_id, "task_id": task_id, "db": db}
        if title:
            kwargs["title"] = title
        if description:
            kwargs["description"] = description
        if priority:
            kwargs["priority"] = priority

        result = update_task_fn(**kwargs)
        return str(result)
    finally:
        db.close()


@mcp.tool()
def delete_task(
    user_id: str,
    task_id: int,
) -> str:
    """Delete a task.

    Use this tool when the user wants to delete, remove, or cancel a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task to delete

    Returns:
        JSON string with deletion result and confirmation
    """
    db = get_db_session()
    try:
        result = delete_task_fn(
            user_id=user_id,
            task_id=task_id,
            db=db,
        )
        return str(result)
    finally:
        db.close()


def get_mcp_server() -> FastMCP:
    """Get the MCP server instance.

    Returns:
        FastMCP: The configured MCP server with all tools registered
    """
    return mcp


# List all available tools for introspection
def get_available_tools() -> list[dict]:
    """Get list of available MCP tools with their schemas.

    Returns:
        list[dict]: List of tool definitions with names and parameters
    """
    return [
        {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "user_id": {"type": "string", "required": True},
                "title": {"type": "string", "required": True},
                "description": {"type": "string", "required": False},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "required": False},
            },
        },
        {
            "name": "list_tasks",
            "description": "List tasks for the user",
            "parameters": {
                "user_id": {"type": "string", "required": True},
                "status": {"type": "string", "enum": ["all", "pending", "completed"], "required": False},
            },
        },
        {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "user_id": {"type": "string", "required": True},
                "task_id": {"type": "integer", "required": True},
            },
        },
        {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "user_id": {"type": "string", "required": True},
                "task_id": {"type": "integer", "required": True},
                "title": {"type": "string", "required": False},
                "description": {"type": "string", "required": False},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "required": False},
            },
        },
        {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "user_id": {"type": "string", "required": True},
                "task_id": {"type": "integer", "required": True},
            },
        },
    ]
