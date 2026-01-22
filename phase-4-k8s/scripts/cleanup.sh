#!/bin/bash
# Clean up Todo Chatbot deployment
# Usage: ./cleanup.sh

set -e

echo "=== Cleaning Up Todo Chatbot ==="

# Uninstall Helm release
if helm status todo-chatbot &> /dev/null; then
    echo "Uninstalling Helm release..."
    helm uninstall todo-chatbot
else
    echo "No Helm release found."
fi

# Remove local images (optional)
read -p "Remove local Docker images? (y/N): " remove_images
if [[ "$remove_images" =~ ^[Yy]$ ]]; then
    echo "Removing Docker images..."
    docker rmi todo-backend:latest 2>/dev/null || true
    docker rmi todo-frontend:latest 2>/dev/null || true
fi

echo ""
echo "=== Cleanup Complete ==="
