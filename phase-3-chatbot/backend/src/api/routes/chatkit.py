"""ChatKit server routes for OpenAI ChatKit integration.

This module implements the ChatKit Python SDK server that handles
ChatKit protocol communication from the frontend widget.

Hackathon Compliance: PDF Page 17 requires "Frontend: OpenAI ChatKit"
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from src.api.dependencies import get_current_user
from src.database import get_session
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.chat_service import ChatService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatkit", tags=["chatkit"])


class ChatKitSessionRequest(BaseModel):
    """Request for creating a ChatKit session."""

    user_id: str | None = None


class ChatKitSessionResponse(BaseModel):
    """Response with ChatKit client secret."""

    client_secret: str
    session_id: str
    expires_at: str


class ThreadMetadata(BaseModel):
    """Thread metadata model."""

    title: str | None = None


class ThreadData(BaseModel):
    """Thread data model."""

    id: str
    metadata: ThreadMetadata | None = None
    created_at: str
    updated_at: str


# In-memory store for demo (in production, use database)
_threads: dict[str, dict] = {}
_thread_items: dict[str, list] = {}


@router.post(
    "/session",
    response_model=ChatKitSessionResponse,
    summary="Create ChatKit session",
    description="Creates a new ChatKit session with client credentials",
)
async def create_chatkit_session(
    request: ChatKitSessionRequest,
    current_user: str = Depends(get_current_user),
) -> ChatKitSessionResponse:
    """Create a ChatKit session for the authenticated user.

    This generates a session token that the frontend ChatKit widget
    uses to authenticate with our backend.

    Args:
        request: Session request (user_id optional, JWT takes precedence)
        current_user: Authenticated user ID from JWT

    Returns:
        ChatKitSessionResponse: Session credentials for ChatKit widget
    """
    import secrets
    from datetime import timedelta

    # Generate session secret
    session_id = f"sess_{secrets.token_hex(16)}"
    client_secret = f"ck_{secrets.token_hex(32)}"
    expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

    # Store session (in production, persist to database)
    _sessions[session_id] = {
        "user_id": current_user,
        "client_secret": client_secret,
        "expires_at": expires_at,
    }

    return ChatKitSessionResponse(
        client_secret=client_secret,
        session_id=session_id,
        expires_at=expires_at,
    )


# Session storage (in production, use Redis or database)
_sessions: dict[str, dict] = {}


def validate_chatkit_session(client_secret: str) -> str | None:
    """Validate ChatKit client secret and return user_id."""
    for session_id, session_data in _sessions.items():
        if session_data.get("client_secret") == client_secret:
            return session_data.get("user_id")
    return None


@router.post(
    "/threads",
    summary="Create a new conversation thread",
    description="Creates a new ChatKit conversation thread",
)
async def create_thread(
    request: Request,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> JSONResponse:
    """Create a new conversation thread."""
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    metadata = body.get("metadata", {})

    # Create conversation in database
    conversation = Conversation(
        user_id=current_user,
        title=metadata.get("title"),
        summary=None,
        message_count=0,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    thread_id = f"thread_{conversation.id}"

    return JSONResponse({
        "id": thread_id,
        "metadata": metadata,
        "created_at": conversation.created_at.isoformat() + "Z" if conversation.created_at else datetime.utcnow().isoformat() + "Z",
        "updated_at": conversation.updated_at.isoformat() + "Z" if conversation.updated_at else datetime.utcnow().isoformat() + "Z",
    })


@router.get(
    "/threads/{thread_id}",
    summary="Get thread details",
    description="Retrieves details for a specific thread",
)
async def get_thread(
    thread_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> JSONResponse:
    """Get thread details."""
    # Extract conversation ID from thread_id
    try:
        conv_id = int(thread_id.replace("thread_", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")

    conversation = db.get(Conversation, conv_id)
    if not conversation or conversation.user_id != current_user:
        raise HTTPException(status_code=404, detail="Thread not found")

    return JSONResponse({
        "id": thread_id,
        "metadata": {"title": conversation.title},
        "created_at": conversation.created_at.isoformat() + "Z" if conversation.created_at else "",
        "updated_at": conversation.updated_at.isoformat() + "Z" if conversation.updated_at else "",
    })


@router.post(
    "/threads/{thread_id}/messages",
    summary="Send a message to the thread",
    description="Sends a message and returns streaming AI response",
)
async def send_message(
    thread_id: str,
    request: Request,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> StreamingResponse:
    """Send a message and get streaming response.

    This is the main ChatKit message endpoint that:
    1. Receives user message
    2. Processes through our Swarm agent with MCP tools
    3. Streams response back in ChatKit format
    """
    body = await request.json()
    user_message = body.get("content", "")

    # Extract conversation ID
    try:
        conv_id = int(thread_id.replace("thread_", ""))
    except ValueError:
        conv_id = None

    async def generate_response() -> AsyncGenerator[str, None]:
        """Generate streaming ChatKit events."""
        try:
            # Process message through ChatService
            chat_service = ChatService(db=db)
            result = chat_service.process_message(
                user_message=user_message,
                conversation_id=conv_id,
                user_id=current_user,
            )

            if result.get("success"):
                response_text = result.get("message", "")
                tool_calls = result.get("tool_calls", [])

                # Send response in ChatKit SSE format
                # Start event
                yield f"event: start\ndata: {json.dumps({'thread_id': thread_id})}\n\n"

                # Tool calls events (if any)
                for tool_name in tool_calls:
                    yield f"event: tool_call\ndata: {json.dumps({'name': tool_name})}\n\n"

                # Content delta events (stream the response in chunks)
                chunk_size = 50
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i + chunk_size]
                    yield f"event: delta\ndata: {json.dumps({'content': chunk})}\n\n"

                # Done event
                yield f"event: done\ndata: {json.dumps({'thread_id': thread_id})}\n\n"

            else:
                error_msg = result.get("error", "Unknown error")
                yield f"event: error\ndata: {json.dumps({'message': error_msg})}\n\n"

        except Exception as e:
            logger.error(f"ChatKit message error: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/threads/{thread_id}/messages",
    summary="Get thread messages",
    description="Retrieves message history for a thread",
)
async def get_thread_messages(
    thread_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> JSONResponse:
    """Get messages for a thread."""
    try:
        conv_id = int(thread_id.replace("thread_", ""))
    except ValueError:
        return JSONResponse({"data": [], "has_more": False})

    # Get messages from database
    statement = select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at)
    messages = db.exec(statement).all()

    items = []
    for msg in messages:
        items.append({
            "id": f"msg_{msg.id}",
            "role": msg.role.value,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() + "Z" if msg.created_at else "",
        })

    return JSONResponse({
        "data": items,
        "has_more": False,
    })


@router.delete(
    "/threads/{thread_id}",
    summary="Delete a thread",
    description="Deletes a conversation thread",
)
async def delete_thread(
    thread_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> JSONResponse:
    """Delete a thread and its messages."""
    try:
        conv_id = int(thread_id.replace("thread_", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")

    conversation = db.get(Conversation, conv_id)
    if not conversation or conversation.user_id != current_user:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Delete messages first
    statement = select(Message).where(Message.conversation_id == conv_id)
    messages = db.exec(statement).all()
    for msg in messages:
        db.delete(msg)

    # Delete conversation
    db.delete(conversation)
    db.commit()

    return JSONResponse({"deleted": True})
