# Phase IV - Local Kubernetes Deployment

## Overview

Containerize and deploy Phase III Todo Chatbot to local Kubernetes (Minikube) using Docker multi-stage builds and Helm charts.

## Quick Access Guide

### Option 1: Port-Forward (Fastest)

```bash
# Terminal 1: Frontend
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Terminal 2: Backend
kubectl port-forward svc/todo-chatbot-backend 8000:8000
```

**Access:** http://localhost:3000

### Option 2: Via Ingress (todo.local)

```bash
# 1. Add to hosts file
# Linux/WSL:
echo "192.168.49.2 todo.local" | sudo tee -a /etc/hosts

# Windows (Admin PowerShell):
Add-Content C:\Windows\System32\drivers\etc\hosts "192.168.49.2 todo.local"

# 2. Start tunnel (required for Windows/WSL)
minikube tunnel

# 3. Access
open http://todo.local
```

### Option 3: Share with Others (ngrok)

```bash
kubectl port-forward svc/todo-chatbot-frontend 3000:3000 &
ngrok http 3000
# Share the ngrok URL
```

### Production URLs (Phase III - Already Deployed)

| Service | URL |
|---------|-----|
| Frontend | https://hackathon-todo-fullstack.vercel.app |
| Backend | https://hackathon-todo-fullstack-backend-production.up.railway.app |

---

## Deployment Status

### Current State (2026-01-23)

| Component | Status | Details |
|-----------|--------|---------|
| Minikube Cluster | ✅ Running | 192.168.49.2 |
| Ingress Addon | ✅ Enabled | nginx |
| todo-backend:v1 | ✅ Running | 572MB, FastAPI + MCP |
| todo-frontend:v1 | ✅ Running | 335MB, Next.js |
| Helm Release | ✅ Deployed | Revision 3 |

### Pod Status

```
NAME                                     READY   STATUS    RESTARTS
todo-chatbot-backend-fb7d7754b-drfg6     1/1     Running   0
todo-chatbot-frontend-7569847659-cbqk6   1/1     Running   0
```

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Containerization | Docker (Docker Desktop 4.57+) |
| Orchestration | Kubernetes (Minikube) |
| Package Manager | Helm 3.x |
| AI DevOps | kubectl-ai, Docker AI (Gordon) |
| Database | External Neon PostgreSQL |

---

## Commands Reference

### Docker Images

```bash
# Build images
docker build -t todo-backend:v1 -f phase-4-k8s/docker/backend/Dockerfile phase-3-chatbot/backend
docker build -t todo-frontend:v1 -f phase-4-k8s/docker/frontend/Dockerfile phase-3-chatbot/frontend

# Load into Minikube
minikube image load todo-backend:v1 todo-frontend:v1

# Verify
minikube image ls | grep todo
```

### Minikube

```bash
# Start cluster
minikube start --driver=docker --memory=4096 --cpus=2

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Get IP
minikube ip

# Dashboard
minikube dashboard
```

### Helm

```bash
# Install
helm install todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-minikube.yaml

# Upgrade
helm upgrade todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-minikube.yaml

# Rollback
helm rollback todo-chatbot <revision>

# History
helm history todo-chatbot

# Uninstall
helm uninstall todo-chatbot

# Lint/Validate
helm lint ./helm/todo-chatbot
helm template todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-minikube.yaml
```

### Kubernetes Debugging

```bash
# Pod status
kubectl get pods -l app.kubernetes.io/instance=todo-chatbot

# Logs
kubectl logs -f deploy/todo-chatbot-backend
kubectl logs -f deploy/todo-chatbot-frontend

# Exec into pod
kubectl exec -it deploy/todo-chatbot-backend -- /bin/bash

# Describe pod
kubectl describe pod -l app.kubernetes.io/name=todo-chatbot-backend

# Service endpoints
kubectl get svc
kubectl get ingress
```

---

## Folder Structure

```
phase-4-k8s/
├── docker/
│   ├── backend/
│   │   ├── Dockerfile          # Multi-stage FastAPI build
│   │   └── .dockerignore
│   └── frontend/
│       ├── Dockerfile          # Multi-stage Next.js build
│       └── .dockerignore
├── helm/
│   └── todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml         # Default values
│       ├── values-minikube.yaml # Minikube-specific values
│       └── templates/
│           ├── _helpers.tpl
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           └── ingress.yaml
├── scripts/
│   ├── build-images.sh
│   ├── deploy-minikube.sh
│   └── cleanup.sh
├── docker-compose.yml          # Local testing
└── CLAUDE.md
```

---

## Configuration

### Environment Variables

