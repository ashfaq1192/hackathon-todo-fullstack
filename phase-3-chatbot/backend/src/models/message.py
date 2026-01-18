"""Message model for AI chatbot feature.

This model stores individual messages in conversations. Each message has a role
(user or assistant) and belongs to a conversation. Messages are used to build
the sliding window context for Gemini API calls.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


class MessageRole(str, Enum):
    """Message role enumeration.

    Attributes:
        USER: Message from the user
        ASSISTANT: Message from the AI assistant (Gemini)
    """

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message model for conversation history.

    Attributes:
        id: Primary key, auto-incremented message ID
        conversation_id: Foreign key to Conversation
        role: Message role (user or assistant)
        content: Message text content
        created_at: Timestamp when message was created
        token_count: Optional token count for context management
        conversation: Relationship to Conversation model (many-to-one)
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: MessageRole = Field(
        sa_column=Column(SAEnum(MessageRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    )
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    token_count: Optional[int] = Field(default=None)

    # Relationship to conversation (lazy loading)
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2026-01-04T10:00:00Z",
                "token_count": 8,
            }
        }


# Import Conversation model for type checking (avoid circular import)
from src.models.conversation import Conversation  # noqa: E402

Message.model_rebuild()
