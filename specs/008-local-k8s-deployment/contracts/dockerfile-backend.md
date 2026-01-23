# Contract: Backend Dockerfile

**Type**: Infrastructure Contract
**Resource**: `phase-4-k8s/docker/backend/Dockerfile`

## Specification

### Build Arguments

| ARG | Default | Description |
|-----|---------|-------------|
| `PYTHON_VERSION` | `3.13` | Python version |

### Build Stages

#### Stage 1: Builder

```dockerfile
FROM python:${PYTHON_VERSION}-slim AS builder
```

**Purpose**: Install dependencies and prepare application

**Requirements**:
- Install `uv` package manager
- Copy `pyproject.toml` and `requirements.txt`
- Install all dependencies to virtual environment
- Copy application source code

#### Stage 2: Runner

```dockerfile
FROM python:${PYTHON_VERSION}-slim AS runner
```

**Purpose**: Minimal production image

**Requirements**:
- Copy virtual environment from builder
- Copy application source
- Set working directory to `/app`
- Expose port `8000`
- Run with `uvicorn`

### Environment Variables (Runtime)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `BETTER_AUTH_SECRET` | Yes | Auth signing secret |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

### Exposed Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 8000 | TCP | FastAPI HTTP server |

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Entry Point

```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Size Constraints

| Metric | Target | Maximum |
|--------|--------|---------|
| Final image size | <300MB | 500MB |
| Layer count | <10 | 15 |

### Build Command

```bash
docker build \
  -t todo-backend:latest \
  -f phase-4-k8s/docker/backend/Dockerfile \
  phase-3-chatbot/backend
```
