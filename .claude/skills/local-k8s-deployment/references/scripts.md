# Deployment Scripts

## Table of Contents
- [build-images.sh](#build-imagessh)
- [deploy-minikube.sh](#deploy-minikubesh)
- [cleanup.sh](#cleanupsh)

## build-images.sh

Build Docker images with size validation:

```bash
#!/bin/bash
# Build Docker images for the application
# Usage: ./build-images.sh [--backend-only | --frontend-only]
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$PROJECT_ROOT/../<source-code-dir>"

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"; exit 1
fi
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running"; exit 1
fi

# Parse arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
[ "$1" = "--backend-only" ] && BUILD_FRONTEND=false
[ "$1" = "--frontend-only" ] && BUILD_BACKEND=false

# Build backend
if [ "$BUILD_BACKEND" = true ]; then
    docker build --progress=plain \
        -t <backend-image>:latest \
        -f "$PROJECT_ROOT/docker/backend/Dockerfile" \
        "$SOURCE_DIR/backend"
fi

# Build frontend
if [ "$BUILD_FRONTEND" = true ]; then
    docker build --progress=plain \
        -t <frontend-image>:latest \
        -f "$PROJECT_ROOT/docker/frontend/Dockerfile" \
        "$SOURCE_DIR/frontend"
fi

echo "Images created:"
docker images | grep -E "REPOSITORY|<backend-image>|<frontend-image>"
echo "Next: minikube image load <backend-image>:latest <frontend-image>:latest"
```

## deploy-minikube.sh

Full deployment workflow:

```bash
#!/bin/bash
# Deploy to Minikube
# Usage: ./deploy-minikube.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HELM_CHART="$PROJECT_ROOT/helm/<release-name>"

# Start Minikube if not running
if ! minikube status | grep -q "Running"; then
    minikube start --driver=docker --memory=4096 --cpus=2
fi

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Load images
minikube image load <backend-image>:latest
minikube image load <frontend-image>:latest

# Deploy with Helm (install or upgrade)
if helm status <release-name> &> /dev/null; then
    helm upgrade <release-name> "$HELM_CHART" -f "$HELM_CHART/values-minikube.yaml"
else
    helm install <release-name> "$HELM_CHART" -f "$HELM_CHART/values-minikube.yaml"
fi

# Wait for pods
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance=<release-name> --timeout=120s

# Show status
kubectl get pods -l app.kubernetes.io/instance=<release-name>
kubectl get services -l app.kubernetes.io/instance=<release-name>

echo "Access: kubectl port-forward svc/<release-name>-frontend 3000:3000"
echo "Or add to /etc/hosts: $(minikube ip) <app>.local"
```

## cleanup.sh

```bash
#!/bin/bash
# Clean up deployment
# Usage: ./cleanup.sh
set -e

if helm status <release-name> &> /dev/null; then
    helm uninstall <release-name>
fi

read -p "Remove Docker images? (y/N): " remove_images
if [[ "$remove_images" =~ ^[Yy]$ ]]; then
    docker rmi <backend-image>:latest 2>/dev/null || true
    docker rmi <frontend-image>:latest 2>/dev/null || true
fi
```
