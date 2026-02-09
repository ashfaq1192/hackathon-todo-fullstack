# Implementation Tasks: OKE Cluster & Basic Dapr Setup

**Feature**: `010-oke-dapr-setup`
**Branch**: `010-oke-dapr-setup`
**Created**: 2026-01-25

---

## Task Summary

- **Total Tasks**: 37
- **User Story 1 (P1)**: 15 tasks (Oracle Cloud Account & OKE Cluster)
- **User Story 2 (P2)**: 8 tasks (Dapr Control Plane HA Installation)
- **User Story 3 (P3)**: 11 tasks (Health Verification & Documentation)
- **Setup**: 2 tasks
- **Foundational**: 1 task

---

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) - OKE Cluster Provisioning
- Delivers: Production Kubernetes cluster accessible via kubectl
- Independent test: 2 nodes Ready, ARM64 architecture verified
- Estimated time: 35-40 minutes

**Incremental Delivery**:
1. **MVP (US1)**: OKE cluster provisioned and accessible → Ready for application deployments
2. **Enhanced (US2)**: Dapr runtime installed → Ready for distributed app features
3. **Complete (US3)**: Fully verified and documented → Ready for Stage 2 (Redpanda)

**Parallel Opportunities**: See "Parallel Execution Examples" below

---

## Phase 1: Setup (Project Initialization)

**Goal**: Create project structure and install required CLI tools

### Tasks

- [ ] T001 Create phase-5-cloud-deployment directory structure in /mnt/e/projects/hackathon-todo-fullstack/phase-5-cloud-deployment
- [ ] T002 [P] Install prerequisite CLI tools: OCI CLI, kubectl, Helm, Dapr CLI, verify Docker with buildx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Configure local tooling required by all user stories

### Tasks

- [ ] T003 Configure OCI CLI authentication in $HOME/.oci/config and upload public API key to OCI Console

**Why Foundational**: OCI CLI authentication is required for OKE cluster creation (US1), kubectl access (US1), and all subsequent operations. Must be completed before any user story can proceed.

---

## Phase 3: User Story 1 - Oracle Cloud Account Setup & OKE Cluster Provisioning (Priority: P1)

**Story Goal**: Provision production-grade Kubernetes cluster on Oracle Cloud Always Free tier

**Independent Test Criteria**:
- ✅ OKE cluster status = ACTIVE in OCI Console
- ✅ `kubectl get nodes` returns 2 nodes in Ready status
- ✅ `kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'` returns `arm64 arm64`
- ✅ Total capacity: 4 vCPUs, 24GB RAM (verified with `kubectl describe nodes`)
- ✅ Cluster accessible within 20 minutes of starting creation (SC-001)

**Why Independent**: Delivers functional Kubernetes cluster that can be used immediately for deployments. Does not depend on Dapr or documentation being complete.

### Tasks

