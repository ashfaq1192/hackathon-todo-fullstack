"""Rate limiting middleware for chat endpoint.

This module implements a sliding window rate limiter to enforce Gemini API rate limits:
- 15 requests per minute per user (matching Gemini's free tier limit)
- Returns 429 Too Many Requests when limit exceeded

Environment Variables:
    RATE_LIMIT_REQUESTS: Maximum requests per window (default: 15)
    RATE_LIMIT_WINDOW_SECONDS: Window duration in seconds (default: 60)
"""

import os
import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """Sliding window rate limiter for per-user request throttling.

    This rate limiter uses a sliding window algorithm to track requests
    per user and enforce rate limits. It's designed to match Gemini API's
    free tier limit of 15 requests per minute.

    Attributes:
        max_requests: Maximum number of requests allowed per window
        window_seconds: Duration of the sliding window in seconds
        requests: Dictionary mapping user_id to list of request timestamps

    Example:
        >>> limiter = RateLimiter(max_requests=15, window_seconds=60)
        >>> if not limiter.is_allowed("user_123"):
        ...     raise HTTPException(status_code=429, detail="Rate limit exceeded")
    """

    def __init__(
        self,
        max_requests: int | None = None,
        window_seconds: int | None = None,
        disable_for_tests: bool = False,
    ):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window (default: from env or 15)
            window_seconds: Duration of the sliding window in seconds (default: from env or 60)
            disable_for_tests: If True, rate limiting will be bypassed (for testing)
        """
        self.max_requests = max_requests or int(
            os.getenv("RATE_LIMIT_REQUESTS", "15")
        )
        self.window_seconds = window_seconds or int(
            os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
        )
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.is_disabled = disable_for_tests or os.getenv("DISABLE_RATE_LIMITER_FOR_TESTS", "0").lower() in ("true", "1")

    def _clean_old_requests(self, user_id: str) -> None:
        """Remove requests outside the current window.

        Args:
            user_id: User identifier to clean requests for
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        self.requests[user_id] = [
            ts for ts in self.requests[user_id] if ts > cutoff_time
        ]

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to make a request.

        Args:
            user_id: User identifier to check

        Returns:
            bool: True if request is allowed, False if rate limited
        """
        if self.is_disabled:
            return True
        self._clean_old_requests(user_id)
        return len(self.requests[user_id]) < self.max_requests

    def record_request(self, user_id: str) -> None:
        """Record a new request for the user.

        Args:
            user_id: User identifier making the request
        """
        if self.is_disabled:
            return
        self.requests[user_id].append(time.time())

    def get_retry_after(self, user_id: str) -> int:
        """Get seconds until user can make another request.

        Args:
            user_id: User identifier to check

        Returns:
            int: Seconds until rate limit resets (minimum 1)
        """
        if not self.requests[user_id]:
            return 0

        oldest_request = min(self.requests[user_id])
        retry_after = self.window_seconds - (time.time() - oldest_request)
        return max(1, int(retry_after))

    def get_remaining_requests(self, user_id: str) -> int:
        """Get number of remaining requests in current window.

        Args:
            user_id: User identifier to check

        Returns:
            int: Number of requests remaining
        """
        self._clean_old_requests(user_id)
        return max(0, self.max_requests - len(self.requests[user_id]))


# Singleton rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create singleton rate limiter instance.

    Returns:
        RateLimiter: Singleton rate limiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        """Initialize rate limit exception.

        Args:
            retry_after: Seconds until rate limit resets
        """
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please wait {retry_after} seconds before retrying.",
            headers={"Retry-After": str(retry_after)},
        )


async def rate_limit_middleware(request: Request, call_next: Callable):
    """FastAPI middleware for rate limiting chat endpoint.

    This middleware only applies to chat endpoints (/api/{user_id}/chat).
    Other endpoints are not rate limited.

    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler

    Returns:
        Response from next handler or 429 error if rate limited
    """
    # Only rate limit chat endpoints
    if "/chat" not in request.url.path:
        return await call_next(request)

    # Extract user_id from path (format: /api/{user_id}/chat)
    path_parts = request.url.path.split("/")
    user_id = None
    for i, part in enumerate(path_parts):
        if part == "api" and i + 1 < len(path_parts):
            user_id = path_parts[i + 1]
            break

    if not user_id or user_id == "chat":
        # Can't determine user_id, let the request through
        # (will be caught by auth middleware anyway)
        return await call_next(request)

    # Check rate limit
    rate_limiter = get_rate_limiter()

    if not rate_limiter.is_allowed(user_id):
        retry_after = rate_limiter.get_retry_after(user_id)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": f"Rate limit exceeded. Please wait {retry_after} seconds before retrying.",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    # Record request and proceed
    rate_limiter.record_request(user_id)

    # Add rate limit headers to response
    response = await call_next(request)

    # Add rate limit info to response headers
    remaining = rate_limiter.get_remaining_requests(user_id)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(rate_limiter.window_seconds)

    return response
