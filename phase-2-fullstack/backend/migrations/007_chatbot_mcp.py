"""Migration: Add conversations and messages tables for AI chatbot feature (Phase III).

This migration creates two new tables:
1. conversations: Stores conversation metadata and AI-generated summaries
2. messages: Stores individual messages in conversations (user and assistant roles)

Architecture: Stateless design with PostgreSQL persistence for horizontal scaling.
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


def create_chatbot_tables():
    """Create conversations and messages tables for Phase III chatbot feature.

    This migration:
    1. Creates conversations table with summary field for context management
    2. Creates messages table with role enum (user/assistant)
    3. Adds indexes for efficient querying
    4. Sets up foreign key relationships
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Check if tables already exist
            logger.info("Checking if conversations table exists...")
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'conversations';
            """
                )
            )

            if result.fetchone():
                logger.info("✓ Conversations table already exists. No migration needed.")
                return

            # Create conversations table
            logger.info("Creating conversations table...")
            conn.execute(
                text(
                    """
                CREATE TABLE conversations (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    title VARCHAR(255),
                    summary VARCHAR(2000),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER NOT NULL DEFAULT 0
                );
            """
                )
            )

            # Create index on user_id for efficient filtering
            conn.execute(
                text(
                    """
                CREATE INDEX idx_conversations_user_id ON conversations(user_id);
            """
                )
            )

            logger.info("✓ Conversations table created successfully.")

            # Create message_role enum type
            logger.info("Creating message_role enum type...")
            conn.execute(
                text(
                    """
                CREATE TYPE message_role AS ENUM ('user', 'assistant');
            """
                )
            )

            # Create messages table
            logger.info("Creating messages table...")
            conn.execute(
                text(
                    """
                CREATE TABLE messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role message_role NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    token_count INTEGER
                );
            """
                )
            )

            # Create indexes on conversation_id and created_at for efficient sliding window queries
            conn.execute(
                text(
                    """
                CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
            """
                )
            )
            conn.execute(
                text(
                    """
                CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
            """
                )
            )

            logger.info("✓ Messages table created successfully.")

            # Commit transaction
            conn.commit()

            logger.info("✓ Phase III chatbot migration completed successfully!")
            logger.info("  - Conversations table: ✓ Created with summary field")
            logger.info("  - Messages table: ✓ Created with role enum")
            logger.info("  - Indexes: ✓ Created for efficient querying")

    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        raise


def rollback_chatbot_tables():
    """Rollback chatbot tables migration.

    WARNING: This will delete all conversation and message data!
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            logger.info("Rolling back Phase III chatbot migration...")

            # Drop tables in reverse order (messages first due to foreign key)
            conn.execute(text("DROP TABLE IF EXISTS messages CASCADE;"))
            logger.info("✓ Messages table dropped.")

            conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE;"))
            logger.info("✓ Conversations table dropped.")

            conn.execute(text("DROP TYPE IF EXISTS message_role CASCADE;"))
            logger.info("✓ Message_role enum type dropped.")

            conn.commit()

            logger.info("✓ Rollback completed successfully!")

    except Exception as e:
        logger.error(f"✗ Rollback failed: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase III Chatbot Migration")
    parser.add_argument(
        "--rollback", action="store_true", help="Rollback migration (WARNING: deletes all data)"
    )
    args = parser.parse_args()

    if args.rollback:
        rollback_chatbot_tables()
    else:
        create_chatbot_tables()
