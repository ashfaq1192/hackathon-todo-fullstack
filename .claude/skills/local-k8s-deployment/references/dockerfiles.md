# Dockerfile Patterns

## Table of Contents
- [FastAPI Backend (Python)](#fastapi-backend-python)
- [Next.js Frontend (Node.js)](#nextjs-frontend-nodejs)
- [.dockerignore Patterns](#dockerignore-patterns)

## FastAPI Backend (Python)

Multi-stage build with virtual environment isolation:

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.13-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Key patterns:
- Virtual env in `/opt/venv` copied between stages (avoids reinstalling)
- Runtime-only system deps in runner (no gcc/git)
- Non-root `appuser` for security
- `HEALTHCHECK` using curl against `/health` endpoint

## Next.js Frontend (Node.js)

Three-stage build with standalone output:

```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
    if [ -f pnpm-lock.yaml ]; then \
        corepack enable pnpm && pnpm install --frozen-lockfile; \
    elif [ -f yarn.lock ]; then \
        yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then \
        npm ci; \
    else \
        npm install; \
    fi

# Stage 2: Builder
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# Inject standalone output if not configured
RUN if ! grep -q "output.*standalone" next.config.js 2>/dev/null; then \
        sed -i 's/const nextConfig = {/const nextConfig = {\n  output: "standalone",/' next.config.js; \
    fi
RUN npm run build

# Stage 3: Runner
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

Key patterns:
- Three stages: deps → builder → runner (optimal layer caching)
- Auto-detects package manager (npm/pnpm/yarn)
- Injects `output: "standalone"` if missing from next.config.js
- Uses `wget` for healthcheck (alpine has no curl by default)
- Non-root `nextjs` user

## .dockerignore Patterns

### Python Backend
```
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.coverage
.env
.env.local
.git/
*.md
docs/
.ruff_cache/
Dockerfile*
.dockerignore
docker-compose*.yml
```

### Node.js Frontend
```
node_modules/
.next/
out/
build/
coverage/
.env
.env.local
.env.*.local
npm-debug.log*
.vercel/
*.tsbuildinfo
.git/
*.md
Dockerfile*
.dockerignore
docker-compose*.yml
__tests__/
e2e/
```
