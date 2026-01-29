# Quickstart Guide: OKE Cluster & Basic Dapr Setup

**Feature**: 010-oke-dapr-setup
**Estimated Time**: 45-60 minutes (including cluster provisioning)
**Difficulty**: Intermediate

---

## What You'll Build

By the end of this guide, you'll have:
- ✅ Oracle Kubernetes Engine (OKE) cluster running on Always Free tier
- ✅ 2 ARM64 worker nodes (4 vCPUs, 24GB RAM total)
- ✅ Dapr control plane installed in High Availability mode
- ✅ kubectl configured for local cluster access
- ✅ Docker buildx set up for ARM64 image builds
- ✅ Zero ongoing costs (100% within Always Free limits)

---

## Prerequisites

### Accounts
- Oracle Cloud account (create at cloud.oracle.com/free)
- Credit card for verification (no charges within Always Free tier)

### Local Tools (install before starting)
```bash
# Verify installations
oci --version        # 3.x.x or higher
kubectl version --client  # v1.26.x or higher
helm version         # v3.x.x
dapr version         # 1.12.x or higher
docker --version     # 20.10+ with buildx
```

### Installation Links
- **OCI CLI**: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm
- **kubectl**: https://kubernetes.io/docs/tasks/tools/
- **Helm**: https://helm.sh/docs/intro/install/
- **Dapr CLI**: https://docs.dapr.io/getting-started/install-dapr-cli/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/

---

## Part 1: Oracle Cloud Setup (15 minutes)

### Step 1.1: Sign Up for Oracle Cloud Free Tier

1. Navigate to https://cloud.oracle.com/free
2. Click "Start for free"
3. Fill in registration form:
   - Email address
   - Country/Territory
   - Cloud account name (choose unique name)
4. Complete identity verification:
   - Credit card (for validation, no charges)
   - Phone verification (SMS code)
5. Wait for email confirmation
6. Verify email and log into OCI Console

**Success Check**: Can access OCI Console dashboard

---

### Step 1.2: Upgrade to "Pay As You Go"

> ⚠️ **Important**: This unlocks OKE while keeping Always Free resources perpetual and free

1. In OCI Console, navigate to: **Billing & Cost Management** (top-left menu)
2. Click **Account Management** → **Upgrade Account**
3. Review terms (confirms Always Free resources remain free)
4. Click **Upgrade to Pay As You Go**
5. Wait for confirmation (usually instant)

**Success Check**:
```
Navigate to: Developer Services → Kubernetes Clusters (OKE)
Should see "Create Cluster" button (not grayed out)
```

---

### Step 1.3: Configure Budget Alert (Recommended)

1. Navigate to: **Billing & Cost Management** → **Budgets**
2. Click **Create Budget**
3. Configure:
   - Budget name: `always-free-monitor`
   - Target compartment: (root)
   - Monthly budget amount: **$10**
   - Alert threshold: **80%** ($8)
4. Add email notification
5. Click **Create**

**Purpose**: Get notified if you accidentally exceed Always Free limits

---

## Part 2: OCI CLI Configuration (10 minutes)

### Step 2.1: Install OCI CLI

