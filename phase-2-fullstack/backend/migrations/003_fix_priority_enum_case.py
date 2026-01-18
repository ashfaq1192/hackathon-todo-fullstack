"""
Migration: Fix priority enum case mismatch

This migration fixes the case mismatch between the PostgreSQL ENUM type
(which has uppercase values: LOW, MEDIUM, HIGH) and the data in the database
(which has lowercase values: low, medium, high).

Solution: Drop the existing ENUM type and recreate it with lowercase values
to match the Python model definition.
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


def fix_priority_enum():
    """
    Fix the priority enum case mismatch.

    Steps:
    1. Convert priority column to VARCHAR temporarily
    2. Drop the old ENUM type
    3. Create new ENUM type with lowercase values
    4. Convert priority column back to the new ENUM type
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            logger.info("Step 1: Converting priority column to VARCHAR...")
            conn.execute(text("""
                ALTER TABLE tasks
                ALTER COLUMN priority TYPE VARCHAR(10);
            """))
            conn.commit()
            logger.info("✓ Priority column converted to VARCHAR")

            logger.info("Step 2: Converting all priority values to lowercase...")
            conn.execute(text("""
                UPDATE tasks
                SET priority = LOWER(priority)
                WHERE priority IN ('LOW', 'MEDIUM', 'HIGH');
            """))
            conn.commit()
            logger.info("✓ Priority values converted to lowercase")

            logger.info("Step 3: Dropping old taskpriority ENUM type...")
            conn.execute(text("""
                DROP TYPE IF EXISTS taskpriority CASCADE;
            """))
            conn.commit()
            logger.info("✓ Old ENUM type dropped")

            logger.info("Step 4: Creating new taskpriority ENUM with lowercase values...")
            conn.execute(text("""
                CREATE TYPE taskpriority AS ENUM ('low', 'medium', 'high');
            """))
            conn.commit()
            logger.info("✓ New ENUM type created with lowercase values")

            logger.info("Step 5: Dropping default constraint temporarily...")
            conn.execute(text("""
                ALTER TABLE tasks
                ALTER COLUMN priority DROP DEFAULT;
            """))
            conn.commit()
            logger.info("✓ Default constraint dropped")

            logger.info("Step 6: Converting priority column back to ENUM...")
            conn.execute(text("""
                ALTER TABLE tasks
                ALTER COLUMN priority TYPE taskpriority
                USING priority::taskpriority;
            """))
            conn.commit()
            logger.info("✓ Priority column converted back to ENUM")

            logger.info("Step 7: Re-adding default value...")
            conn.execute(text("""
                ALTER TABLE tasks
                ALTER COLUMN priority SET DEFAULT 'medium'::taskpriority;
            """))
            conn.commit()
            logger.info("✓ Default value re-added")

            # Verify the change
            logger.info("Verifying ENUM values...")
            result = conn.execute(text("""
                SELECT e.enumlabel
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'taskpriority'
                ORDER BY e.enumsortorder;
            """))

            enum_values = [row[0] for row in result.fetchall()]
            logger.info(f"✓ Verification: ENUM values are now: {enum_values}")

            if enum_values == ['low', 'medium', 'high']:
                logger.info("✓ Migration successful! ENUM values are correct.")
            else:
                logger.error(f"✗ Unexpected ENUM values: {enum_values}")
                sys.exit(1)

    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        logger.error("Rolling back changes...")
        sys.exit(1)


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Running migration: Fix priority ENUM case mismatch")
    logger.info("=" * 70)
    fix_priority_enum()
    logger.info("=" * 70)
    logger.info("Migration completed successfully!")
    logger.info("=" * 70)
