---
name: backend-railway-deployment
description: Deploy FastAPI backend to Railway with correct configuration. Use when (1) Deploying backend to Railway, (2) Debugging Railway build failures, (3) Configuring Python dependencies, (4) Setting up database connections, (5) Troubleshooting module import errors.
---

# Backend Railway Deployment

This skill provides step-by-step instructions for deploying the FastAPI backend to Railway, including all configuration settings that work for this project.

## Project Configuration

### Verified Working Settings

| Setting | Value |
|---------|-------|
| **Platform** | Railway |
| **Framework** | FastAPI + Uvicorn |
| **Python Version** | 3.13+ |
| **Root Directory** | `phase-3-chatbot/backend` |
| **Start Command** | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |

### Environment Variables (Railway Dashboard)

Set these in Railway Dashboard → Service → Variables:

```
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname?sslmode=require

# AI/LLM
GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-2.0-flash-exp

# Authentication
JWT_SECRET_KEY=<must-match-frontend-jwt-secret>

# App Config
ENVIRONMENT=production
PORT=8080
```

**SECURITY:** Never commit API keys to git. Always use environment variables.

## Critical Configuration Files

### 1. requirements.txt

**Location:** `phase-3-chatbot/backend/requirements.txt`

```txt
fastapi>=0.115.0
uvicorn>=0.32.0
sqlmodel>=0.0.22
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
pydantic>=2.9.0
pydantic-settings>=2.6.0

# OpenAI Swarm (from GitHub - NOT PyPI)
swarm @ git+https://github.com/openai/swarm.git
openai>=1.0.0

# MCP and SSE
mcp>=1.0.0
sse-starlette>=1.6.0

# Token counting and retry
tiktoken
tenacity
```

**CRITICAL Dependencies:**
- `swarm` must be installed from GitHub (not PyPI): `swarm @ git+https://github.com/openai/swarm.git`
- `openai>=1.0.0` for Gemini client compatibility
- `mcp>=1.0.0` for Model Context Protocol
- `sse-starlette>=1.6.0` for Server-Sent Events

### 2. Procfile (Optional)

**Location:** `phase-3-chatbot/backend/Procfile`

```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

Railway auto-detects Python and uses this if present.

### 3. runtime.txt (Optional)

**Location:** `phase-3-chatbot/backend/runtime.txt`

```
python-3.13
```

## Deployment Methods

### Method 1: Railway Dashboard (Recommended)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Create new project or select existing
3. Connect GitHub repository
4. Set **Root Directory** to `phase-3-chatbot/backend`
5. Add environment variables
6. Deploy

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up
```

## Common Errors and Fixes

### Error: "ModuleNotFoundError: No module named 'swarm'"

**Cause:** `swarm` package not in PyPI, must be from GitHub

**Fix:** Update requirements.txt:
```txt
# Wrong:
openai-agents>=0.6.5

# Correct:
swarm @ git+https://github.com/openai/swarm.git
```

### Error: "ModuleNotFoundError: No module named 'sse_starlette'"

**Cause:** Missing dependency

**Fix:** Add to requirements.txt:
```txt
sse-starlette>=1.6.0
```

### Error: "ModuleNotFoundError: No module named 'mcp'"

**Cause:** Missing MCP dependency

**Fix:** Add to requirements.txt:
```txt
mcp>=1.0.0
```

### Error: "ModuleNotFoundError: No module named 'openai'"

**Cause:** openai package not explicitly listed

**Fix:** Add to requirements.txt:
```txt
openai>=1.0.0
```

### Error: Database connection failed

**Cause:** Missing SSL mode or wrong URL format

**Fix:** Ensure DATABASE_URL includes `?sslmode=require`:
```
postgresql://user:pass@host:port/dbname?sslmode=require
```

### Error: "BetterAuthError: default secret"

**Cause:** JWT_SECRET_KEY not set

**Fix:** Add JWT_SECRET_KEY to Railway environment variables

## Deployment Checklist

- [ ] Root Directory set to `phase-3-chatbot/backend` in Railway
- [ ] `swarm` installed from GitHub (not PyPI)
- [ ] `openai`, `mcp`, `sse-starlette` in requirements.txt
- [ ] DATABASE_URL set with `?sslmode=require`
- [ ] GEMINI_API_KEY set (not the exposed one - generate new!)
- [ ] JWT_SECRET_KEY matches frontend
- [ ] No secrets committed to git

## Health Check

After deployment, verify:

```bash
# Check root endpoint
curl https://hackathon-todo-fullstack-backend-production.up.railway.app/

# Expected response:
# {"message": "Welcome to the Todo API", ...}
```

## Architecture

```
phase-3-chatbot/backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment config
│   ├── models/              # SQLModel database models
│   ├── database/            # Database connection
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py      # Chat endpoint
│   │       ├── mcp.py       # MCP tools endpoint
│   │       └── tasks.py     # CRUD endpoints
│   └── services/
│       ├── chat_service.py  # Swarm + Gemini integration
│       └── gemini_client.py # OpenAI-compatible Gemini client
├── requirements.txt
└── Procfile
```

## Gemini Client Configuration

The backend uses Gemini API via OpenAI-compatible interface:

```python
# gemini_client.py
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Use with model: "gemini-2.0-flash-exp"
```

## URLs

- **Production:** https://hackathon-todo-fullstack-backend-production.up.railway.app
- **Railway Dashboard:** https://railway.app/project/[project-id]

## Security Notes

1. **Rotate exposed keys immediately** - If a key was committed to git, revoke and regenerate
2. **Use Railway's secret management** - Never hardcode secrets
3. **SSL required for database** - Always use `sslmode=require`
4. **CORS configuration** - Ensure frontend URL is allowed
