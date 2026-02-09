from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List

# Import your MCP tools here
from src.mcp.tools.example_tool import example_tool


mcp = FastMCP(
    name="todo-mcp-server",
    description="MCP server for managing tasks and conversations.",
    version="1.0.0",
)

# Register your MCP tools here
@mcp.tool()
def example_tool(
    param1: str,
    param2: int | None = None
) -> Dict[str, Any]:
    """
    Example MCP tool for demonstration.
    """
    pass # Schema definition only, implementation is in src/mcp/tools/example_tool.py


def get_mcp_server() -> FastMCP:
    """
    Returns the configured FastMCP server instance.
    """
    return mcp
