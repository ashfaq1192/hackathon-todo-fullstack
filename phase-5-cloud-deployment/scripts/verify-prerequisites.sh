#!/bin/bash

echo "=== Phase V Prerequisites Verification ==="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# 1. OCI CLI
echo -n "1. OCI CLI: "
if command -v oci &> /dev/null; then
    VERSION=$(oci --version 2>&1)
    echo -e "${GREEN}✓ Installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILURES=$((FAILURES+1))
fi

# 2. kubectl
echo -n "2. kubectl: "
if command -v kubectl &> /dev/null; then
    VERSION=$(kubectl version --client --short 2>&1 | head -1)
    echo -e "${GREEN}✓ Installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILURES=$((FAILURES+1))
fi

# 3. Helm
echo -n "3. Helm: "
if command -v helm &> /dev/null; then
    VERSION=$(helm version --short 2>&1)
    echo -e "${GREEN}✓ Installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILURES=$((FAILURES+1))
fi

# 4. Dapr CLI
echo -n "4. Dapr CLI: "
if command -v dapr &> /dev/null; then
    VERSION=$(dapr version 2>&1 | grep "CLI version" | awk '{print $3}')
    echo -e "${GREEN}✓ Installed${NC} (v$VERSION)"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILURES=$((FAILURES+1))
fi

# 5. Docker
echo -n "5. Docker: "
if command -v docker &> /dev/null; then
    VERSION=$(docker --version 2>&1 | awk '{print $3}' | tr -d ',')
    echo -e "${GREEN}✓ Installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILURES=$((FAILURES+1))
fi

# 6. Docker buildx
echo -n "6. Docker buildx: "
if docker buildx version &> /dev/null; then
    VERSION=$(docker buildx version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Available${NC} ($VERSION)"
else
    echo -e "${RED}✗ Not available${NC}"
    FAILURES=$((FAILURES+1))
fi

echo ""
echo "======================================"
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}All prerequisites satisfied!${NC}"
    echo "You can proceed with Stage 1 implementation."
    exit 0
else
    echo -e "${RED}$FAILURES tool(s) missing${NC}"
    echo "Please install missing tools before proceeding."
    echo "See SETUP_PREREQUISITES.md for installation instructions."
    exit 1
fi
