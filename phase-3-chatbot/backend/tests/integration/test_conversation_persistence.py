"""Integration tests for conversation persistence (User Story 6).

Tests the complete end-to-end flow:
1. User sends messages and they persist in the database
2. Conversations can be continued across multiple requests
3. Messages maintain order and context

Note: ChatService.process_message is mocked to avoid requiring actual Gemini API
credentials in test environment. The mock simulates successful responses.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool
from unittest.mock import patch, MagicMock

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
    """Mock ChatService to avoid Swarm/Gemini initialization.

    This fixture completely mocks ChatService to bypass Swarm initialization issues.
    The mock simulates simple responses for conversation persistence testing.
    """
    # Mock GeminiClient
    mock_gemini_client = MagicMock()
    mock_gemini_client.get_client.return_value = MagicMock()
    mock_gemini_client.model = "gemini-2.0-flash-exp"

    message_counter = [0]  # Use list to allow mutation in closure

    def mock_process_message(self, user_message: str, conversation_id: int | None, user_id: str):
        """Mock implementation that returns simple responses."""
        message_counter[0] += 1

        return {
            "success": True,
            "message": f"Response #{message_counter[0]} to: {user_message[:50]}",
            "conversation_id": conversation_id,
            "tool_calls": [],
        }

    with patch("src.services.gemini_client.get_gemini_client", return_value=mock_gemini_client):
        with patch("src.services.chat_service.ChatService.process_message", new=mock_process_message):
            yield


def test_conversation_creation(client, session, auth_token, mock_chat_service):
    """Test that a new conversation is created when no conversation_id is provided."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Hello, this is my first message.",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify conversation was created
    assert data["conversation_id"] is not None
    conversation = session.get(Conversation, data["conversation_id"])
    assert conversation is not None
    assert conversation.user_id == "test_user_123"
    assert conversation.message_count == 2  # User + Assistant


def test_message_persistence(client, session, auth_token, mock_chat_service):
    """Test that messages are persisted in the database."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "This message should be saved.",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]

    # Verify messages were persisted
    statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(statement).all()

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "This message should be saved."
    assert messages[1].role == MessageRole.ASSISTANT


def test_conversation_continuation(client, session, auth_token, mock_chat_service):
    """Test that conversations can be continued with conversation_id."""
    # First message - creates conversation
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "First message",
            "conversation_id": None,
        },
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Second message - continues conversation
    response2 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Second message",
            "conversation_id": conversation_id,
        },
    )

    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conversation_id

    # Verify conversation has 4 messages
    conversation = session.get(Conversation, conversation_id)
    assert conversation.message_count == 4

    # Verify all messages are in the correct order
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    messages = session.exec(statement).all()

    assert len(messages) == 4
    assert messages[0].content == "First message"
    assert messages[0].role == MessageRole.USER
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[2].content == "Second message"
    assert messages[2].role == MessageRole.USER
    assert messages[3].role == MessageRole.ASSISTANT


def test_new_conversation_separate(client, session, auth_token, mock_chat_service):
    """Test that new conversations are created separately."""
    # First conversation
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Conversation 1",
            "conversation_id": None,
        },
    )

    conversation_id_1 = response1.json()["conversation_id"]

    # Second conversation (new)
    response2 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Conversation 2",
            "conversation_id": None,  # No conversation_id = new conversation
        },
    )

    conversation_id_2 = response2.json()["conversation_id"]

    # Verify they are different conversations
    assert conversation_id_1 != conversation_id_2

    # Verify each has its own messages
    conv1_messages = session.exec(
        select(Message).where(Message.conversation_id == conversation_id_1)
    ).all()
    conv2_messages = session.exec(
        select(Message).where(Message.conversation_id == conversation_id_2)
    ).all()

    assert len(conv1_messages) == 2
    assert len(conv2_messages) == 2
    assert conv1_messages[0].content == "Conversation 1"
    assert conv2_messages[0].content == "Conversation 2"


def test_conversation_user_isolation(client, session, auth_token, mock_chat_service):
    """Test that users cannot access other users' conversations."""
    # Create conversation for test_user_123
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "My private conversation",
            "conversation_id": None,
        },
    )

    conversation_id = response.json()["conversation_id"]

    # Create token for different user
    other_token = jwt.encode(
        {"user_id": "other_user", "sub": "other_user"},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    # Try to access first user's conversation with different user
    response2 = client.post(
        "/api/other_user/chat",
        headers={"Authorization": f"Bearer {other_token}"},
        json={
            "message": "Trying to access other conversation",
            "conversation_id": conversation_id,
        },
    )

    # Should return 404 (conversation not found for this user)
    assert response2.status_code == 404


def test_multiple_messages_in_sequence(client, session, auth_token, mock_chat_service):
    """Test sending multiple messages in a single conversation."""
    # First message
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "Message 1", "conversation_id": None},
    )
    conversation_id = response1.json()["conversation_id"]

    # Send 4 more messages
    for i in range(2, 6):
        response = client.post(
            "/api/test_user_123/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"message": f"Message {i}", "conversation_id": conversation_id},
        )
        assert response.status_code == 200
        assert response.json()["conversation_id"] == conversation_id

    # Verify all messages are persisted (5 user + 5 assistant = 10)
    conversation = session.get(Conversation, conversation_id)
    assert conversation.message_count == 10

    # Verify message content and order
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    messages = session.exec(statement).all()

    assert len(messages) == 10

    # Check user messages are in correct order
    user_messages = [m for m in messages if m.role == MessageRole.USER]
    for i, msg in enumerate(user_messages, 1):
        assert msg.content == f"Message {i}"
