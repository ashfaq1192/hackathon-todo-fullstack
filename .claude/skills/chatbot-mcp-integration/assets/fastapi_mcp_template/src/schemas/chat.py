from pydantic import BaseModel


class ChatMessage(BaseModel):
    """
    Request model for a user's chat message.
    """
    content: str


class ChatResponse(BaseModel):
    """
    Response model for the chatbot's reply.
    """
    response: str
