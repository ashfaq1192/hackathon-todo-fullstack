# Verification Checklist: OKE Cluster & Basic Dapr Setup

**Feature**: 010-oke-dapr-setup
**Date**: 2026-01-25
**Purpose**: Comprehensive validation checklist ensuring all success criteria are met

---

## Pre-Deployment Verification

### ✅ Oracle Cloud Account

- [ ] Oracle Cloud account created and verified
- [ ] Upgraded to "Pay As You Go" (retaining Always Free resources)
- [ ] $300 trial credits visible in account (30-day expiration)
- [ ] Budget alert configured (recommended: $10 threshold)
- [ ] Home region selected with Always Free capacity (us-ashburn-1, us-phoenix-1, or eu-frankfurt-1)

**Validation Command**:
```bash
oci iam region list --output table
# Verify home region is listed and available
```

---

### ✅ Local Tooling Installed

- [ ] **OCI CLI** installed and on PATH
  ```bash
  oci --version
  # Expected: 3.x.x or higher
  ```

- [ ] **kubectl** installed (version 1.26+)
  ```bash
  kubectl version --client
  # Expected: v1.26.x or higher
  ```

- [ ] **Helm** installed (version 3.x)
  ```bash
  helm version
  # Expected: v3.x.x
  ```

- [ ] **Dapr CLI** installed (version 1.12+)
  ```bash
  dapr version
  # Expected: CLI version 1.12.x or higher
  ```

- [ ] **Docker with Buildx** installed
  ```bash
  docker --version
  docker buildx version
  # Expected: Docker 20.10+ with buildx plugin
  ```

---

### ✅ OCI CLI Configuration

- [ ] OCI CLI configured with `oci setup config`
- [ ] Config file exists: `$HOME/.oci/config`
- [ ] API key pair generated: `$HOME/.oci/oci_api_key.pem` (private) and `$HOME/.oci/oci_api_key_public.pem` (public)
- [ ] Public key uploaded to OCI Console → Profile → API Keys
- [ ] Permissions set correctly: `chmod 600 ~/.oci/oci_api_key.pem`

**Validation Command**:
```bash
oci iam region list
# Should return list of regions without errors
```

---

## Cluster Provisioning Verification

### ✅ OKE Cluster Created

- [ ] Cluster created via "Quick Create" workflow
- [ ] Cluster name: `todo-chatbot-cluster` (or custom)
- [ ] Kubernetes version: 1.26+ (verify: ____)
- [ ] Cluster state: **ACTIVE**
- [ ] VCN, subnets, security lists, load balancer auto-created

**Validation Command**:
```bash
oci ce cluster list --compartment-id <compartment-ocid> --output table
# Verify cluster is listed with ACTIVE state
```

**OCI Console Verification**:
- Navigate to: Developer Services → Kubernetes Clusters (OKE)
- Verify cluster shows green checkmark (ACTIVE)
- Note cluster OCID: `____________________`

---

### ✅ Node Pool Configuration

- [ ] Node pool created with cluster
- [ ] Node pool state: **ACTIVE**
- [ ] Shape: **VM.Standard.A1.Flex** (ARM64)
- [ ] Number of nodes: **2**
- [ ] OCPUs per node: **2** (total: 4 OCPUs)
- [ ] Memory per node: **12 GB** (total: 24 GB)
- [ ] Image: Oracle Linux 8.x

**Validation Command**:
```bash
oci ce node-pool list --compartment-id <compartment-ocid> --output table
# Verify node pool ACTIVE with 2 nodes
```

---

### ✅ Worker Nodes Ready

- [ ] All 2 nodes in **Ready** status
- [ ] Architecture: **arm64** (verified)
- [ ] OS: Oracle Linux 8.x
- [ ] Kubernetes version matches cluster version

**Validation Commands**:
```bash
kubectl get nodes
# Expected: 2 nodes, STATUS=Ready

kubectl get nodes -o wide
# Verify INTERNAL-IP, OS-IMAGE, KERNEL-VERSION

kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'
# Expected output: arm64 arm64
```

**Success Criteria (SC-002)**:
```bash
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, cpu: .status.capacity.cpu, memory: .status.capacity.memory, arch: .status.nodeInfo.architecture}'
# Verify each node: cpu="2", memory="12Gi", arch="arm64"
```

