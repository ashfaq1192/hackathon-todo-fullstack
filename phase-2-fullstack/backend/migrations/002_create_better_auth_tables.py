"""
Migration: Create Better Auth tables

This migration creates the required Better Auth tables in the database.
These tables are needed for user authentication, sessions, and verification.

Run this script once after deploying the frontend with Better Auth.
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


def create_better_auth_tables():
    """
    Create Better Auth tables if they don't exist.

    Tables created:
    - user: Core user account information
    - session: Active user sessions
    - account: OAuth/social login accounts (optional)
    - verification: Email verification tokens
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Check if 'user' table already exists
            logger.info("Checking if Better Auth tables already exist...")
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('user', 'session', 'verification', 'account');
            """))

            existing_tables = [row[0] for row in result.fetchall()]

            if existing_tables:
                logger.info(f"✓ Better Auth tables already exist: {', '.join(existing_tables)}")
                logger.info("Skipping migration.")
                return

            # Create 'user' table
            logger.info("Creating 'user' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
                    name TEXT,
                    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    image TEXT
                );
            """))

            # Create 'session' table
            logger.info("Creating 'session' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS session (
                    id TEXT PRIMARY KEY,
                    "expiresAt" TIMESTAMP NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "ipAddress" TEXT,
                    "userAgent" TEXT,
                    "userId" TEXT NOT NULL,
                    FOREIGN KEY ("userId") REFERENCES "user"(id) ON DELETE CASCADE
                );
            """))

            # Create 'account' table (for OAuth, optional but Better Auth expects it)
            logger.info("Creating 'account' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS account (
                    id TEXT PRIMARY KEY,
                    "accountId" TEXT NOT NULL,
                    "providerId" TEXT NOT NULL,
                    "userId" TEXT NOT NULL,
                    "accessToken" TEXT,
                    "refreshToken" TEXT,
                    "idToken" TEXT,
                    "accessTokenExpiresAt" TIMESTAMP,
                    "refreshTokenExpiresAt" TIMESTAMP,
                    scope TEXT,
                    password TEXT,
                    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY ("userId") REFERENCES "user"(id) ON DELETE CASCADE
                );
            """))

            # Create 'verification' table (for email verification)
            logger.info("Creating 'verification' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS verification (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    value TEXT NOT NULL,
                    "expiresAt" TIMESTAMP NOT NULL,
                    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Create indexes for better performance
            logger.info("Creating indexes...")
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_session_userId ON session("userId");'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_account_userId ON account("userId");'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_verification_identifier ON verification(identifier);'))

            # Commit the transaction
            conn.commit()

            logger.info("✓ Successfully created all Better Auth tables")
            logger.info("✓ Tables created: user, session, account, verification")

    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Running migration: Create Better Auth tables")
    logger.info("=" * 60)
    create_better_auth_tables()
    logger.info("=" * 60)
    logger.info("Migration completed successfully!")
    logger.info("=" * 60)
