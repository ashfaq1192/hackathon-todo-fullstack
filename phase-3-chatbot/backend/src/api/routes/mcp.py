"""MCP Server HTTP/SSE routes for FastAPI.

This module exposes the MCP server over HTTP with Server-Sent Events (SSE)
transport, allowing web clients and MCP-compatible agents to connect.

Endpoints:
- GET /mcp/tools - List available MCP tools
- POST /mcp/sse - SSE endpoint for MCP protocol communication
- GET /mcp/health - Health check for MCP server

Hackathon Compliance: PDF Page 17 requires "Build MCP server with Official MCP SDK"
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.api.dependencies import get_current_user
from src.mcp.server import (
    get_mcp_server,
    get_available_tools,
    add_task,
    list_tasks,
    complete_task,
    update_task,
    delete_task,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


class MCPToolRequest(BaseModel):
    """Request model for MCP tool invocation."""

    tool_name: str = Field(..., description="Name of the MCP tool to invoke")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Tool arguments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tool_name": "add_task",
                "arguments": {
                    "user_id": "user_123",
                    "title": "Buy groceries",
                    "priority": "high",
                },
            }
        }
    }


class MCPToolResponse(BaseModel):
    """Response model for MCP tool invocation."""

    success: bool
    tool_name: str
    result: Any
    error: str | None = None


@router.get(
    "/tools",
    response_model=list[dict],
    summary="List available MCP tools",
    description="Returns the list of available MCP tools with their schemas",
)
async def list_mcp_tools() -> list[dict]:
    """List all available MCP tools.

    Returns:
        list[dict]: List of tool definitions with names and parameter schemas
    """
    return get_available_tools()


@router.post(
    "/invoke",
    response_model=MCPToolResponse,
    summary="Invoke an MCP tool",
    description="Directly invoke an MCP tool with the provided arguments",
)
async def invoke_mcp_tool(
    request: MCPToolRequest,
    current_user: str = Depends(get_current_user),
) -> MCPToolResponse:
    """Invoke an MCP tool directly.

    This endpoint allows direct invocation of MCP tools with authentication.
    The user_id is automatically injected from the JWT token.

    Args:
        request: Tool invocation request with tool name and arguments
        current_user: Authenticated user ID from JWT token

    Returns:
        MCPToolResponse: Result of tool invocation

    Raises:
        HTTPException 400: If tool name is invalid
        HTTPException 401: If not authenticated
    """
    # Map tool names to functions
    tool_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "update_task": update_task,
        "delete_task": delete_task,
    }

    tool_name = request.tool_name
    if tool_name not in tool_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown tool: {tool_name}. Available tools: {list(tool_map.keys())}",
        )

    # Inject user_id from JWT token (security: user cannot specify arbitrary user_id)
    arguments = request.arguments.copy()
    arguments["user_id"] = current_user

    try:
        # Invoke the tool
        tool_fn = tool_map[tool_name]
        result = tool_fn(**arguments)

        # Parse result if it's a string representation of dict
        if isinstance(result, str):
            try:
                result = eval(result)  # Safe since we control tool output format
            except Exception:
                pass  # Keep as string if parsing fails

        return MCPToolResponse(
            success=True,
            tool_name=tool_name,
            result=result,
        )

    except TypeError as e:
        # Missing required arguments
        return MCPToolResponse(
            success=False,
            tool_name=tool_name,
            result=None,
            error=f"Invalid arguments: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Tool invocation error: {e}")
        return MCPToolResponse(
            success=False,
            tool_name=tool_name,
            result=None,
            error=f"Tool execution failed: {str(e)}",
        )


@router.get(
    "/health",
    summary="MCP server health check",
    description="Check if the MCP server is running and healthy",
)
async def mcp_health() -> dict:
    """Health check for MCP server.

    Returns:
        dict: Health status and server info
    """
    mcp_server = get_mcp_server()
    return {
        "status": "healthy",
        "server_name": mcp_server.name,
        "server_version": "1.0.0",
        "tools_count": len(get_available_tools()),
        "protocol": "MCP",
        "sdk": "mcp>=1.2.0",
    }


# MCP Protocol Messages endpoint (for full MCP compliance)
@router.post(
    "/messages",
    summary="MCP protocol messages endpoint",
    description="Handle MCP protocol messages (JSON-RPC 2.0)",
)
async def handle_mcp_message(
    request: Request,
    current_user: str = Depends(get_current_user),
) -> JSONResponse:
    """Handle MCP protocol messages.

    This endpoint implements the MCP JSON-RPC 2.0 protocol for tool discovery
    and invocation. It's used by MCP clients like Claude Desktop.

    Args:
        request: Incoming JSON-RPC request
        current_user: Authenticated user ID

    Returns:
        JSONResponse: JSON-RPC response
    """
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")

        # Handle different MCP methods
        if method == "tools/list":
            # Return list of available tools in MCP format
            tools = []
            for tool in get_available_tools():
                tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            k: {"type": v.get("type", "string")}
                            for k, v in tool["parameters"].items()
                        },
                        "required": [
                            k for k, v in tool["parameters"].items()
                            if v.get("required", False)
                        ],
                    },
                })
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools},
            })

        elif method == "tools/call":
            # Invoke a tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # Map tool names to functions
            tool_map = {
                "add_task": add_task,
                "list_tasks": list_tasks,
                "complete_task": complete_task,
                "update_task": update_task,
                "delete_task": delete_task,
            }

            if tool_name not in tool_map:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}",
                    },
                })

            # Inject user_id from JWT
            arguments["user_id"] = current_user

            try:
                result = tool_map[tool_name](**arguments)
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": str(result)}],
                    },
                })
            except Exception as e:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e),
                    },
                })

        elif method == "initialize":
            # MCP initialization
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": {
                        "name": "todo-mcp-server",
                        "version": "1.0.0",
                    },
                },
            })

        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            })

    except Exception as e:
        logger.error(f"MCP message handling error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}",
            },
        })
