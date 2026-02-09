"""Integration tests for task creation via chat (User Story 1).

Tests the complete end-to-end flow:
1. User sends natural language message to chat endpoint
2. JWT authentication validates user
3. Chat service processes message with Swarm Agent (mocked)
4. Swarm Agent calls add_task MCP tool (mocked response)
5. Task is created in database
6. Conversation and messages are persisted
7. Response is returned with confirmation

Note: ChatService.process_message is mocked to avoid requiring actual Gemini API
credentials in test environment. The mock simulates successful tool execution.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool
from unittest.mock import AsyncMock, patch

from src.config import JWT_ALGORITHM, JWT_SECRET_KEY
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.models.task import Task


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


@pytest.fixture(name="mock_chat_service")
def mock_chat_service_fixture(session):
    """Mock Gemini client to avoid requiring API credentials.

    This fixture mocks the get_gemini_client function and ChatService.process_message
    to simulate successful tool execution without requiring actual Gemini API calls.
    """
    from unittest.mock import MagicMock

    # Mock GeminiClient
    mock_gemini_client = MagicMock()
    mock_gemini_client.get_client.return_value = MagicMock()
    mock_gemini_client.model = "gemini-2.0-flash-exp"

    def mock_process_message(self, user_message: str, conversation_id: int | None, user_id: str):
        """Mock implementation that calls add_task tool directly."""
        from src.mcp.tools.add_task import add_task

        # Simulate Swarm Agent parsing the message and calling add_task
        # Extract task title from message (simple parsing for test)
        title = user_message.replace("Add a task to ", "").replace("Create a high priority task: ", "").replace("Add another task to ", "").replace("Add Alice's task", "Alice's task").replace("Add Bob's task", "Bob's task")

        # Call actual add_task tool with the session from ChatService
        result = add_task(
            user_id=user_id,
            title=title,
            db=self.db
        )

        # Return mock response similar to what Swarm Agent would return
        if result.get("success"):
            return {
                "success": True,
                "message": f"✅ Task '{title}' created successfully with ID {result['task_id']}!",
                "conversation_id": conversation_id,
                "tool_calls": ["add_task"],
            }
        else:
            return {
                "success": False,
                "message": f"Failed to create task: {result.get('message')}",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

    with patch("src.services.gemini_client.get_gemini_client", return_value=mock_gemini_client):
        with patch("src.services.chat_service.ChatService.process_message", new=mock_process_message):
            yield


def test_chat_create_task_success(client, session, auth_token, mock_chat_service):
    """Test successful task creation via natural language chat.

    User Story 1: "Users can add tasks by describing them in natural language"
    Example: User sends "Add a task to buy groceries" and task is created.
    """
    # Send chat message to create task
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Add a task to buy groceries",
            "conversation_id": None,  # New conversation
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "groceries" in data["message"].lower() or "task" in data["message"].lower()
    assert data["conversation_id"] is not None
    assert data["message_id"] is not None
    assert "add_task" in data["tool_calls"]

    # Verify task was created in database
    statement = select(Task).where(Task.user_id == "test_user_123")
    tasks = session.exec(statement).all()

    assert len(tasks) == 1
    task = tasks[0]
    assert "groceries" in task.title.lower()
    assert task.complete is False
    assert task.user_id == "test_user_123"

    # Verify conversation was created
    conversation = session.get(Conversation, data["conversation_id"])
    assert conversation is not None
    assert conversation.user_id == "test_user_123"
    assert conversation.message_count == 2  # User message + assistant response

    # Verify messages were persisted
    statement = select(Message).where(Message.conversation_id == conversation.id)
    messages = session.exec(statement).all()

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "Add a task to buy groceries"
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == data["message"]


def test_chat_create_task_with_details(client, session, auth_token, mock_chat_service):
    """Test task creation with description and priority via chat."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Create a high priority task: Complete project report with detailed analysis",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify task details
    statement = select(Task).where(Task.user_id == "test_user_123")
    tasks = session.exec(statement).all()

    assert len(tasks) == 1
    task = tasks[0]
    assert "project report" in task.title.lower() or "complete" in task.title.lower()
    # Note: Priority extraction depends on Gemini's understanding and tool call


