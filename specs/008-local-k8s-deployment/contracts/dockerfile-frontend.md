# Contract: Frontend Dockerfile

**Type**: Infrastructure Contract
**Resource**: `phase-4-k8s/docker/frontend/Dockerfile`

## Specification

### Build Arguments

| ARG | Default | Description |
|-----|---------|-------------|
| `NODE_VERSION` | `22` | Node.js version |

### Build Stages

#### Stage 1: Dependencies

```dockerfile
FROM node:${NODE_VERSION}-alpine AS deps
```

**Purpose**: Install node_modules

**Requirements**:
- Copy `package.json` and lock file
- Install dependencies with `pnpm` or `npm`
- Use `--frozen-lockfile` for reproducibility

#### Stage 2: Builder

```dockerfile
FROM node:${NODE_VERSION}-alpine AS builder
```

**Purpose**: Build Next.js application

**Requirements**:
- Copy node_modules from deps stage
- Copy application source
- Set `NEXT_TELEMETRY_DISABLED=1`
- Run `npm run build`
- Enable standalone output mode

#### Stage 3: Runner

```dockerfile
FROM node:${NODE_VERSION}-alpine AS runner
```

**Purpose**: Minimal production image

**Requirements**:
- Create non-root user `nextjs`
- Copy standalone output from builder
- Copy static and public directories
- Set `NODE_ENV=production`
- Expose port `3000`

### Environment Variables (Runtime)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | Backend API URL |
| `BETTER_AUTH_SECRET` | Yes | Auth signing secret |
| `DATABASE_URL` | Yes | For Better Auth |
| `NODE_ENV` | No | Environment (default: production) |

### Exposed Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 3000 | TCP | Next.js HTTP server |

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
```

### Entry Point

```dockerfile
CMD ["node", "server.js"]
```

### Size Constraints

| Metric | Target | Maximum |
|--------|--------|---------|
| Final image size | <300MB | 500MB |
| Layer count | <10 | 15 |

### Build Command

```bash
docker build \
  -t todo-frontend:latest \
  -f phase-4-k8s/docker/frontend/Dockerfile \
  phase-3-chatbot/frontend
```

### Next.js Configuration

Required in `next.config.js`:

```javascript
module.exports = {
  output: 'standalone',
  // ... other config
}
```
