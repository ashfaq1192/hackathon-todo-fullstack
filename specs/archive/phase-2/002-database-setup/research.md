# Research: Database & Models Setup

**Date**: 2025-12-18
**Feature**: 002-database-setup
**Phase**: Phase 0 - Research & Technical Decisions

## Research Questions

This document consolidates technical research for database setup with Neon PostgreSQL and SQLModel.

---

## 1. Database Connection Strategy

### Decision: SQLModel with PostgreSQL engine and connection pooling

**Research Question**: How to establish reliable, performant connection to Neon Serverless PostgreSQL?

**Options Considered**:
1. **Direct psycopg2 connections** - Low-level PostgreSQL adapter
2. **SQLAlchemy Core** - SQL expression language without ORM
3. **SQLModel (chosen)** - Pydantic-based ORM built on SQLAlchemy

**Rationale**:
- SQLModel provides type-safe models with Pydantic validation (NFR-004)
- Built on SQLAlchemy, inherits mature connection pooling (NFR-002)
- Declarative syntax reduces boilerplate vs raw SQLAlchemy
- Automatic parameterized queries prevent SQL injection (NFR-003)
- Integrates seamlessly with FastAPI (needed in Stage 2)

**Implementation Pattern**:
```python
from sqlmodel import create_engine, Session

# Connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=15,  # Total 20 max connections (NFR-002)
    pool_pre_ping=True,  # Verify connections before use
    connect_args={"sslmode": "require"}  # SSL/TLS (NFR-001)
)
```

**Alternatives Rejected**:
- psycopg2 direct: Too low-level, manual SQL error-prone
- SQLAlchemy Core: No ORM benefits, similar complexity

**Dependencies**: SQLModel 0.0.22+, psycopg2-binary

---

## 2. Task Model Design with Auto-Timestamps

### Decision: SQLModel with `datetime.utcnow` defaults and `onupdate` trigger

**Research Question**: How to implement automatic created_at and updated_at timestamps?

**Options Considered**:
1. **Application-level timestamps** - Set in Python code before save
2. **Database triggers** - PostgreSQL trigger functions
3. **SQLAlchemy defaults (chosen)** - Column defaults with `onupdate`

**Rationale**:
- SQLAlchemy `default=datetime.utcnow` auto-sets created_at on insert
- `onupdate=datetime.utcnow` auto-updates updated_at on modification
- No manual timestamp management in application code
- Database-agnostic (works across PostgreSQL, SQLite for tests)
- Simpler than maintaining trigger functions

**Implementation Pattern**:
```python
from datetime import datetime
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None, max_length=1000)
    complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
```

**Alternatives Rejected**:
- Application-level: Error-prone, easy to forget in updates
- Database triggers: Over-engineering for simple use case

**Validation Rules** (from FR-004 to FR-008):
- user_id: Required, indexed (foreign key concept for Better Auth)
- title: Required, max 200 chars
- description: Optional, max 1000 chars
- complete: Defaults to False
- Timestamps: Auto-generated, non-nullable

---

## 3. Database Initialization Strategy

### Decision: Auto-create tables with `SQLModel.metadata.create_all()` for Stage 1

**Research Question**: Should we use migrations (Alembic) or auto-create tables?

**Options Considered**:
1. **Alembic migrations** - Version-controlled schema changes
2. **Auto-create with create_all() (chosen)** - Automatic table generation
3. **Manual SQL scripts** - Raw CREATE TABLE statements

**Rationale**:
- Stage 1 scope: Single Task table, no schema evolution yet
- `create_all()` idempotent (safe to re-run, only creates missing tables)
- Simplifies initial setup (Principle I: Simplicity First)
- Defer migrations to future when schema changes needed (Out of Scope)
- Aligns with acceptance criteria AC-004 (tables created automatically)

**Implementation Pattern**:
```python
from sqlmodel import SQLModel, create_engine

def init_db(engine):
    """Create all tables defined in SQLModel models."""
    SQLModel.metadata.create_all(engine)
```

**Alternatives Rejected**:
- Alembic: Over-engineering for foundation stage with single table
- Manual SQL: Not DRY, duplicates model definitions

**Future Consideration**: Add Alembic in later stages when schema evolution needed

---

## 4. Testing Strategy with Pytest Fixtures

### Decision: In-memory SQLite for unit tests, Neon PostgreSQL for integration

**Research Question**: How to test database operations without affecting production data?

**Options Considered**:
1. **Mocking database calls** - Mock engine/session
2. **Docker PostgreSQL** - Containerized test database
3. **In-memory SQLite + Neon for integration (chosen)** - Hybrid approach

**Rationale**:
- SQLite in-memory (`:memory:`) for fast unit tests (models, validation)
- SQLModel abstracts DB differences (same code works on both)
- Neon test database for integration tests (real connection)
- Pytest fixtures provide clean session per test
- Achieves 70%+ coverage requirement (SC-005)

**Implementation Pattern**:
```python
# tests/conftest.py
import pytest
from sqlmodel import create_engine, Session, SQLModel

@pytest.fixture(scope="function")
def test_engine():
    """In-memory SQLite engine for unit tests."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def test_session(test_engine):
    """Clean database session for each test."""
    with Session(test_engine) as session:
        yield session
        session.rollback()
```

**Test Coverage Areas**:
1. **Task model validation** (test_task_model.py):
   - Required fields (user_id, title)
   - Max length constraints
   - Default values (complete=False, timestamps)
   - Invalid data rejection

2. **Connection health** (test_connection.py):
   - Successful connection
   - Invalid DATABASE_URL error handling
   - Connection pool behavior

3. **CRUD operations** (test_crud.py):
   - Create task and verify ID returned
   - Read task by ID
   - Read tasks by user_id (multi-user isolation)

**Alternatives Rejected**:
- Mocking: Doesn't test real database behavior
- Docker only: Slower, requires Docker runtime

---

## 5. Environment Configuration

### Decision: python-dotenv with .env file (gitignored)

**Research Question**: How to manage DATABASE_URL securely?

**Rationale**:
- python-dotenv loads `.env` into `os.environ`
- `.env` in `.gitignore` prevents credential leaks (TC-004)
- `.env.example` documents required variables
- Standard pattern for Python projects

**Implementation**:
```python
# backend/src/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment")
```

**Dependencies**: python-dotenv

---

## 6. Neon PostgreSQL Best Practices

### Connection String Format

Neon provides connection string in format:
```
postgresql://[user]:[password]@[endpoint]/[database]?sslmode=require
```

**Best Practices**:
- Always use `sslmode=require` (NFR-001)
- Use pooling (`pool_pre_ping=True`) for serverless architecture
- Set reasonable pool size (5-20 connections per NFR-002)
- Connection timeout: Neon auto-scales, but set 30s timeout for failures

**Error Handling**:
- Network issues: Retry with exponential backoff
- Invalid credentials: Fail fast with clear error
- SSL errors: Verify `sslmode=require` in connection string

---

## Research Summary

All technical decisions resolved. No "NEEDS CLARIFICATION" items remaining.

**Key Technologies**:
- SQLModel 0.0.22+ (ORM with Pydantic validation)
- psycopg2-binary (PostgreSQL adapter)
- python-dotenv (environment configuration)
- pytest (testing framework)

**Architecture Choices**:
1. SQLModel for type-safe models with auto-timestamps
2. Connection pooling (5-20 connections) for performance
3. Auto-create tables with `create_all()` (defer migrations)
4. Hybrid testing: SQLite for units, Neon for integration
5. Environment-based configuration with .env

**Ready for Phase 1**: Design (data-model.md, contracts/, quickstart.md)
