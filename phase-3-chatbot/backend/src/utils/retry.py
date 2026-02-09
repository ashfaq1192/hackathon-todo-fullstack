"""Retry utilities with exponential backoff for Gemini API.

This module provides retry decorators using the tenacity library for handling
transient failures in Gemini API calls. The retry strategy implements:
- Exponential backoff: 1s, 2s, 4s (3 attempts total)
- Retry on specific exceptions (rate limit, network errors, timeouts)
- Integration with circuit breaker for coordinated failure handling

Environment Variables:
    CHAT_RETRY_MAX_ATTEMPTS: Maximum retry attempts (default: 3)
"""

import os
from typing import TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Type variable for generic retry decorator
T = TypeVar("T")


# Maximum retry attempts from environment
MAX_RETRY_ATTEMPTS = int(os.getenv("CHAT_RETRY_MAX_ATTEMPTS", "3"))


# Common retryable exceptions
class RetryableError(Exception):
    """Base exception for retryable errors."""

    pass


class RateLimitError(RetryableError):
    """Exception for Gemini API rate limit errors."""

    pass


class NetworkError(RetryableError):
    """Exception for network connectivity errors."""

    pass


class TimeoutError(RetryableError):
    """Exception for request timeout errors."""

    pass


def with_exponential_backoff(
    max_attempts: int | None = None,
    min_wait: int = 1,
    max_wait: int = 10,
):
    """Decorator for exponential backoff retry logic.

    This decorator retries the decorated function with exponential backoff
    on retryable exceptions. The backoff sequence is: 1s, 2s, 4s (by default).

    Args:
        max_attempts: Maximum retry attempts (default: from CHAT_RETRY_MAX_ATTEMPTS env var, or 3)
        min_wait: Minimum wait time in seconds (default: 1)
        max_wait: Maximum wait time in seconds (default: 10)

    Returns:
        Decorator function

    Example:
        >>> @with_exponential_backoff(max_attempts=3)
        ... async def call_gemini_api():
        ...     # API call that might fail
        ...     return await client.chat.completions.create(...)

        >>> # Will retry up to 3 times with 1s, 2s, 4s delays
        >>> result = await call_gemini_api()
    """
    attempts = max_attempts or MAX_RETRY_ATTEMPTS

    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((RetryableError, ConnectionError)),
        reraise=True,
    )


def with_gemini_retry():
    """Decorator specifically for Gemini API calls.

    This decorator is preconfigured with the recommended retry settings
    for Gemini API:
    - 3 attempts maximum
    - Exponential backoff: 1s, 2s, 4s
    - Retries on rate limit, network, and timeout errors

    Returns:
        Decorator function

    Example:
        >>> @with_gemini_retry()
        ... async def generate_chat_response(messages):
        ...     client = get_gemini_client()
        ...     return await client.chat.completions.create(
        ...         model=client.model,
        ...         messages=messages
        ...     )
    """
    return with_exponential_backoff(max_attempts=MAX_RETRY_ATTEMPTS, min_wait=1, max_wait=4)


# Synchronous version for non-async functions
def with_exponential_backoff_sync(
    max_attempts: int | None = None,
    min_wait: int = 1,
    max_wait: int = 10,
):
    """Decorator for exponential backoff retry logic (synchronous version).

    Args:
        max_attempts: Maximum retry attempts (default: from CHAT_RETRY_MAX_ATTEMPTS env var, or 3)
        min_wait: Minimum wait time in seconds (default: 1)
        max_wait: Maximum wait time in seconds (default: 10)

    Returns:
        Decorator function

    Example:
        >>> @with_exponential_backoff_sync(max_attempts=3)
        ... def call_api():
        ...     # Synchronous API call
        ...     return requests.get("https://api.example.com")
    """
    attempts = max_attempts or MAX_RETRY_ATTEMPTS

    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((RetryableError, ConnectionError)),
        reraise=True,
    )
