# Data Model: Local Kubernetes Deployment

**Feature**: 008-local-k8s-deployment
**Date**: 2026-01-22

## Overview

This feature is infrastructure-focused and does not introduce new application data models. The data model documents Kubernetes resource structures and Docker artifacts.

## Kubernetes Resources

### 1. Docker Images

| Image | Base | Build Context | Target Size |
|-------|------|---------------|-------------|
| `todo-backend:latest` | `python:3.13-slim` | `phase-3-chatbot/backend/` | <300MB |
| `todo-frontend:latest` | `node:22-alpine` | `phase-3-chatbot/frontend/` | <300MB |

### 2. Helm Chart: todo-chatbot

**Chart.yaml Attributes**:

| Field | Value | Description |
|-------|-------|-------------|
| `name` | `todo-chatbot` | Chart name |
| `version` | `0.1.0` | Chart version |
| `appVersion` | `1.0.0` | Application version |
| `type` | `application` | Chart type |

### 3. Kubernetes Deployment: Backend

| Attribute | Value | Notes |
|-----------|-------|-------|
| `replicas` | 1 | Single replica for local dev |
| `image` | `todo-backend:latest` | Local image |
| `imagePullPolicy` | `Never` | Uses locally loaded image |
| `containerPort` | 8000 | FastAPI default port |
| `resources.requests.memory` | `256Mi` | Minimum memory |
| `resources.requests.cpu` | `100m` | Minimum CPU |
| `resources.limits.memory` | `512Mi` | Maximum memory |
| `resources.limits.cpu` | `500m` | Maximum CPU |

**Health Probes**:

| Probe | Type | Path | Port | Initial Delay | Period |
|-------|------|------|------|---------------|--------|
| liveness | httpGet | `/health` | 8000 | 10s | 10s |
| readiness | httpGet | `/health` | 8000 | 5s | 5s |

### 4. Kubernetes Deployment: Frontend

| Attribute | Value | Notes |
|-----------|-------|-------|
| `replicas` | 1 | Single replica for local dev |
| `image` | `todo-frontend:latest` | Local image |
| `imagePullPolicy` | `Never` | Uses locally loaded image |
| `containerPort` | 3000 | Next.js default port |
| `resources.requests.memory` | `256Mi` | Minimum memory |
| `resources.requests.cpu` | `100m` | Minimum CPU |
| `resources.limits.memory` | `512Mi` | Maximum memory |
| `resources.limits.cpu` | `500m` | Maximum CPU |

**Health Probes**:

| Probe | Type | Path | Port | Initial Delay | Period |
|-------|------|------|------|---------------|--------|
| liveness | httpGet | `/` | 3000 | 15s | 10s |
| readiness | httpGet | `/` | 3000 | 10s | 5s |

### 5. Kubernetes Services

| Service | Type | Port | Target Port | Selector |
|---------|------|------|-------------|----------|
| `todo-chatbot-backend` | ClusterIP | 8000 | 8000 | `app: backend` |
| `todo-chatbot-frontend` | ClusterIP | 3000 | 3000 | `app: frontend` |

### 6. Kubernetes ConfigMap

| Key | Description | Example |
|-----|-------------|---------|
| `BACKEND_URL` | Internal backend URL | `http://todo-chatbot-backend:8000` |
| `NEXT_PUBLIC_BACKEND_URL` | Frontend-accessible backend | `http://todo.local/api` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG` |

### 7. Kubernetes Secret

| Key | Description | Source |
|-----|-------------|--------|
| `DATABASE_URL` | Neon PostgreSQL connection | `.env` or values.yaml |
| `OPENAI_API_KEY` | OpenAI API credentials | `.env` or values.yaml |
| `BETTER_AUTH_SECRET` | Auth signing secret | `.env` or values.yaml |

### 8. Kubernetes Ingress

| Attribute | Value |
|-----------|-------|
| `ingressClassName` | `nginx` |
| `host` | `todo.local` |
| `paths[0]` | `/api/*` → backend:8000 |
| `paths[1]` | `/*` → frontend:3000 |

## Entity Relationships

```text
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Ingress (nginx)                    │   │
│  │                    host: todo.local                   │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                  │
│           ┌───────────────┴───────────────┐                 │
│           │                               │                 │
│           ▼                               ▼                 │
│  ┌─────────────────┐            ┌─────────────────┐        │
│  │ Frontend Service│            │ Backend Service │        │
│  │    (ClusterIP)  │            │   (ClusterIP)   │        │
│  │     :3000       │            │     :8000       │        │
│  └────────┬────────┘            └────────┬────────┘        │
│           │                               │                 │
│           ▼                               ▼                 │
│  ┌─────────────────┐            ┌─────────────────┐        │
│  │ Frontend Pod    │            │ Backend Pod     │        │
│  │ (Next.js)       │───────────▶│ (FastAPI+MCP)   │        │
│  │                 │   API      │                 │        │
│  └─────────────────┘   calls    └────────┬────────┘        │
│                                          │                  │
│                                          │ PostgreSQL       │
│                                          ▼                  │
│                               ┌─────────────────┐           │
│                               │ ConfigMap/Secret│           │
│                               │ (env variables) │           │
│                               └─────────────────┘           │
│                                          │                  │
└──────────────────────────────────────────┼──────────────────┘
                                           │
                                           ▼
                                ┌─────────────────┐
                                │ Neon PostgreSQL │
                                │   (External)    │
                                └─────────────────┘
```

## State Transitions

### Pod Lifecycle

```text
Pending → ContainerCreating → Running → Ready
                                  │
                                  ▼ (probe fails)
                             CrashLoopBackOff
                                  │
                                  ▼ (probe succeeds)
                               Running
```

### Deployment Update Strategy

| Strategy | Value | Description |
|----------|-------|-------------|
| `type` | `RollingUpdate` | Zero-downtime updates |
| `maxUnavailable` | 0 | Always maintain capacity |
| `maxSurge` | 1 | Create new pod before terminating old |

## Validation Rules

| Resource | Rule | Validation |
|----------|------|------------|
| Docker Image | Size limit | Must be <500MB |
| Pod | Memory limit | Must not exceed 512Mi |
| Secret | Required keys | DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET |
| Ingress | Host resolution | `todo.local` must be in /etc/hosts |
