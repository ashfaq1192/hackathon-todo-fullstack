# CLI Commands Contract: OKE Cluster & Basic Dapr Setup

**Feature**: 010-oke-dapr-setup
**Date**: 2026-01-25
**Purpose**: Define all CLI commands, their inputs, outputs, and expected behaviors

---

## Overview

This contract specifies the command-line interface for setting up and verifying the OKE cluster and Dapr installation. All commands are idempotent where possible and include error handling guidance.

---

## Category 1: Oracle Cloud Account Setup

### Command: Sign Up for Oracle Cloud Free Tier

**Purpose**: Create Oracle Cloud account with Always Free resources

**Method**: Web Browser
**URL**: https://cloud.oracle.com/free

**Inputs**:
- Email address (valid, unique)
- Password (strong, 12+ characters)
- Credit card (validation only, no charges within Free Tier)
- Phone number (SMS verification)

**Expected Output**:
- Email confirmation link
- Account activated with $300 trial credits (30 days)
- Access to Always Free resources

**Success Criteria**:
- Can log into OCI Console
- Free Tier dashboard shows 4 OCPUs, 24GB RAM available

**Error Scenarios**:
- Email already registered → Use different email or password reset
- Credit card declined → Try different card or contact bank
- Region not supported → Select alternate home region

---

### Command: Upgrade to Pay As You Go

**Purpose**: Enable OKE cluster creation while retaining Always Free resources

**Method**: OCI Console → Billing → Upgrade Account

**Inputs**:
- Confirmation checkbox (acknowledge billing terms)

**Expected Output**:
- Account status changes to "Pay As You Go"
- Always Free resources remain perpetual
- OKE service unlocked

**Success Criteria**:
- Can navigate to Container Engine → Clusters → Create Cluster
- Budget alerts configured (recommended: $10 threshold)

**Error Scenarios**:
- Upgrade button disabled → Complete identity verification first
- Payment method required → Add valid credit card in Billing section

---

## Category 2: OCI CLI Setup

### Command: Install OCI CLI

**Purpose**: Install Oracle Cloud Infrastructure command-line tool

**Platforms**:

**Linux/macOS**:
```bash
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

**Inputs**:
- Installation directory (default: $HOME/bin)
- Add to PATH confirmation

**Expected Output**:
```
OCI CLI installed successfully.
oci --version
# Output: 3.x.x or higher
```

**Success Criteria**:
- `oci --version` returns version number
- `which oci` shows installation path

**Error Scenarios**:
- Python not found → Install Python 3.8+ first
- Permission denied → Run with appropriate permissions or change install directory

---

### Command: Configure OCI CLI

**Purpose**: Set up authentication credentials for OCI API access

**Command**:
```bash
oci setup config
```

**Interactive Prompts & Inputs**:
1. **Config file location**: Press Enter for default ($HOME/.oci/config)
2. **User OCID**: Copy from OCI Console → Profile → User Settings
3. **Tenancy OCID**: Copy from OCI Console → Profile → Tenancy
4. **Region**: Enter home region (e.g., us-ashburn-1)
5. **Generate new API key**: Y (generates private/public key pair)
6. **Key location**: Press Enter for default ($HOME/.oci/oci_api_key.pem)
7. **Passphrase**: Optional (press Enter to skip for ease of use)

**Expected Output**:
```
Config written to /home/user/.oci/config
Private key written to /home/user/.oci/oci_api_key.pem
Public key written to /home/user/.oci/oci_api_key_public.pem