---

## kubectl Configuration Verification

### ✅ Kubeconfig Generated

- [ ] Kubeconfig file created: `$HOME/.kube/config`
- [ ] Generated using OCI CLI with OIDC token auth
- [ ] Cluster endpoint configured (PUBLIC_ENDPOINT)
- [ ] Token version: 2.0.0
- [ ] Context set to OKE cluster

**Validation Commands**:
```bash
kubectl cluster-info
# Expected: Kubernetes control plane running at https://...

kubectl config current-context
# Expected: context-<cluster-id>
```

**Success Criteria (SC-001)**: Cluster accessible via kubectl within 20 minutes of creation
- Cluster creation start time: ____:____
- Cluster ACTIVE time: ____:____
- kubectl configured time: ____:____
- **Total time**: ____ minutes (should be ≤20 minutes)

---

### ✅ kubectl Operations Functional

- [ ] Can list nodes without errors
- [ ] Can list pods in all namespaces
- [ ] Can describe nodes
- [ ] Can check cluster health endpoint

**Validation Commands (SC-005)**:
```bash
kubectl get nodes
kubectl get pods --all-namespaces
kubectl describe nodes
kubectl get --raw /healthz
# All commands should execute without authentication errors
```

---

## Docker ARM64 Verification

### ✅ Multi-Arch Builder Created

- [ ] Buildx builder created: `multiarch`
- [ ] Builder supports linux/arm64 platform
- [ ] Builder bootstrapped and active

**Validation Commands**:
```bash
docker buildx ls
# Verify multiarch builder exists and is running

docker buildx inspect multiarch
# Verify Platforms includes linux/arm64
```

---

### ✅ ARM64 Image Build Test

- [ ] Backend Dockerfile builds successfully for ARM64
- [ ] Frontend Dockerfile builds successfully for ARM64
- [ ] Images loaded into local Docker daemon
- [ ] Image architecture verified as arm64

**Validation Commands** (FR-016, FR-017):
```bash
# Build backend for ARM64
docker buildx build --platform linux/arm64 \
  -t todo-backend:test-arm64 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --load \
  phase-3-chatbot/backend

# Verify architecture
docker inspect todo-backend:test-arm64 | grep -i architecture
# Expected: "Architecture": "arm64"

# Build frontend for ARM64
docker buildx build --platform linux/arm64 \
  -t todo-frontend:test-arm64 \
  -f phase-4-k8s/docker/frontend/Dockerfile \
  --load \
  phase-3-chatbot/frontend

# Verify architecture
docker inspect todo-frontend:test-arm64 | grep -i architecture
# Expected: "Architecture": "arm64"
```

---

## Dapr Installation Verification

### ✅ Dapr Helm Repository

- [ ] Dapr Helm repository added
- [ ] Repository updated to latest charts

**Validation Commands**:
```bash
helm repo list | grep dapr
# Expected: dapr https://dapr.github.io/helm-charts/

helm search repo dapr
# Expected: dapr/dapr chart version 1.14.x
```

---

### ✅ Dapr Control Plane Installed

- [ ] Dapr installed in namespace: **dapr-system**
- [ ] Installation method: **Helm**
- [ ] Dapr version: **1.12+** (actual: ____)
- [ ] HA mode enabled: **global.ha.enabled=true**
- [ ] Helm release status: **deployed**

**Validation Commands** (FR-004, FR-005):
```bash
helm list -n dapr-system
# Expected: dapr release with STATUS=deployed

helm get values dapr -n dapr-system
# Verify: global.ha.enabled: true
```

---

### ✅ Dapr Components Running

- [ ] **dapr-operator**: 3 replicas, all Running
- [ ] **dapr-sidecar-injector**: 3 replicas, all Running
- [ ] **dapr-sentry**: 3 replicas, all Running
- [ ] **dapr-placement-server**: 3 replicas, all Running
- [ ] Total pods: **12** (4 components × 3 replicas)

**Validation Commands** (FR-006, FR-007, SC-003):
```bash
kubectl get pods -n dapr-system
# Count: 12 pods total, all STATUS=Running, all READY=1/1

dapr status -k
# Expected: All 4 components HEALTHY=True, STATUS=Running, REPLICAS=3
```

