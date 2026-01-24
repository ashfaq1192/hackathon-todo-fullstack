---
name: local-k8s-deployment
description: Deploy full-stack applications (FastAPI backend + Next.js frontend) to a local Kubernetes cluster using Docker multi-stage builds, Minikube, and Helm charts. Use when (1) Containerizing a full-stack application with Docker multi-stage builds, (2) Deploying to local Kubernetes with Minikube, (3) Creating Helm charts for frontend/backend services, (4) Setting up Kubernetes ingress, configmaps, and secrets, (5) Building Docker images with health checks and non-root users, (6) Creating deployment/cleanup scripts for local K8s workflows, (7) Configuring external database connectivity from K8s pods
---

# Local Kubernetes Deployment

Deploy a full-stack application (Python backend + Node.js frontend) to a local Kubernetes cluster using Docker multi-stage builds, Minikube, and Helm 3.

## Workflow

1. Create multi-stage Dockerfiles (backend + frontend)
2. Create .dockerignore files
3. Create docker-compose.yml for local container testing
4. Create Helm chart structure (Chart.yaml, values, templates)
5. Create deployment scripts (build, deploy, cleanup)
6. Build images → load into Minikube → deploy with Helm
7. Verify with health checks and port-forwarding

## Prerequisites

- Docker Desktop 4.53+ (or Docker Engine)
- Minikube
- Helm 3.x
- kubectl

## Quick Start

```bash
# 1. Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# 2. Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Build images
docker build -t <backend-image>:v1 -f docker/backend/Dockerfile <backend-source-dir>
docker build -t <frontend-image>:v1 -f docker/frontend/Dockerfile <frontend-source-dir>

# 4. Load into Minikube
minikube image load <backend-image>:v1 <frontend-image>:v1

# 5. Deploy with Helm
helm install <release> ./helm/<release> -f ./helm/<release>/values-minikube.yaml

# 6. Verify
kubectl get pods -l app.kubernetes.io/instance=<release>

# 7. Access
kubectl port-forward svc/<release>-frontend 3000:3000
```

## Project Structure

Generate this directory structure:

```
<k8s-dir>/
├── docker/
│   ├── backend/
│   │   ├── Dockerfile          # Multi-stage Python build
│   │   └── .dockerignore
│   └── frontend/
│       ├── Dockerfile          # Multi-stage Node.js build
│       └── .dockerignore
├── helm/<release-name>/
│   ├── Chart.yaml
│   ├── values.yaml             # Defaults (no secrets)
│   ├── values-minikube.yaml    # Local overrides (with secrets)
│   └── templates/
│       ├── _helpers.tpl
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       ├── configmap.yaml
│       ├── secrets.yaml
│       └── ingress.yaml
├── scripts/
│   ├── build-images.sh
│   ├── deploy-minikube.sh
│   └── cleanup.sh
└── docker-compose.yml          # Local container testing
```

## Key Design Decisions

- **imagePullPolicy: Never** — Use local images loaded via `minikube image load` (no registry needed)
- **ClusterIP services** — Internal networking; expose via Ingress or port-forward
- **envFrom with ConfigMap + Secret** — All env vars injected from K8s resources
- **stringData in Secrets** — Avoids manual base64 encoding
- **Non-root users** — Security best practice in Dockerfiles
- **Health probes** — Liveness + readiness on both services
- **Standalone Next.js output** — Minimal production image with `node server.js`
- **External database** — No StatefulSets needed; connect to managed DB (e.g., Neon PostgreSQL)

## Ingress Routing Pattern

Route `/api` paths to backend, everything else to frontend:

```yaml
paths:
  - path: /api
    pathType: Prefix
    service: backend
  - path: /health
    pathType: Exact
    service: backend
  - path: /
    pathType: Prefix
    service: frontend
```

Access via `<app>.local` after adding to `/etc/hosts`:
```bash
echo "$(minikube ip) <app>.local" | sudo tee -a /etc/hosts
```

## Common Operations

```bash
# Upgrade deployment
helm upgrade <release> ./helm/<release> -f ./helm/<release>/values-minikube.yaml

# Rollback
helm rollback <release> <revision>

# View logs
kubectl logs -f deploy/<release>-backend
kubectl logs -f deploy/<release>-frontend

# Exec into pod
kubectl exec -it deploy/<release>-backend -- /bin/bash

# Check pod details
kubectl describe pod -l app.kubernetes.io/name=<release>-backend

# Dashboard
minikube dashboard
```

## Debugging

- **Pod not starting**: `kubectl describe pod -l app.kubernetes.io/name=<release>-backend`
- **Image not found**: `minikube image ls | grep <image>` then reload if missing
- **Ingress not working**: Check `kubectl get pods -n ingress-nginx` and `kubectl describe ingress`
- **DB connection failed**: Verify `DATABASE_URL` in secrets, check external DB connectivity

## References

- **Dockerfile patterns**: See [references/dockerfiles.md](references/dockerfiles.md) for complete multi-stage build examples
- **Helm chart patterns**: See [references/helm-chart.md](references/helm-chart.md) for all template examples
- **Script patterns**: See [references/scripts.md](references/scripts.md) for build/deploy/cleanup scripts