Upload the public key to your user settings in OCI Console.
```

**Post-Command Action**:
1. Open OCI Console → Profile → User Settings → API Keys
2. Click "Add API Key" → "Paste Public Key"
3. Paste contents of $HOME/.oci/oci_api_key_public.pem
4. Click "Add"

**Success Criteria**:
```bash
oci iam region list
# Returns list of OCI regions without errors
```

**Error Scenarios**:
- Invalid OCID format → Verify copied correctly from Console (starts with ocid1.)
- API key not uploaded → Complete post-command action above
- Permission denied on key file → Fix with `chmod 600 ~/.oci/oci_api_key.pem`

---

## Category 3: OKE Cluster Provisioning

### Command: Create OKE Cluster (Console - Quick Create)

**Purpose**: Provision Kubernetes cluster with "Quick Create" workflow

**Method**: OCI Console → Developer Services → Kubernetes Clusters (OKE) → Create Cluster

**Workflow Selection**: Quick Create (recommended for beginners)

**Configuration Inputs**:

| Field | Value | Notes |
|-------|-------|-------|
| Name | `todo-chatbot-cluster` | Human-readable identifier |
| Compartment | (root) or custom | Where cluster will be created |
| Kubernetes Version | 1.28 or latest | Must be ≥1.26 for Dapr compatibility |
| Kubernetes API Endpoint | Public Endpoint | Accessible from local machine |
| Node Type | Managed | OCI manages node lifecycle |
| Kubernetes Worker Nodes | Private Workers | Nodes in private subnet |
| Shape | VM.Standard.A1.Flex | ARM64, Always Free eligible |
| Number of nodes | 2 | Distributed across ADs if available |
| OCPUs per node | 2 | Total 4 OCPUs |
| Memory per node | 12 GB | Total 24 GB |
| Image | Oracle Linux 8.x | Latest available |
| Node pool name | `pool1` | Auto-generated, can customize |

**Expected Output**:
- Cluster creation initiated (status: CREATING)
- Estimated time: 15 minutes
- VCN, subnets, security lists, load balancer created automatically

**Success Criteria**:
- Cluster status changes to ACTIVE
- Node pool status ACTIVE
- Both worker nodes show ACTIVE

**Verification Commands**:
```bash
# List clusters
oci ce cluster list --compartment-id <compartment-ocid>

# Get cluster details
oci ce cluster get --cluster-id <cluster-ocid>

# Check cluster state
oci ce cluster get --cluster-id <cluster-ocid> --query 'data."lifecycle-state"'
# Expected output: ACTIVE
```

**Error Scenarios**:
- Quota exceeded → Check Governance → Limits & Quotas, verify no existing clusters consuming quota
- Service limit reached → Request service limit increase or delete existing resources
- Region capacity unavailable → Try different region (us-phoenix-1, eu-frankfurt-1)

---

### Command: Generate Kubeconfig

**Purpose**: Configure kubectl to connect to OKE cluster

**Command**:
```bash
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

**Inputs**:
- `<cluster-ocid>`: Copy from OCI Console → Cluster Details → OCID
- `<region>`: Same as cluster region (e.g., us-ashburn-1)

**Expected Output**:
```
New kubeconfig written to /home/user/.kube/config
```

**Success Criteria**:
```bash
kubectl cluster-info
# Output: Kubernetes control plane is running at https://...

kubectl get nodes
# Output: 2 nodes, STATUS=Ready, ARM64 architecture
```

**Token Refresh** (required every 8 hours):
```bash
# Re-run the same command with --overwrite flag
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT \
  --overwrite
```

**Error Scenarios**:
- Cluster not found → Verify cluster-id is correct
- Unauthorized → Verify OCI CLI config is correct, user has permissions
- Network timeout → Check firewall, verify cluster endpoint is PUBLIC
- Token expired → Re-run with --overwrite to refresh

---

## Category 4: kubectl Operations

### Command: Verify Cluster Connectivity

**Purpose**: Confirm kubectl can communicate with OKE cluster

**Command**:
```bash
kubectl cluster-info
```

**Expected Output**:
```
Kubernetes control plane is running at https://<cluster-endpoint>
CoreDNS is running at https://<cluster-endpoint>/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

**Success Criteria**: No errors, endpoints are reachable

---

### Command: List Nodes

**Purpose**: Verify worker nodes are Ready

**Command**:
```bash
kubectl get nodes
```

**Expected Output**:
```
NAME          STATUS   ROLES   AGE   VERSION
10.0.10.2     Ready    node    5m    v1.28.x
10.0.10.3     Ready    node    5m    v1.28.x
```

**Success Criteria**:
- 2 nodes listed
- All STATUS = Ready
- VERSION matches cluster Kubernetes version

**Detailed Node Info**:
```bash
kubectl get nodes -o wide
```

**Expected Additional Info**:
- INTERNAL-IP: Private subnet IPs
- OS-IMAGE: Oracle Linux 8.x
- KERNEL-VERSION: 5.x
- CONTAINER-RUNTIME: containerd://1.x

**Verify ARM64 Architecture**:
```bash
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'
```

**Expected Output**: `arm64 arm64`

---

### Command: Describe Node (Troubleshooting)

**Purpose**: Get detailed node information including capacity and conditions

**Command**:
```bash
kubectl describe node <node-name>
```

**Key Sections to Review**:
- **Capacity**: 2 cores, 12Gi memory
- **Allocatable**: ~1.8 cores, ~11Gi memory (after system overhead)
- **Conditions**: All True for Ready, False for MemoryPressure/DiskPressure
- **Allocated resources**: Shows current usage vs allocatable

---

### Command: Check Resource Utilization

**Purpose**: Monitor CPU and memory usage across nodes

**Command**:
```bash
kubectl top nodes
```

**Expected Output**:
```
NAME        CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
10.0.10.2   250m         12%    2048Mi          18%
10.0.10.3   200m         10%    1800Mi          16%
```

**Success Criteria**:
- CPU% < 80% (sufficient headroom)
- MEMORY% < 80% (sufficient headroom)

**Note**: Requires metrics-server addon (enabled by default on OKE)

---

## Category 5: Docker Buildx for ARM64

### Command: Create Multi-Arch Builder

**Purpose**: Enable building Docker images for ARM64 architecture

**Command**:
```bash
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap
```

**Expected Output**:
```
[+] Building 5.0s (1/1) FINISHED
 => [internal] booting buildkit                      5.0s