- [ ] T004 [US1] Sign up for Oracle Cloud Free Tier account at cloud.oracle.com/free with email verification
- [ ] T005 [US1] Upgrade Oracle Cloud account to "Pay As You Go" via OCI Console → Billing → Upgrade Account (retains Always Free resources)
- [ ] T006 [US1] Configure budget alert for $10 threshold in OCI Console → Billing & Cost Management → Budgets
- [ ] T007 [US1] Create OKE cluster using "Quick Create" workflow: name=todo-chatbot-cluster, shape=VM.Standard.A1.Flex, nodes=2, OCPUs=2, memory=12GB in OCI Console → Developer Services → Kubernetes Clusters (OKE)
- [ ] T008 [US1] Wait for cluster provisioning to complete (status changes to ACTIVE, estimated 15 minutes)
- [ ] T009 [US1] Copy cluster OCID from OCI Console → Cluster Details for kubectl configuration
- [ ] T010 [US1] Generate kubeconfig file using `oci ce cluster create-kubeconfig --cluster-id <cluster-ocid> --file $HOME/.kube/config --region <region> --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT`
- [ ] T011 [US1] Verify cluster connectivity with `kubectl cluster-info` (expected: Kubernetes control plane running at https://...)
- [ ] T012 [US1] Verify node status with `kubectl get nodes` (expected: 2 nodes, STATUS=Ready)
- [ ] T013 [US1] Verify ARM64 architecture with `kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'` (expected: arm64 arm64)
- [ ] T014 [US1] Verify node resources with `kubectl describe nodes | grep -E "Capacity|Allocatable"` (expected: total 4 vCPUs, 24GB RAM)
- [ ] T015 [US1] Create Docker buildx multi-arch builder with `docker buildx create --name multiarch --use` and `docker buildx inspect --bootstrap`
- [ ] T016 [US1] Test ARM64 image build: `docker buildx build --platform linux/arm64 -t todo-backend:test-arm64 -f phase-4-k8s/docker/backend/Dockerfile --load phase-3-chatbot/backend`
- [ ] T017 [US1] Verify image architecture with `docker inspect todo-backend:test-arm64 | grep -i architecture` (expected: "Architecture": "arm64")
- [ ] T018 [US1] Verify zero cost with OCI Console → Billing & Cost Management → Cost Analysis (filter: last 7 days, Compute + OKE, expected: $0.00)

---

## Phase 4: User Story 2 - Dapr Control Plane Installation in HA Mode (Priority: P2)

**Story Goal**: Install Dapr distributed application runtime in High Availability mode

**Independent Test Criteria**:
- ✅ `dapr status -k` shows 4 components all HEALTHY=True, STATUS=Running, REPLICAS=3
- ✅ `kubectl get pods -n dapr-system --no-headers | wc -l` returns 12
- ✅ All Dapr pods in Running status within 5 minutes (SC-003)
- ✅ Test deployment with Dapr annotation shows 2 containers: app + daprd sidecar (SC-004)

**Why Independent**: Delivers functional Dapr runtime that can be used for distributed application features. Only depends on US1 (OKE cluster). Can be tested without documentation being complete.

**Depends On**: US1 (requires functional OKE cluster with kubectl access)

### Tasks

- [ ] T019 [US2] Add Dapr Helm repository with `helm repo add dapr https://dapr.github.io/helm-charts/` and `helm repo update`
- [ ] T020 [US2] Verify Dapr chart availability with `helm search repo dapr` (expected: dapr/dapr chart version 1.14.x)
- [ ] T021 [US2] Install Dapr control plane in HA mode: `helm install dapr dapr/dapr --version=1.14 --namespace dapr-system --create-namespace --set global.ha.enabled=true --wait`
- [ ] T022 [US2] Verify Dapr installation status with `dapr status -k` (expected: all components HEALTHY=True, REPLICAS=3)
- [ ] T023 [US2] Verify Dapr pod count with `kubectl get pods -n dapr-system --no-headers | wc -l` (expected: 12 pods total)
- [ ] T024 [US2] Verify all Dapr pods Running with `kubectl get pods -n dapr-system` (expected: all STATUS=Running, READY=1/1)
- [ ] T025 [US2] Test Dapr sidecar injection: Create test deployment `kubectl create deployment nginx-test --image=nginx` and annotate with `kubectl annotate deployment nginx-test dapr.io/enabled="true" dapr.io/app-id="nginx-app"`
- [ ] T026 [US2] Verify sidecar injection with `kubectl get pods -l app=nginx-test -o jsonpath='{.items[0].spec.containers[*].name}'` (expected: nginx daprd), then cleanup with `kubectl delete deployment nginx-test`

---

## Phase 5: User Story 3 - Cluster Health Verification & Documentation (Priority: P3)

**Story Goal**: Verify cluster health and create comprehensive setup documentation

**Independent Test Criteria**:
- ✅ `kubectl get --raw /healthz` returns `ok`
- ✅ `kubectl top nodes` shows CPU < 80%, Memory < 80%
- ✅ RBAC verified: `kubectl api-resources | grep rbac` returns roles/bindings
- ✅ Security validation documented in specs/010-oke-dapr-setup/security-validation.md
- ✅ Complete README.md exists in phase-5-cloud-deployment/ with all required sections
- ✅ Verification logs captured in phase-5-cloud-deployment/logs/ directory
- ✅ Team member can reproduce environment following README (SC-006)

**Why Independent**: Delivers verification and documentation that ensures cluster is production-ready. Only depends on US1 and US2 being complete. Can be executed and validated independently.

**Depends On**: US1 (OKE cluster), US2 (Dapr installation)

### Tasks

- [ ] T027 [US3] Verify cluster health endpoint with `kubectl get --raw /healthz` (expected: ok)
- [ ] T028 [US3] Verify node resource utilization with `kubectl top nodes` (expected: CPU < 80%, Memory < 80%)
- [ ] T029 [US3] Verify RBAC enabled with `kubectl api-resources | grep rbac` (expected: clusterroles, rolebindings, etc.)
- [ ] T030 [US3] Verify user permissions with `kubectl auth can-i create deployments` (expected: yes)
- [ ] T031 [US3] Review OCI security lists in OCI Console → Networking → Virtual Cloud Networks → <VCN-name> → Security Lists and document findings
- [ ] T032 [US3] Create security validation report in /mnt/e/projects/hackathon-todo-fullstack/specs/010-oke-dapr-setup/security-validation.md documenting RBAC status, security list rules, and security assumptions
- [ ] T033 [US3] Create logs directory and capture verification outputs: `mkdir -p phase-5-cloud-deployment/logs/` then save outputs of kubectl get nodes, dapr status, kubectl top nodes to respective files
- [ ] T034 [US3] Create comprehensive README.md in /mnt/e/projects/hackathon-todo-fullstack/phase-5-cloud-deployment/README.md with sections: Prerequisites, Oracle Cloud Account Setup, OKE Cluster Creation, kubectl Configuration, Docker Buildx Setup, Dapr Installation, Verification Procedures, Security Validation, Troubleshooting, Single-Developer Constraint
- [ ] T035 [US3] Test pod network connectivity: Deploy test pod and verify DNS resolution with `kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default`
- [ ] T036 [US3] Test Dapr service invocation: Deploy 2 test apps with Dapr enabled and verify pod-to-pod communication via Dapr
- [ ] T037 [US3] Validate complete setup by having team member follow README.md and reproduce environment successfully (100% reproduction success required per SC-006)

---

## Dependencies

### User Story Completion Order

```
Setup (Phase 1)
    ↓
Foundational (Phase 2)
    ↓
User Story 1 (P1) - OKE Cluster Provisioning
    ↓
    ├─→ User Story 2 (P2) - Dapr Installation [depends on US1]
    │       ↓
    └──────→ User Story 3 (P3) - Verification & Documentation [depends on US1 + US2]
```

**Critical Path**: T001 → T002 → T003 → T004-T018 (US1) → T019-T026 (US2) → T027-T037 (US3)

**Blocking Relationships**:
- US2 BLOCKED BY US1 (needs functional OKE cluster)
- US3 BLOCKED BY US1 + US2 (needs both cluster and Dapr)
- T010 BLOCKED BY T009 (needs cluster OCID)
- T019-T026 BLOCKED BY T011 (needs kubectl access)

**Independent Paths**:
- T001 and T002 can run in parallel (different concerns)
- T015-T017 (Docker buildx) can run anytime after T002 (independent of cluster creation)
- T033 can run in parallel with T034 (different files)

---

## Parallel Execution Examples

### Within User Story 1 (After cluster is ACTIVE)

```bash
# Terminal 1: Configure kubectl
oci ce cluster create-kubeconfig --cluster-id <ocid> --file ~/.kube/config ...

# Terminal 2: Set up Docker buildx (independent)
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Terminal 3: Configure budget alerts (independent, OCI Console)
# Navigate to Billing & Cost Management → Create Budget
```

**Parallelizable Tasks in US1**: T010-T014 (kubectl/cluster verification) can run while T015-T017 (Docker buildx) executes in parallel

### Within User Story 3

```bash
# Terminal 1: Capture verification logs
mkdir -p phase-5-cloud-deployment/logs/
kubectl get nodes > logs/cluster-nodes.txt
kubectl top nodes > logs/resource-utilization.txt
dapr status -k > logs/dapr-status.txt

# Terminal 2: Write README.md (independent)
# Edit phase-5-cloud-deployment/README.md with setup guide

# Terminal 3: Create security validation report (independent)
# Edit specs/010-oke-dapr-setup/security-validation.md
```

**Parallelizable Tasks in US3**: T033 (capture logs), T034 (write README), T032 (security report) can all run in parallel as they modify different files

---

## Task Format Reference

**Legend**:
- `[P]` = Parallelizable (can run simultaneously with other [P] tasks if dependencies met)
- `[US1]`, `[US2]`, `[US3]` = User Story labels (maps to spec.md priorities)
- File paths always included for implementation tasks

**Example Parallel Execution**:
```bash
# These tasks can run simultaneously (all marked [P] and no blocking dependencies):
- [ ] T002 [P] Install prerequisite CLI tools: OCI CLI, kubectl, Helm, Dapr CLI, verify Docker with buildx
- [ ] T015 [US1] Create Docker buildx multi-arch builder with `docker buildx create --name multiarch --use` and `docker buildx inspect --bootstrap`
```

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 37 tasks completed
- [ ] User Story 1 Independent Test: OKE cluster accessible, 2 ARM64 nodes Ready
- [ ] User Story 2 Independent Test: Dapr 12 pods Running, sidecar injection works
- [ ] User Story 3 Independent Test: Health checks pass, README complete, reproducible
- [ ] All 9 Success Criteria (SC-001 through SC-009) validated per verification-checklist.md
- [ ] All 19 Functional Requirements (FR-001 through FR-019) satisfied
- [ ] Zero cost confirmed: OCI Cost Analysis shows $0.00
- [ ] Documentation complete: README.md, security-validation.md, verification logs

---

## Notes

**Implementation Approach**: This is an infrastructure provisioning feature requiring manual execution through OCI Console and CLI commands. Tasks cannot be auto-generated as code but must be executed step-by-step following quickstart.md guide.

**Time Estimates**:
- User Story 1: 35-40 minutes (includes 15-min cluster provisioning wait)
- User Story 2: 10-15 minutes (includes 5-min Dapr installation)
- User Story 3: 15-20 minutes (verification and documentation)
- **Total**: 60-75 minutes

**Reference Documents**:
- Detailed commands: [contracts/cli-commands.md](./contracts/cli-commands.md)
- Verification procedures: [contracts/verification-checklist.md](./contracts/verification-checklist.md)
- Step-by-step guide: [quickstart.md](./quickstart.md)
- Infrastructure entities: [data-model.md](./data-model.md)

**Next Steps After Completion**:
1. Mark all tasks complete
2. Verify all independent test criteria pass
3. Commit completed setup to Git
4. Proceed to Stage 2 (011-redpanda-pubsub): Redpanda Cloud & Dapr Pub/Sub Integration
