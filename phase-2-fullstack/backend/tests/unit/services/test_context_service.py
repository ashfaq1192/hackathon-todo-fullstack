"""Unit tests for the ContextService."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.context_service import ContextService


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_gemini_client():
    """Fixture for a mocked Gemini client."""
    with patch("src.services.context_service.get_gemini_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_client.return_value.chat.completions.create = AsyncMock()
        mock_get.return_value = mock_client
        yield mock_client


def test_count_tokens():
    """Test token counting."""
    service = ContextService(db=MagicMock())
    assert service.count_tokens("Hello world") == 2


def test_get_context_messages_no_summary(mock_db_session):
    """Test getting context messages without a summary."""
    conversation = Conversation(id=1, summary=None)
    messages = [
        Message(role=MessageRole.ASSISTANT, content="Hi"),
        Message(role=MessageRole.USER, content="Hello"),
    ]
    mock_db_session.get.return_value = conversation
    mock_db_session.exec.return_value.all.return_value = messages

    service = ContextService(db=mock_db_session)
    context = service.get_context_messages(conversation_id=1, include_summary=False)

    assert len(context) == 2
    assert context[0]["role"] == "user"


def test_get_context_messages_with_summary(mock_db_session):
    """Test getting context messages with a summary."""
    conversation = Conversation(id=1, summary="This is a summary.")
    messages = [Message(role=MessageRole.USER, content="Hello")]
    mock_db_session.get.return_value = conversation
    mock_db_session.exec.return_value.all.return_value = messages

    service = ContextService(db=mock_db_session)
    context = service.get_context_messages(conversation_id=1)

    assert len(context) == 2
    assert context[0]["role"] == "system"
    assert "Summary: This is a summary." in context[0]["content"]
    assert context[1]["role"] == "user"


def test_should_regenerate_summary():
    """Test the summary regeneration trigger."""
    service = ContextService(db=MagicMock())
    os.environ["CHAT_SUMMARY_INTERVAL"] = "5"
    service.summary_interval = 5

    assert service.should_regenerate_summary(Conversation(message_count=5)) is True
    assert service.should_regenerate_summary(Conversation(message_count=6)) is False
    assert service.should_regenerate_summary(Conversation(message_count=10)) is True


@pytest.mark.asyncio
async def test_generate_summary(mock_db_session, mock_gemini_client):
    """Test summary generation."""
    messages = [Message(role=MessageRole.USER, content="Test message")]
    mock_db_session.exec.return_value.all.return_value = messages
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Generated summary."
    mock_gemini_client.get_client.return_value.chat.completions.create.return_value = mock_response

    service = ContextService(db=mock_db_session)
    summary = await service.generate_summary(conversation_id=1)

    assert summary == "Generated summary."
    mock_gemini_client.get_client.return_value.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_update_conversation_summary(mock_db_session, mock_gemini_client):
    """Test updating the conversation summary."""
    conversation = Conversation(id=1, message_count=20)
    mock_db_session.get.return_value = conversation
    
    # Mock generate_summary to avoid actual API call
    with patch.object(ContextService, 'generate_summary', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "New summary"
        
        service = ContextService(db=mock_db_session)
        service.summary_interval = 20
        
        await service.update_conversation_summary(conversation_id=1)

        assert conversation.summary == "New summary"
        mock_db_session.add.assert_called_with(conversation)
        mock_db_session.commit.assert_called()
