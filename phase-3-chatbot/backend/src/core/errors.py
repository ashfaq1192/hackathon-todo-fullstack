"""
Error handling and custom exceptions for the API.

This module defines custom exception classes and global exception handlers
for consistent error responses across all API endpoints.
"""

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom Exception Classes


class AuthError(Exception):
    """
    Exception raised for authentication failures.

    Raised when JWT token validation fails, token is expired,
    or authentication credentials are invalid.
    """

    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """
    Exception raised for authorization failures.

    Raised when a user attempts to access a resource they don't have
    permission to access (e.g., accessing another user's tasks).
    """

    def __init__(self, message: str = "Access forbidden"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """
    Exception raised when a requested resource is not found.

    Raised when a task, user, or other resource does not exist
    in the database.
    """

    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    """
    Exception raised for database operation failures.

    Raised when a database query, connection, or transaction fails.
    """

    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)


# Exception Handlers


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    T038: Handle FastAPI HTTPException and return JSON response.

    Args:
        request: The incoming HTTP request
        exc: The HTTPException raised

    Returns:
        JSON response with error details and appropriate status code

    Example response:
        {
            "error": "Unauthorized",
            "message": "Invalid authentication credentials",
            "status_code": 401
        }
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    T039: Handle database errors and return 500 Internal Server Error.

    Args:
        request: The incoming HTTP request
        exc: The SQLAlchemyError raised

    Returns:
        JSON response with generic error message (hides internal DB details)

    Example response:
        {
            "error": "Database Error",
            "message": "An error occurred while processing your request",
            "status_code": 500
        }
    """
    logger.error(f"Database error: {type(exc).__name__} - {str(exc)}")

    # Don't expose internal database errors to clients
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "An error occurred while processing your request. Please try again later.",
            "status_code": 500,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    T040: Handle all unhandled exceptions and return 500 with generic message.

    This is the catch-all handler for any exception not caught by
    more specific handlers. It prevents internal error details from
    leaking to clients.

    Args:
        request: The incoming HTTP request
        exc: The unhandled exception

    Returns:
        JSON response with generic error message

    Example response:
        {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500
        }
    """
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please contact support if this persists.",
            "status_code": 500,
        },
    )


async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    """
    Handle custom AuthError exceptions and return 401 Unauthorized.

    Args:
        request: The incoming HTTP request
        exc: The AuthError raised

    Returns:
        JSON response with authentication error details
    """
    logger.warning(f"Authentication error: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "Authentication Error",
            "message": exc.message,
            "status_code": 401,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """
    Handle custom ForbiddenError exceptions and return 403 Forbidden.

    Args:
        request: The incoming HTTP request
        exc: The ForbiddenError raised

    Returns:
        JSON response with authorization error details
    """
    logger.warning(f"Authorization error: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Forbidden",
            "message": exc.message,
            "status_code": 403,
        },
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """
    Handle custom NotFoundError exceptions and return 404 Not Found.

    Args:
        request: The incoming HTTP request
        exc: The NotFoundError raised

    Returns:
        JSON response with not found error details
    """
    logger.info(f"Resource not found: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "status_code": 404,
        },
    )
