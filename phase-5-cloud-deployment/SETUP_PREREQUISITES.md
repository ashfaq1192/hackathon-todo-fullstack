# Prerequisites Installation Guide

**Date**: 2026-01-25
**Status**: Required before starting Stage 1

## Current Tool Status

✅ **kubectl** - v1.35.0 (Installed)
✅ **Helm** - v3.17.0 (Installed)
❌ **OCI CLI** - Not installed (Required)
❌ **Dapr CLI** - Not installed (Required)
❌ **Docker** - WSL 2 integration not enabled (Required)

---

## 1. Install OCI CLI (Oracle Cloud Infrastructure CLI)

**Required for**: Cluster provisioning, kubectl configuration

### Installation on WSL 2 / Linux

```bash
# Download and run installer
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

**During installation prompts**:
- Installation directory: Press Enter (default: ~/lib/oracle-cli)
- Add to PATH: Y
- Update PATH now: Y
- Install additional dependencies: Y

**Verify installation**:
```bash
oci --version
# Expected: 3.x.x or higher
```

**Post-installation**:
```bash
# Reload shell to pick up PATH changes
source ~/.bashrc
```

### Configuration (After Oracle Account Setup)

```bash
# Run interactive setup
oci setup config
```

**You'll need from OCI Console**:
1. User OCID (Profile → User Settings → copy OCID)
2. Tenancy OCID (Profile → Tenancy → copy OCID)
3. Region (e.g., us-ashburn-1, us-phoenix-1)

**The setup will**:
- Create ~/.oci/config file
- Generate API key pair (~/.oci/oci_api_key.pem)
- You must upload the PUBLIC key to OCI Console

---

## 2. Install Dapr CLI

**Required for**: Dapr status checks, sidecar testing

### Installation on WSL 2 / Linux

```bash
# Download and install
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Verify installation**:
```bash
dapr version
# Expected: CLI version: 1.12.x or higher
```

**Add to PATH** (if needed):
```bash
echo 'export PATH=$PATH:$HOME/.dapr/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## 3. Enable Docker Desktop WSL 2 Integration

**Required for**: Building ARM64 images, local testing

### Steps

1. **Open Docker Desktop**
   - Ensure Docker Desktop is running on Windows

2. **Enable WSL 2 Integration**:
   - Docker Desktop → Settings → Resources → WSL Integration
   - Toggle ON: "Enable integration with my default WSL distro"
   - Check the box for your specific WSL 2 distro (e.g., Ubuntu)
   - Click "Apply & Restart"

3. **Verify in WSL 2**:
   ```bash
   docker --version
   # Expected: Docker version 20.10.x or higher

   docker buildx version
   # Expected: github.com/docker/buildx vX.X.X
   ```

4. **Test Docker**:
   ```bash
   docker run hello-world
   # Should pull and run successfully
   ```

---

## 4. Complete Verification Script

After installing all tools, run this verification:

```bash
cat > /mnt/e/projects/hackathon-todo-fullstack/phase-5-cloud-deployment/scripts/verify-prerequisites.sh <<'EOF'
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
EOF

chmod +x /mnt/e/projects/hackathon-todo-fullstack/phase-5-cloud-deployment/scripts/verify-prerequisites.sh
```

Run the verification:
```bash
cd /mnt/e/projects/hackathon-todo-fullstack
./phase-5-cloud-deployment/scripts/verify-prerequisites.sh
```

---

## Installation Order

**Recommended sequence**:

1. ✅ kubectl (Already installed)
2. ✅ Helm (Already installed)
3. ❌ **Install OCI CLI** (15 minutes)
4. ❌ **Install Dapr CLI** (5 minutes)
5. ❌ **Enable Docker Desktop WSL 2** (10 minutes)

**Total estimated time**: 30 minutes

---

## Troubleshooting

### OCI CLI: "command not found" after installation

```bash
# Reload shell environment
source ~/.bashrc

# Or manually add to PATH
export PATH=$PATH:~/lib/oracle-cli/bin
```

### Dapr CLI: "command not found"

```bash
# Check if binary exists
ls -la ~/.dapr/bin/dapr

# Add to PATH
echo 'export PATH=$PATH:$HOME/.dapr/bin' >> ~/.bashrc
source ~/.bashrc
```

### Docker: "Cannot connect to Docker daemon"

- Ensure Docker Desktop is running on Windows
- Verify WSL 2 integration is enabled in Docker Desktop settings
- Restart Docker Desktop after enabling integration
- Restart WSL 2 terminal

---

## Next Steps After Installation

Once all tools are verified:

1. **Upgrade Oracle Cloud Account** to "Pay As You Go" (keeps Always Free)
2. **Configure OCI CLI** with `oci setup config`
3. **Create OKE cluster** via OCI Console
4. **Follow quickstart.md** for complete setup

---

## References

- OCI CLI: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm
- Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/
- Docker Desktop WSL 2: https://docs.docker.com/desktop/wsl/
- kubectl: https://kubernetes.io/docs/tasks/tools/
- Helm: https://helm.sh/docs/intro/install/

---

**Status**: Review and install missing tools before proceeding