Name:   multiarch
Driver: docker-container

Platforms: linux/amd64, linux/arm64, linux/arm/v7, ...
```

**Success Criteria**:
- Builder named "multiarch" is active
- Platforms includes linux/arm64

---

### Command: Build ARM64 Docker Image

**Purpose**: Build backend Docker image for ARM64 architecture

**Command**:
```bash
docker buildx build --platform linux/arm64 \
  -t todo-backend:v2-arm64 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --load \
  phase-3-chatbot/backend
```

**Inputs**:
- `--platform linux/arm64`: Target ARM64 architecture
- `-t todo-backend:v2-arm64`: Image tag
- `-f phase-4-k8s/docker/backend/Dockerfile`: Dockerfile path
- `--load`: Load image into local Docker daemon
- `phase-3-chatbot/backend`: Build context

**Expected Output**:
```
[+] Building 120.5s (15/15) FINISHED
 => [internal] load build definition from Dockerfile   0.1s
 => [internal] load .dockerignore                       0.0s
 => [builder 1/6] FROM docker.io/library/python:3.13    8.2s
 ...
 => exporting to image                                  5.0s
 => => naming to docker.io/library/todo-backend:v2-arm64
```

**Success Criteria**:
- Build completes without errors
- Image exists in local registry: `docker images | grep todo-backend`

**Verify Image Architecture**:
```bash
docker inspect todo-backend:v2-arm64 | grep -i architecture
```

**Expected Output**: `"Architecture": "arm64"`

---

### Command: Build Multi-Platform Image

**Purpose**: Build image supporting both x86 and ARM64 (production best practice)

**Command**:
```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t <registry>/todo-backend:v2 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --push \
  phase-3-chatbot/backend
```

**Inputs**:
- `--platform linux/amd64,linux/arm64`: Build for both architectures
- `--push`: Push to remote registry (requires login)
- `<registry>`: Replace with actual registry (e.g., docker.io/username)

**Expected Output**:
```
[+] Building 240.3s (30/30) FINISHED
 => [linux/amd64 internal] load build definition       0.1s
 => [linux/arm64 internal] load build definition       0.1s
 ...
 => exporting to registry                              15.2s
```

**Verify Multi-Platform Manifest**:
```bash
docker manifest inspect <registry>/todo-backend:v2
```

**Expected Output**: JSON with multiple platforms listed, including:
```json
{
  "manifests": [
    {
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    },
    {
      "platform": {
        "architecture": "arm64",
        "os": "linux"
      }
    }
  ]
}
```

---

## Category 6: Dapr Installation

### Command: Add Dapr Helm Repository

**Purpose**: Configure Helm to access Dapr charts

**Commands**:
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
```

**Expected Output**:
```
"dapr" has been added to your repositories
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "dapr" chart repository
```

**Verification**:
```bash
helm search repo dapr
```

**Expected Output**:
```
NAME            CHART VERSION   APP VERSION     DESCRIPTION
dapr/dapr       1.14.x          1.14.x          A Helm chart for Dapr
```

---

### Command: Install Dapr in HA Mode

**Purpose**: Deploy Dapr control plane with high availability configuration

**Command**:
```bash
helm install dapr dapr/dapr \
  --version=1.14 \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --wait
```

