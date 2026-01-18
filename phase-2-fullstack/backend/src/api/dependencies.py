"""
FastAPI dependencies for authentication and authorization.

This module provides reusable dependencies for JWT validation
and user ID verification in API endpoints.
"""

import logging

from fastapi import Header, HTTPException, status

from src.core.auth import AuthError, extract_user_id_from_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_user(authorization: str | None = Header(None)) -> str:
    """
    FastAPI dependency to extract and validate current user from JWT token.

    Args:
        authorization: Authorization header value (expected format: "Bearer <token>")

    Returns:
        User ID extracted from valid JWT token

    Raises:
        HTTPException: 401 Unauthorized if token is missing, malformed, or invalid

    Example:
        @app.get("/api/{user_id}/tasks")
        def list_tasks(user_id: str, current_user: str = Depends(get_current_user)):
            verify_user_id_match(current_user, user_id)
            ...
    """
    # Verify Authorization header format
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or malformed Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected format: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token (remove "Bearer " prefix)
    token = authorization[7:]  # len("Bearer ") = 7

    try:
        # Extract user_id from token
        user_id = extract_user_id_from_token(token)
        logger.info(f"User authenticated: {user_id}")
        return user_id

    except AuthError as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def verify_user_id_match(current_user: str, path_user_id: str) -> None:
    """
    Verify that the authenticated user matches the user_id in the URL path.

    This prevents users from accessing other users' resources.

    Args:
        current_user: User ID from JWT token (authenticated user)
        path_user_id: User ID from URL path parameter

    Raises:
        HTTPException: 403 Forbidden if user_id mismatch

    Example:
        @app.get("/api/{user_id}/tasks")
        def list_tasks(user_id: str, current_user: str = Depends(get_current_user)):
            verify_user_id_match(current_user, user_id)
            # Now safe to proceed - user is authorized
            ...
    """
    if current_user != path_user_id:
        logger.warning(
            f"Authorization failed: user '{current_user}' attempted to access user '{path_user_id}' resources"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot access resources for user '{path_user_id}'",
        )

    logger.debug(f"Authorization successful: user '{current_user}' accessing own resources")
