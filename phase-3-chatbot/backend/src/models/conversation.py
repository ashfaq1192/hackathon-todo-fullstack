"""Conversation model for AI chatbot feature.

This model stores conversation metadata and summaries for the sliding window
context management strategy. Each conversation belongs to a user and maintains
a summary field that is regenerated every 20 messages using Gemini API.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation model for persistent chat history.

    Attributes:
        id: Primary key, auto-incremented conversation ID
        user_id: Foreign key to user (from Better Auth)
        title: Optional conversation title (can be auto-generated from first message)
        summary: AI-generated summary of conversation (max 500 tokens)
                 Updated every 20 messages to maintain context efficiency
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last modified
        message_count: Total number of messages in this conversation
        messages: Relationship to Message model (one-to-many)
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)
    summary: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    message_count: int = Field(default=0, nullable=False)

    # Relationship to messages (lazy loading)
    messages: list["Message"] = Relationship(back_populates="conversation")

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_abc123",
                "title": "Task Management Discussion",
                "summary": "User discussed adding groceries and project tasks.",
                "created_at": "2026-01-04T10:00:00Z",
                "updated_at": "2026-01-04T10:30:00Z",
                "message_count": 8,
            }
        }


# Import Message model for type checking (avoid circular import)
from src.models.message import Message  # noqa: E402

Conversation.model_rebuild()
