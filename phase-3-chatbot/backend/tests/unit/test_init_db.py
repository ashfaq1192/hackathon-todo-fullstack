"""
Unit tests for database initialization.

This module tests that the `init_db` function correctly creates
database tables based on the defined SQLModel models.
"""

import pytest
from sqlalchemy import inspect
from sqlmodel import create_engine

from src.database import init_db


@pytest.fixture(scope="function")
def clean_engine():
    """
    Create an in-memory SQLite engine without any tables.
    """
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()


def test_init_db_creates_tables(clean_engine):
    """
    T035: Verify that init_db() creates the 'tasks' table successfully.
    """
    # Ensure the table does not exist initially
    inspector = inspect(clean_engine)
    assert not inspector.has_table("tasks"), "Pre-condition failed: 'tasks' table already exists."

    # Run the initialization function
    init_db(clean_engine)

    # Verify the table was created
    inspector = inspect(clean_engine)
    assert inspector.has_table("tasks"), "Post-condition failed: 'tasks' table was not created."


def test_tasks_table_has_required_columns(clean_engine):
    """
    T036: Verify that the 'tasks' table has all the required columns.
    """
    init_db(clean_engine)
    inspector = inspect(clean_engine)
    columns = [col["name"] for col in inspector.get_columns("tasks")]

    expected_columns = [
        "id",
        "user_id",
        "title",
        "description",
        "complete",
        "created_at",
        "updated_at",
    ]

    assert all(col in columns for col in expected_columns)
    assert len(columns) == len(expected_columns)


def test_user_id_index_exists(clean_engine):
    """
    T037: Verify that the user_id index exists on the 'tasks' table.
    """
    init_db(clean_engine)
    inspector = inspect(clean_engine)
    indexes = inspector.get_indexes("tasks")

    assert any(idx["name"] == "ix_tasks_user_id" for idx in indexes)
