from typing import Generator
from sqlmodel import create_engine, SQLModel, Session
from src.config import settings
from src.models.task import Task # Import your models here
from src.models.conversation import Conversation
from src.models.message import Message


engine = create_engine(settings.DATABASE_URL)


def create_db_and_tables():
    """
    Creates all database tables defined as SQLModel classes.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to provide a database session.
    Yields a session and ensures it's closed afterwards.
    """
    with Session(engine) as session:
        yield session
