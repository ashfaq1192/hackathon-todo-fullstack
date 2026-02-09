# Phase V Stage 1 - Next Steps Action Plan

**Date**: 2026-01-25
**Status**: Ready to proceed with "Pay As You Go" upgrade
**Estimated Time**: 60-75 minutes total

---

## Implementation Sequence

### Phase A: Local Prerequisites (30 minutes)

**Status**: 🚧 In Progress

#### A1. Install OCI CLI (15 minutes)

```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Reload shell
source ~/.bashrc

# Verify
oci --version
```

**Expected**: `3.x.x` or higher

---

#### A2. Install Dapr CLI (5 minutes)

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Add to PATH
echo 'export PATH=$PATH:$HOME/.dapr/bin' >> ~/.bashrc
source ~/.bashrc

# Verify
dapr version
```

**Expected**: CLI version 1.12.x or higher

---

#### A3. Enable Docker Desktop WSL 2 (10 minutes)

1. Open **Docker Desktop** on Windows
2. Go to: **Settings** → **Resources** → **WSL Integration**
3. Toggle ON: **"Enable integration with my default WSL distro"**
4. Check your WSL distro name
5. Click **"Apply & Restart"**

**Verify in WSL**:
```bash
docker --version
docker buildx version
docker run hello-world
```

---

#### A4. Verify All Tools

```bash
cd /mnt/e/projects/hackathon-todo-fullstack
./phase-5-cloud-deployment/scripts/verify-prerequisites.sh
```

**Expected**: All checks show ✅ green

**⛔ STOP HERE** until all tools are installed and verified

---

### Phase B: Oracle Cloud Configuration (10 minutes)

**Status**: ⏳ Waiting for Phase A completion

#### B1. Upgrade to "Pay As You Go" (3 minutes)

1. Log into **OCI Console**: https://cloud.oracle.com/
2. Navigate to: **☰ Menu** → **Billing & Cost Management**
3. Click: **Account Management** → **Upgrade Account**
4. Review terms:
   - ✅ Always Free resources remain free forever
   - ✅ $300 trial credits for 30 days
   - ✅ No charges if staying within Always Free limits
5. Click: **Upgrade to Pay As You Go**
6. Wait for confirmation (usually instant)

**Verify**:
- Go to: **☰ Menu** → **Developer Services** → **Kubernetes Clusters (OKE)**
- "Create Cluster" button should be **enabled** (not grayed out)

---

#### B2. Configure Budget Alert (2 minutes)

1. **Billing & Cost Management** → **Budgets**
2. Click: **Create Budget**
3. Configure:
   - **Budget name**: `always-free-monitor`
   - **Target compartment**: (root)
   - **Monthly budget amount**: `$10`
   - **Alert threshold**: `80%` ($8.00)
   - **Email**: Your email address
4. Click: **Create**

**Purpose**: Get notified if costs approach $10 (should stay at $0.00)

---

#### B3. Configure OCI CLI Authentication (5 minutes)

```bash
# Run interactive setup
oci setup config
```

**Interactive Prompts** (have OCI Console open):

1. **Config file location**: Press Enter (default: `~/.oci/config`)

2. **User OCID**:
   - OCI Console → **Profile icon** (top-right) → **User Settings**
   - Copy **OCID** (starts with `ocid1.user.oc1..`)
   - Paste into terminal

3. **Tenancy OCID**:
   - OCI Console → **Profile icon** → **Tenancy: <name>**
   - Copy **OCID** (starts with `ocid1.tenancy.oc1..`)
   - Paste into terminal

4. **Region**: Enter your home region
   - Example: `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`
   - Find in OCI Console → top-right dropdown

5. **Generate new API key**: Type `Y`

6. **Key location**: Press Enter (default: `~/.oci/oci_api_key.pem`)

7. **Passphrase**: Press Enter (skip for learning environment)

**Post-Configuration**:

1. **Upload Public Key to OCI Console**:
   ```bash
   # Display public key
   cat ~/.oci/oci_api_key_public.pem
   ```

2. In OCI Console:
   - **Profile** → **User Settings** → **API Keys**
   - Click: **Add API Key** → **Paste Public Key**
   - Paste the contents from above
   - Click: **Add**

3. **Verify Configuration**:
   ```bash
   oci iam region list
   ```
   **Expected**: Table of Oracle Cloud regions

**⛔ STOP HERE** until OCI CLI is configured and verified

---

### Phase C: OKE Cluster Creation (20 minutes)

**Status**: ⏳ Waiting for Phase B completion

Follow the complete step-by-step guide:

```bash
# Open quickstart guide
cat /mnt/e/projects/hackathon-todo-fullstack/specs/010-oke-dapr-setup/quickstart.md | less
```

**Key Steps**:

1. **Navigate to OKE Service**
   - OCI Console → **Developer Services** → **Kubernetes Clusters (OKE)**
   - Click: **Create Cluster**

2. **Configure Cluster** (Quick Create):
   - **Name**: `todo-chatbot-cluster`
   - **Kubernetes Version**: 1.28 (or latest)
   - **Shape**: VM.Standard.A1.Flex (ARM64)
   - **Nodes**: 2
   - **OCPUs per node**: 2
   - **Memory per node**: 12 GB

3. **Wait for Provisioning** (15 minutes)
   - Cluster status: CREATING → ACTIVE
   - Refresh page periodically
   - ☕ Take a break

4. **Copy Cluster OCID**
   - Click cluster name → **Cluster Details**
   - Copy **OCID**: `ocid1.cluster.oc1...`
   - Save to notepad

---

### Phase D: kubectl & Docker Setup (10 minutes)

**Status**: ⏳ Waiting for Phase C completion

#### D1. Configure kubectl (2 minutes)

```bash
# Generate kubeconfig (replace placeholders)
oci ce cluster create-kubeconfig \
  --cluster-id <your-cluster-ocid> \
  --file $HOME/.kube/config \
  --region <your-region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

