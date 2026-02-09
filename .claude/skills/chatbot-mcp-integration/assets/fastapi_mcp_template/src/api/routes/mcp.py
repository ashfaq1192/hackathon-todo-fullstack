from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from src.mcp.server import get_mcp_server


router = APIRouter()

@router.get("/tools", response_model=List[Dict[str, Any]])
async def list_mcp_tools():
    """
    Returns a list of all available MCP tools with their schemas.
    """
    mcp_server = get_mcp_server()
    # Assuming get_mcp_server().get_tools_schemas() returns a list of dicts
    # In FastMCP, tools schemas are automatically generated.
    return [tool.model_dump(mode="json") for tool in mcp_server.get_tools_schemas()]


@router.get("/health", response_model=Dict[str, str])
async def mcp_health():
    """
    Health check for the MCP server.
    """
    mcp_server = get_mcp_server()
    return {"status": "ok", "server_name": mcp_server.name}
