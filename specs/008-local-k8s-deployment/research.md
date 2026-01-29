# Research: Local Kubernetes Deployment

**Feature**: 008-local-k8s-deployment
**Date**: 2026-01-22

## Research Tasks Completed

### 1. Backend Containerization (FastAPI + MCP)

**Decision**: Multi-stage Docker build with Python 3.13-slim base

**Rationale**:
- Python 3.13 required per `pyproject.toml` (`requires-python = ">=3.13"`)
- Multi-stage build separates build dependencies from runtime
- `python:3.13-slim` base provides minimal image size (~150MB base)
- UV package manager for faster, reproducible installs

**Key Dependencies Identified**:
- FastAPI 0.115+
- SQLModel 0.0.22+
- OpenAI Agents SDK (from git)
- MCP 1.2.0+
- psycopg2-binary (PostgreSQL driver)

**Alternatives Considered**:
- Alpine base: Rejected due to psycopg2 compilation issues
- Distroless: Rejected, needs shell for debugging in dev
- Poetry: Rejected, UV is project standard per constitution

### 2. Frontend Containerization (Next.js 16)

**Decision**: Multi-stage Docker build with Node 22-alpine base

**Rationale**:
- Next.js 16.1.3 with React 19 (per package.json)
- Node 22 required per `.nvmrc` file
- Alpine variant for smallest image size (~180MB final)
- Standalone output mode for optimized production builds

**Build Stages**:
1. `deps`: Install node_modules
2. `builder`: Build Next.js application
3. `runner`: Production image with standalone output

**Alternatives Considered**:
- Node 20: Rejected, project specifies Node 22
- Debian base: Rejected, larger image size
- Bun: Rejected, pnpm is project standard

### 3. Minikube Configuration

**Decision**: Minikube with Docker driver and required addons

**Rationale**:
- Docker driver works best on WSL2/Linux
- Required addons: ingress, metrics-server
- 4GB memory minimum, 2 CPUs recommended
- Single-node cluster sufficient for development

**Configuration**:
```bash
minikube start --driver=docker --memory=4096 --cpus=2
minikube addons enable ingress
minikube addons enable metrics-server
```

**Alternatives Considered**:
- Kind: Rejected, Minikube has better addon support
- k3s: Rejected, more complex setup
- Docker Desktop K8s: Rejected, Minikube specified in constitution

### 4. Helm Chart Structure

**Decision**: Standard Helm 3 chart with separate values files

**Rationale**:
- Helm 3 (Tiller-less) is current standard
- `values.yaml` for defaults, `values-minikube.yaml` for local overrides
- Separate templates per resource for clarity
- Helper functions in `_helpers.tpl` for DRY

**Chart Components**:
- Backend: Deployment, Service, health probes
- Frontend: Deployment, Service, health probes
- Shared: ConfigMap, Secret, Ingress

**Alternatives Considered**:
- Kustomize: Rejected, Helm specified in constitution
- Raw manifests: Rejected, need templating for env configs

### 5. Health Probes

**Decision**: HTTP liveness and readiness probes

**Backend Probes**:
- Liveness: `GET /health` (checks app is running)
- Readiness: `GET /health` (same endpoint, confirms ready for traffic)
- Initial delay: 10s (FastAPI startup time)
- Period: 10s, Timeout: 5s

**Frontend Probes**:
- Liveness: `GET /` (Next.js serves homepage)
- Readiness: `GET /` (confirms SSR is ready)
- Initial delay: 15s (Next.js cold start)
- Period: 10s, Timeout: 5s

**Alternatives Considered**:
- TCP probes: Rejected, HTTP provides better health insight
- Exec probes: Rejected, adds container overhead

### 6. Environment Configuration

**Decision**: ConfigMaps for non-sensitive, Secrets for sensitive data

**ConfigMap Values** (non-sensitive):
- `BACKEND_URL`: Internal service URL
- `FRONTEND_URL`: Ingress URL
- `LOG_LEVEL`: DEBUG/INFO

**Secret Values** (sensitive):
- `DATABASE_URL`: Neon PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API credentials
- `BETTER_AUTH_SECRET`: Authentication secret

**Alternatives Considered**:
- External Secrets: Rejected, overkill for local development
- Vault: Rejected, Phase V scope

### 7. AI DevOps Tools

**Decision**: Use kubectl-ai as primary AI tool (with Gordon as fallback)

**Rationale**:
- kubectl-ai is GCP-backed, stable, well-documented
- Works with multiple LLM providers (Gemini, OpenAI)
- Read-only by default (safe for exploration)
- Gordon may not be available in all regions

**Installation**:
```bash
# kubectl-ai
kubectl krew install ai
kubectl ai "check cluster status"

# Gordon (if Docker Desktop 4.53+)
docker ai "create Dockerfile for FastAPI"
```

**Alternatives Considered**:
- Kagent: Noted for future, requires more setup
- Pure Claude Code: Used as fallback for all AI generation

### 8. Image Loading Strategy

**Decision**: Use `minikube image load` for local images

**Rationale**:
- Avoids need for external registry
- Images built locally, loaded directly into Minikube
- Faster than pushing to Docker Hub
- Supports offline development

**Workflow**:
```bash
docker build -t todo-backend:latest ...
docker build -t todo-frontend:latest ...
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

**Alternatives Considered**:
- Docker Hub: Rejected, adds network dependency
- Minikube registry addon: More complex setup
- eval $(minikube docker-env): Can cause env issues

## Resolved Clarifications

All technical context items resolved through research. No NEEDS CLARIFICATION markers remain.

## Dependencies Verified

| Dependency | Version | Status |
|------------|---------|--------|
| Docker Desktop | 4.53+ | Required (Gordon optional) |
| Minikube | Latest | Required |
| Helm | 3.x | Required |
| kubectl | Compatible with Minikube | Required |
| kubectl-ai | Via krew | Recommended |
| Phase III Code | Complete | Verified exists |
| Neon PostgreSQL | External | Verified accessible |