**Verify**:
```bash
kubectl cluster-info
kubectl get nodes
```

**Expected**: 2 nodes in Ready status

---

#### D2. Setup Docker Buildx (3 minutes)

```bash
# Create multi-arch builder
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap
```

**Test ARM64 build**:
```bash
docker buildx build --platform linux/arm64 \
  -t todo-backend:test-arm64 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --load \
  phase-3-chatbot/backend
```

**Verify**:
```bash
docker inspect todo-backend:test-arm64 | grep -i architecture
```
**Expected**: `"Architecture": "arm64"`

---

#### D3. Verify Cluster (5 minutes)

```bash
# Node status
kubectl get nodes -o wide

# ARM64 architecture
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'
# Expected: arm64 arm64

# Resource capacity
kubectl describe nodes | grep -E "Capacity|Allocatable"
# Expected: 4 vCPUs total, 24GB RAM total
```

---

### Phase E: Dapr Installation (10 minutes)

**Status**: ⏳ Waiting for Phase D completion

#### E1. Add Dapr Helm Repository (1 minute)

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm search repo dapr
```

---

#### E2. Install Dapr Control Plane (5 minutes)

```bash
helm install dapr dapr/dapr \
  --version=1.14 \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --wait
```

**Wait**: 3-5 minutes for installation

---

#### E3. Verify Dapr (2 minutes)

```bash
# Dapr status
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION
# dapr-operator          dapr-system  True     Running  3         1.14.x
# dapr-sidecar-injector  dapr-system  True     Running  3         1.14.x
# dapr-sentry            dapr-system  True     Running  3         1.14.x
# dapr-placement-server  dapr-system  True     Running  3         1.14.x

# Pod count
kubectl get pods -n dapr-system --no-headers | wc -l
# Expected: 12
```

---

#### E4. Test Sidecar Injection (2 minutes)

```bash
# Create test deployment
kubectl create deployment nginx-test --image=nginx
kubectl annotate deployment nginx-test dapr.io/enabled="true" dapr.io/app-id="nginx-app"

# Wait for ready
kubectl wait --for=condition=ready pod -l app=nginx-test --timeout=60s

# Verify sidecar
kubectl get pods -l app=nginx-test -o jsonpath='{.items[0].spec.containers[*].name}'
# Expected: nginx daprd

