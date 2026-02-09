"""Chat API routes for AI-powered conversational task management.

This module implements the chat endpoint for Phase III:
- POST /api/{user_id}/chat - Process natural language message and return response
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from src.api.dependencies import get_current_user
from src.database import get_session
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.chat_service import ChatService
from src.services.context_service import ContextService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create APIRouter instance for chat endpoints
router = APIRouter()


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID for context")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": 1,
            }
        }
    }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    success: bool
    message: str = Field(..., description="Assistant's response")
    conversation_id: int = Field(..., description="Conversation ID for this chat")
    message_id: int = Field(..., description="ID of the assistant's message")
    tool_calls: list[str] = Field(default_factory=list, description="Tools that were executed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Task 'Buy groceries' created successfully! ✅",
                "conversation_id": 1,
                "message_id": 42,
                "tool_calls": ["add_task"],
            }
        }
    }


# T058: Comprehensive error messages for all edge cases
class ChatErrorResponse(BaseModel):
    """Error response model for chat endpoint."""

    detail: str = Field(..., description="Human-readable error description")
    error_code: str = Field(..., description="Machine-readable error code")
    suggestions: list[str] = Field(default_factory=list, description="Suggestions to resolve the error")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Rate limit exceeded. Please wait before sending another message.",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "suggestions": ["Wait 60 seconds before retrying", "Reduce message frequency"],
            }
        }
    }


# Error codes for chat endpoint
class ChatErrorCodes:
    """Standardized error codes for chat endpoint (T058)."""

    AUTH_MISSING = "AUTH_MISSING"
    AUTH_INVALID = "AUTH_INVALID"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    USER_MISMATCH = "USER_MISMATCH"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    CONVERSATION_ACCESS_DENIED = "CONVERSATION_ACCESS_DENIED"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    MESSAGE_EMPTY = "MESSAGE_EMPTY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    AI_SERVICE_TIMEOUT = "AI_SERVICE_TIMEOUT"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def get_error_suggestions(error_code: str) -> list[str]:
    """Get helpful suggestions for error codes (T058).

    Args:
        error_code: The standardized error code

    Returns:
        list[str]: List of suggestions to help the user resolve the error
    """
    suggestions_map = {
        ChatErrorCodes.AUTH_MISSING: [
            "Please log in to use the chat feature",
            "If you're logged in, try refreshing the page",
        ],
        ChatErrorCodes.AUTH_INVALID: [
            "Your session may have expired. Please log in again",
            "Clear your browser cookies and try logging in again",
        ],
        ChatErrorCodes.AUTH_EXPIRED: [
            "Your session has expired. Please log in again",
            "Click the login button to start a new session",
        ],
        ChatErrorCodes.USER_MISMATCH: [
            "You can only access your own conversations",
            "Check that you're logged in with the correct account",
        ],
        ChatErrorCodes.CONVERSATION_NOT_FOUND: [
            "Start a new conversation instead",
            "The conversation may have been deleted",
        ],
        ChatErrorCodes.MESSAGE_TOO_LONG: [
            "Messages must be 2000 characters or less",
            "Try breaking your message into smaller parts",
        ],
        ChatErrorCodes.MESSAGE_EMPTY: [
            "Type a message before sending",
            "Try saying 'Show my tasks' or 'Add a task to buy groceries'",
        ],
        ChatErrorCodes.RATE_LIMIT_EXCEEDED: [
            "Wait 60 seconds before sending another message",
            "You can send up to 15 messages per minute",
        ],
        ChatErrorCodes.AI_SERVICE_UNAVAILABLE: [
            "The AI service is temporarily unavailable",
            "Please try again in a few minutes",
            "Your message has been saved and you can retry",
        ],
        ChatErrorCodes.AI_SERVICE_TIMEOUT: [
            "The AI took too long to respond",
            "Try sending a shorter message",
            "Please try again",
        ],
        ChatErrorCodes.DATABASE_ERROR: [
            "A temporary database error occurred",
            "Please try again in a moment",
            "If the problem persists, contact support",
        ],
        ChatErrorCodes.INTERNAL_ERROR: [
            "An unexpected error occurred",
            "Please try again",
            "If the problem persists, contact support",
        ],
    }
    return suggestions_map.get(error_code, ["Please try again"])


# User Story 1: Natural Language Task Creation (T016-T017)
@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process chat message with AI assistant",
    description="Send a natural language message to the AI assistant for task management",
    responses={
        200: {"description": "Successfully processed message and returned response"},
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User ID in URL doesn't match JWT token user_id"},
        422: {"description": "Validation error - Invalid message format"},
        500: {"description": "Internal server error - Chat processing failed"},
    },
)
async def process_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChatResponse:
    """Process natural language message through AI assistant.

    **Security (FR-006)**:
    - Extracts user_id from validated JWT token claims (NOT from URL parameter)
    - Validates that JWT user_id matches URL parameter to prevent spoofing
    - All conversations and messages are isolated by authenticated user_id

    **Stateless Architecture (TC-006)**:
    - No session state stored in server memory
    - All conversation state persists in PostgreSQL
    - Enables horizontal scaling on Vercel serverless functions

    Args:
        user_id: User ID from URL path (must match JWT token user_id)
        request: Chat request with message and optional conversation_id
        current_user: User ID extracted from JWT token (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        ChatResponse: Assistant's response with conversation metadata

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If URL user_id doesn't match JWT user_id
        HTTPException 500: If chat processing fails
    """
    # CRITICAL (FR-006): Validate user_id from JWT matches URL parameter
    # This prevents users from accessing other users' conversations by changing URL
    if current_user != user_id:
        logger.warning(
            f"User ID mismatch: JWT user_id={current_user}, URL user_id={user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "User ID in URL doesn't match authenticated user",
                "error_code": ChatErrorCodes.USER_MISMATCH,
                "suggestions": get_error_suggestions(ChatErrorCodes.USER_MISMATCH),
            },
        )

    # Get or create conversation
    conversation_id = request.conversation_id
    if conversation_id:
        # Retrieve existing conversation and verify ownership
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Conversation {conversation_id} not found or not accessible",
                    "error_code": ChatErrorCodes.CONVERSATION_NOT_FOUND,
                    "suggestions": get_error_suggestions(ChatErrorCodes.CONVERSATION_NOT_FOUND),
                },
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user,
            title=None,  # Can be auto-generated from first message later
            summary=None,
            message_count=0,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        conversation_id = conversation.id

    # Save user message to database
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=request.message,
    )
    session.add(user_message)
    session.commit()

    # Update conversation message count
    conversation.message_count += 1
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    # Process message through ChatService (Swarm Agent + Gemini)
    try:
        chat_service = ChatService(db=session)
        result = chat_service.process_message(
            user_message=request.message,
            conversation_id=conversation_id,
            user_id=current_user,
        )

        # Determine the message content for the assistant's response
        assistant_response_content = result.get("message", "An unknown error occurred with the AI assistant.")
        # Save assistant response to database
        assistant_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=assistant_response_content,
        )
        session.add(assistant_message)
        session.commit()
        session.refresh(assistant_message)

        # Update conversation message count again for assistant message
        conversation.message_count += 1
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # T038-T039: Check if summary should be regenerated (every 20 messages)
        context_service = ContextService(db=session)
        if context_service.should_regenerate_summary(conversation):
            try:
                await context_service.update_conversation_summary(conversation_id)
                logger.info(f"Summary regenerated for conversation {conversation_id}")
            except Exception as summary_error:
                logger.warning(f"Failed to regenerate summary: {summary_error}")

        return ChatResponse(
            success=result.get("success", False),
            message=assistant_response_content,
            conversation_id=conversation_id,
            message_id=assistant_message.id,
            tool_calls=result.get("tool_calls", []),
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        session.rollback()

        # T058: Determine specific error code based on exception type
        error_str = str(e).lower()
        if "circuit_breaker" in error_str:
            error_code = ChatErrorCodes.AI_SERVICE_UNAVAILABLE
        elif "timeout" in error_str:
            error_code = ChatErrorCodes.AI_SERVICE_TIMEOUT
        elif "database" in error_str or "sql" in error_str:
            error_code = ChatErrorCodes.DATABASE_ERROR
        else:
            error_code = ChatErrorCodes.INTERNAL_ERROR

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Failed to process message. Please try again.",
                "error_code": error_code,
                "suggestions": get_error_suggestions(error_code),
            },
        )