**Success Criteria (SC-003)**: 100% of Dapr pods in Running state within 5 minutes
- Dapr installation start time: ____:____
- All pods Running time: ____:____
- **Total time**: ____ minutes (should be ≤5 minutes)

---

### ✅ Dapr Sidecar Injection

- [ ] Test deployment created with Dapr annotations
- [ ] Dapr sidecar automatically injected
- [ ] Pod shows 2 containers (app + daprd)

**Validation Commands** (FR-008, SC-004):
```bash
# Create test deployment
kubectl create deployment nginx-test --image=nginx
kubectl annotate deployment nginx-test dapr.io/enabled="true" dapr.io/app-id="nginx-app"
kubectl rollout status deployment/nginx-test

# Verify sidecar injection
kubectl get pods -l app=nginx-test -o jsonpath='{.items[0].spec.containers[*].name}'
# Expected output: nginx daprd

# Cleanup
kubectl delete deployment nginx-test
```

**Success Criteria (SC-004)**: Sidecar injection works on first test deployment ✅

---

## Security Validation

### ✅ RBAC Enabled

- [ ] RBAC API resources available
- [ ] ClusterRoles and ClusterRoleBindings exist
- [ ] Current user has appropriate permissions

**Validation Commands** (FR-019):
```bash
kubectl api-resources | grep rbac
# Expected: clusterroles, rolebindings, etc.

kubectl get clusterroles | wc -l
# Expected: 50+ (many system roles)

kubectl auth can-i create deployments
# Expected: yes
```

---

### ✅ Security List Review

- [ ] Default security lists reviewed in OCI Console
- [ ] Ingress rules: Only necessary ports (443, 6443) open
- [ ] Egress rules: Allow outbound for image pulls
- [ ] No overly permissive rules (e.g., 0.0.0.0/0 on all ports)

**OCI Console Path**: Networking → Virtual Cloud Networks → <VCN-name> → Security Lists

**Documented Findings**:
- Ingress rules: ________________________
- Egress rules: ________________________
- Security concerns (if any): ________________________

---

### ✅ Security Assumptions Documented

- [ ] Security validation results saved to `specs/010-oke-dapr-setup/security-validation.md`
- [ ] Assumptions documented: learning environment, not production
- [ ] Known limitations listed: no network policies, pod security standards not enforced

**Create Document**:
```bash
cat > specs/010-oke-dapr-setup/security-validation.md <<EOF
# Security Validation Report

**Date**: $(date +%Y-%m-%d)
**Cluster**: todo-chatbot-cluster

## RBAC Status
- Enabled: Yes
- Current user role: cluster-admin

## Security List Configuration
- Ingress: [document findings]
- Egress: [document findings]

## Security Assumptions
- This is a learning/portfolio environment, not production
- Network policies NOT configured (Stage 1 scope limit)
- Pod security standards NOT enforced (Stage 1 scope limit)
- Secrets stored in Kubernetes Secrets (basic, not encrypted at rest)
- Public ingress for demo purposes (acceptable for Always Free tier)
- No compliance requirements (GDPR, HIPAA, etc.)

## Recommendations for Production
1. Implement NetworkPolicies for pod-to-pod traffic control
2. Enable Pod Security Standards (restricted profile)
3. Use External Secrets Operator for secrets management
4. Enable audit logging
5. Implement least-privilege RBAC roles
EOF
```

**Success Criteria (SC-009)**: Security configuration verified and documented ✅

---

## Health Checks & Monitoring

### ✅ Cluster Health

- [ ] Kubernetes API server health endpoint returns "ok"
- [ ] All nodes in Ready state
- [ ] No MemoryPressure, DiskPressure, or PIDPressure conditions

**Validation Commands** (FR-014, SC-007):
```bash
kubectl get --raw /healthz
# Expected: ok

kubectl describe nodes | grep -A 5 "Conditions:"
# Verify: Ready=True, MemoryPressure=False, DiskPressure=False
```

---

### ✅ Resource Utilization

- [ ] Node CPU usage < 80%
- [ ] Node memory usage < 80%
- [ ] Dapr control plane memory usage ~1.5GB (as expected)

