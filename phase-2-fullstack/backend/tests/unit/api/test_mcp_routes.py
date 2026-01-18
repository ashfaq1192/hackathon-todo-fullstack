"""Unit tests for MCP API routes."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app  # Assuming your FastAPI app is in src/main.py
from src.mcp.server import get_mcp_server
from src.api.dependencies import get_current_user

# Sample user for authentication
TEST_USER = "test_user"

# Mock the get_current_user dependency
def override_get_current_user():
    return TEST_USER

app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def mock_mcp_server():
    """Fixture to mock the MCP server and its functions."""
    with patch("src.api.routes.mcp.get_mcp_server", autospec=True) as mock_server:
        server_instance = MagicMock()
        server_instance.name = "test-server"
        mock_server.return_value = server_instance
        yield


def test_mcp_health(mock_mcp_server):
    """Test the /mcp/health endpoint."""
    response = client.get("/api/mcp/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["server_name"] == "test-server"
    assert "tools_count" in data


@patch("src.api.routes.mcp.get_available_tools")
def test_list_mcp_tools(mock_get_tools):
    """Test the /mcp/tools endpoint."""
    mock_tools = [
        {"name": "add_task", "description": "Add a task"},
        {"name": "list_tasks", "description": "List tasks"},
    ]
    mock_get_tools.return_value = mock_tools

    response = client.get("/api/mcp/tools")
    assert response.status_code == 200
    assert response.json() == mock_tools


@patch("src.api.routes.mcp.add_task")
def test_invoke_mcp_tool_success(mock_add_task):
    """Test successful invocation of an MCP tool via /mcp/invoke."""
    mock_add_task.return_value = {"status": "success", "task_id": 1}

    payload = {
        "tool_name": "add_task",
        "arguments": {"title": "Test Task", "priority": "high"},
    }
    response = client.post("/api/mcp/invoke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "add_task"
    assert data["result"] == {"status": "success", "task_id": 1}
    mock_add_task.assert_called_once_with(
        title="Test Task", priority="high", user_id=TEST_USER
    )


def test_invoke_mcp_tool_unknown_tool():
    """Test invoking an unknown MCP tool."""
    payload = {"tool_name": "unknown_tool", "arguments": {}}
    response = client.post("/api/mcp/invoke", json=payload)
    assert response.status_code == 400
    assert "Unknown tool" in response.json()["detail"]


@patch("src.api.routes.mcp.add_task")
def test_invoke_mcp_tool_invalid_args(mock_add_task):
    """Test invoking an MCP tool with invalid arguments."""
    mock_add_task.side_effect = TypeError("Missing required argument")

    payload = {"tool_name": "add_task", "arguments": {}}  # Missing 'title'
    response = client.post("/api/mcp/invoke", json=payload)
    assert response.status_code == 200  # Endpoint handles it gracefully
    data = response.json()
    assert data["success"] is False
    assert "Invalid arguments" in data["error"]


@patch("src.api.routes.mcp.get_available_tools")
@patch("src.api.routes.mcp.add_task")
async def test_handle_mcp_message_json_rpc(mock_add_task, mock_get_tools):
    """Test the /mcp/messages endpoint for JSON-RPC calls."""
    # Mock the tools for the 'tools/list' call
    mock_get_tools.return_value = [{"name": "add_task", "description": "Add a new task", "parameters": {}}]

    # Test 'tools/list'
    list_payload = {"jsonrpc": "2.0", "method": "tools/list", "id": "1"}
    response = client.post("/api/mcp/messages", json=list_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1"
    assert "tools" in data["result"]
    assert data["result"]["tools"][0]["name"] == "add_task"

    # Test 'tools/call'
    mock_add_task.return_value = "Task added"
    call_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "add_task", "arguments": {"title": "From RPC"}},
        "id": "2",
    }
    response = client.post("/api/mcp/messages", json=call_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "2"
    assert data["result"]["content"][0]["text"] == "Task added"
    mock_add_task.assert_called_with(title="From RPC", user_id=TEST_USER)

    # Test unknown tool in 'tools/call'
    unknown_tool_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "fake_tool", "arguments": {}},
        "id": "3",
    }
    response = client.post("/api/mcp/messages", json=unknown_tool_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "3"
    assert data["error"]["message"] == "Unknown tool: fake_tool"