# Cleanup
kubectl delete deployment nginx-test
```

---

### Phase F: Validation & Documentation (5 minutes)

**Status**: ⏳ Waiting for Phase E completion

#### F1. Capture Logs

```bash
mkdir -p phase-5-cloud-deployment/logs/

kubectl get nodes > phase-5-cloud-deployment/logs/cluster-nodes.txt
kubectl get nodes -o wide > phase-5-cloud-deployment/logs/cluster-nodes-detailed.txt
dapr status -k > phase-5-cloud-deployment/logs/dapr-status.txt
kubectl get pods -n dapr-system > phase-5-cloud-deployment/logs/dapr-pods.txt
kubectl top nodes > phase-5-cloud-deployment/logs/resource-utilization.txt
kubectl get --raw /healthz > phase-5-cloud-deployment/logs/cluster-health.txt
```

---

#### F2. Verify Cost ($0.00)

1. OCI Console → **Billing & Cost Management** → **Cost Analysis**
2. Date range: **Last 7 days**
3. Filter by service: **Compute**, **Container Engine for Kubernetes**
4. **Verify**: Total cost = **$0.00** ✅

---

#### F3. Complete Verification

```bash
cat > phase-5-cloud-deployment/scripts/verify-stage1.sh <<'EOF'
#!/bin/bash
set -e

echo "=== Stage 1 Verification ==="
echo ""

# 1. Cluster connectivity
kubectl cluster-info >/dev/null 2>&1 && echo "✅ Cluster accessible" || echo "❌ Cluster not accessible"

# 2. Node count
NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
[ "$NODE_COUNT" = "2" ] && echo "✅ 2 nodes found" || echo "❌ Expected 2 nodes, found $NODE_COUNT"

# 3. ARM64 architecture
ARCH=$(kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.architecture}')
[ "$ARCH" = "arm64" ] && echo "✅ ARM64 architecture" || echo "❌ Expected arm64, found $ARCH"

# 4. Dapr installed
dapr status -k >/dev/null 2>&1 && echo "✅ Dapr installed" || echo "❌ Dapr not installed"

# 5. Dapr pod count
DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers | wc -l)
[ "$DAPR_PODS" = "12" ] && echo "✅ 12 Dapr pods (HA mode)" || echo "❌ Expected 12 pods, found $DAPR_PODS"

# 6. All pods running
NOT_RUNNING=$(kubectl get pods -n dapr-system --no-headers | grep -v Running | wc -l)
[ "$NOT_RUNNING" = "0" ] && echo "✅ All Dapr pods Running" || echo "❌ $NOT_RUNNING pods not Running"

echo ""
echo "Stage 1 complete! Ready for Stage 2 (Redpanda Pub/Sub)."
EOF

chmod +x phase-5-cloud-deployment/scripts/verify-stage1.sh
./phase-5-cloud-deployment/scripts/verify-stage1.sh
```

**Expected**: All checks show ✅

---

## Summary Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| A | Install prerequisites | 30 min | 🚧 Current |
| B | Oracle Cloud config | 10 min | ⏳ Pending |
| C | Create OKE cluster | 20 min | ⏳ Pending |
| D | kubectl & Docker setup | 10 min | ⏳ Pending |
| E | Install Dapr | 10 min | ⏳ Pending |
| F | Validation | 5 min | ⏳ Pending |
| **Total** | | **60-75 min** | |

---

## Current Action Required

**START HERE**: Install the 3 missing tools

1. **OCI CLI** (15 min)
2. **Dapr CLI** (5 min)
3. **Docker WSL 2** (10 min)

Once all tools are verified with the `verify-prerequisites.sh` script, you can proceed to Phase B (Oracle Cloud configuration).

---

## Need Help?

- **Detailed commands**: See `specs/010-oke-dapr-setup/contracts/cli-commands.md`
- **Verification procedures**: See `specs/010-oke-dapr-setup/contracts/verification-checklist.md`
- **Complete guide**: See `specs/010-oke-dapr-setup/quickstart.md`
- **Troubleshooting**: See quickstart.md "Common Issues & Solutions" section

---

**Next Update**: After Phase A (prerequisites) is complete
