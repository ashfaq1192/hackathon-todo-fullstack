"""Integration tests for deleting tasks via chat (User Story 5).

Tests the complete end-to-end flow:
1. User sends natural language message to chat endpoint
2. JWT authentication validates user
3. Chat service processes message with Swarm Agent (mocked)
4. Swarm Agent calls delete_task MCP tool (mocked response)
5. Task is permanently removed from database
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
        title="Task to delete",
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
        """Mock implementation that calls delete_task tool directly."""
        from src.mcp.tools.delete_task import delete_task

        # Extract task ID from message (simple parsing for test)
        # Patterns: "Delete task 3", "Remove task 5", "task 2"
        match = re.search(r'task\s+(\d+)', user_message, re.IGNORECASE)
        if not match:
            return {
                "success": False,
                "message": "Could not identify task ID in your message.",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

        task_id = int(match.group(1))

        # Call actual delete_task tool with the session from ChatService
        result = delete_task(
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
                "tool_calls": ["delete_task"],
            }
        else:
            return {
                "success": False,
                "message": f"Failed to delete task: {result.get('message')}",
                "conversation_id": conversation_id,
                "tool_calls": [],
            }

    with patch("src.services.gemini_client.get_gemini_client", return_value=mock_gemini_client):
        with patch("src.services.chat_service.ChatService.process_message", new=mock_process_message):
            yield


def test_chat_delete_task_success(client, session, auth_token, sample_task, mock_chat_service):
    """Test successfully deleting a task via natural language chat.

    User Story 5: "Users can remove tasks by asking the chatbot"
    Example: User sends "Delete task 4" and task is permanently removed.
    """
    task_id = sample_task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Delete task {task_id}",
            "conversation_id": None,
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "delete_task" in data["tool_calls"]
    assert "deleted" in data["message"].lower() or "removed" in data["message"].lower() or "🗑️" in data["message"]

    # Verify task was permanently removed from database
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_chat_delete_task_not_found(client, session, auth_token, mock_chat_service):
    """Test error when task ID doesn't exist."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Delete task 99999",  # Non-existent ID
            "conversation_id": None,
        },
    )

    assert response.status_code == 200  # Request succeeds, but tool returns error
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["message"].lower() or "failed" in data["message"].lower()


def test_chat_delete_task_wrong_user(client, session, auth_token, mock_chat_service):
    """Test that users cannot delete other users' tasks via chat."""
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

    # test_user_123 tries to delete other_user's task
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Delete task {other_task.id}",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["message"].lower() or "doesn't belong" in data["message"].lower()

    # Verify task still exists
    session.refresh(other_task)
    assert other_task is not None


def test_chat_delete_completed_task(client, session, auth_token, mock_chat_service):
    """Test deleting a task that's already completed."""
    task = Task(
        user_id="test_user_123",
        title="Completed task to delete",
        complete=True,  # Already completed
        priority=TaskPriority.low,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Delete task {task_id}",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True

    # Verify deletion
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_chat_delete_task_returns_details(client, session, auth_token, mock_chat_service):
    """Test that response includes task details for user feedback."""
    task = Task(
        user_id="test_user_123",
        title="Important Meeting",
        description="With CEO",
        complete=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Remove task {task_id}",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    # Message should mention the task title for confirmation
    assert "Important Meeting" in data["message"] or "deleted" in data["message"].lower()


def test_chat_delete_task_conversation_persistence(client, session, auth_token, sample_task, mock_chat_service):
    """Test that conversation and messages are persisted when deleting tasks."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": f"Delete task {sample_task.id}",
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


def test_chat_delete_task_count_verification(client, session, auth_token, mock_chat_service):
    """Test that total task count decreases after deletion via chat."""
    # Create 3 tasks
    for i in range(3):
        task = Task(user_id="test_user_123", title=f"Task {i}", complete=False)
        session.add(task)
    session.commit()

    # Verify initial count
    initial_count = len(session.exec(select(Task).where(Task.user_id == "test_user_123")).all())
    assert initial_count == 3

    # Delete one task
    task_to_delete = session.exec(select(Task).where(Task.user_id == "test_user_123")).first()
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {task_to_delete.id}", "conversation_id": None},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify count decreased
    final_count = len(session.exec(select(Task).where(Task.user_id == "test_user_123")).all())
    assert final_count == 2


def test_chat_delete_multiple_tasks_sequentially(client, session, auth_token, mock_chat_service):
    """Test deleting multiple tasks one by one via chat."""
    task1 = Task(user_id="test_user_123", title="Task 1", complete=False)
    task2 = Task(user_id="test_user_123", title="Task 2", complete=False)
    task3 = Task(user_id="test_user_123", title="Task 3", complete=False)

    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)
    session.refresh(task3)

    task1_id = task1.id
    task2_id = task2.id
    task3_id = task3.id

    # Delete them sequentially
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {task1_id}", "conversation_id": None},
    )
    response2 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {task2_id}", "conversation_id": response1.json()["conversation_id"]},
    )
    response3 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {task3_id}", "conversation_id": response2.json()["conversation_id"]},
    )

    assert response1.json()["success"] is True
    assert response2.json()["success"] is True
    assert response3.json()["success"] is True

    # Verify all are deleted
    assert session.get(Task, task1_id) is None
    assert session.get(Task, task2_id) is None
    assert session.get(Task, task3_id) is None

    # Verify conversation has 6 messages (3 user + 3 assistant)
    conversation = session.get(Conversation, response1.json()["conversation_id"])
    assert conversation.message_count == 6


def test_chat_delete_task_preserves_other_users_tasks(client, session, auth_token, mock_chat_service):
    """Test that deleting one user's tasks doesn't affect others."""
    alice_task = Task(user_id="user_alice", title="Alice task", complete=False)
    bob_task = Task(user_id="test_user_123", title="Bob task", complete=False)

    session.add(alice_task)
    session.add(bob_task)
    session.commit()
    session.refresh(alice_task)
    session.refresh(bob_task)

    # test_user_123 deletes their task
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {bob_task.id}", "conversation_id": None},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify Alice's task is unaffected
    session.refresh(alice_task)
    assert alice_task is not None


def test_chat_delete_task_double_delete_attempt(client, session, auth_token, mock_chat_service):
    """Test that attempting to delete the same task twice fails on second attempt."""
    task = Task(user_id="test_user_123", title="Task", complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # First delete - should succeed
    response1 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {task_id}", "conversation_id": None},
    )
    assert response1.json()["success"] is True

    # Second delete - should fail (task no longer exists)
    response2 = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": f"Delete task {task_id}", "conversation_id": response1.json()["conversation_id"]},
    )
    assert response2.json()["success"] is False
    assert "not found" in response2.json()["message"].lower()
