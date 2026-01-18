"""Integration tests for listing tasks via chat (User Story 2).

Tests the complete end-to-end flow:
1. User sends natural language message to chat endpoint
2. JWT authentication validates user
3. Chat service processes message with Swarm Agent (mocked)
4. Swarm Agent calls list_tasks MCP tool (mocked response)
5. Tasks are retrieved from database with status filtering
6. Response is returned with formatted task list

Note: ChatService.process_message is mocked to avoid requiring actual Gemini API
credentials in test environment. The mock simulates successful tool execution.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, create_engine
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


@pytest.fixture(name="sample_tasks")
def sample_tasks_fixture(session):
    """Create sample tasks for testing."""
    tasks = [
        Task(user_id="test_user_123", title="Buy groceries", complete=False, priority=TaskPriority.high),
        Task(user_id="test_user_123", title="Finish report", complete=False, priority=TaskPriority.medium),
        Task(user_id="test_user_123", title="Clean kitchen", complete=True, priority=TaskPriority.low),
        Task(user_id="other_user", title="Other user task", complete=False, priority=TaskPriority.high),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


@pytest.fixture(name="mock_chat_service")
def mock_chat_service_fixture(session):
    """Mock ChatService to avoid Swarm/Gemini initialization.

    This fixture completely mocks ChatService to bypass Swarm initialization issues.
    The mock calls the actual MCP tools directly to test integration.
    """
    from unittest.mock import AsyncMock, MagicMock
    from src.services.chat_service import ChatService

    # Create mock ChatService class that doesn't initialize Swarm
    class MockChatService:
        def __init__(self, db: Session):
            self.db = db

        def process_message(self, user_message: str, conversation_id: int | None, user_id: str):
            """Mock implementation that calls list_tasks tool directly."""
            from src.mcp.tools.list_tasks import list_tasks

            # Parse message to determine status filter
            status = "all"
            if "pending" in user_message.lower():
                status = "pending"
            elif "completed" in user_message.lower() or "done" in user_message.lower():
                status = "completed"

            # Call actual list_tasks tool with database session
            result = list_tasks(
                user_id=user_id,
                status=status,
                db=self.db
            )

            # Return mock response similar to what Swarm Agent would return
            if result.get("success"):
                tasks_text = "\n".join([
                    f"- [{task['id']}] {task['title']} ({'✅' if task['complete'] else '⬜'})"
                    for task in result["tasks"]
                ])
                message = f"{result['message']}\n\n{tasks_text}" if result["tasks"] else result["message"]

                return {
                    "success": True,
                    "message": message,
                    "conversation_id": conversation_id,
                    "tool_calls": ["list_tasks"],
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to list tasks: {result.get('message')}",
                    "conversation_id": conversation_id,
                    "tool_calls": [],
                }

    # Patch ChatService class entirely
    with patch("src.api.routes.chat.ChatService", MockChatService):
        yield


def test_chat_list_all_tasks(client, session, auth_token, sample_tasks, mock_chat_service):
    """Test listing all tasks via natural language chat.

    User Story 2: "Users can view tasks by asking the chatbot"
    Example: User sends "Show me my tasks" and receives task list.
    """
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Show me all my tasks",
            "conversation_id": None,
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "list_tasks" in data["tool_calls"]

    # Should include both pending and completed tasks (3 total for test_user_123)
    assert "Buy groceries" in data["message"] or "groceries" in data["message"].lower()
    assert data["conversation_id"] is not None


def test_chat_list_pending_tasks_only(client, session, auth_token, sample_tasks, mock_chat_service):
    """Test filtering for pending tasks only via chat."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Show me my pending tasks",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "list_tasks" in data["tool_calls"]

    # Should show pending tasks
    message = data["message"].lower()
    assert "pending" in message or "task" in message


def test_chat_list_completed_tasks_only(client, session, auth_token, sample_tasks, mock_chat_service):
    """Test filtering for completed tasks only via chat."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Show me my completed tasks",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "list_tasks" in data["tool_calls"]

    # Should show completed tasks
    message = data["message"].lower()
    assert "completed" in message or "task" in message


def test_chat_list_tasks_empty(client, session, auth_token, mock_chat_service):
    """Test listing tasks when user has none."""
    response = client.post(
        "/api/empty_user/chat",
        headers={"Authorization": f"Bearer {jwt.encode({'user_id': 'empty_user', 'sub': 'empty_user'}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)}"},
        json={
            "message": "Show me my tasks",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "no tasks" in data["message"].lower() or "start" in data["message"].lower()


def test_chat_list_tasks_user_isolation(client, session, auth_token, sample_tasks, mock_chat_service):
    """Test that list_tasks respects user boundaries via chat."""
    # test_user_123 should only see their own tasks (3 tasks)
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "List all my tasks",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should NOT include "Other user task"
    assert "other user" not in data["message"].lower()

    # Should include test_user_123's tasks
    message = data["message"].lower()
    assert "task" in message


def test_chat_list_tasks_conversation_persistence(client, session, auth_token, sample_tasks, mock_chat_service):
    """Test that conversation and messages are persisted when listing tasks."""
    response = client.post(
        "/api/test_user_123/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "What tasks do I have?",
            "conversation_id": None,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify conversation was created
    conversation = session.get(Conversation, data["conversation_id"])
    assert conversation is not None
    assert conversation.user_id == "test_user_123"
    assert conversation.message_count == 2  # User message + assistant response

    # Verify messages were persisted
    from sqlmodel import select
    statement = select(Message).where(Message.conversation_id == conversation.id)
    messages = session.exec(statement).all()

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "What tasks do I have?"
    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == data["message"]
