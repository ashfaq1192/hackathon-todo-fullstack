"""
Database connection module for Neon PostgreSQL.

This module manages database connections with connection pooling,
SSL/TLS security, and error handling for the Neon Serverless PostgreSQL database.
"""

import logging
import os

from sqlmodel import Session, create_engine, text

from ..config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the engine instance
_engine = None


def reset_engine():
    """Resets the global engine instance."""
    global _engine  # noqa: PLW0603
    _engine = None


def get_engine():
    """
    Returns the SQLAlchemy engine instance. Creates it if it doesn't exist.
    This allows for lazy initialization and injection of a test engine.
    """
    global _engine  # noqa: PLW0603
    if _engine is None:
        # Check if we are running tests and a test engine is provided
        if os.environ.get("PYTEST_IN_PROGRESS") == "1" and "test_database_url" in os.environ:
            logger.info("Using test database engine.")
            _engine = create_engine(
                os.environ["test_database_url"],
                connect_args={"check_same_thread": False, "uri": True},  # Allow SQLite across threads with URI mode
            )
        else:
            logger.info("Creating production database engine.")
            _engine = create_engine(
                DATABASE_URL,
                pool_size=5,
                max_overflow=15,
                pool_pre_ping=True,
                connect_args={"sslmode": "require"},
                echo=False,
            )
    return _engine


def get_session() -> Session:
    """
    Provide a database session for executing queries.

    Returns:
        Session: A SQLModel session connected to the database

    Example:
        with get_session() as session:
            tasks = session.exec(select(Task)).all()
    """
    return Session(get_engine())


def check_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is successful, False otherwise

    Raises:
        Exception: If connection fails with clear error message
    """
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to database. "
            f"Please verify DATABASE_URL is correct and Neon database is accessible. "
            f"Error: {str(e)}"
        ) from e
