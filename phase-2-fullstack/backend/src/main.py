"""
Main FastAPI application entry point.

This module creates the FastAPI app instance, registers exception handlers,
and includes all API routes.
"""

import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from src.core.errors import (
    AuthError,
    DatabaseError,
    ForbiddenError,
    NotFoundError,
    auth_error_handler,
    database_error_handler,
    forbidden_error_handler,
    general_exception_handler,
    http_exception_handler,
    not_found_error_handler,
)
from src.middleware.rate_limiter import rate_limit_middleware
from src.database import init_db, get_engine
# Import models to register them with SQLModel.metadata before table creation
from src.models import Task  # noqa: F401
from src.models.conversation import Conversation  # noqa: F401
from src.models.message import Message  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Initialize database tables
    - Shutdown: Cleanup resources

    Args:
        app: The FastAPI application instance
    """
    # Startup
    import os

    # Skip database initialization during tests (test fixtures handle it)
    if os.environ.get("PYTEST_IN_PROGRESS") != "1":
        logger.info("Starting up FastAPI application...")
        try:
            engine = get_engine()
            init_db(engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    else:
        logger.info("Test mode: skipping app startup database initialization")

    yield

    # Shutdown
    if os.environ.get("PYTEST_IN_PROGRESS") != "1":
        logger.info("Shutting down FastAPI application...")


# Create FastAPI application instance
app = FastAPI(
    title="Todo API",
    description="RESTful API for Todo CRUD Operations (Phase II - Stage 2)",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware to allow frontend requests
import os

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
    allow_headers=["*"],  # Allow all headers
)

# Add rate limiting middleware for chat endpoint (T059)
# Enforces 15 requests/minute to match Gemini API free tier limits
from starlette.middleware.base import BaseHTTPMiddleware
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)


# Register Exception Handlers (T037-T040)

# Custom exception handlers
app.add_exception_handler(AuthError, auth_error_handler)
app.add_exception_handler(ForbiddenError, forbidden_error_handler)
app.add_exception_handler(NotFoundError, not_found_error_handler)

# HTTP exception handler
app.add_exception_handler(HTTPException, http_exception_handler)

# Database error handler
app.add_exception_handler(SQLAlchemyError, database_error_handler)
app.add_exception_handler(DatabaseError, database_error_handler)

# General exception handler (catch-all)
app.add_exception_handler(Exception, general_exception_handler)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Simple status response indicating the API is running

    Example response:
        {
            "status": "healthy",
            "service": "Todo API",
            "version": "0.2.0"
        }
    """
    return {
        "status": "healthy",
        "service": "Todo API",
        "version": "0.2.0",
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message and links to documentation

    Example response:
        {
            "message": "Welcome to Todo API",
            "docs": "/docs",
            "health": "/health"
        }
    """
    return {
        "message": "Welcome to Todo API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }



# Register API Routes (T054)
from src.api.routes.tasks import router as tasks_router
from src.api.routes.chat import router as chat_router
from src.api.routes.mcp import router as mcp_router
from src.api.routes.chatkit import router as chatkit_router

app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(mcp_router, prefix="/api", tags=["MCP"])
app.include_router(chatkit_router, prefix="/api", tags=["ChatKit"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
