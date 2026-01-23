# Contract: Helm Chart

**Type**: Infrastructure Contract
**Resource**: `phase-4-k8s/helm/todo-chatbot/`

## Specification

### Chart.yaml

```yaml
apiVersion: v2
name: todo-chatbot
description: Todo Chatbot application with AI-powered task management
type: application
version: 0.1.0
appVersion: "1.0.0"
```

### values.yaml Structure

```yaml
# Global settings
global:
  imagePullPolicy: Never  # Local images

# Backend configuration
backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    DATABASE_URL: ""      # Set in secrets
    OPENAI_API_KEY: ""    # Set in secrets
    BETTER_AUTH_SECRET: "" # Set in secrets
  probes:
    liveness:
      path: /health
      initialDelaySeconds: 10
      periodSeconds: 10
    readiness:
      path: /health
      initialDelaySeconds: 5
      periodSeconds: 5

# Frontend configuration
frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    NEXT_PUBLIC_BACKEND_URL: ""  # Set via configmap
  probes:
    liveness:
      path: /
      initialDelaySeconds: 15
      periodSeconds: 10
    readiness:
      path: /
      initialDelaySeconds: 10
      periodSeconds: 5

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

# Secrets (create: true to generate from values)
secrets:
  create: true
```

### values-minikube.yaml

```yaml
# Minikube-specific overrides
backend:
  env:
    DATABASE_URL: "postgresql://..."  # From .env
    OPENAI_API_KEY: "sk-..."          # From .env
    BETTER_AUTH_SECRET: "..."          # From .env

frontend:
  env:
    NEXT_PUBLIC_BACKEND_URL: "http://todo.local/api"

ingress:
  hosts:
    - host: todo.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend
```

### Template Files Required

| File | K8s Resource | Purpose |
|------|--------------|---------|
| `_helpers.tpl` | N/A | Template helper functions |
| `backend-deployment.yaml` | Deployment | Backend pod spec |
| `backend-service.yaml` | Service | Backend service |
| `frontend-deployment.yaml` | Deployment | Frontend pod spec |
| `frontend-service.yaml` | Service | Frontend service |
| `configmap.yaml` | ConfigMap | Non-sensitive config |
| `secrets.yaml` | Secret | Sensitive config |
| `ingress.yaml` | Ingress | External routing |

### Validation Commands

```bash
# Lint chart
helm lint phase-4-k8s/helm/todo-chatbot

# Template rendering (dry-run)
helm template todo-chatbot phase-4-k8s/helm/todo-chatbot \
  -f phase-4-k8s/helm/todo-chatbot/values-minikube.yaml

# Dry-run install
helm install todo-chatbot phase-4-k8s/helm/todo-chatbot \
  -f phase-4-k8s/helm/todo-chatbot/values-minikube.yaml \
  --dry-run
```

### Install/Upgrade Commands

```bash
# Install
helm install todo-chatbot phase-4-k8s/helm/todo-chatbot \
  -f phase-4-k8s/helm/todo-chatbot/values-minikube.yaml

# Upgrade
helm upgrade todo-chatbot phase-4-k8s/helm/todo-chatbot \
  -f phase-4-k8s/helm/todo-chatbot/values-minikube.yaml

# Uninstall
helm uninstall todo-chatbot
```