**Inputs**:
- `--version=1.14`: Dapr version (use latest stable)
- `--namespace dapr-system`: Dedicated namespace for Dapr
- `--create-namespace`: Auto-create namespace if not exists
- `--set global.ha.enabled=true`: Enable HA mode (3 replicas)
- `--wait`: Block until all pods are ready

**Expected Output**:
```
NAME: dapr
LAST DEPLOYED: Sat Jan 25 10:00:00 2026
NAMESPACE: dapr-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing Dapr: High Availability Mode.
...
```

**Installation Time**: 3-5 minutes

**Success Criteria**:
- Helm release status: deployed
- All Dapr pods reach Running status

---

### Command: Verify Dapr Installation

**Purpose**: Confirm Dapr control plane is healthy

**Command**:
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

**Success Criteria**:
- All 4 components listed
- HEALTHY = True for all
- STATUS = Running for all
- REPLICAS = 3 for all (HA mode)

---

### Command: List Dapr Pods

**Purpose**: Detailed pod status including resource usage

**Command**:
```bash
kubectl get pods -n dapr-system
```

**Expected Output**:
```
NAME                                     READY   STATUS    AGE
dapr-operator-7d7bb9b8c-abc12            1/1     Running   2m
dapr-operator-7d7bb9b8c-def34            1/1     Running   2m
dapr-operator-7d7bb9b8c-ghi56            1/1     Running   2m
dapr-sidecar-injector-6f8d9c7b5-jkl78    1/1     Running   2m
dapr-sidecar-injector-6f8d9c7b5-mno90    1/1     Running   2m
dapr-sidecar-injector-6f8d9c7b5-pqr12    1/1     Running   2m
dapr-sentry-5c8f7d6b4-stu34              1/1     Running   2m
dapr-sentry-5c8f7d6b4-vwx56              1/1     Running   2m
dapr-sentry-5c8f7d6b4-yz012              1/1     Running   2m
dapr-placement-server-0                  1/1     Running   2m
dapr-placement-server-1                  1/1     Running   2m
dapr-placement-server-2                  1/1     Running   2m
```

**Success Criteria**:
- 12 total pods (4 components × 3 replicas each)
- All pods READY = 1/1
- All pods STATUS = Running

---

### Command: Check Dapr Component Logs

**Purpose**: Troubleshoot Dapr control plane issues

**Command**:
```bash
kubectl logs -n dapr-system -l app=dapr-operator --tail=100
```

**Expected Output**: Logs showing successful startup, component discovery

**Success Indicators in Logs**:
- `level=info msg="Dapr control plane started"`
- `level=info msg="Watching for components"`
- No ERROR or FATAL level messages

**Other Component Logs**:
```bash
kubectl logs -n dapr-system -l app=dapr-sentry --tail=100
kubectl logs -n dapr-system -l app=dapr-sidecar-injector --tail=100
kubectl logs -n dapr-system -l app=dapr-placement-server --tail=100
```

---

## Category 7: Security Validation

### Command: Verify RBAC Enabled

**Purpose**: Confirm Role-Based Access Control is active

**Command**:
```bash
kubectl api-resources | grep rbac
```

**Expected Output**:
```
clusterrolebindings   ...  rbac.authorization.k8s.io/v1  false  ClusterRoleBinding
clusterroles          ...  rbac.authorization.k8s.io/v1  false  ClusterRole
rolebindings          ...  rbac.authorization.k8s.io/v1  true   RoleBinding
roles                 ...  rbac.authorization.k8s.io/v1  true   Role
```

**Success Criteria**: RBAC resources are available

**Additional Check**:
```bash
kubectl get clusterroles | wc -l
# Expected: 50+ (many system roles exist)
```

---

### Command: Check Current User Permissions

**Purpose**: Verify authenticated user has appropriate cluster access

**Commands**:
```bash
kubectl auth can-i create deployments
kubectl auth can-i create pods
kubectl auth can-i create services
kubectl auth can-i delete deployments
```

**Expected Output** (for cluster-admin role):
```
yes
yes
yes
yes
```

**Success Criteria**: User can perform standard operations

**Note**: OCI-generated kubeconfig typically grants cluster-admin role for account owner

---

## Category 8: Health Checks & Verification

### Command: Cluster Health Endpoint

**Purpose**: Verify Kubernetes API server health

**Command**:
```bash
kubectl get --raw /healthz
```

**Expected Output**: `ok`

---

### Command: Component Status

