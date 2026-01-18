"""
Database initialization utility.

This module provides a function to create database tables
from SQLModel metadata.
"""

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(engine):
    """
    Create database tables.

    Args:
        engine: The SQLAlchemy engine to use.

    Raises:
        SQLAlchemyError: If an error occurs during table creation.
    """
    try:
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise
