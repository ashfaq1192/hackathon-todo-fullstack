"""Integration tests for completing tasks via chat (User Story 3).

Tests the complete end-to-end flow:
1. User sends natural language message to chat endpoint
2. JWT authentication validates user
3. Chat service processes message with Swarm Agent (mocked)
4. Swarm Agent calls complete_task MCP tool (mocked response)
5. Task status is updated in database
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


@pytest.fixture(name="pending_task")
def pending_task_fixture(session):
    """Create a pending task for testing."""
    task = Task(
        user_id="test_user_123",
        title="Buy groceries",
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
        """Mock implementation that calls complete_task tool directly."""
        from src.mcp.tools.complete_task import complete_task

        # Extract task ID from message (simple parsing for test)
        # Patterns: "Mark task 3 as complete", "Complete task 5", "task 2 is done"
        match = re.search(r'task\s+(\d+)', user_message, re.IGNORECASE)
        if not match:
            return {
                "success": False,
                "message": "Could not identify task ID in your message.",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

        task_id = int(match.group(1))

        # Call actual complete_task tool with the session from ChatService
        result = complete_task(
            user_id=user_id,
            task_id=task_id,
            db=self.db
        )

        # Return mock response similar to what Swarm Agent would return
        if result.get("success"):
            return {
                "success": True,
                "message": result["message"],
                "conversation_id": conversation_id,
                "tool_calls": ["complete_task"],
            }
        else:
            return {
                "success": False,
                "message": f"Failed to complete task: {result.get('message')}",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

    with patch("src.services.gemini_client.get_gemini_client", return_value=mock_gemini_client):
        with patch("src.services.chat_service.ChatService.process_message", new=mock_process_message):
            yield


def test_chat_complete_task_success(client, session, auth_token, pending_task, mock_chat_service):
    """Test successfully completing a task via natural language chat.

    User Story 3: "Users can mark tasks as done through conversation"
    Example: User sends "Mark task 3 as complete" and status changes to complete.
    """
    task_id = pending_task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Mark task {task_id} as complete",
            "conversation_id": None,
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "complete_task" in data["tool_calls"]
    assert "complete" in data["message"].lower() or "✅" in data["message"]

    # Verify task was marked complete in database
    session.refresh(pending_task)
    assert pending_task.complete is True


def test_chat_complete_task_idempotency(client, session, auth_token, mock_chat_service):
    """Test that completing an already-completed task is idempotent."""
    # Create already-completed task
    task = Task(
        user_id="test_user_123",
        title="Already done",
        complete=True,
        priority=TaskPriority.low,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Complete task {task.id}",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "already" in data["message"].lower()

    # Verify task is still complete
    session.refresh(task)
    assert task.complete is True


def test_chat_complete_task_not_found(client, session, auth_token, mock_chat_service):
    """Test error when task ID doesn't exist."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Mark task 99999 as complete",  # Non-existent ID
            "conversation_id": None,
        },
    )

    assert response.status_code == 200  # Request succeeds, but tool returns error
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["message"].lower() or "failed" in data["message"].lower()


def test_chat_complete_task_wrong_user(client, session, auth_token, mock_chat_service):
    """Test that users cannot complete other users' tasks via chat."""
    # Create task for different user
    other_task = Task(
        user_id="other_user",
        title="Other user's task",
        complete=False,
        priority=TaskPriority.high,
    )
    session.add(other_task)
    session.commit()
    session.refresh(other_task)

    # test_user_123 tries to complete other_user's task
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Mark task {other_task.id} as complete",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["message"].lower() or "doesn't belong" in data["message"].lower()

    # Verify task is still incomplete
    session.refresh(other_task)
    assert other_task.complete is False


def test_chat_complete_task_preserves_other_fields(client, session, auth_token, mock_chat_service):
    """Test that completing a task doesn't modify other fields."""
    task = Task(
        user_id="test_user_123",
        title="Important task",
        description="With details",
        complete=False,
        priority=TaskPriority.high,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    original_title = task.title
    original_description = task.description
    original_priority = task.priority
    original_created_at = task.created_at

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Complete task {task.id}",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify other fields are unchanged
    session.refresh(task)
    assert task.title == original_title
    assert task.description == original_description
    assert task.priority == original_priority
    assert task.created_at == original_created_at
    assert task.complete is True  # Only this should change


def test_chat_complete_task_conversation_persistence(client, session, auth_token, pending_task, mock_chat_service):
    """Test that conversation and messages are persisted when completing tasks."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Mark task {pending_task.id} as done",
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
    assert f"task {pending_task.id}" in messages[0].content.lower()
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == data["message"]


def test_chat_complete_multiple_tasks_sequentially(client, session, auth_token, mock_chat_service):
    """Test completing multiple tasks in sequence via chat."""
    task1 = Task(user_id="test_user_123", title="Task 1", complete=False)
    task2 = Task(user_id="test_user_123", title="Task 2", complete=False)
    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    # Complete first task
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Complete task {task1.id}", "conversation_id": None},
    )
    assert response1.status_code == 200
    assert response1.json()["success"] is True
    conversation_id = response1.json()["conversation_id"]

    # Complete second task in same conversation
    response2 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Complete task {task2.id}", "conversation_id": conversation_id},
    )
    assert response2.status_code == 200
    assert response2.json()["success"] is True

    # Verify both tasks are complete
    session.refresh(task1)
    session.refresh(task2)
    assert task1.complete is True
    assert task2.complete is True

    # Verify conversation has 4 messages (2 user + 2 assistant)
    conversation = session.get(Conversation, conversation_id)
    assert conversation.message_count == 4