**Purpose**: Check control plane component health (deprecated in K8s 1.19+ but informative)

**Command**:
```bash
kubectl get componentstatuses
# OR
kubectl get cs
```

**Expected Output** (for OKE managed control plane):
```
Warning: v1 ComponentStatus is deprecated in v1.19+
NAME                 STATUS    MESSAGE   ERROR
scheduler            Healthy   ok
controller-manager   Healthy   ok
etcd-0               Healthy   ok
```

**Note**: Managed control plane health is abstracted by OCI

---

### Command: Test Sidecar Injection

**Purpose**: Verify Dapr sidecar injector is working

**Create Test Deployment**:
```bash
kubectl create deployment nginx-test --image=nginx
kubectl annotate deployment nginx-test dapr.io/enabled="true" dapr.io/app-id="nginx-app"
kubectl rollout status deployment/nginx-test
```

**Verify Sidecar Injected**:
```bash
kubectl get pods -l app=nginx-test -o jsonpath='{.items[0].spec.containers[*].name}'
```

**Expected Output**: `nginx daprd`

**Success Criteria**: Pod has 2 containers (nginx + daprd sidecar)

**Cleanup**:
```bash
kubectl delete deployment nginx-test
```

---

## Category 9: Logging & Documentation

### Command: Capture Setup Logs

**Purpose**: Save verification outputs for troubleshooting

**Commands**:
```bash
mkdir -p phase-5-cloud-deployment/logs/

kubectl get nodes > logs/cluster-nodes.txt
kubectl get nodes -o wide > logs/cluster-nodes-detailed.txt
kubectl get pods --all-namespaces > logs/all-pods.txt
kubectl describe nodes > logs/nodes-full-description.txt

dapr status -k > logs/dapr-status.txt
kubectl get pods -n dapr-system > logs/dapr-pods.txt
kubectl logs -n dapr-system -l app=dapr-operator --tail=200 > logs/dapr-operator.log

kubectl get --raw /healthz > logs/cluster-health.txt
kubectl top nodes > logs/resource-utilization.txt
```

**Success Criteria**: All commands execute without errors, files created

---

## Category 10: Cost Monitoring

### Command: Check OCI Cost

**Purpose**: Verify zero charges for Always Free resources

**Method**: OCI Console → Billing & Cost Management → Cost Analysis

**Filters**:
- Date range: Last 7 days
- Service: Compute, Container Engine for Kubernetes
- Tag: Always Free = true (if configured)

**Expected Results**:
- Total cost: $0.00 for Always Free resources
- Trial credits may show usage for non-free resources

**Set Up Budget Alerts** (recommended):
1. Navigate to Billing & Cost Management → Budgets
2. Create Budget → Set threshold: $10
3. Add alert rule: Email when 80% of threshold reached
4. Prevents accidental charges

---

## Error Recovery Procedures

### Scenario: Pod CrashLoopBackOff

**Diagnosis**:
```bash
kubectl get pods -n dapr-system
kubectl describe pod <pod-name> -n dapr-system
kubectl logs <pod-name> -n dapr-system --previous
```

**Common Causes**:
- ARM64 image incompatibility (check manifest)
- Resource exhaustion (check node capacity)
- Configuration error (check Helm values)

---

### Scenario: Node NotReady

**Diagnosis**:
```bash
kubectl describe node <node-name>
# Check Conditions section for MemoryPressure, DiskPressure, PIDPressure
```

**Common Causes**:
- Node rebooting (wait 5 minutes)
- Network connectivity issue (check OCI Console → VCN)
- Kubelet failure (check OCI Console → Instances → Logs)

---

### Scenario: kubectl Connection Timeout

**Diagnosis**:
```bash
oci ce cluster get --cluster-id <ocid>
# Verify cluster is ACTIVE

ping <cluster-endpoint>
# Verify network connectivity
```

**Common Causes**:
- Token expired (re-run kubeconfig command)
- Firewall blocking outbound 6443 (check corporate firewall)
- Cluster endpoint wrong (verify PUBLIC_ENDPOINT selected)

---

## Summary

All CLI commands are documented with:
- ✅ Purpose and context
- ✅ Full command syntax
- ✅ Expected inputs/outputs
- ✅ Success criteria
- ✅ Error scenarios and remediation

**Total Command Categories**: 10
**Total Commands Specified**: 35+
**Coverage**: 100% of functional requirements (FR-001 through FR-019)