**Linux/macOS**:
```bash
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

**During installation**:
- Installation directory: Press Enter (default)
- Add to PATH: Y
- Update PATH now: Y

**Verify**:
```bash
oci --version
# Expected: 3.x.x
```

---

### Step 2.2: Configure OCI CLI Authentication

```bash
oci setup config
```

**Interactive Prompts** (have OCI Console open):

1. **Config file location**: Press Enter (default: `~/.oci/config`)

2. **User OCID**:
   - Go to OCI Console → Profile icon (top-right) → **User Settings**
   - Copy **OCID** (starts with `ocid1.user.oc1..`)
   - Paste into terminal

3. **Tenancy OCID**:
   - Go to OCI Console → Profile icon → **Tenancy: <name>**
   - Copy **OCID** (starts with `ocid1.tenancy.oc1..`)
   - Paste into terminal

4. **Region**: Enter your home region (e.g., `us-ashburn-1`)
   - Find in OCI Console → top-right dropdown (e.g., "US East (Ashburn)")

5. **Generate new API key**: Type `Y`

6. **Key location**: Press Enter (default: `~/.oci/oci_api_key.pem`)

7. **Passphrase**: Press Enter (skip for ease of use in learning environment)

**Post-Configuration**:

1. **Upload Public Key**:
   - OCI Console → Profile → User Settings → **API Keys**
   - Click **Add API Key** → **Paste Public Key**
   - Paste contents of `~/.oci/oci_api_key_public.pem`
   - Click **Add**

2. **Verify**:
   ```bash
   oci iam region list
   # Should list Oracle Cloud regions without errors
   ```

**Success Check**: `oci iam region list` returns regions table

---

## Part 3: Create OKE Cluster (20 minutes)

### Step 3.1: Navigate to OKE Service

1. OCI Console → **Developer Services** → **Kubernetes Clusters (OKE)**
2. Click **Create Cluster**

---

### Step 3.2: Configure Cluster (Quick Create)

**Workflow Selection**: **Quick Create** (recommended)

**Basic Information**:
- **Name**: `todo-chatbot-cluster`
- **Compartment**: (root) or select custom
- **Kubernetes Version**: **1.28** (or latest)
- **Kubernetes API Endpoint**: **Public Endpoint**
- **Kubernetes Worker Nodes**: **Private Workers**

**Node Configuration**:
- **Shape**: **VM.Standard.A1.Flex** (ARM64 - Always Free eligible)
- **Number of nodes**: **2**
- **OCPUs per node**: **2**
- **Memory per node**: **12 GB**
- **Image**: **Oracle Linux 8.x** (latest)

**Network**:
- (Auto-configured by Quick Create - VCN, subnets, security lists, load balancer)

**Click**: **Next** → Review → **Create Cluster**

---

### Step 3.3: Wait for Cluster Provisioning

**Estimated Time**: 15 minutes

**Monitoring**:
- Cluster status will show: **CREATING**
- Refresh page periodically
- Watch for status change to: **ACTIVE** ✅

**During Wait**: ☕ Take a break or continue reading next steps

---

### Step 3.4: Verify Cluster Creation

**OCI Console Check**:
- Cluster status: **ACTIVE** (green checkmark)
- Node pool status: **ACTIVE**
- Worker nodes: **2 nodes active**

**Copy Cluster OCID**:
- Click cluster name → **Cluster Details**
- Click **Copy** next to OCID field
- Save to notepad: `ocid1.cluster.oc1...`

**Success Check**: Cluster shows ACTIVE status with 2 active worker nodes

---

## Part 4: Configure kubectl (5 minutes)

### Step 4.1: Generate Kubeconfig

```bash
# Replace <cluster-ocid> with your actual cluster OCID
# Replace <region> with your region (e.g., us-ashburn-1)

oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

**Example**:
```bash
oci ce cluster create-kubeconfig \
  --cluster-id ocid1.cluster.oc1.iad.aaaaaaaaexample \
  --file $HOME/.kube/config \
  --region us-ashburn-1 \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

**Expected Output**:
```
New kubeconfig written to /home/user/.kube/config
```

---

### Step 4.2: Verify kubectl Access

```bash
kubectl cluster-info
```

**Expected Output**:
```
Kubernetes control plane is running at https://...
CoreDNS is running at https://...
```

**Check Nodes**:
```bash
kubectl get nodes
```

**Expected Output**:
```
NAME          STATUS   ROLES   AGE   VERSION
10.0.10.2     Ready    node    5m    v1.28.x
10.0.10.3     Ready    node    5m    v1.28.x
```

**Verify ARM64 Architecture**:
```bash
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'
```

**Expected Output**: `arm64 arm64`

**Success Check**: 2 nodes in Ready status with ARM64 architecture ✅

---

## Part 5: Docker Buildx for ARM64 (5 minutes)

### Step 5.1: Create Multi-Arch Builder

```bash
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap
```

**Expected Output**:
```
[+] Building 5.0s (1/1) FINISHED
Name:   multiarch
Driver: docker-container

Platforms: linux/amd64, linux/arm64, linux/arm/v7, ...
```

---

### Step 5.2: Test ARM64 Build

**Test with Phase IV Backend Dockerfile**:
```bash
docker buildx build --platform linux/arm64 \
  -t todo-backend:test-arm64 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --load \
  phase-3-chatbot/backend