**Backend (via Kubernetes Secrets):**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `GEMINI_API_KEY` - Gemini API key for chatbot
- `BETTER_AUTH_SECRET` - Auth secret (must match frontend)
- `JWT_SECRET_KEY` - JWT signing key

**Frontend (via ConfigMap):**
- `NEXT_PUBLIC_BACKEND_URL` - Public API URL
- `BACKEND_URL` - Internal K8s service URL

### Helm Values Override

```bash
# Override specific values
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-minikube.yaml \
  --set backend.replicaCount=2 \
  --set configMap.data.LOG_LEVEL=DEBUG
```

---

## Session Log

### 2026-01-22: Implementation Started

- Created multi-stage Dockerfiles for backend and frontend
- Created Helm chart structure
- Set up docker-compose for local testing

### 2026-01-23: Deployment Completed

- Built Docker images (backend: 572MB, frontend: 335MB)
- Started Minikube cluster
- Enabled ingress addon
- Deployed via Helm
- Verified health checks passing
- Demonstrated upgrade/rollback lifecycle
- Installed and documented kubectl-ai

---

## AI DevOps Tools Usage (FR-011, FR-012)

### kubectl-ai

**Installation:**
```bash
# Install krew
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)

# Add to PATH
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Install kubectl-ai
kubectl krew install ai
```

**Configuration:**
```bash
export GEMINI_API_KEY="<your-api-key>"
```

**Usage:**
```bash
kubectl ai "list all pods and their status"
kubectl ai "why is the backend pod failing"
kubectl ai "scale the frontend to 3 replicas"
```

### Docker AI (Gordon)

**Availability:** Docker Desktop 4.53+ with Beta features enabled

```bash
docker ai "create a Dockerfile for FastAPI app"
docker ai "optimize this Dockerfile for size"
```

---

## End-to-End Test Results

### Backend API Tests

| Endpoint | Status | Response |
|----------|--------|----------|
| `/health` | ✅ 200 | `{"status":"healthy","service":"Todo API","version":"0.2.0"}` |
| `/docs` | ✅ 200 | OpenAPI documentation |
| `/api/mcp/health` | ✅ 200 | `{"status":"healthy","tools_count":5}` |
| `/api/mcp/tools` | ✅ 200 | 5 MCP tools available |

### MCP Tools Available

1. `add_task` - Create a new task
2. `list_tasks` - List user tasks
3. `complete_task` - Mark task complete
4. `update_task` - Update task details
5. `delete_task` - Delete a task

### Cross-Service Connectivity

```bash
# Test from frontend pod
kubectl exec deploy/todo-chatbot-frontend -- node -e "
const http = require('http');
http.get('http://todo-chatbot-backend:8000/health', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});"

# Result: {"status":"healthy","service":"Todo API","version":"0.2.0"}
```

---

## Lifecycle Operations

### Revision History

| Revision | Status | Description |
|----------|--------|-------------|
| 1 | superseded | Initial install |
| 2 | superseded | Upgrade (LOG_LEVEL=INFO) |
| 3 | deployed | Rollback to 1 |

### Upgrade Example

```bash
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-minikube.yaml \
  --set configMap.data.LOG_LEVEL=INFO
```

### Rollback Example

```bash
helm rollback todo-chatbot 1
```

---

## Troubleshooting

### Pod not starting

```bash
kubectl describe pod -l app.kubernetes.io/name=todo-chatbot-backend
kubectl logs deploy/todo-chatbot-backend --previous
```

### Image not found

```bash
# Verify image is in Minikube
minikube image ls | grep todo

# Reload if needed
minikube image load todo-backend:v1
```

### Ingress not working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress todo-chatbot
```

### Database connection failed

- Verify `DATABASE_URL` in secrets
- Check Neon dashboard for connection limits
- Ensure `sslmode=require` in connection string

---

## Requirements Compliance

| Requirement | Status |
|-------------|--------|
| FR-001: Containerize backend | ✅ |
| FR-002: Containerize frontend | ✅ |
| FR-003: Multi-stage builds <500MB | ⚠️ Backend 572MB |
| FR-004: docker-compose.yml | ✅ |
| FR-005: Deploy to Minikube with Helm | ✅ |
| FR-006: Helm includes all resources | ✅ |
| FR-007: ConfigMaps/Secrets | ✅ |
| FR-008: Backend health probes | ✅ |
| FR-009: Frontend health probes | ✅ |
| FR-010: Scripts | ✅ |
| FR-011: AI DevOps tool usage | ✅ |
| FR-012: Document AI tool | ✅ |
| FR-013: Neon connectivity | ✅ |
| FR-014: Environment-specific values | ✅ |
| FR-015: Ingress addon | ✅ |
