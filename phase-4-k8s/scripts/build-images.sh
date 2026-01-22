#!/bin/bash
# Build Docker images for Todo Chatbot
# Usage: ./build-images.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PHASE3_DIR="$PROJECT_ROOT/../phase-3-chatbot"

echo "=== Building Todo Chatbot Docker Images ==="

# Check if phase-3-chatbot exists
if [ ! -d "$PHASE3_DIR" ]; then
    echo "Error: phase-3-chatbot directory not found at $PHASE3_DIR"
    exit 1
fi

# Build backend image
echo ""
echo "--- Building Backend Image ---"
docker build \
    -t todo-backend:latest \
    -f "$PROJECT_ROOT/docker/backend/Dockerfile" \
    "$PHASE3_DIR/backend"

# Build frontend image
echo ""
echo "--- Building Frontend Image ---"
docker build \
    -t todo-frontend:latest \
    -f "$PROJECT_ROOT/docker/frontend/Dockerfile" \
    "$PHASE3_DIR/frontend"

echo ""
echo "=== Build Complete ==="
echo "Images created:"
docker images | grep -E "todo-backend|todo-frontend"
