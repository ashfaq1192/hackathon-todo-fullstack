# Phase V - Cloud Deployment (Google Kubernetes Engine)

**Branch**: `main`
**Last Updated**: 2026-02-09
**Status**: Deployed and Live

---

## Live Application

| Service | URL | Status |
|---------|-----|--------|
| **Frontend (UI)** | [http://34.44.146.146](http://34.44.146.146) | Deployed |
| **Backend (API)** | [http://34.57.215.48](http://34.57.215.48) | Deployed |
| **Health Check** | [http://34.57.215.48/health](http://34.57.215.48/health) | Healthy |
| **API Docs** | [http://34.57.215.48/docs](http://34.57.215.48/docs) | Available |

---

## Overview

Phase V deploys the Todo Chatbot application to **Google Kubernetes Engine (GKE)** with:
- **GKE Standard Cluster** with LoadBalancer services for external access
- **Docker Hub** images (multi-stage builds, linux/amd64)
- **Neon PostgreSQL** as external managed database
- **Gemini AI** for chatbot functionality
- **Better Auth** for JWT-based authentication

---

## Architecture

```
                        Internet
                           |
              +------------+------------+
              |                         |
              v                         v
   +-------------------+    +-------------------+
   | Frontend LB       |    | Backend LB        |
   | 34.44.146.146:80  |    | 34.57.215.48:80   |
   +-------------------+    +-------------------+
              |                         |
              v                         v
   +-------------------+    +-------------------+
   | Frontend Pod      |    | Backend Pod       |
   | Next.js 16        |    | FastAPI           |
   | Port 3000         |    | Port 8000         |
   | Better Auth       |    | MCP Tools (5)     |
   +-------------------+    | Gemini AI Client  |
                            +-------------------+
                                       |
                                       v
                            +-------------------+
                            | Neon PostgreSQL   |
                            | (External DB)     |
                            | SSL/TLS           |
                            +-------------------+
```

---

## Docker Hub Images

All images are built for `linux/amd64` and publicly available:

| Image | Tag | Description |
|-------|-----|-------------|
| `ashfaq1192/todo-frontend` | **v4** | Next.js + Better Auth (GKE IPs baked in) |
| `ashfaq1192/todo-backend` | v2 | FastAPI + MCP Tools + Gemini AI |

### Pull Images

```bash
docker pull ashfaq1192/todo-frontend:v4
docker pull ashfaq1192/todo-backend:v2
```

---

## Deployment Guide

### Prerequisites

- GKE cluster running with `kubectl` connected
- Docker installed locally + Docker Hub account
- `gcloud` CLI authenticated

### Step 1: Deploy Services to Get LoadBalancer IPs

```bash
kubectl create namespace todo-app
kubectl apply -f deploy.yaml
kubectl get svc -n todo-app --watch
# Wait for EXTERNAL-IP to be assigned (1-3 minutes)
```

### Step 2: Build Frontend with Correct IPs

Next.js `NEXT_PUBLIC_*` variables are **baked into the JS bundle at build time**.
They CANNOT be changed at runtime via K8s env vars. Use `--build-arg`:

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://<BACKEND_LB_IP> \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://<BACKEND_LB_IP>/api \
  --platform linux/amd64 \
  -t ashfaq1192/todo-frontend:v4 \
  -f phase-4-k8s/docker/frontend/Dockerfile \
  phase-3-chatbot/frontend

docker push ashfaq1192/todo-frontend:v4
```

### Step 3: Create Kubernetes Secrets

```bash
kubectl delete secret project-secrets --namespace=todo-app --ignore-not-found=true

kubectl create secret generic project-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL="${REAL_DB_URL}" \
  --from-literal=JWT_SECRET_KEY="${JWT_SECRET}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_KEY}" \
  --from-literal=GEMINI_MODEL="gemini-2.5-flash" \
  --from-literal=GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/" \
  --from-literal=CORS_ORIGINS="http://<FRONTEND_LB_IP>,http://localhost:3000" \
  --from-literal=BETTER_AUTH_SECRET="${BETTER_AUTH}" \
  --from-literal=BETTER_AUTH_URL="http://<FRONTEND_LB_IP>" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="http://<FRONTEND_LB_IP>" \
  --from-literal=NEXT_PUBLIC_API_URL="http://<BACKEND_LB_IP>" \
  --from-literal=DAPR_ENABLED="false"
```

### Step 4: Update Deployment and Restart

```bash
# Update image version in deploy.yaml to v4, then:
kubectl apply -f deploy.yaml
kubectl delete pods --all --namespace=todo-app

# Verify pods are running
kubectl get pods -n todo-app --watch
```

### Step 5: Verify

1. Open `http://<FRONTEND_LB_IP>` in browser
2. Sign up / Log in
3. Create, complete, and delete tasks
4. Test the AI chatbot

---

## Critical Lessons Learned

### 1. NEXT_PUBLIC_* Variables Are Build-Time Only

| Variable Type | When Read | Can Change at Runtime? |
|---------------|-----------|----------------------|
| `NEXT_PUBLIC_*` | `npm run build` | NO - frozen in JS bundle |
| Server-side (e.g. `DATABASE_URL`) | Server startup | YES - via K8s env vars |

If you set `NEXT_PUBLIC_API_URL` in a K8s ConfigMap/Secret, the **browser will still call localhost**.
You MUST use `--build-arg` during `docker build`.

### 2. .dockerignore Blocks .env Files

The frontend `.dockerignore` excludes `.env`, `.env.local`, etc.:
```
.env
.env.local
.env.development.local
```

Creating a `.env` file and hoping Docker copies it into the image will **silently fail**.
The `--build-arg` approach bypasses `.dockerignore` entirely.

### 3. Two-Pass Deployment Pattern

You can't know LoadBalancer IPs before deploying, but you need them to build the frontend.
Solution:

1. **First pass**: Deploy with any image to get LoadBalancer IPs
2. **Build**: Rebuild frontend with correct IPs via `--build-arg`
3. **Second pass**: Push new image, update deployment, restart pods

### 4. Backend Doesn't Need Rebuilding for Config Changes

The backend reads `CORS_ORIGINS`, `DATABASE_URL`, etc. from environment at startup.
To change these, just update K8s Secrets and restart pods - no Docker rebuild needed.

### 5. CORS Must Include Frontend LB IP

The backend defaults to `CORS_ORIGINS=http://localhost:3000`. In GKE, the browser
is at `http://34.44.146.146`, so CORS must include that origin:
```
CORS_ORIGINS=http://34.44.146.146,http://localhost:3000
```

### 6. Always Use --platform linux/amd64

GKE nodes are x86_64. Building on Apple Silicon (ARM64) without `--platform linux/amd64`
produces images that crash with `exec format error`.

---

## Directory Structure

```
phase-5-cloud-deployment/
├── README.md                       # This file
├── IMPLEMENTATION_GUIDE.md         # Detailed implementation reference
├── SETUP_PREREQUISITES.md          # Prerequisites installation
├── NEXT_STEPS.md                   # Future enhancements
├── GKE_debugging.md                # GKE-specific debugging notes
├── k8s/                            # Kubernetes manifests
│   ├── backend-loadbalancer.yaml   # Backend LoadBalancer service
│   └── kafka/                      # Kafka/Redpanda manifests (future)
├── dapr/                           # Dapr components (future)
│   └── components/
├── services/                       # Microservices (future)
│   ├── audit-service/
│   ├── notification-service/
│   └── recurring-task-service/
├── scripts/                        # Deployment scripts
│   └── verify-prerequisites.sh
└── docs.md                         # Additional documentation
```

---

## Environment Variables Reference

### Build-Time (Frontend - via --build-arg)

| Variable | Example Value | Purpose |
|----------|---------------|---------|
| `NEXT_PUBLIC_API_URL` | `http://34.57.215.48` | Browser API calls to backend |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | `http://34.44.146.146` | Auth redirect URLs |
| `BETTER_AUTH_URL` | `http://34.44.146.146` | Server-side auth URL |
| `NEXT_PUBLIC_CHATKIT_API_ENDPOINT` | `http://34.57.215.48/api` | ChatKit endpoint |

### Runtime (Both - via K8s Secrets)

| Variable | Used By | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | Both | Neon PostgreSQL connection |
| `JWT_SECRET_KEY` | Both | Token signing (MUST match) |
| `BETTER_AUTH_SECRET` | Frontend | Session signing |
| `CORS_ORIGINS` | Backend | Allowed frontend origins |
| `GEMINI_API_KEY` | Backend | AI chatbot API |
| `GEMINI_MODEL` | Backend | Model version (gemini-2.5-flash) |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "Failed to fetch" in browser | `NEXT_PUBLIC_*` vars not set during build | Rebuild with `--build-arg` |
| CORS errors | Backend `CORS_ORIGINS` missing frontend IP | Update K8s secret, restart pods |
| 401 on all API calls | JWT secret mismatch | Ensure same `JWT_SECRET_KEY` in both |
| `exec format error` | ARM64 image on AMD64 node | Rebuild with `--platform linux/amd64` |
| ImagePullBackOff | Image not pushed or wrong tag | Verify `docker push` completed |
| LoadBalancer `<pending>` | Quota or permission issue | Check `kubectl describe svc` events |

---

## Related Documentation

- **GKE Deployment Skill**: [../.claude/skills/gke-fullstack-deployment/](../.claude/skills/gke-fullstack-deployment/) (comprehensive pitfalls + workflow guide)
- **Phase IV (Local K8s)**: [../phase-4-k8s/README.md](../phase-4-k8s/README.md)
- **Phase III (Chatbot)**: [../phase-3-chatbot/README.md](../phase-3-chatbot/README.md)
- **Hackathon Requirements**: [../Hackathon II - Todo Spec-Driven Development.pdf](../Hackathon%20II%20-%20Todo%20Spec-Driven%20Development.pdf)

---

**Maintained by**: AI-Assisted Development (Claude Code + Gemini)
**Last Updated**: 2026-02-09
