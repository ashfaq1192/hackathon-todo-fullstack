# Quickstart: Database & Models Setup

**Feature**: 002-database-setup
**Stage**: Stage 1 (Phase II)
**Estimated Time**: 15 minutes

## Overview

Get the database layer running in 15 minutes. This guide covers:
1. Setting up Neon PostgreSQL database
2. Configuring environment variables
3. Installing dependencies
4. Running tests

---

## Prerequisites

- Python 3.13+ installed
- UV package manager ([install guide](https://github.com/astral-sh/uv))
- Neon PostgreSQL account (free tier)
- Git (for version control)

---

## Step 1: Set Up Neon PostgreSQL (5 minutes)

### 1.1 Create Neon Account
1. Go to [neon.tech](https://neon.tech)
2. Sign up (free tier sufficient)
3. Create a new project (name: `hackathon-todo`)

### 1.2 Get Connection String
1. In Neon dashboard, go to **Connection Details**
2. Copy the **Connection String** (should look like):
   ```
   postgresql://user:password@ep-something.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Keep this handy for next step

---

## Step 2: Configure Environment (2 minutes)

### 2.1 Create Backend Directory
```bash
cd /path/to/hackathon-todo
mkdir -p backend
cd backend
```

### 2.2 Create .env File
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Neon connection string
# .env file should contain:
DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
```

**Important**: Never commit `.env` to git (already in `.gitignore`)

---

## Step 3: Install Dependencies (3 minutes)

### 3.1 Initialize UV Project
```bash
# From backend/ directory
uv init

# Or if pyproject.toml exists:
uv sync
```

### 3.2 Add Required Packages
```bash
uv add sqlmodel psycopg2-binary python-dotenv
uv add --dev pytest pytest-cov
```

This creates/updates `pyproject.toml` with dependencies:
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

---

## Step 4: Verify Setup (5 minutes)

### 4.1 Test Database Connection
Create a test script `test_connection.py`:

```python
from dotenv import load_dotenv
import os
from sqlmodel import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, echo=True)

try:
    with engine.connect() as conn:
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```bash
python test_connection.py
```

Expected output:
```
✅ Database connection successful!
```

### 4.2 Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_task_model.py -v
```

Expected output:
```
=================== test session starts ===================
collected 15 items

tests/unit/test_task_model.py ........  [53%]
tests/unit/test_connection.py ...      [73%]
tests/unit/test_crud.py ....           [100%]

=================== 15 passed in 2.31s ====================
```

---

## Project Structure

After setup, your directory should look like:

```
backend/
├── src/
│   ├── models/
│   │   └── task.py           # Task SQLModel
│   ├── database/
│   │   ├── connection.py     # Database engine and session
│   │   └── init_db.py        # Table creation
│   └── config.py             # Load DATABASE_URL
├── tests/
│   ├── unit/
│   │   ├── test_task_model.py
│   │   ├── test_connection.py
│   │   └── test_crud.py
│   └── conftest.py           # Pytest fixtures
├── .env                      # Your DATABASE_URL (gitignored)
├── .env.example              # Template
├── pyproject.toml            # Dependencies
└── README.md                 # Setup docs
```

---

## Common Issues & Solutions

### Issue 1: "DATABASE_URL not found"
**Symptom**: `ValueError: DATABASE_URL not found in environment`

**Solution**:
1. Verify `.env` file exists in `backend/` directory
2. Check `.env` contains `DATABASE_URL=postgresql://...`
3. Ensure no extra spaces: `DATABASE_URL=value` (not `DATABASE_URL = value`)

### Issue 2: "SSL connection required"
**Symptom**: `psycopg2.OperationalError: SSL connection required`

**Solution**: Add `?sslmode=require` to connection string:
```
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Issue 3: "psycopg2 not found"
**Symptom**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**: Install psycopg2-binary:
```bash
uv add psycopg2-binary
```

### Issue 4: Tests fail with connection errors
**Symptom**: `pytest` fails with database connection errors

**Solution**: Unit tests use in-memory SQLite (no Neon connection needed). If integration tests fail:
1. Check Neon database is running
2. Verify DATABASE_URL is correct
3. Check network connectivity

---

## Quick Commands Reference

```bash
# Install dependencies
uv add sqlmodel psycopg2-binary python-dotenv
uv add --dev pytest pytest-cov

# Run tests
pytest                                    # All tests
pytest --cov=src                         # With coverage
pytest tests/unit/test_task_model.py -v  # Specific file

# Code quality
ruff check src/                          # Lint code
ruff format src/                         # Format code

# Database operations (after implementation)
python -m src.database.init_db           # Create tables
```

---

## Next Steps

After completing this quickstart:

1. **Verify Acceptance Criteria** (from spec.md):
   - [ ] Database connection established
   - [ ] Task model defined with validation
   - [ ] Tables created automatically
   - [ ] CRUD operations work
   - [ ] Tests pass with 70%+ coverage

2. **Proceed to Stage 2**: Backend API (CRUD Operations)
   - Branch: `003-task-crud-api`
   - Builds FastAPI endpoints using Task model

3. **Review Documentation**:
   - [data-model.md](./data-model.md) - Task entity details
   - [research.md](./research.md) - Technical decisions
   - [contracts/task-schema.md](./contracts/task-schema.md) - Data contract

---

## Development Workflow

### Daily Workflow
```bash
# 1. Pull latest changes
git pull origin main

# 2. Activate environment (if using venv)
source .venv/bin/activate

# 3. Run tests (ensure nothing broken)
pytest

# 4. Make changes to src/ files

# 5. Run tests again
pytest --cov=src

# 6. Lint and format
ruff check src/
ruff format src/

# 7. Commit when tests pass
git add .
git commit -m "feat(db): add Task model validation"
```

### Running Individual Tests
```bash
# Test specific functionality
pytest tests/unit/test_task_model.py::test_create_valid_task -v

# Run tests matching pattern
pytest -k "task_model" -v

# Stop on first failure (useful for debugging)
pytest -x
```

---

## Getting Help

- **Spec Issues**: See [spec.md](./spec.md) for requirements
- **Technical Decisions**: See [research.md](./research.md) for rationale
- **Data Model Questions**: See [data-model.md](./data-model.md)
- **Neon PostgreSQL**: [Neon Docs](https://neon.tech/docs)
- **SQLModel**: [SQLModel Docs](https://sqlmodel.tiangolo.com/)

---

## Summary

You should now have:
- ✅ Neon PostgreSQL database created
- ✅ DATABASE_URL configured in `.env`
- ✅ Dependencies installed (SQLModel, psycopg2-binary, pytest)
- ✅ Tests passing
- ✅ Ready to implement Stage 1 tasks

**Estimated Total Time**: 15 minutes

**Next Command**: Run `/sp.tasks` to generate implementation tasks
