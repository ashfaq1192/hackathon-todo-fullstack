from datetime import datetime, UTC
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class Message(SQLModel, table=True):
    """
    SQLModel for a single message within a conversation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(max_length=20, nullable=False) # e.g., "user", "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
