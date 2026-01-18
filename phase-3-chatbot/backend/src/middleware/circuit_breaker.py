"""Circuit breaker implementation for Gemini API resilience.

This module implements a circuit breaker pattern to prevent cascading failures
when the Gemini API is experiencing issues. The circuit breaker has three states:
- CLOSED: Normal operation, requests pass through
- OPEN: API is failing, requests are rejected immediately
- HALF_OPEN: Testing if API has recovered

Environment Variables:
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: Number of failures before opening circuit (default: 5)
    CIRCUIT_BREAKER_OPEN_DURATION: Seconds to keep circuit open (default: 60)
"""

import os
import time
from enum import Enum
from typing import Callable


class CircuitState(str, Enum):
    """Circuit breaker states.

    Attributes:
        CLOSED: Normal operation, requests pass through
        OPEN: API is failing, requests are rejected immediately
        HALF_OPEN: Testing if API has recovered
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker for Gemini API calls.

    This circuit breaker tracks failures and automatically opens the circuit
    when the failure threshold is reached. After the open duration elapses,
    the circuit moves to HALF_OPEN state to test if the API has recovered.

    Example:
        >>> breaker = CircuitBreaker()
        >>> try:
        ...     result = breaker.call(risky_api_call, arg1, arg2)
        ... except CircuitBreakerError:
        ...     # Circuit is open, fallback logic here
        ...     result = fallback_value
    """

    def __init__(
        self,
        failure_threshold: int | None = None,
        open_duration: int | None = None,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
                               (default: from CIRCUIT_BREAKER_FAILURE_THRESHOLD env var, or 5)
            open_duration: Seconds to keep circuit open
                           (default: from CIRCUIT_BREAKER_OPEN_DURATION env var, or 60)
        """
        self.failure_threshold = failure_threshold or int(
            os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")
        )
        self.open_duration = open_duration or int(
            os.getenv("CIRCUIT_BREAKER_OPEN_DURATION", "60")
        )

        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at: float | None = None

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Result of function execution

        Raises:
            CircuitBreakerError: If circuit is open and cannot execute request
            Exception: Any exception raised by the function
        """
        if self.state == CircuitState.OPEN:
            # Check if circuit should move to HALF_OPEN
            if self.opened_at and (time.time() - self.opened_at) >= self.open_duration:
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. API is currently unavailable. "
                    f"Will retry in {self._time_until_half_open():.0f} seconds."
                )

        try:
            # Execute function
            result = func(*args, **kwargs)

            # Success - reset failure count and close circuit
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0
            return result

        except Exception as e:
            # Failure - increment count and check threshold
            self.failure_count += 1

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = time.time()

            # Re-raise exception
            raise e

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state.

        This is useful for testing or manual recovery.
        """
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.opened_at = None

    def _time_until_half_open(self) -> float:
        """Calculate time remaining until circuit moves to HALF_OPEN.

        Returns:
            float: Seconds until HALF_OPEN state, or 0 if already past
        """
        if not self.opened_at:
            return 0
        elapsed = time.time() - self.opened_at
        remaining = self.open_duration - elapsed
        return max(0, remaining)

    @property
    def is_open(self) -> bool:
        """Check if circuit is currently open.

        Returns:
            bool: True if circuit is OPEN, False otherwise
        """
        return self.state == CircuitState.OPEN


# Singleton circuit breaker instance for Gemini API
_gemini_circuit_breaker: CircuitBreaker | None = None


def get_circuit_breaker() -> CircuitBreaker:
    """Get or create singleton circuit breaker for Gemini API.

    Returns:
        CircuitBreaker: Singleton circuit breaker instance
    """
    global _gemini_circuit_breaker
    if _gemini_circuit_breaker is None:
        _gemini_circuit_breaker = CircuitBreaker()
    return _gemini_circuit_breaker