```

**Verify Architecture**:
```bash
docker inspect todo-backend:test-arm64 | grep -i architecture
```

**Expected Output**: `"Architecture": "arm64"`

**Success Check**: Image builds successfully and architecture is arm64 ✅

---

## Part 6: Install Dapr (10 minutes)

### Step 6.1: Add Dapr Helm Repository

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
```

**Verify**:
```bash
helm search repo dapr
```

**Expected Output**:
```
NAME        CHART VERSION   APP VERSION   DESCRIPTION
dapr/dapr   1.14.x          1.14.x        A Helm chart for Dapr
```

---

### Step 6.2: Install Dapr Control Plane (HA Mode)

```bash
helm install dapr dapr/dapr \
  --version=1.14 \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --wait
```

**Installation Time**: 3-5 minutes

**Expected Output**:
```
NAME: dapr
LAST DEPLOYED: <timestamp>
NAMESPACE: dapr-system
STATUS: deployed
REVISION: 1
```

---

### Step 6.3: Verify Dapr Installation

**Check Control Plane Status**:
```bash
dapr status -k
```

**Expected Output**:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-operator          dapr-system  True     Running  3         1.14.x   2m
dapr-sidecar-injector  dapr-system  True     Running  3         1.14.x   2m
dapr-sentry            dapr-system  True     Running  3         1.14.x   2m
dapr-placement-server  dapr-system  True     Running  3         1.14.x   2m
```

**Check Pods**:
```bash
kubectl get pods -n dapr-system
```

**Expected**: 12 pods total (4 components × 3 replicas), all Running

**Success Check**: All Dapr components show HEALTHY=True and STATUS=Running ✅

---

### Step 6.4: Test Dapr Sidecar Injection

```bash
# Create test deployment with Dapr enabled
kubectl create deployment nginx-test --image=nginx
kubectl annotate deployment nginx-test dapr.io/enabled="true" dapr.io/app-id="nginx-app"

# Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=nginx-test --timeout=60s

# Verify sidecar injected
kubectl get pods -l app=nginx-test -o jsonpath='{.items[0].spec.containers[*].name}'
```

**Expected Output**: `nginx daprd`

**Cleanup**:
```bash
kubectl delete deployment nginx-test
```

**Success Check**: Pod contains both nginx and daprd containers ✅

---

## Part 7: Validation & Documentation (5 minutes)

### Step 7.1: Run Complete Verification

**Create Verification Script**:
```bash
cat > verify-stage1.sh <<'EOF'
#!/bin/bash
set -e

echo "=== Stage 1 Verification ==="

# 1. Cluster connectivity
kubectl cluster-info >/dev/null 2>&1 && echo "✅ Cluster accessible" || echo "❌ Cluster not accessible"

# 2. Node count and architecture
NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
[ "$NODE_COUNT" = "2" ] && echo "✅ 2 nodes found" || echo "❌ Expected 2 nodes, found $NODE_COUNT"

ARCH=$(kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.architecture}')
[ "$ARCH" = "arm64" ] && echo "✅ ARM64 architecture" || echo "❌ Expected arm64, found $ARCH"

# 3. Dapr installation
dapr status -k >/dev/null 2>&1 && echo "✅ Dapr installed" || echo "❌ Dapr not installed"

# 4. Dapr pod count
DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers | wc -l)
[ "$DAPR_PODS" = "12" ] && echo "✅ 12 Dapr pods (HA mode)" || echo "❌ Expected 12 pods, found $DAPR_PODS"

# 5. All pods running
NOT_RUNNING=$(kubectl get pods -n dapr-system --no-headers | grep -v Running | wc -l)
[ "$NOT_RUNNING" = "0" ] && echo "✅ All Dapr pods Running" || echo "❌ $NOT_RUNNING pods not Running"

echo ""
echo "Stage 1 setup complete! Ready for Stage 2 (Redpanda Pub/Sub)."
EOF

chmod +x verify-stage1.sh
./verify-stage1.sh
```

**Expected Output**: All checks show ✅

---

### Step 7.2: Capture Setup Logs

```bash
mkdir -p phase-5-cloud-deployment/logs/

