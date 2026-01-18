from datetime import datetime, UTC
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Conversation(SQLModel, table=True):
    """
    SQLModel for a user's conversation with the chatbot.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False) # Link to the user who owns the conversation
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    messages: List["Message"] = Relationship(back_populates="conversation")