**Validation Commands** (SC-007):
```bash
kubectl top nodes
# Verify CPU% and MEMORY% within acceptable limits

kubectl top pods -n dapr-system
# Check Dapr resource usage
```

**Resource Utilization Report**:
| Node | CPU(cores) | CPU% | Memory(bytes) | Memory% |
|------|-----------|------|---------------|---------|
| Node 1 | _______ | ____% | ____________ | ______% |
| Node 2 | _______ | ____% | ____________ | ______% |

---

### ✅ Pod Network Connectivity

- [ ] Pods can communicate with Kubernetes API server
- [ ] Pods can resolve DNS (CoreDNS functional)
- [ ] Dapr service invocation test passes

**Validation Commands** (SC-007):
```bash
# Test CoreDNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default
# Expected: DNS resolution successful

# Test internet connectivity (for image pulls)
kubectl run -it --rm debug --image=busybox --restart=Never -- ping -c 3 8.8.8.8
# Expected: Packets received
```

---

## Logging & Documentation

### ✅ Verification Logs Captured

- [ ] Logs directory created: `phase-5-cloud-deployment/logs/`
- [ ] Cluster nodes output saved
- [ ] Dapr status output saved
- [ ] All verification commands output captured

**Capture Commands** (FR-018):
```bash
mkdir -p phase-5-cloud-deployment/logs/

kubectl get nodes > phase-5-cloud-deployment/logs/cluster-nodes.txt
kubectl get nodes -o wide > phase-5-cloud-deployment/logs/cluster-nodes-detailed.txt
kubectl get pods --all-namespaces > phase-5-cloud-deployment/logs/all-pods.txt
kubectl describe nodes > phase-5-cloud-deployment/logs/nodes-full-description.txt

dapr status -k > phase-5-cloud-deployment/logs/dapr-status.txt
kubectl get pods -n dapr-system > phase-5-cloud-deployment/logs/dapr-pods.txt
kubectl logs -n dapr-system -l app=dapr-operator --tail=200 > phase-5-cloud-deployment/logs/dapr-operator.log

kubectl get --raw /healthz > phase-5-cloud-deployment/logs/cluster-health.txt
kubectl top nodes > phase-5-cloud-deployment/logs/resource-utilization.txt
```

---

### ✅ Documentation Complete

- [ ] README.md created/updated in `phase-5-cloud-deployment/`
- [ ] README includes: Oracle Cloud account setup, OKE cluster creation, kubectl configuration, Dapr installation
- [ ] Troubleshooting section added with common issues
- [ ] Security validation results documented

**Documentation Checklist** (FR-009, FR-010):
```markdown
phase-5-cloud-deployment/README.md should include:
- [ ] Prerequisites section (tools, accounts)
- [ ] Oracle Cloud account setup steps
- [ ] OKE cluster creation (Quick Create workflow)
- [ ] kubectl configuration (kubeconfig generation)
- [ ] Docker buildx setup for ARM64
- [ ] Dapr installation steps (Helm)
- [ ] Verification procedures (this checklist)
- [ ] Troubleshooting guide (FR-010):
  - Cluster creation failures
  - kubectl connection issues
  - Dapr installation timeouts
  - ARM64 image build errors
  - Token expiration handling
- [ ] Security validation summary
- [ ] Single-developer-per-tenancy constraint (FR-009)
```

---

## Cost Verification

### ✅ Zero Cost Confirmed

- [ ] OCI Cost Analysis dashboard checked
- [ ] All resources within Always Free tier limits
- [ ] Total charges: **$0.00** for compute/networking

**Validation Steps** (SC-008):
1. Navigate to: OCI Console → Billing & Cost Management → Cost Analysis
2. Set date range: Last 7 days
3. Filter by service: Compute, Container Engine for Kubernetes
4. Verify total cost: $0.00

**Screenshot**: (Optional) Save screenshot of Cost Analysis dashboard showing $0.00

---

## Final Acceptance Criteria

### Success Criteria Validation

