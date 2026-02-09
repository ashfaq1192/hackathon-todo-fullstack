#!/bin/bash
# Build Docker images for Todo Chatbot
# Usage: ./build-images.sh [--backend-only | --frontend-only | --services-only | --all]
#
# Options:
#   --backend-only    Build only the backend image
#   --frontend-only   Build only the frontend image
#   --services-only   Build only the consumer service images (notification, recurring, audit)
#   --all             Build all images including consumer services
#   (no option)       Build backend and frontend images

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PHASE3_DIR="$PROJECT_ROOT/../phase-3-chatbot"
PHASE5_DIR="$PROJECT_ROOT/../phase-5-cloud-deployment"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== Building Todo Chatbot Docker Images ==="
echo "Project root: $PROJECT_ROOT"
echo "Source code: $PHASE3_DIR"

# Check prerequisites
echo ""
echo "--- Checking Prerequisites ---"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Please start Docker Desktop or Docker daemon"
    exit 1
fi

echo -e "${GREEN}Docker is available${NC}"

# Check if phase-3-chatbot exists
if [ ! -d "$PHASE3_DIR" ]; then
    echo -e "${RED}Error: phase-3-chatbot directory not found at $PHASE3_DIR${NC}"
    exit 1
fi

if [ ! -d "$PHASE3_DIR/backend" ] || [ ! -d "$PHASE3_DIR/frontend" ]; then
    echo -e "${RED}Error: backend or frontend directory missing in phase-3-chatbot${NC}"
    exit 1
fi

echo -e "${GREEN}Source code found${NC}"

# Parse arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
BUILD_SERVICES=false

if [ "$1" = "--backend-only" ]; then
    BUILD_FRONTEND=false
elif [ "$1" = "--frontend-only" ]; then
    BUILD_BACKEND=false
elif [ "$1" = "--services-only" ]; then
    BUILD_BACKEND=false
    BUILD_FRONTEND=false
    BUILD_SERVICES=true
elif [ "$1" = "--all" ]; then
    BUILD_SERVICES=true
fi

# Build backend image
if [ "$BUILD_BACKEND" = true ]; then
    echo ""
    echo "--- Building Backend Image ---"
    echo "Dockerfile: $PROJECT_ROOT/docker/backend/Dockerfile"
    echo "Context: $PHASE3_DIR/backend"

    START_TIME=$(date +%s)

    docker build \
        --progress=plain \
        -t todo-backend:latest \
        -f "$PROJECT_ROOT/docker/backend/Dockerfile" \
        "$PHASE3_DIR/backend"

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    # Get image size
    BACKEND_SIZE=$(docker images todo-backend:latest --format "{{.Size}}")
    echo -e "${GREEN}Backend image built in ${DURATION}s${NC}"
    echo "Size: $BACKEND_SIZE"

    # Check if size is under 500MB (rough check)
    SIZE_MB=$(docker images todo-backend:latest --format "{{.Size}}" | grep -oE '[0-9.]+' | head -1)
    UNIT=$(docker images todo-backend:latest --format "{{.Size}}" | grep -oE '[A-Z]+' | head -1)

    if [ "$UNIT" = "GB" ]; then
        echo -e "${RED}Warning: Backend image exceeds 500MB target${NC}"
    else
        echo -e "${GREEN}Backend image size OK (target: <500MB)${NC}"
    fi
fi

# Build frontend image
if [ "$BUILD_FRONTEND" = true ]; then
    echo ""
    echo "--- Building Frontend Image ---"
    echo "Dockerfile: $PROJECT_ROOT/docker/frontend/Dockerfile"
    echo "Context: $PHASE3_DIR/frontend"

    START_TIME=$(date +%s)

    docker build \
        --progress=plain \
        -t todo-frontend:latest \
        -f "$PROJECT_ROOT/docker/frontend/Dockerfile" \
        "$PHASE3_DIR/frontend"

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    # Get image size
    FRONTEND_SIZE=$(docker images todo-frontend:latest --format "{{.Size}}")
    echo -e "${GREEN}Frontend image built in ${DURATION}s${NC}"
    echo "Size: $FRONTEND_SIZE"

    # Check if size is under 500MB
    SIZE_MB=$(docker images todo-frontend:latest --format "{{.Size}}" | grep -oE '[0-9.]+' | head -1)
    UNIT=$(docker images todo-frontend:latest --format "{{.Size}}" | grep -oE '[A-Z]+' | head -1)

    if [ "$UNIT" = "GB" ]; then
        echo -e "${RED}Warning: Frontend image exceeds 500MB target${NC}"
    else
        echo -e "${GREEN}Frontend image size OK (target: <500MB)${NC}"
    fi
fi

# Build consumer service images (Dapr)
if [ "$BUILD_SERVICES" = true ]; then
    SERVICES_DIR="$PHASE5_DIR/services"

    if [ ! -d "$SERVICES_DIR" ]; then
        echo -e "${RED}Error: services directory not found at $SERVICES_DIR${NC}"
        exit 1
    fi

    for SERVICE in notification-service recurring-task-service audit-service; do
        IMAGE_NAME="todo-${SERVICE%%-service}"  # notification, recurring-task, audit
        # Simplify image names
        case "$SERVICE" in
            notification-service) IMAGE_NAME="todo-notification" ;;
            recurring-task-service) IMAGE_NAME="todo-recurring" ;;
            audit-service) IMAGE_NAME="todo-audit" ;;
        esac

        echo ""
        echo "--- Building $SERVICE Image ---"
        echo "Dockerfile: $SERVICES_DIR/$SERVICE/Dockerfile"

        START_TIME=$(date +%s)

        docker build \
            --progress=plain \
            -t "$IMAGE_NAME:latest" \
            -f "$SERVICES_DIR/$SERVICE/Dockerfile" \
            "$SERVICES_DIR/$SERVICE"

        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))

        SIZE=$(docker images "$IMAGE_NAME:latest" --format "{{.Size}}")
        echo -e "${GREEN}$SERVICE image built in ${DURATION}s (${SIZE})${NC}"
    done
fi

echo ""
echo "=== Build Complete ==="
echo "Images created:"
docker images | grep -E "REPOSITORY|todo-"

echo ""
echo "Next steps:"
echo "  1. Test with docker-compose: docker-compose -f $PROJECT_ROOT/docker-compose.yml up"
echo "  2. Load into Minikube: minikube image load todo-backend:latest todo-frontend:latest"
echo "  3. For Dapr services: minikube image load todo-notification:latest todo-recurring:latest todo-audit:latest"
