"""Integration tests for updating tasks via chat (User Story 4).

Tests the complete end-to-end flow:
1. User sends natural language message to chat endpoint
2. JWT authentication validates user
3. Chat service processes message with Swarm Agent (mocked)
4. Swarm Agent calls update_task MCP tool (mocked response)
5. Task fields are updated in database
6. Response is returned with confirmation

Note: ChatService.process_message is mocked to avoid requiring actual Gemini API
credentials in test environment. The mock simulates successful tool execution.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool
from unittest.mock import patch

from src.config import JWT_ALGORITHM, JWT_SECRET_KEY
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.models.task import Task, TaskPriority


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Task.metadata.create_all(engine)
    Conversation.metadata.create_all(engine)
    Message.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """Create test client with dependency override."""
    from src.database import get_session

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="auth_token")
def auth_token_fixture():
    """Generate valid JWT token for testing."""
    payload = {
        "user_id": "test_user_123",
        "sub": "test_user_123",
        "email": "test@example.com",
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(name="sample_task")
def sample_task_fixture(session):
    """Create a sample task for testing."""
    task = Task(
        user_id="test_user_123",
        title="Old title",
        description="Old description",
        complete=False,
        priority=TaskPriority.medium,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="mock_chat_service")
def mock_chat_service_fixture(session):
    """Mock Gemini client to avoid requiring API credentials.

    This fixture mocks the get_gemini_client function and ChatService.process_message
    to simulate successful tool execution without requiring actual Gemini API calls.
    """
    from unittest.mock import MagicMock
    import re

    # Mock GeminiClient
    mock_gemini_client = MagicMock()
    mock_gemini_client.get_client.return_value = MagicMock()
    mock_gemini_client.model = "gemini-2.0-flash-exp"

    def mock_process_message(self, user_message: str, conversation_id: int | None, user_id: str):
        """Mock implementation that calls update_task tool directly."""
        from src.mcp.tools.update_task import update_task

        # Extract task ID from message (simple parsing for test)
        match = re.search(r'task\s+(\d+)', user_message, re.IGNORECASE)
        if not match:
            return {
                "success": False,
                "message": "Could not identify task ID in your message.",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

        task_id = int(match.group(1))

        # Parse update parameters from message
        title = None
        description = None
        priority = None

        if "title to" in user_message.lower():
            # Extract new title: "Change task 2 title to 'New Title'"
            title_match = re.search(r'title to ["\'](.+?)["\']', user_message, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)

        if "description to" in user_message.lower():
            # Extract new description
            desc_match = re.search(r'description to ["\'](.+?)["\']', user_message, re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1)

        if "priority to" in user_message.lower():
            # Extract priority: "Set task 3 priority to high"
            prio_match = re.search(r'priority to (low|medium|high)', user_message, re.IGNORECASE)
            if prio_match:
                priority = prio_match.group(1).lower()

        # Call actual update_task tool with the session from ChatService
        result = update_task(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            db=self.db
        )

        # Return mock response similar to what Swarm Agent would return
        if result.get("success"):
            return {
                "success": True,
                "message": result["message"],
                "conversation_id": conversation_id,
                "tool_calls": ["update_task"],
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update task: {result.get('message')}",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

    with patch("src.services.gemini_client.get_gemini_client", return_value=mock_gemini_client):
        with patch("src.services.chat_service.ChatService.process_message", new=mock_process_message):
            yield


def test_chat_update_task_title(client, session, auth_token, sample_task, mock_chat_service):
    """Test updating task title via natural language chat.

    User Story 4: "Users can modify task details through natural language"
    Example: User sends "Change task 2 title to 'Buy organic groceries'" and title updates.
    """
    task_id = sample_task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Change task {task_id} title to 'Buy organic groceries'",
            "conversation_id": None,
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "update_task" in data["tool_calls"]
    assert "title" in data["message"].lower() or "updated" in data["message"].lower()

    # Verify task title was updated in database
    session.refresh(sample_task)
    assert sample_task.title == "Buy organic groceries"
    assert sample_task.description == "Old description"  # Unchanged


def test_chat_update_task_description(client, session, auth_token, sample_task, mock_chat_service):
    """Test updating task description via chat."""
    task_id = sample_task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Change task {task_id} description to 'New detailed description'",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "update_task" in data["tool_calls"]

    # Verify description was updated
    session.refresh(sample_task)
    assert sample_task.description == "New detailed description"
    assert sample_task.title == "Old title"  # Unchanged


def test_chat_update_task_priority(client, session, auth_token, sample_task, mock_chat_service):
    """Test updating task priority via chat."""
    task_id = sample_task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Set task {task_id} priority to high",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "update_task" in data["tool_calls"]

    # Verify priority was updated
    session.refresh(sample_task)
    assert sample_task.priority == TaskPriority.high


def test_chat_update_task_not_found(client, session, auth_token, mock_chat_service):
    """Test error when task ID doesn't exist."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Change task 99999 title to 'New title'",  # Non-existent ID
            "conversation_id": None,
        },
    )

    assert response.status_code == 200  # Request succeeds, but tool returns error
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["message"].lower() or "failed" in data["message"].lower()


def test_chat_update_task_wrong_user(client, session, auth_token, mock_chat_service):
    """Test that users cannot update other users' tasks via chat."""
    # Create task for different user
    other_task = Task(
        user_id="other_user",
        title="Other user's task",
        complete=False,
        priority=TaskPriority.low,
    )
    session.add(other_task)
    session.commit()
    session.refresh(other_task)

    # test_user_123 tries to update other_user's task
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Change task {other_task.id} title to 'Hacked title'",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["message"].lower() or "doesn't belong" in data["message"].lower()

    # Verify task is unchanged
    session.refresh(other_task)
    assert other_task.title == "Other user's task"


def test_chat_update_task_preserves_complete_status(client, session, auth_token, mock_chat_service):
    """Test that updating doesn't affect complete status."""
    task = Task(
        user_id="test_user_123",
        title="Completed task",
        complete=True,  # Already complete
        priority=TaskPriority.low,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Change task {task.id} title to 'Updated completed task'",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify complete status is preserved
    session.refresh(task)
    assert task.complete is True  # Should remain complete
    assert task.title == "Updated completed task"


def test_chat_update_task_conversation_persistence(client, session, auth_token, sample_task, mock_chat_service):
    """Test that conversation and messages are persisted when updating tasks."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Change task {sample_task.id} title to 'Updated via chat'",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify conversation was created
    conversation = session.get(Conversation, data["conversation_id"])
    assert conversation is not None
    assert conversation.user_id == "test_user_123"
    assert conversation.message_count == 2

    # Verify messages were persisted
    statement = select(Message).where(Message.conversation_id == conversation.id)
    messages = session.exec(statement).all()

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert f"task {sample_task.id}" in messages[0].content.lower()
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == data["message"]


def test_chat_update_multiple_fields(client, session, auth_token, mock_chat_service):
    """Test updating multiple task fields simultaneously via chat."""
    task = Task(
        user_id="test_user_123",
        title="Original",
        description="Original desc",
        priority=TaskPriority.low,
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Update both title and priority in one message
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Change task {task.id} title to 'Updated' and set priority to high",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify both fields were updated
    session.refresh(task)
    assert task.title == "Updated"
    assert task.priority == TaskPriority.high