- [ ] **SC-001**: OKE cluster provisioned and accessible via kubectl within 20 minutes ✅ (verified above)
- [ ] **SC-002**: All cluster nodes Ready with correct resource allocation (2 nodes × 2 OCPUs × 12GB) ✅
- [ ] **SC-003**: Dapr control plane 100% pods Running within 5 minutes ✅
- [ ] **SC-004**: Automatic Dapr sidecar injection works on first test deployment ✅
- [ ] **SC-005**: All basic kubectl operations execute without auth errors ✅
- [ ] **SC-006**: Complete setup documentation created ✅
- [ ] **SC-007**: All verification commands execute successfully ✅
- [ ] **SC-008**: Zero cost incurred (confirmed via Cost Analysis) ✅
- [ ] **SC-009**: Basic security configuration verified and documented ✅

### Functional Requirements Validation

- [ ] **FR-001**: OKE cluster with 2 worker nodes, VM.Standard.A1.Flex ✅
- [ ] **FR-002**: Each node 2 OCPUs × 12GB RAM (total: 4 OCPUs, 24GB) ✅
- [ ] **FR-003**: kubectl configured with OIDC token authentication ✅
- [ ] **FR-004**: Dapr version 1.12+ installed via Helm ✅
- [ ] **FR-005**: Dapr in HA mode (global.ha.enabled=true) ✅
- [ ] **FR-006**: Dapr control plane in dapr-system namespace ✅
- [ ] **FR-007**: All Dapr pods Running within 5 minutes ✅
- [ ] **FR-008**: Automatic Dapr sidecar injection enabled ✅
- [ ] **FR-009**: Complete setup documented in README.md ✅
- [ ] **FR-010**: Troubleshooting steps provided ✅
- [ ] **FR-011**: OKE "Quick Create" workflow used ✅
- [ ] **FR-012**: OCI CLI configured for authenticated access ✅
- [ ] **FR-013**: Dapr core components installed (Pub/Sub, State, Bindings, Secrets, Service Invocation capabilities) ✅
- [ ] **FR-014**: Cluster health validated (nodes, pods, resources, network) ✅
- [ ] **FR-015**: Cluster access credentials configured (8-hour token expiration) ✅
- [ ] **FR-016**: Docker images built for ARM64 architecture ✅
- [ ] **FR-017**: Multi-architecture Docker builds documented ✅
- [ ] **FR-018**: Basic verification logs saved to files ✅
- [ ] **FR-019**: Basic security validation performed ✅

---

## Stage Completion Sign-Off

**Completed by**: ________________________
**Date**: ________________________
**Total time**: ________ hours
**Issues encountered**: ________________________

**Ready for Stage 2 (Redpanda Pub/Sub)**: ☐ Yes ☐ No

**If No, blocking issues**:
1. ________________________
2. ________________________

---

## Appendix: Quick Verification Script

Save as `verify-stage1.sh`:

```bash
#!/bin/bash
set -e

echo "=== Stage 1 Verification Script ==="
echo ""

echo "1. Checking cluster connectivity..."
kubectl cluster-info || { echo "FAIL: kubectl not configured"; exit 1; }

echo "2. Checking nodes..."
NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
if [ "$NODE_COUNT" != "2" ]; then
  echo "FAIL: Expected 2 nodes, found $NODE_COUNT"
  exit 1
fi

echo "3. Checking node architecture..."
ARCH=$(kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.architecture}')
if [ "$ARCH" != "arm64" ]; then
  echo "FAIL: Expected arm64, found $ARCH"
  exit 1
fi

echo "4. Checking Dapr installation..."
dapr status -k || { echo "FAIL: Dapr not installed"; exit 1; }

echo "5. Checking Dapr pods..."
DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers | wc -l)
if [ "$DAPR_PODS" != "12" ]; then
  echo "FAIL: Expected 12 Dapr pods, found $DAPR_PODS"
  exit 1
fi

echo "6. Checking pod status..."
NOT_RUNNING=$(kubectl get pods -n dapr-system --no-headers | grep -v Running | wc -l)
if [ "$NOT_RUNNING" != "0" ]; then
  echo "FAIL: $NOT_RUNNING pods not in Running state"
  kubectl get pods -n dapr-system
  exit 1
fi

echo ""
echo "=== ALL CHECKS PASSED ==="
echo "Stage 1 (OKE Cluster & Basic Dapr Setup) is complete and verified."
```

**Run**:
```bash
chmod +x verify-stage1.sh
./verify-stage1.sh
```

---

**Verification Checklist Complete**
