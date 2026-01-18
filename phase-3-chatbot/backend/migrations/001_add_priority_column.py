"""
Migration: Add priority column to tasks table.

This migration adds a 'priority' column to the existing tasks table
with a default value of 'medium' for all existing rows.

Run this script once after deploying the updated backend code.
"""

import logging
import sys
from pathlib import Path

# Add backend/src to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from src.database import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_priority_column():
    """
    Add priority column to tasks table if it doesn't exist.

    This migration:
    1. Checks if the priority column already exists
    2. Adds the column with default value 'medium' if it doesn't exist
    3. Sets existing NULL values to 'medium'
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Check if column already exists
            logger.info("Checking if priority column already exists...")
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name = 'priority';
            """))

            if result.fetchone():
                logger.info("✓ Priority column already exists. No migration needed.")
                return

            # Add priority column with default value
            logger.info("Adding priority column to tasks table...")
            conn.execute(text("""
                ALTER TABLE tasks
                ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium';
            """))

            # Commit the transaction
            conn.commit()
            logger.info("✓ Successfully added priority column with default value 'medium'")

            # Verify the column was added
            result = conn.execute(text("""
                SELECT column_name, column_default, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name = 'priority';
            """))

            column_info = result.fetchone()
            if column_info:
                logger.info(f"✓ Verification: Column added - {column_info}")
            else:
                logger.error("✗ Verification failed: Column not found after migration")
                sys.exit(1)

    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Running migration: Add priority column to tasks table")
    logger.info("=" * 60)
    add_priority_column()
    logger.info("=" * 60)
    logger.info("Migration completed successfully!")
    logger.info("=" * 60)
