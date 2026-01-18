"""
JWT authentication logic for API endpoints.

This module handles JWT token validation and user ID extraction
for authenticating API requests.
"""

import logging
from datetime import UTC, datetime

from jose import JWTError, jwt

from src.config import JWT_ALGORITHM, JWT_SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Exception raised for authentication failures."""

    pass


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string (without "Bearer " prefix)

    Returns:
        Dictionary containing token claims (sub, user_id, exp, etc.)

    Raises:
        AuthError: If token is invalid, expired, or signature verification fails

    Example:
        claims = decode_jwt_token("eyJ...")
        user_id = claims.get("user_id")
    """
    if not JWT_SECRET_KEY:
        logger.error("JWT_SECRET_KEY not configured")
        raise AuthError("JWT authentication not configured")

    try:
        # Decode and verify JWT token
        claims = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Verify token hasn't expired (python-jose does this automatically, but we can add extra checks)
        exp = claims.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=UTC) < datetime.now(UTC):
            logger.warning("Token expired")
            raise AuthError("Token has expired")

        return claims

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise AuthError(f"Invalid token: {str(e)}") from e


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user_id from JWT token claims.

    Args:
        token: JWT token string (without "Bearer " prefix)

    Returns:
        User ID string extracted from token claims

    Raises:
        AuthError: If token is invalid or user_id claim is missing

    Example:
        user_id = extract_user_id_from_token("eyJ...")
    """
    claims = decode_jwt_token(token)

    # Try to get user_id from claims (supports both "user_id" and "sub" claims)
    user_id = claims.get("user_id") or claims.get("sub")

    if not user_id:
        logger.warning("Token missing user_id claim")
        raise AuthError("Token missing user_id claim")

    return user_id
