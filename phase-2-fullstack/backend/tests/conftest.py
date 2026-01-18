"""
Pytest configuration and fixtures for testing.

This module provides shared fixtures for all tests, including
test database engines and sessions using SQLite in-memory.
"""

import importlib
import os
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, SQLModel

import src.database.connection
from src.config import JWT_ALGORITHM, JWT_SECRET_KEY
from src.main import app


@pytest.fixture(scope="function")
def test_engine():
    """
    Create a shared in-memory SQLite engine for unit tests.

    Uses a shared cache so all connections see the same database.
    Each test function gets a fresh database that is disposed after the test.
    """
    # Use a unique database name for this test to ensure isolation
    # But use shared cache so multiple connections can see the same data
    import uuid
    db_name = f"test_{uuid.uuid4().hex}"

    # Set environment variables to signal connection.py to use a test engine
    os.environ["PYTEST_IN_PROGRESS"] = "1"
    # Use file::memory: with shared cache and URI mode
    os.environ["test_database_url"] = f"sqlite:///file:{db_name}?mode=memory&cache=shared&uri=true"

    # Reload connection module to pick up the new environment variables
    importlib.reload(src.database.connection)

    # Reset the engine to force re-initialization with test settings
    src.database.connection.reset_engine()

    # IMPORTANT: Import models BEFORE creating tables
    from src.models.task import Task  # noqa: F401

    # Use the get_engine function to ensure the test engine is created
    engine = src.database.connection.get_engine()

    # Create tables (models must be imported first!)
    SQLModel.metadata.create_all(engine)

    yield engine

    # Dispose the engine and clean up environment variables
    engine.dispose()
    del os.environ["PYTEST_IN_PROGRESS"]
    del os.environ["test_database_url"]
    src.database.connection.reset_engine()  # Reset again for isolation
    importlib.reload(src.database.connection)  # Reload again to reset to production config


@pytest.fixture
def test_session(test_engine):
    """
    Provide a clean database session for each test.

    The session is rolled back after each test to ensure
    no data persists between tests.
    """
    with Session(test_engine) as session:
        yield session
        session.rollback()


# API Test Fixtures (T042-T044)


@pytest.fixture
def api_client(test_engine):
    """
    T042: Create a FastAPI TestClient for integration tests.

    This fixture provides a test client that uses an in-memory SQLite database
    for fast, isolated integration testing of API endpoints.

    Returns:
        TestClient instance configured for testing

    Example:
        def test_endpoint(api_client):
            response = api_client.get("/health")
            assert response.status_code == 200
    """
    # Override the get_session dependency to use test database
    # Note: get_engine() will return test_engine because PYTEST_IN_PROGRESS is set
    from src.database import get_engine, get_session as original_get_session

    def override_get_session():
        # This will use the test engine due to environment variables
        engine = get_engine()
        with Session(engine) as session:
            yield session

    app.dependency_overrides[original_get_session] = override_get_session

    # Use test engine for API client
    with TestClient(app) as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_jwt_token():
    """
    T043: Create a valid test JWT token with user_id claim.

    Returns:
        Valid JWT token string for testing authenticated endpoints

    Example:
        def test_authenticated_endpoint(api_client, mock_jwt_token):
            headers = {"Authorization": f"Bearer {mock_jwt_token}"}
            response = api_client.get("/api/user123/tasks", headers=headers)
            assert response.status_code == 200
    """
    payload = {
        "sub": "user123",
        "user_id": "user123",
        "exp": datetime.now(UTC) + timedelta(minutes=30),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@pytest.fixture
def mock_invalid_token():
    """
    T044: Create an invalid/expired JWT token for testing error cases.

    Returns:
        Expired or malformed JWT token string

    Example:
        def test_expired_token(api_client, mock_invalid_token):
            headers = {"Authorization": f"Bearer {mock_invalid_token}"}
            response = api_client.get("/api/user123/tasks", headers=headers)
            assert response.status_code == 401
    """
    # Create token that expired 1 hour ago
    payload = {
        "sub": "user123",
        "user_id": "user123",
        "exp": datetime.now(UTC) - timedelta(hours=1),
        "iat": datetime.now(UTC) - timedelta(hours=2),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@pytest.fixture
def create_jwt_token():
    """
    Factory fixture to create JWT tokens with custom user_id for testing.

    Returns:
        Function that creates JWT tokens with specified user_id

    Example:
        def test_user_isolation(api_client, create_jwt_token):
            token1 = create_jwt_token("user1")
            token2 = create_jwt_token("user2")
            # Test that user1 cannot access user2's resources
    """

    def _create_token(user_id: str, exp_minutes: int = 30) -> str:
        """
        Create a JWT token for the specified user.

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

    return _create_token
