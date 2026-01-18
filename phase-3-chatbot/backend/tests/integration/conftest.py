"""Shared fixtures for integration tests."""

import os
import pytest


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    """Disable rate limiting for all integration tests.

    This fixture runs automatically before each test and resets after.
    It sets the environment variable that the rate limiter checks.
    """
    # Set environment variable to disable rate limiting
    os.environ["DISABLE_RATE_LIMITER_FOR_TESTS"] = "true"

    # Reset the singleton rate limiter to pick up the new setting
    from src.middleware.rate_limiter import _rate_limiter, RateLimiter
    import src.middleware.rate_limiter as rate_limiter_module

    # Reset singleton to None so it gets recreated with the new setting
    rate_limiter_module._rate_limiter = None

    yield

    # Cleanup: reset rate limiter state after test
    rate_limiter_module._rate_limiter = None
    # Keep the env var set for subsequent tests in the same session


@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset FastAPI app dependency overrides after each test."""
    from src.main import app

    yield

    # Clear any dependency overrides that might have been set
    app.dependency_overrides.clear()
