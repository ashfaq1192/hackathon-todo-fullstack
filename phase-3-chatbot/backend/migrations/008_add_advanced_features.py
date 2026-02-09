"""Migration: Add advanced features columns to tasks table (Phase V).

This migration adds:
1. due_date TIMESTAMP (nullable) - for deadline tracking
2. recurring VARCHAR(10) DEFAULT 'none' - recurring task type (none/daily/weekly/monthly/yearly)
3. recurring_end_date TIMESTAMP (nullable) - when recurring schedule ends
4. tags TEXT[] DEFAULT '{}' - PostgreSQL array for task labels/categories

Indexes:
- idx_tasks_due_date - efficient due date queries and sorting
- idx_tasks_recurring - filter recurring tasks
- idx_tasks_tags - GIN index for array containment queries
- idx_tasks_priority - filter by priority level
- idx_tasks_complete - filter by completion status
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


def add_advanced_features():
    """Add advanced feature columns and indexes to tasks table.

    This migration:
    1. Adds due_date, recurring, recurring_end_date, tags columns
    2. Creates indexes for efficient querying and filtering
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Check if columns already exist
            logger.info("Checking if due_date column exists...")
            result = conn.execute(
                text(
                    """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'due_date';
            """
                )
            )

            if result.fetchone():
                logger.info("Advanced features columns already exist. No migration needed.")
                return

            # Add due_date column
            logger.info("Adding due_date column...")
            conn.execute(
                text(
                    """
                ALTER TABLE tasks
                ADD COLUMN due_date TIMESTAMP;
            """
                )
            )

            # Add recurring column with default 'none'
            logger.info("Adding recurring column...")
            conn.execute(
                text(
                    """
                ALTER TABLE tasks
                ADD COLUMN recurring VARCHAR(10) NOT NULL DEFAULT 'none';
            """
                )
            )

            # Add recurring_end_date column
            logger.info("Adding recurring_end_date column...")
            conn.execute(
                text(
                    """
                ALTER TABLE tasks
                ADD COLUMN recurring_end_date TIMESTAMP;
            """
                )
            )

            # Add tags column (PostgreSQL array)
            logger.info("Adding tags column...")
            conn.execute(
                text(
                    """
                ALTER TABLE tasks
                ADD COLUMN tags TEXT[] NOT NULL DEFAULT '{}';
            """
                )
            )

            # Create indexes
            logger.info("Creating indexes...")

            conn.execute(
                text(
                    """
                CREATE INDEX idx_tasks_due_date ON tasks(due_date);
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX idx_tasks_recurring ON tasks(recurring);
            """
                )
            )

            # GIN index for array containment queries (e.g., WHERE tags @> ARRAY['work'])
            conn.execute(
                text(
                    """
                CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX idx_tasks_priority ON tasks(priority);
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX idx_tasks_complete ON tasks(complete);
            """
                )
            )

            # Commit transaction
            conn.commit()

            logger.info("Phase V advanced features migration completed successfully!")
            logger.info("  - due_date: TIMESTAMP (nullable)")
            logger.info("  - recurring: VARCHAR(10) DEFAULT 'none'")
            logger.info("  - recurring_end_date: TIMESTAMP (nullable)")
            logger.info("  - tags: TEXT[] DEFAULT '{}'")
            logger.info("  - Indexes: due_date, recurring, tags (GIN), priority, complete")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def rollback_advanced_features():
    """Rollback advanced features migration.

    WARNING: This will remove all advanced feature data!
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            logger.info("Rolling back Phase V advanced features migration...")

            # Drop indexes first
            conn.execute(text("DROP INDEX IF EXISTS idx_tasks_due_date;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_tasks_recurring;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_tasks_tags;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_tasks_priority;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_tasks_complete;"))
            logger.info("Indexes dropped.")

            # Drop columns
            conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;"))
            conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS recurring;"))
            conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS recurring_end_date;"))
            conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS tags;"))
            logger.info("Columns dropped.")

            conn.commit()

            logger.info("Rollback completed successfully!")

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase V Advanced Features Migration")
    parser.add_argument(
        "--rollback", action="store_true", help="Rollback migration (WARNING: deletes all data)"
    )
    args = parser.parse_args()

    if args.rollback:
        rollback_advanced_features()
    else:
        add_advanced_features()
