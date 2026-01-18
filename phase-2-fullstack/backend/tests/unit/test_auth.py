"""
Unit tests for JWT authentication module.

This module tests JWT token validation, decoding, and user ID extraction.
"""

import pytest
from datetime import UTC, datetime, timedelta
from jose import jwt
from fastapi import HTTPException

from src.core.auth import AuthError, decode_jwt_token, extract_user_id_from_token
from src.api.dependencies import get_current_user, verify_user_id_match
from src.config import JWT_SECRET_KEY, JWT_ALGORITHM


def create_test_token(user_id: str, exp_minutes: int = 30) -> str:
    """
    Helper function to create a valid JWT token for testing.

    Args:
        user_id: User ID to include in token
        exp_minutes: Token expiration time in minutes (default: 30)

    Returns:
        Encoded JWT token string
    """
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "exp": datetime.now(UTC) + timedelta(minutes=exp_minutes),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def test_decode_jwt_token_valid():
    """
    T033: Verify decode_jwt_token() extracts claims correctly from valid token.
    """
    # Create valid token
    token = create_test_token("user123")

    # Decode token
    claims = decode_jwt_token(token)

    # Verify claims
    assert claims is not None
    assert claims.get("user_id") == "user123"
    assert claims.get("sub") == "user123"
    assert "exp" in claims
    assert "iat" in claims


def test_decode_jwt_token_invalid_signature():
    """
    T034: Verify decode_jwt_token() raises AuthError for invalid signature.
    """
    # Create token with wrong secret
    wrong_secret_token = jwt.encode(
        {"user_id": "user123", "exp": datetime.now(UTC) + timedelta(minutes=30)},
        "wrong-secret-key",
        algorithm=JWT_ALGORITHM,
    )

    # Should raise AuthError
    with pytest.raises(AuthError) as exc_info:
        decode_jwt_token(wrong_secret_token)

    assert "Invalid token" in str(exc_info.value)


def test_decode_jwt_token_expired():
    """
    T034: Verify decode_jwt_token() raises AuthError for expired token.
    """
    # Create expired token (expired 1 minute ago)
    expired_token = create_test_token("user123", exp_minutes=-1)

    # Should raise AuthError
    with pytest.raises(AuthError) as exc_info:
        decode_jwt_token(expired_token)

    assert "Invalid token" in str(exc_info.value) or "expired" in str(exc_info.value).lower()


def test_decode_jwt_token_malformed():
    """
    T034: Verify decode_jwt_token() raises AuthError for malformed token.
    """
    malformed_tokens = [
        "not-a-jwt-token",
        "invalid.token.format",
        "",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
    ]

    for malformed_token in malformed_tokens:
        with pytest.raises(AuthError):
            decode_jwt_token(malformed_token)


def test_extract_user_id_from_token_valid():
    """
    T035: Verify extract_user_id_from_token() returns user_id from valid token.
    """
    token = create_test_token("user456")

    user_id = extract_user_id_from_token(token)

    assert user_id == "user456"


def test_extract_user_id_from_token_uses_sub_claim():
    """
    T035: Verify extract_user_id_from_token() can extract from 'sub' claim.
    """
    # Create token with only 'sub' claim (no 'user_id')
    payload = {
        "sub": "user789",
        "exp": datetime.now(UTC) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    user_id = extract_user_id_from_token(token)

    assert user_id == "user789"


def test_extract_user_id_from_token_missing_claim():
    """
    T035: Verify extract_user_id_from_token() raises AuthError if user_id missing.
    """
    # Create token without user_id or sub claim
    payload = {
        "exp": datetime.now(UTC) + timedelta(minutes=30),
        "email": "test@example.com",
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    with pytest.raises(AuthError) as exc_info:
        extract_user_id_from_token(token)

    assert "missing user_id claim" in str(exc_info.value).lower()


def test_extract_user_id_from_token_invalid():
    """
    T035: Verify extract_user_id_from_token() raises AuthError for invalid token.
    """
    with pytest.raises(AuthError):
        extract_user_id_from_token("invalid-token")


def test_get_current_user_valid_token():
    """
    Verify get_current_user() dependency extracts user from valid Bearer token.
    """
    token = create_test_token("user123")
    authorization_header = f"Bearer {token}"

    user_id = get_current_user(authorization_header)

    assert user_id == "user123"


def test_get_current_user_missing_bearer_prefix():
    """
    Verify get_current_user() raises 401 if Authorization header missing 'Bearer ' prefix.
    """
    token = create_test_token("user123")

    # Missing 'Bearer ' prefix
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token)

    assert exc_info.value.status_code == 401
    assert "Missing or invalid Authorization header" in exc_info.value.detail


def test_get_current_user_missing_header():
    """
    Verify get_current_user() raises 401 if Authorization header is missing.
    """
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("")

    assert exc_info.value.status_code == 401


def test_get_current_user_invalid_token():
    """
    Verify get_current_user() raises 401 for invalid token.
    """
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("Bearer invalid-token")

    assert exc_info.value.status_code == 401


def test_verify_user_id_match_success():
    """
    T036: Verify verify_user_id_match() succeeds when user IDs match.
    """
    # Should not raise exception
    verify_user_id_match("user123", "user123")


def test_verify_user_id_match_failure():
    """
    T036: Verify verify_user_id_match() raises 403 for user ID mismatch.
    """
    with pytest.raises(HTTPException) as exc_info:
        verify_user_id_match("user123", "user456")

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail
    assert "user456" in exc_info.value.detail
