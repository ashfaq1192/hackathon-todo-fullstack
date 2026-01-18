import os
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from src.database.connection import get_session
from src.services.chat_service import get_chat_service
from src.schemas.chat import ChatMessage, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Main chat endpoint for the AI-powered chatbot.
    Receives a user message, processes it with the AI agent, and returns a response.
    """
    user_id = request.state.user_id  # Assume user_id is set by authentication middleware
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    chat_service = get_chat_service(session, user_id)
    
    # Process the message with the AI agent
    response_content = await chat_service.process_message(message.content)

    return ChatResponse(response=response_content)

# Optional: Add a ChatKit session endpoint if needed by the frontend
@router.post("/session")
async def chatkit_session_endpoint(request: Request):
    """
    Provides session configuration for OpenAI ChatKit, including authentication context.
    """
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # In a real implementation, you might generate a short-lived token here
    # or return configuration data that includes the user_id for ChatKit.
    return {
        "session_id": f"chatkit-session-{user_id}-{os.urandom(8).hex()}",
        "user_id": user_id,
        "config": {
            "//": "Add ChatKit specific config here based on user_id"
        }
    }
