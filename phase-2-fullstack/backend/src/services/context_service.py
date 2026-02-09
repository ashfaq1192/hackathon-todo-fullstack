"""Context service for conversation sliding window and summarization.

This service implements the stateless context management strategy:
1. Fetch the N most recent messages from database (sliding window)
2. Include conversation summary if available (regenerated every 20 messages)
3. Build context array for Gemini API with token limit enforcement
"""

import os
from typing import Optional

import tiktoken
from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.gemini_client import get_gemini_client


class ContextService:
    """Service for managing conversation context with sliding window.

    This service provides:
    - Sliding window context (default: 15 most recent messages)
    - Summary integration for token efficiency
    - Token counting with tiktoken
    - Summary regeneration trigger (every 20 messages)

    Environment Variables:
        CHAT_CONTEXT_WINDOW_SIZE: Number of recent messages to include (default: 15)
        CHAT_SUMMARY_INTERVAL: Message count trigger for summary regeneration (default: 20)
        CHAT_SUMMARY_MAX_TOKENS: Maximum tokens for summary (default: 500)
    """

    def __init__(self, db: Session):
        """Initialize context service.

        Args:
            db: SQLModel database session
        """
        self.db = db
        self.window_size = int(os.getenv("CHAT_CONTEXT_WINDOW_SIZE", "15"))
        self.summary_interval = int(os.getenv("CHAT_SUMMARY_INTERVAL", "20"))
        self.summary_max_tokens = int(os.getenv("CHAT_SUMMARY_MAX_TOKENS", "500"))

        # Initialize tiktoken encoder for token counting
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4")
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            int: Number of tokens in text
        """
        return len(self.encoder.encode(text))

    def get_context_messages(
        self, conversation_id: int, include_summary: bool = True
    ) -> list[dict]:
        """Build context messages array for Gemini API.

        Fetches the N most recent messages from database and optionally includes
        the conversation summary as a system message.

        Args:
            conversation_id: Conversation ID to fetch messages for
            include_summary: Whether to include conversation summary (default: True)

        Returns:
            list[dict]: Array of message dictionaries with 'role' and 'content' keys
                        Format: [{"role": "system", "content": "..."}, ...]

        Example:
            >>> context = service.get_context_messages(conversation_id=1)
            >>> # Returns: [
            >>> #   {"role": "system", "content": "Summary: User discussed tasks..."},
            >>> #   {"role": "user", "content": "Add groceries"},
            >>> #   {"role": "assistant", "content": "Task added!"},
            >>> # ]
        """
        context = []

        # Fetch conversation with summary
        conversation = self.db.get(Conversation, conversation_id)
        if not conversation:
            return context

        # Add summary as system message if available and requested
        if include_summary and conversation.summary:
            context.append({"role": "system", "content": f"Summary: {conversation.summary}"})

        # Fetch N most recent messages (sliding window)
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(self.window_size)
        )
        messages = self.db.exec(statement).all()

        # Reverse to chronological order and convert to context format
        for message in reversed(messages):
            context.append({"role": message.role.value, "content": message.content})

        return context

    def should_regenerate_summary(self, conversation: Conversation) -> bool:
        """Check if conversation summary should be regenerated.

        Summary is regenerated every CHAT_SUMMARY_INTERVAL messages (default: 20).

        Args:
            conversation: Conversation to check

        Returns:
            bool: True if summary should be regenerated
        """
        return conversation.message_count > 0 and conversation.message_count % self.summary_interval == 0

    async def generate_summary(self, conversation_id: int) -> Optional[str]:
        """Generate or regenerate conversation summary using Gemini.

        Fetches all messages in the conversation and asks Gemini to summarize
        them in a concise format (max CHAT_SUMMARY_MAX_TOKENS tokens).

        Args:
            conversation_id: Conversation ID to summarize

        Returns:
            Optional[str]: Generated summary text, or None if generation fails
        """
        # Fetch all messages for summarization
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages = self.db.exec(statement).all()

        if not messages:
            return None

        # Build message history for summarization
        message_history = []
        for msg in messages:
            message_history.append(f"{msg.role.value}: {msg.content}")

        conversation_text = "\n".join(message_history)

        # Generate summary with Gemini
        try:
            gemini_client = get_gemini_client()
            client = gemini_client.get_client()

            summary_prompt = f"""Summarize the following conversation in a concise format (max {self.summary_max_tokens} tokens).
Focus on key topics, tasks discussed, and important decisions.

Conversation:
{conversation_text}

Summary:"""

            response = await client.chat.completions.create(
                model=gemini_client.model,
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=self.summary_max_tokens,
            )

            summary = response.choices[0].message.content
            return summary.strip() if summary else None

        except Exception as e:
            # Log error but don't crash - summary is optional
            print(f"Error generating summary: {e}")
            return None

    async def update_conversation_summary(self, conversation_id: int) -> None:
        """Update conversation summary if regeneration interval reached.

        This method checks if summary should be regenerated based on message count,
        generates a new summary, and updates the conversation record.

        Args:
            conversation_id: Conversation ID to update summary for
        """
        conversation = self.db.get(Conversation, conversation_id)
        if not conversation:
            return

        if self.should_regenerate_summary(conversation):
            summary = await self.generate_summary(conversation_id)
            if summary:
                conversation.summary = summary
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)
