"""
Unit tests for database connection module.

Tests database connection establishment, health checks,
and error handling for invalid configurations.
"""

import importlib  # Added importlib
import os
from unittest import mock

import pytest
from sqlmodel import (
    Session,  # Added Session
    create_engine,
    text,
)

import src.database.connection  # Added this import
import src.config


def test_successful_connection(test_engine):
    """


    T013: Verify successful database connection using the test engine.


    """

    # Use the test_engine directly

    with test_engine.connect() as conn:
        assert conn is not None

        result = conn.execute(text("SELECT 1"))

        assert result.scalar() == 1


def test_connection_health_check(test_engine):
    """


    T014: Verify connection health check with the test engine.


    """

    with Session(test_engine) as session:  # Create session from test_engine
        result = session.execute(text("SELECT 1"))

        assert result.scalar() == 1


def test_invalid_database_url_error_handling():
    """


    T015: Verify error handling for invalid DATABASE_URL when creating engine directly.


    """

    invalid_url = "postgresql://invalid:invalid@nonexistent-host/db"

    engine = create_engine(invalid_url, pool_pre_ping=True)

    with pytest.raises(Exception) as exc_info:
        with engine.connect():
            pass

    assert exc_info.value is not None


def test_check_connection_error_handling():
    """


    Test that check_connection raises an informative error for invalid connection.


    This test specifically targets the error handling in the check_connection function.


    """

    # Use mock.patch to override DATABASE_URL in the config module
    invalid_url = "postgresql://invalid:invalid@nonexistent-host:5432/db"

    with mock.patch('src.config.DATABASE_URL', invalid_url):
        # Also patch in the connection module since it imports from config
        with mock.patch('src.database.connection.DATABASE_URL', invalid_url):
            # Reset engine to force it to use the mocked URL
            src.database.connection.reset_engine()

            # The check_connection function should raise ConnectionError
            try:
                result = src.database.connection.check_connection()
                # If we get here, the connection didn't fail as expected
                pytest.fail(f"Expected ConnectionError but check_connection returned: {result}")
            except ConnectionError as e:
                # This is what we expect
                assert "Failed to connect to database" in str(e)

    # Reset engine after test to restore normal state
    src.database.connection.reset_engine()
