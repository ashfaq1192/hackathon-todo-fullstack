"""
Models package for the application.

This package exports all database models.
Models must be imported here to ensure they are registered with SQLModel.metadata
before database initialization (table creation).
"""

from .task import Task

__all__ = ["Task"]
