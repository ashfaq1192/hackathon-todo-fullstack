# Database Migrations

This directory contains database migration scripts for the Todo application.

## Running Migrations

Migrations should be run **once** after deploying new backend code that changes the database schema.

### Migration 001: Add Priority Column

Adds a `priority` column to the `tasks` table with values: `low`, `medium`, `high`.

**Local Development:**
```bash
cd backend
source .venv/bin/activate
python migrations/001_add_priority_column.py
```

**Railway Deployment:**
1. After deploying the backend with the new code
2. Open Railway dashboard → Your service → Shell
3. Run:
```bash
python migrations/001_add_priority_column.py
```

## Migration Safety

- Migrations are idempotent (safe to run multiple times)
- Each migration checks if changes already exist before applying
- Existing data is preserved with sensible defaults
- All operations are logged for verification

## Creating New Migrations

When creating new migrations:
1. Number them sequentially (002_, 003_, etc.)
2. Include descriptive names
3. Add safety checks (check if already applied)
4. Log all operations
5. Update this README