def test_chat_continue_conversation(client, session, auth_token, mock_chat_service):
    """Test continuing an existing conversation."""
    # First message - create conversation
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "Add a task to buy milk", "conversation_id": None},
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Second message - continue conversation
    response2 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Add another task to buy bread",
            "conversation_id": conversation_id,
        },
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["conversation_id"] == conversation_id

    # Verify conversation has 4 messages (2 user + 2 assistant)
    conversation = session.get(Conversation, conversation_id)
    assert conversation.message_count == 4

    # Verify both tasks were created
    statement = select(Task).where(Task.user_id == "test_user_123")
    tasks = session.exec(statement).all()
    assert len(tasks) == 2


def test_chat_authentication_required(client):
    """Test that chat endpoint requires JWT authentication."""
    response = client.post(
        "/api/test_user_123/chat",
        json={"message": "Add a task to test"},
    )

    # Should return 401 Unauthorized (missing Authorization header)
    assert response.status_code == 401


def test_chat_invalid_token(client):
    """Test that chat endpoint rejects invalid JWT tokens."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": "Bearer invalid-token-here"},
        json={"message": "Add a task to test"},
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401


def test_chat_user_id_mismatch(client, auth_token):
    """Test that JWT user_id must match URL user_id (FR-006 security requirement)."""
    # Token is for test_user_123, but URL has different_user
    response = client.post(
        "/api/different_user/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "Add a task to test"},
    )

    # Should return 403 Forbidden (user ID mismatch)
    assert response.status_code == 403
    data = response.json()
    # API returns structured error response with 'message' containing error details
    error_message = data.get("message", {})
    if isinstance(error_message, dict):
        assert "doesn't match" in error_message.get("message", "").lower()
    else:
        assert "doesn't match" in str(error_message).lower()


def test_chat_conversation_ownership(client, session, auth_token):
    """Test that users can only access their own conversations."""
    # Create conversation for test_user_123
    conversation = Conversation(
        user_id="different_user",  # Different user owns this
        message_count=0,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # test_user_123 tries to access different_user's conversation
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Add a task",
            "conversation_id": conversation.id,
        },
    )

    # Should return 404 Not Found (conversation not accessible)
    assert response.status_code == 404
    data = response.json()
    # API returns structured error response with 'message' containing error details
    error_message = data.get("message", {})
    if isinstance(error_message, dict):
        assert "not found or not accessible" in error_message.get("message", "").lower()
    else:
        assert "not found" in str(error_message).lower()


def test_chat_empty_message_validation(client, auth_token):
    """Test that empty messages are rejected."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "", "conversation_id": None},
    )

    # Should return 422 Validation Error
    assert response.status_code == 422


def test_chat_user_isolation(client, session, mock_chat_service):
    """Test that tasks are properly isolated by user_id."""
    # Create tokens for two different users
    token1 = jwt.encode(
        {"user_id": "user_alice", "sub": "user_alice"},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    token2 = jwt.encode(
        {"user_id": "user_bob", "sub": "user_bob"},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    # Alice creates a task
    response1 = client.post(
        "/api/user_alice/chat",
        headers={"Authorization": f"Bearer {token1}"},
        json={"message": "Add Alice's task"},
    )
    assert response1.status_code == 200

    # Bob creates a task
    response2 = client.post(
        "/api/user_bob/chat",
        headers={"Authorization": f"Bearer {token2}"},
        json={"message": "Add Bob's task"},
    )
    assert response2.status_code == 200

    # Verify tasks are isolated
    alice_tasks = session.exec(select(Task).where(Task.user_id == "user_alice")).all()
    bob_tasks = session.exec(select(Task).where(Task.user_id == "user_bob")).all()

    assert len(alice_tasks) == 1
    assert len(bob_tasks) == 1
    assert alice_tasks[0].user_id == "user_alice"
    assert bob_tasks[0].user_id == "user_bob"