kubectl get nodes > phase-5-cloud-deployment/logs/cluster-nodes.txt
kubectl get nodes -o wide > phase-5-cloud-deployment/logs/cluster-nodes-detailed.txt
dapr status -k > phase-5-cloud-deployment/logs/dapr-status.txt
kubectl get pods -n dapr-system > phase-5-cloud-deployment/logs/dapr-pods.txt
kubectl top nodes > phase-5-cloud-deployment/logs/resource-utilization.txt
```

---

### Step 7.3: Check Costs (Verify $0.00)

1. OCI Console → **Billing & Cost Management** → **Cost Analysis**
2. Date range: Last 7 days
3. Filter by service: Compute, Container Engine for Kubernetes
4. **Verify**: Total cost = **$0.00** ✅

---

## Common Issues & Solutions

### Issue: "Cluster creation failed - quota exceeded"

**Cause**: Existing resources consuming Always Free quota

**Solution**:
1. Check quota: Governance → Limits & Quotas → Compute
2. Delete any existing compute instances or clusters
3. Verify: 4 OCPUs and 24GB RAM available
4. Retry cluster creation

---

### Issue: "kubectl: connection refused"

**Cause**: Token expired (8-hour expiration) or kubeconfig misconfigured

**Solution**:
```bash
# Refresh kubeconfig token
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT \
  --overwrite

# Test connection
kubectl get nodes
```

---

### Issue: "Docker build fails with exec format error"

**Cause**: Built x86 image but trying to run on ARM64

**Solution**:
- Always use `--platform linux/arm64` in buildx commands
- Verify image architecture before deploying:
  ```bash
  docker inspect <image> | grep -i architecture
  ```

---

### Issue: "Dapr pods CrashLoopBackOff"

**Cause**: Insufficient cluster resources or ARM64 compatibility issue

**Solution**:
1. Check node resources:
   ```bash
   kubectl top nodes
   kubectl describe nodes | grep -A 5 "Allocated resources"
   ```
2. Verify Dapr images are multi-arch (they are by default)
3. Check pod logs:
   ```bash
   kubectl logs -n dapr-system <pod-name>
   ```

---

## Next Steps

**You've successfully completed Stage 1!** 🎉

**What you have now**:
- Production-grade Kubernetes cluster on Oracle Cloud (free forever)
- Dapr control plane in HA mode (fault-tolerant)
- kubectl access configured
- Docker buildx ready for ARM64 deployments

**Next**: Stage 2 - Redpanda Pub/Sub Integration
- Sign up for Redpanda Cloud (14-day $100 credits)
- Configure Dapr Pub/Sub component
- Implement event-driven architecture

---

## Useful Commands Reference

**Cluster Management**:
```bash
# View cluster details
oci ce cluster get --cluster-id <ocid>

# List all clusters
oci ce cluster list --compartment-id <compartment-ocid>

# Refresh kubectl token (every 8 hours)
oci ce cluster create-kubeconfig --cluster-id <ocid> --file ~/.kube/config --region <region> --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT --overwrite
```

**Node Operations**:
```bash
# Check node status
kubectl get nodes -o wide

# Describe node (detailed info)
kubectl describe node <node-name>

# Monitor resources
kubectl top nodes
```

**Dapr Management**:
```bash
# Dapr status
dapr status -k

# Dapr dashboard (opens localhost:8080)
dapr dashboard -k

# Upgrade Dapr
helm upgrade dapr dapr/dapr -n dapr-system --set global.ha.enabled=true

# Uninstall Dapr (if needed)
helm uninstall dapr -n dapr-system
```

---

## Learning Resources

**Oracle Cloud OKE**:
- Official Docs: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- Always Free FAQ: https://www.oracle.com/cloud/free/faq.html

**Dapr**:
- Getting Started: https://docs.dapr.io/getting-started/
- Kubernetes Deployment: https://docs.dapr.io/operations/hosting/kubernetes/
- HA Configuration: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-production/

**Kubernetes**:
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- OKE Best Practices: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengbestpractices.htm

---

**Quickstart Complete** - Total time: 45-60 minutes
