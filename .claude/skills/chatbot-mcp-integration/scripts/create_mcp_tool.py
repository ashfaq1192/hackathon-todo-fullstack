import argparse
import os

def create_mcp_tool_script(tool_name: str, description: str, output_dir: str):
    tool_filename = f"{tool_name}.py"
    tool_file_path = os.path.join(output_dir, tool_filename)

    tool_content = f"""
from sqlmodel import Session
# from src.models import Task # Example import, adjust as needed

def {tool_name}(
    session: Session,
    user_id: str,
    # Add other parameters as needed, e.g., title: str, description: str | None = None
) -> dict:
    """
    MCP tool for {description.lower()}.
    """
    # TODO: Implement the business logic for the '{tool_name}' tool here.
    # Ensure proper session management and user_id filtering.

    # Example return structure
    return {{
        "status": "success",
        "message": f"Tool '{tool_name}' executed for user {{user_id}}.",
        # Add other relevant data as needed
    }}
"""
    os.makedirs(output_dir, exist_ok=True)
    with open(tool_file_path, "w") as f:
        f.write(tool_content.strip())
    print(f"✅ Created MCP tool file: {tool_file_path}")

    # Create a basic unit test file
    test_output_dir = os.path.join(output_dir, "../../tests/unit/mcp")
    test_filename = f"test_{tool_name}.py"
    test_file_path = os.path.join(test_output_dir, test_filename)

    test_content = f"""
import pytest
from unittest.mock import MagicMock
from sqlmodel import Session
from src.mcp.tools.{tool_name} import {tool_name}

def test_{tool_name}_success():
    mock_session = MagicMock(spec=Session)
    test_user_id = "test_user_123"
    test_description = "Test description for {tool_name}"

    # TODO: Configure mock_session for any database operations expected by the tool
    # Example: mock_session.add.return_value = None
    # Example: mock_session.commit.return_value = None
    # Example: mock_session.refresh.return_value = None

    result = {tool_name}(session=mock_session, user_id=test_user_id, description=test_description)

    assert result["status"] == "success"
    assert "message" in result
    # TODO: Add more specific assertions based on the tool's expected output
    # Example: mock_session.add.assert_called_once()
    # Example: mock_session.commit.assert_called_once()

# TODO: Add more test cases:
# - test_{tool_name}_failure_db_error
# - test_{tool_name}_with_specific_parameters
# - etc.
"""
    os.makedirs(test_output_dir, exist_ok=True)
    with open(test_file_path, "w") as f:
        f.write(test_content.strip())
    print(f"✅ Created unit test file: {test_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scaffold a new MCP tool and its corresponding unit test."
    )
    parser.add_argument("tool_name", help="Name of the MCP tool (e.g., add_task, list_tasks)")
    parser.add_argument(
        "--description",
        default="perform an action",
        help="Brief description of what the tool does."
    )
    parser.add_argument(
        "--output_dir",
        default="phase-3-chatbot/backend/src/mcp/tools",
        help="Directory where the tool file will be created."
    )
    args = parser.parse_args()

    create_mcp_tool_script(args.tool_name, args.description, args.output_dir)
