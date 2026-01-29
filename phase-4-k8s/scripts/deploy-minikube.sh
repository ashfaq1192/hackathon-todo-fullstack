#!/bin/bash
# Deploy Todo Chatbot to Minikube
# Usage: ./deploy-minikube.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HELM_CHART="$PROJECT_ROOT/helm/todo-chatbot"

echo "=== Deploying Todo Chatbot to Minikube ==="

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "Starting Minikube..."
    minikube start
fi

# Enable required addons
echo ""
echo "--- Enabling Minikube Addons ---"
minikube addons enable ingress
minikube addons enable metrics-server

# Load images into Minikube
echo ""
echo "--- Loading Images into Minikube ---"
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Deploy with Helm
echo ""
echo "--- Deploying with Helm ---"
if helm status todo-chatbot &> /dev/null; then
    echo "Upgrading existing deployment..."
    helm upgrade todo-chatbot "$HELM_CHART" -f "$HELM_CHART/values-minikube.yaml"
else
    echo "Installing new deployment..."
    helm install todo-chatbot "$HELM_CHART" -f "$HELM_CHART/values-minikube.yaml"
fi

# Wait for pods to be ready
echo ""
echo "--- Waiting for Pods ---"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-chatbot --timeout=120s

# Show status
echo ""
echo "=== Deployment Complete ==="
kubectl get pods -l app.kubernetes.io/instance=todo-chatbot
kubectl get services -l app.kubernetes.io/instance=todo-chatbot

echo ""
echo "To access the application:"
echo "  minikube service todo-chatbot-frontend"
echo ""
echo "Or add to /etc/hosts:"
echo "  $(minikube ip) todo.local"
