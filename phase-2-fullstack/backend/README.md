# Backend Setup and Quickstart

This document provides a quick guide to setting up and running the backend services for the `hackathon-todo` application. It covers database configuration, dependency installation, and running tests.

## Overview

This guide will help you:
1. Set up your Neon PostgreSQL database.
2. Configure necessary environment variables.
3. Install project dependencies.
4. Run the test suite to verify your setup.

## Prerequisites

- Python 3.13+ installed
- UV package manager ([installation guide](https://github.com/astral-sh/uv))
- Neon PostgreSQL account (free tier is sufficient)
- Git (for version control)

## 1. Set Up Neon PostgreSQL

### 1.1 Create Neon Account
1. Go to [neon.tech](https://neon.tech)
2. Sign up (free tier sufficient)
3. Create a new project (e.g., `hackathon-todo`)

### 1.2 Get Connection String
1. In your Neon dashboard, navigate to **Connection Details**.
2. Copy the **Connection String**. It should look similar to:
   ```
   postgresql://user:password@ep-something.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Keep this string handy; you'll need it in the next step.

## 2. Configure Environment

### 2.1 Create `.env` File
From the `backend/` directory, create a `.env` file by copying the example:

```bash
cp .env.example .env
```

### 2.2 Add Your Database URL to `.env`
Edit the newly created `.env` file and replace the placeholder with your actual Neon connection string:

```dotenv
# .env file content:
DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
```
**Important**: The `.env` file is already in `.gitignore` and should **never** be committed to version control.

## 3. Install Dependencies

### 3.1 Initialize UV Project
From the `backend/` directory:

```bash
uv init
# Or if pyproject.toml already exists:
uv sync
```

### 3.2 Add Required Packages
```bash
uv add sqlmodel psycopg2-binary python-dotenv
uv add --dev pytest pytest-cov
```
This process updates `pyproject.toml` with the following dependencies:
```toml
[project]
dependencies = [
    "sqlmodel>=0.0.22",
    "psycopg2-binary>=2.9.0",
    "python-dotenv>=1.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0"
]
```

## 4. Verify Setup

### 4.1 Run Tests
From the `backend/` directory:

```bash
# Run all tests
../.venv/bin/pytest

# Run tests with coverage report
../.venv/bin/pytest --cov=src --cov-report=term-missing

# Run specific test file
../.venv/bin/pytest tests/unit/test_task_model.py -v
```

Expected successful test output will show all tests passing.

## Project Structure

After setup, your `backend/` directory should have a structure similar to this:

```
backend/
├── src/
│   ├── models/
│   │   └── task.py           # Task SQLModel definition
│   ├── database/
│   │   ├── connection.py     # Database engine and session management
│   │   ├── init_db.py        # Database table creation logic
│   │   └── crud.py           # CRUD operations for tasks
│   └── config.py             # Environment configuration loading
├── tests/
│   ├── unit/
│   │   ├── test_task_model.py # Unit tests for Task model
│   │   ├── test_connection.py # Unit tests for database connection
│   │   ├── test_init_db.py    # Unit tests for database initialization
│   │   └── test_crud.py       # Unit tests for CRUD operations
│   └── conftest.py           # Pytest fixtures for testing
├── .env                      # Your DATABASE_URL (gitignored)
├── .env.example              # Template for environment variables
├── pyproject.toml            # Project dependencies and metadata
└── README.md                 # This setup documentation
```

## Common Issues & Solutions

### Issue: `DATABASE_URL` not found
**Symptom**: `ValueError: DATABASE_URL not found in environment`

**Solution**:
1. Ensure a `.env` file exists in the `backend/` directory.
2. Verify that the `.env` file contains `DATABASE_URL=postgresql://...`.
3. Check for extra spaces; format should be `DATABASE_URL=value` (not `DATABASE_URL = value`).

### Issue: "SSL connection required"
**Symptom**: `psycopg2.OperationalError: SSL connection required`

**Solution**: Ensure your connection string includes `?sslmode=require`:
```
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Issue: `psycopg2` not found
**Symptom**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**: Install `psycopg2-binary`:
```bash
uv add psycopg2-binary
```

### Issue: Tests fail with connection errors
**Symptom**: `pytest` reports database connection errors.

**Solution**: Unit tests utilize an in-memory SQLite database, so they do not require a live Neon connection. If you are running integration tests (not covered in this quickstart) or encounter unexpected connection errors:
1. Confirm your Neon database is running and accessible.
2. Double-check that your `DATABASE_URL` in `.env` is correct.
3. Verify your network connectivity.

## Quick Commands Reference

```bash
# Install dependencies
uv sync --extra dev                             # Install all dependencies

# Run tests
source .venv/bin/activate                       # Activate environment
pytest                                          # All tests
pytest --cov=src --cov-report=term-missing     # With coverage (82%+)
pytest tests/unit/test_crud.py -v              # Specific file

# Code quality
ruff check src/                                 # Lint code
ruff format src/                                # Format code

# Database operations
python -c "from src.database import init_db, get_engine; init_db(get_engine())"  # Create tables
```

## API Usage Examples

### Create and Query Tasks

```python
from src.database import get_session
from src.database.crud import create_task, get_task_by_id, get_tasks_by_user

# Get a database session
session = get_session()

# Create a task
task = create_task(
    session=session,
    user_id="user_123",
    title="Complete Phase II",
    description="Implement database layer"
)
print(f"✅ Created task ID: {task.id}")

# Retrieve task by ID
retrieved_task = get_task_by_id(session, task.id)
print(f"📋 Task: {retrieved_task.title}")

# Get all tasks for a user
user_tasks = get_tasks_by_user(session, "user_123")
print(f"📊 User has {len(user_tasks)} tasks")
```

## Test Coverage Status

**Current Coverage**: 82% (Exceeds 70% requirement) ✅

| File | Coverage | Status |
|------|----------|--------|
| config.py | 88% | ✅ |
| connection.py | 88% | ✅ |
| crud.py | 70% | ✅ |
| init_db.py | 77% | ✅ |
| task.py | 100% | ✅ |

**Total Tests**: 17 passing
- Connection tests: 4
- Task model tests: 6
- Init DB tests: 3
- CRUD tests: 4

## Next Steps

**Stage 2**: Backend API (Branch: `003-task-crud-api`)
- FastAPI endpoints for CRUD operations
- Request/response validation
- API documentation with OpenAPI/Swagger

## Resources

- [Neon Documentation](https://neon.tech/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Status**: ✅ Stage 1 Complete (Database Foundation)
**Tests**: 17/17 passing | **Coverage**: 82% | **Ready for**: Stage 2
