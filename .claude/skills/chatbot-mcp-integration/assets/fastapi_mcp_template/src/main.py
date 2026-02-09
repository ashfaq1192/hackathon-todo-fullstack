from fastapi import FastAPI, Depends, Request
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlmodel import Session

from src.database.connection import create_db_and_tables, get_session
from src.api.routes import chat, mcp
from src.core.middleware import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous context manager for managing the lifecycle of the FastAPI application.
    It ensures the database tables are created before the application starts and
    can perform cleanup actions when the application shuts down.
    """
    print("Creating database tables...")
    create_db_and_tables()
    yield


app = FastAPI(
    title="AI Chatbot Backend",
    version="1.0.0",
    description="FastAPI backend for AI-powered Todo Chatbot with MCP tools.",
    lifespan=lifespan,
)

# Apply authentication middleware
app.middleware("http")(auth_middleware)

# Include API routes
app.include_router(chat.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP Tools"])


@app.get("/")
async def root():
    return {"message": "AI Chatbot Backend is running!"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint to ensure the application is running.
    """
    return {"status": "ok"}
