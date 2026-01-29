# Data Model: OKE Cluster & Basic Dapr Setup

**Feature**: 010-oke-dapr-setup
**Date**: 2026-01-25
**Purpose**: Define infrastructure entities, their attributes, relationships, and state transitions

---

## Overview

This document defines the infrastructure components (not application data) that comprise the OKE cluster and Dapr installation. Unlike application data models with databases and schemas, this infrastructure model describes cloud resources, their configuration, and operational states.

---

## Entity 1: OKE Cluster

**Purpose**: Oracle Kubernetes Engine managed cluster resource

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| cluster_id (OCID) | String | Unique, Immutable | Oracle Cloud Identifier (format: ocid1.cluster.oc1...) |
| cluster_name | String | Required, 1-255 chars | Human-readable cluster name |
| kubernetes_version | String | Required, Format: X.Y (e.g., "1.28") | K8s version supported by OKE |
| region | String | Required, Enum | Oracle Cloud region (us-ashburn-1, us-phoenix-1, eu-frankfurt-1) |
| vcn_id | String | Required, Immutable | Virtual Cloud Network OCID |
| compartment_id | String | Required | Organizational compartment OCID |
| endpoint | URL | Read-only | Kubernetes API server endpoint (e.g., https://...)  |
| state | Enum | Read-only | CREATING, ACTIVE, UPDATING, DELETING, FAILED, INACTIVE |
| created_at | DateTime | Read-only | Cluster creation timestamp |
| updated_at | DateTime | Read-only | Last modification timestamp |

**State Transitions**:
```
CREATING (15 min avg) → ACTIVE
ACTIVE → UPDATING (when changing config) → ACTIVE
ACTIVE → DELETING → [DELETED]
Any state → FAILED (on errors)
```

**Validation Rules**:
- Kubernetes version must be OKE-supported (1.26, 1.27, 1.28 as of Jan 2026)
- Region must have Always Free capacity available
- VCN must exist in same compartment and region
- State ACTIVE required before node pool creation

**Relationships**:
- **Has many**: Node Pools (1..n)
- **Belongs to**: VCN (1), Compartment (1)
- **Referenced by**: Kubeconfig (1..n)

---

## Entity 2: Node Pool

**Purpose**: Group of worker nodes with identical configuration

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| nodepool_id | String | Unique, Immutable | Node pool OCID |
| nodepool_name | String | Required | Human-readable name |
| cluster_id | String | Required, Foreign Key | Parent OKE cluster OCID |
| node_shape | String | Required | VM.Standard.A1.Flex (ARM64, Always Free) |
| node_count | Integer | Required, 1-10 | Number of nodes (2 for this feature) |
| ocpus_per_node | Integer | Required, 1-4 | OCPUs per node (2 for this feature) |
| memory_gb_per_node | Integer | Required | Memory per node (12GB for this feature) |
| node_image_id | String | Required | Oracle Linux image OCID |
| availability_domains | Array[String] | Optional | ADs for node distribution |
| state | Enum | Read-only | CREATING, ACTIVE, UPDATING, DELETING, FAILED |

**State Transitions**:
```
CREATING (5-10 min) → ACTIVE
ACTIVE → SCALING → ACTIVE (when changing node_count)
ACTIVE → UPDATING → ACTIVE (when changing config)
ACTIVE → DELETING → [DELETED]
```

**Validation Rules**:
- Total OCPUs across all nodes ≤ 4 (Always Free limit)
- Total memory across all nodes ≤ 24GB (Always Free limit)
- node_shape must be VM.Standard.A1.Flex (only Always Free eligible shape for OKE)
- Minimum node_count = 1, recommended = 2 for HA testing

**Relationships**:
- **Belongs to**: OKE Cluster (1)
- **Composed of**: Worker Nodes (n)

---

## Entity 3: Worker Node

**Purpose**: Individual compute instance running Kubernetes workloads

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| node_id | String | Unique | Kubernetes node identifier (not OCID) |
| instance_id | String | Unique | OCI compute instance OCID |
| nodepool_id | String | Required | Parent node pool OCID |
| node_name | String | Unique | Kubernetes node name (oke-cXXX-nXXX) |
| internal_ip | IP Address | Required | Private IP for pod networking |
| external_ip | IP Address | Optional | Public IP (if enabled) |
| availability_domain | String | Required | AD placement for node |
| architecture | String | Read-only | arm64 (for VM.Standard.A1.Flex) |
| os | String | Read-only | Oracle Linux 8.x |
| kubelet_version | String | Read-only | Matches cluster kubernetes_version |
| status | Enum | Read-only | NotReady, Ready, SchedulingDisabled |
| cpu_capacity | String | Read-only | 2 cores (2000m in K8s units) |
| memory_capacity | String | Read-only | 12Gi |
| cpu_allocatable | String | Read-only | ~1800m (after system pods) |
| memory_allocatable | String | Read-only | ~11Gi (after system pods) |

**State Transitions**:
```
NotReady (initial boot) → Ready (kubelet healthy)
Ready → NotReady (node failure, network issue)
Ready → SchedulingDisabled (manual cordon/drain)
```

**Validation Rules**:
- Architecture must be arm64 (validates Docker images are ARM64-compatible)
- Status Ready required before scheduling pods
- Allocatable resources always < Capacity (reserved for system)

**Relationships**:
- **Belongs to**: Node Pool (1)
- **Hosts**: Pods (0..n)

---

## Entity 4: Dapr Control Plane

**Purpose**: Distributed application runtime management layer

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| namespace | String | Required | dapr-system (Kubernetes namespace) |
| version | String | Required | 1.12+, 1.13+, 1.14+ |
| deployment_mode | Enum | Required | standard, ha (this feature uses ha) |
| installation_method | Enum | Required | cli, helm (this feature uses helm) |
| mtls_enabled | Boolean | Default: true | Mutual TLS for service-to-service |
| tracing_enabled | Boolean | Default: false | OpenTelemetry tracing (Stage 5) |
| metrics_enabled | Boolean | Default: true | Prometheus metrics export |

**HA Configuration** (when deployment_mode = ha):
- Replicas per component: 3
- Anti-affinity: enabled (distribute across nodes)
- Resource requests: defined (prevent eviction)

**Validation Rules**:
- Namespace dapr-system must not exist before installation
- Version must be Helm chart compatible (dapr/dapr chart)
- HA mode requires ≥2 worker nodes for anti-affinity

**Relationships**:
- **Composed of**: Dapr Components (4: Placement, Operator, Sentry, Sidecar Injector)
- **Deployed in**: Kubernetes Cluster (1)

---

## Entity 5: Dapr Component (Control Plane Service)

**Purpose**: Individual Dapr control plane microservice

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| component_name | Enum | Required | placement, operator, sentry, sidecar-injector |
| deployment_name | String | Required | dapr-{component_name} |
| namespace | String | Required | dapr-system |
| replicas | Integer | Required | 1 (standard), 3 (HA mode) |
| image | String | Required | daprio/{component}:1.14.x |
| status | Enum | Read-only | Running, Pending, Failed, CrashLoopBackOff |
| cpu_request | String | Required | 100m (0.1 core) |
| memory_request | String | Required | 128Mi - 512Mi (varies by component) |
| cpu_limit | String | Optional | 1000m (1 core) |
| memory_limit | String | Optional | 512Mi - 1Gi |

**Component Responsibilities**:
- **Placement**: Actor placement and state distribution
- **Operator**: Watches for component CRDs, manages lifecycle
- **Sentry**: Certificate Authority for mTLS, issues certificates
- **Sidecar Injector**: Webhook to inject daprd sidecar into pods

**State Transitions**:
```
Pending (image pull, scheduling) → Running
Running → Failed (health check fails)
Failed → CrashLoopBackOff (repeated failures)
```

**Validation Rules**:
- All 4 components must reach Running status for healthy control plane
- Replicas = 3 enforced for HA mode
- Images must support arm64 architecture (verified multi-arch)

**Relationships**:
- **Part of**: Dapr Control Plane (1)
- **Runs in**: Kubernetes Pods (replicas count)

---

## Entity 6: Kubeconfig

**Purpose**: Configuration file for kubectl CLI access to cluster

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| file_path | Path | Required | $HOME/.kube/config (default) |
| cluster_name | String | Required | Friendly name for cluster context |
| cluster_endpoint | URL | Required | API server URL from OKE cluster |
| cluster_ca_cert | String (Base64) | Required | Certificate Authority for server validation |
| user_name | String | Required | OCI user identifier |
| auth_method | Enum | Required | exec (OCI CLI token provider) |
| token_version | String | Required | 2.0.0 |
| token_expiration | Duration | Read-only | 8 hours from generation |
| context_name | String | Required | Combination of cluster + user |
| current_context | String | Required | Active context for kubectl commands |

**Validation Rules**:
- cluster_endpoint must be reachable (network connectivity)
- Token expires after 8 hours (requires refresh)
- OCI CLI must be installed and configured for exec auth
- File permissions must be 0600 (read/write owner only)

**Relationships**:
- **References**: OKE Cluster (1)
- **Used by**: kubectl CLI

---

## Entity 7: OCI CLI Configuration

**Purpose**: Oracle Cloud Infrastructure command-line tool settings

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| config_file_path | Path | Required | $HOME/.oci/config (default) |
| profile_name | String | Default: DEFAULT | Named profile for multi-account |
| user_ocid | String | Required | User's Oracle Cloud ID |
| tenancy_ocid | String | Required | Organization/account ID |
| region | String | Required | Default OCI region |
| key_file_path | Path | Required | Path to API signing private key |
| fingerprint | String | Required | Public key fingerprint for validation |

**Validation Rules**:
- user_ocid, tenancy_ocid must exist and match Oracle Cloud account
- key_file must exist with correct permissions (0600)
- fingerprint must match uploaded public key in Console
- Region must be valid OCI region identifier

**Relationships**:
- **Used by**: Kubeconfig (exec auth provider)
- **Authenticates to**: OCI API

---

## Composite Entities (Derived)

### Full Cluster Configuration
Combination of OKE Cluster + Node Pool + Worker Nodes + Network that represents the complete infrastructure.

**Total Resource Allocation**:
- OCPUs: 2 nodes × 2 OCPUs = 4 OCPUs (100% of Always Free quota)
- Memory: 2 nodes × 12GB = 24GB (100% of Always Free quota)
- Architecture: ARM64 (aarch64)
- OS: Oracle Linux 8.x

**State Validation**:
All components must reach ACTIVE/Ready state:
1. OKE Cluster: ACTIVE
2. Node Pool: ACTIVE
3. All Worker Nodes: Ready
4. Dapr Control Plane: All 4 components Running

---

## State Management

**Infrastructure State Storage**: Oracle Cloud Infrastructure (OCI) backend
- OKE resources stored in OCI control plane (not customer-managed)
- Kubeconfig stored locally on developer machine
- Dapr component definitions stored in Kubernetes API server (etcd)

**Operational State Tracking**:
```bash
# Cluster state
oci ce cluster get --cluster-id <ocid> --query 'data."lifecycle-state"'

# Node state
kubectl get nodes -o wide

# Dapr state
dapr status -k
kubectl get pods -n dapr-system
```

---

## Entity Relationships Diagram

```
Oracle Cloud Tenancy
└─ Compartment
   └─ VCN (Virtual Cloud Network)
      └─ OKE Cluster [cluster_id]
         ├─ Node Pool [nodepool_id]
         │  ├─ Worker Node 1 [Ready, arm64]
         │  └─ Worker Node 2 [Ready, arm64]
         │
         └─ Dapr Control Plane [dapr-system namespace]
            ├─ Placement (3 replicas) [Running]
            ├─ Operator (3 replicas) [Running]
            ├─ Sentry (3 replicas) [Running]
            └─ Sidecar Injector (3 replicas) [Running]

Local Developer Machine
├─ OCI CLI Configuration [$HOME/.oci/config]
│  └─ Authenticates → OCI API
│
└─ Kubeconfig [$HOME/.kube/config]
   └─ Connects to → OKE Cluster API Server
```

---

## Validation Queries

**Check Cluster Health**:
```bash
# Cluster reachable
kubectl cluster-info

# All nodes ready
kubectl get nodes
# Expected: 2 nodes, STATUS=Ready, ARM64

# Dapr control plane healthy
dapr status -k
# Expected: 4 components, STATUS=Running, HEALTHY=True
```

**Check Resource Allocation**:
```bash
# Total cluster capacity
kubectl describe nodes | grep -E "Capacity|Allocatable"

# Dapr resource usage
kubectl top pods -n dapr-system
```

**Check Architecture**:
```bash
# Verify ARM64
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'
# Expected output: arm64 arm64
```

---

## Data Model Compliance

**From Spec Requirements**:
- ✅ FR-001: OKE Cluster with 2 worker nodes, VM.Standard.A1.Flex (ARM64)
- ✅ FR-002: Each node 2 OCPUs × 12GB RAM = 4 OCPUs, 24GB total
- ✅ FR-003: Kubeconfig with OIDC token authentication
- ✅ FR-004: Dapr version 1.12+ installed via Helm
- ✅ FR-005: Dapr HA mode enabled (3 replicas per component)
- ✅ FR-006: Dapr control plane in dapr-system namespace
- ✅ FR-016: ARM64 architecture enforced at node level

**Entity Completeness**:
All functional requirements map to concrete entities with measurable attributes and validation rules. No ambiguous or placeholder entities remain.
