# Phase IV - Local Kubernetes Deployment

## Overview
Containerize and deploy Phase III Todo Chatbot to local Kubernetes (Minikube).

## Technology Stack
- **Containerization**: Docker (Docker Desktop 4.53+)
- **Docker AI**: Gordon (optional)
- **Orchestration**: Kubernetes (Minikube)
- **Package Manager**: Helm Charts
- **AI DevOps**: kubectl-ai, Kagent

## Folder Structure
```
phase-4-k8s/
├── docker/
│   ├── backend/Dockerfile      # FastAPI + MCP server
│   └── frontend/Dockerfile     # Next.js app
├── helm/
│   └── todo-chatbot/           # Helm chart
├── scripts/
│   ├── build-images.sh         # Build Docker images
│   ├── deploy-minikube.sh      # Deploy to Minikube
│   └── cleanup.sh              # Clean up resources
└── CLAUDE.md
```

## Commands

### Docker
```bash
# Build images
./scripts/build-images.sh

# Or manually
docker build -t todo-backend:latest -f docker/backend/Dockerfile ../phase-3-chatbot/backend
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile ../phase-3-chatbot/frontend
```

### Minikube
```bash
# Start Minikube
minikube start

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Deploy
./scripts/deploy-minikube.sh
```

### Helm
```bash
# Install
helm install todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-minikube.yaml

# Upgrade
helm upgrade todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-minikube.yaml

# Uninstall
helm uninstall todo-chatbot
```

## AIOps Tools Usage
```bash
# Docker AI (Gordon)
docker ai "create a Dockerfile for FastAPI app"

# kubectl-ai
kubectl ai "check pod status"
kubectl ai "why is the backend pod failing"

# Kagent
kagent "analyze cluster health"
```
