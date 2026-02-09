# Implementation Plan: OKE Cluster & Basic Dapr Setup

**Branch**: `010-oke-dapr-setup` | **Date**: 2026-01-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-oke-dapr-setup/spec.md`

---

## Summary

Provision a production-grade Kubernetes cluster on Oracle Cloud's Always Free tier (OKE) and install Dapr control plane in High Availability mode. This establishes the foundation infrastructure for Phase V Advanced Cloud Deployment, enabling deployment of the Todo Chatbot application to a real cloud environment without incurring costs.

**Key Deliverables**:
- OKE cluster with 2 ARM64 worker nodes (4 vCPUs, 24GB RAM total)
- Dapr control plane in HA mode (3 replicas per component)
- kubectl configured with OIDC token authentication
- Docker buildx for multi-architecture ARM64 image builds
- Complete documentation and verification procedures
- Zero ongoing costs (100% within Always Free tier limits)

---

## Technical Context

**Platform**: Oracle Kubernetes Engine (OKE) Always Free tier
**Compute Shape**: VM.Standard.A1.Flex (ARM64/aarch64 architecture)
**Kubernetes Version**: 1.26+ (1.28 recommended for latest features)
**Container Runtime**: containerd 1.x (OKE default)
**Networking**: OCI VCN with public/private subnets, security lists, load balancer

**Primary Dependencies**:
- **Orchestration**: Kubernetes 1.26+ (OKE managed control plane)
- **Distributed Runtime**: Dapr 1.12+ (installed via Helm charts)
- **Package Manager**: Helm 3.x
- **CLI Tools**: OCI CLI 3.x, kubectl 1.26+, Dapr CLI 1.12+
- **Build Tools**: Docker 20.10+ with buildx plugin

**Storage**: N/A (infrastructure-only stage, no application data)

**Testing**: Infrastructure validation via kubectl commands, Dapr status checks, health endpoints

**Target Platform**: Oracle Cloud Infrastructure (OCI), Always Free tier

**Project Type**: Infrastructure/DevOps (single repository, phase-5-cloud-deployment directory)

**Performance Goals**:
- Cluster provisioning: ≤15 minutes
- kubectl configuration: ≤5 minutes
- Dapr installation: ≤5 minutes
- Total setup time: ≤20 minutes (SC-001)

**Constraints**:
- ARM64 architecture only (Always Free limitation)
- 4 vCPUs total, 24GB RAM total (Always Free quota)
- Public cluster endpoint (private endpoint requires paid tier)
- Single region deployment
- 8-hour token expiration for kubectl (OIDC limitation)

**Scale/Scope**:
- 2 worker nodes (minimum for HA testing)
- 12 Dapr control plane pods (4 components × 3 replicas)
- ~1.5GB RAM for Dapr, ~22GB available for applications
- Foundation for subsequent Stage 2-6 deployments

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase V Requirements (Constitution v1.7.0, Lines 777-989)

✅ **Gradual Implementation Strategy** (Principle VIII):
- Stage 1 (this feature): OKE Cluster & Basic Dapr Setup
- Stage 2: Redpanda Pub/Sub Integration
- Stage 3: Advanced Dapr Features
- Stage 4: CI/CD with GitHub Actions
- Stage 5: Observability with Grafana Cloud
- Each stage independently testable ✅

✅ **Free Tier Services** (Lines 822):
- Oracle Cloud Always Free: 4 vCPUs, 24GB RAM perpetual ✅
- Zero cost for this stage (SC-008) ✅

✅ **Dapr HA Mode** (Line 824):
- `--enable-ha=true` flag specified ✅
- 3 replicas per control plane component ✅

✅ **Spec-Driven Development** (Principles I, II):
- Spec → Plan → Tasks → Implement workflow followed ✅
- This plan document created via `/sp.plan` command ✅
- All decisions documented in research.md ✅

✅ **Documentation Requirements** (Principle V):
- Complete setup guide (quickstart.md) ✅
- Troubleshooting procedures (cli-commands.md) ✅
- Verification checklist (verification-checklist.md) ✅

✅ **No Manual Code Writing** (Principle V):
- Infrastructure-as-code using OCI Console + CLI ✅
- Declarative Helm charts for Dapr ✅
- All commands scripted and documented ✅

✅ **Definition of Done** (Constitution Lines 905-941):
- All MVP criteria from constitution mapped to success criteria ✅
- Comprehensive verification procedures defined ✅

### Gates Status

| Gate | Status | Notes |
|------|--------|-------|
| SDD Workflow | ✅ PASS | Spec → Plan → Tasks → Implement |
| Gradual Implementation | ✅ PASS | Stage 1 of 5-stage strategy |
| Free Tier Compliance | ✅ PASS | 100% within Always Free limits |
| Documentation | ✅ PASS | Comprehensive docs created |
| No Manual Code | ✅ PASS | Infrastructure-as-code approach |
| Testing | ✅ PASS | Verification procedures defined |

**All gates passed. Proceed to Phase 0 (Research).**

---

## Project Structure

### Documentation (this feature)

```text
specs/010-oke-dapr-setup/
├── plan.md                      # This file (Phase 0 output)
├── research.md                  # Phase 0: Technology research & decisions
├── data-model.md                # Phase 1: Infrastructure entities
├── quickstart.md                # Phase 1: Step-by-step setup guide
├── contracts/                   # Phase 1: Interface specifications
│   ├── cli-commands.md          # All CLI commands with inputs/outputs
│   └── verification-checklist.md # Complete validation checklist
├── checklists/                  # Quality assurance
│   └── requirements.md          # Spec validation checklist
└── tasks.md                     # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-5-cloud-deployment/
├── README.md                    # Main setup guide (references quickstart.md)
├── logs/                        # Verification command outputs (FR-018)
│   ├── cluster-nodes.txt
│   ├── dapr-status.txt
│   ├── resource-utilization.txt
│   └── ...
├── scripts/                     # Automation scripts (future)
│   ├── setup-oke.sh             # Automated cluster creation
│   ├── install-dapr.sh          # Automated Dapr installation
│   └── verify-stage1.sh         # Validation script
└── CLAUDE.md                    # Development session log

# Existing from Phase IV (reused for ARM64 builds)
phase-4-k8s/
├── docker/
│   ├── backend/Dockerfile       # Multi-stage backend (Python)
│   └── frontend/Dockerfile      # Multi-stage frontend (Node.js)
└── ...
```

**Structure Decision**: Infrastructure-focused directory under `phase-5-cloud-deployment/` for Stage 1. Application deployment directories (helm charts, dapr components) will be added in later stages. Existing Phase IV Dockerfiles are reused with ARM64 build process.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All requirements align with constitution principles and constraints.

---

## Phase 0: Research & Technology Decisions

**Status**: ✅ Complete

**Output**: [research.md](./research.md)

**Decisions Made**:
1. Oracle Cloud "Pay As You Go" upgrade strategy (retains Always Free)
2. OKE "Quick Create" workflow with VM.Standard.A1.Flex (ARM64)
3. Docker Buildx for multi-architecture image builds
4. Dapr Helm installation with HA mode enabled
5. kubectl OIDC token authentication (8-hour expiration)
6. Basic security validation approach (RBAC, security lists)
7. Basic logging strategy (file-based command outputs)

**Alternatives Considered**: Documented in research.md for each decision

**Risks Identified & Mitigated**:
- ARM64 compatibility: Verified base images are multi-arch, documented buildx process
- Token expiration: Documented refresh procedure, acceptable for learning environment
- Quota exhaustion: Budget alerts configured, single-developer constraint documented
- Security exposure: Basic validation defined, assumptions explicitly stated

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

**Output**:
- [data-model.md](./data-model.md) - Infrastructure entities (OKE cluster, nodes, Dapr components)
- [contracts/cli-commands.md](./contracts/cli-commands.md) - 35+ CLI commands with full specifications
- [contracts/verification-checklist.md](./contracts/verification-checklist.md) - Comprehensive validation procedures
- [quickstart.md](./quickstart.md) - Step-by-step implementation guide

**Entities Defined** (7 total):
1. **OKE Cluster**: Managed Kubernetes cluster with control plane
2. **Node Pool**: Group of worker nodes with identical configuration
3. **Worker Node**: Individual compute instance running Kubernetes
4. **Dapr Control Plane**: Distributed application runtime layer
5. **Dapr Component**: Individual control plane microservice (4 types)
6. **Kubeconfig**: Configuration file for kubectl access
7. **OCI CLI Configuration**: Authentication settings for OCI API

**Contracts Specified**:
- **CLI Commands**: 35+ commands across 10 categories (account setup, OCI CLI, OKE provisioning, kubectl, Docker buildx, Dapr installation, security, health checks, logging, cost monitoring)
- **Verification Procedures**: Complete checklist covering all 19 functional requirements and 9 success criteria

**API Contracts**: N/A (infrastructure stage, no application APIs)

---

## Implementation Phases

### Phase 2: Task Generation

**Command**: `/sp.tasks` (NOT part of `/sp.plan` - user runs separately)

**Input**: This plan document + spec.md

**Expected Output**: tasks.md with granular, ordered tasks

**Task Categories** (estimated):
1. Oracle Cloud account setup (3-5 tasks)
2. OCI CLI installation & configuration (4-6 tasks)
3. OKE cluster provisioning (5-7 tasks)
4. kubectl configuration (2-3 tasks)
5. Docker buildx setup (3-4 tasks)
6. Dapr installation (4-6 tasks)
7. Security validation (3-4 tasks)
8. Verification & logging (4-5 tasks)
9. Documentation (3-4 tasks)

**Total Estimated Tasks**: 30-45

---

### Phase 3: Implementation

**Command**: `/sp.implement` (executed after tasks.md approval)

**Approach**: Manual execution of infrastructure tasks (not code generation)

**Why Manual**: Infrastructure provisioning requires:
- Interactive web console workflows (OCI account signup, cluster creation)
- Multi-step authentication setups (credit card verification, API key upload)
- External service dependencies (Oracle Cloud, Dapr project)
- Human verification at checkpoints (budget alerts, cost monitoring)

**Implementation Strategy**:
1. Developer follows quickstart.md step-by-step
2. Executes CLI commands from cli-commands.md
3. Verifies each checkpoint using verification-checklist.md
4. Captures logs per FR-018
5. Documents completion and any issues encountered

**Automation Opportunities** (future enhancement):
- `setup-oke.sh`: Scripted cluster creation using OCI CLI
- `install-dapr.sh`: Automated Dapr installation
- `verify-stage1.sh`: Complete validation script

---

## Testing Strategy

### Infrastructure Validation

**Cluster Health Checks** (SC-007):
```bash
# Node status
kubectl get nodes
# Expected: 2 nodes, STATUS=Ready, ARM64

# Resource capacity
kubectl describe nodes | grep -E "Capacity|Allocatable"
# Expected: Total 4 vCPUs, 24GB RAM

# Cluster health endpoint
kubectl get --raw /healthz
# Expected: ok

# Resource utilization
kubectl top nodes
# Expected: CPU < 80%, Memory < 80%
```

**Dapr Validation** (SC-003, SC-004):
```bash
# Control plane status
dapr status -k
# Expected: All 4 components HEALTHY=True, REPLICAS=3

# Pod count
kubectl get pods -n dapr-system --no-headers | wc -l
# Expected: 12

# Sidecar injection test
kubectl create deployment nginx-test --image=nginx
kubectl annotate deployment nginx-test dapr.io/enabled="true" dapr.io/app-id="nginx-app"
kubectl get pods -l app=nginx-test -o jsonpath='{.items[0].spec.containers[*].name}'
# Expected: nginx daprd
```

**Security Validation** (SC-009):
```bash
# RBAC enabled
kubectl api-resources | grep rbac
# Expected: clusterroles, rolebindings, etc.

# User permissions
kubectl auth can-i create deployments
# Expected: yes
```

**ARM64 Validation** (FR-016):
```bash
# Node architecture
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.architecture}'
# Expected: arm64 arm64

# Image architecture test
docker buildx build --platform linux/arm64 -t test:arm64 -f phase-4-k8s/docker/backend/Dockerfile --load phase-3-chatbot/backend
docker inspect test:arm64 | grep -i architecture
# Expected: "Architecture": "arm64"
```

**Cost Validation** (SC-008):
- OCI Console → Billing & Cost Management → Cost Analysis
- Filter: Last 7 days, Compute + Container Engine for Kubernetes
- Expected: $0.00

### Success Criteria Validation

Refer to [contracts/verification-checklist.md](./contracts/verification-checklist.md) for complete validation procedures covering all 9 success criteria:
- SC-001: 20-minute provisioning timeline ✅
- SC-002: 2 nodes × 2 vCPUs × 12GB RAM ✅
- SC-003: Dapr 100% pods Running in 5 minutes ✅
- SC-004: Sidecar injection on first test ✅
- SC-005: kubectl operations without auth errors ✅
- SC-006: Documentation created and reproducible ✅
- SC-007: All verification commands successful ✅
- SC-008: Zero cost incurred ✅
- SC-009: Security validated and documented ✅

---

## Dependencies & Sequencing

### External Dependencies

1. **Oracle Cloud Account**:
   - Prerequisite: Valid email, credit card for verification
   - Dependency: Always Free tier program availability
   - Blocker if: Region capacity unavailable (mitigation: try alternate region)

2. **Dapr Project**:
   - Dependency: Helm charts v1.12+ stable release
   - Dependency: Multi-arch Docker images (already available)
   - Blocker if: Chart repository unavailable (mitigation: use cached charts)

3. **Network Connectivity**:
   - Required: Outbound HTTPS to cloud.oracle.com, github.com, dapr.io
   - Blocker if: Corporate firewall blocks cloud services (mitigation: use personal network)

### Internal Dependencies

1. **Completed Phase IV**:
   - Required: Dockerfiles for backend/frontend (phase-4-k8s/docker/)
   - Required: Knowledge of Kubernetes concepts
   - Blocker if: Phase IV not completed (mitigation: complete Phase IV first)

2. **Local Tooling**:
   - Required: OCI CLI, kubectl, Helm, Dapr CLI, Docker installed
   - Blocker if: Tools missing (mitigation: install per prerequisites)

### Task Sequencing

**Critical Path**:
1. Oracle account setup → OCI CLI config → OKE cluster creation → kubectl config → Dapr installation → Validation

**Parallel Opportunities**:
- Docker buildx setup can happen any time before image builds (later stages)
- Documentation can be written in parallel with validation

**Blocking Relationships**:
- kubectl config BLOCKED BY cluster provisioning (need cluster OCID)
- Dapr installation BLOCKED BY kubectl config (need cluster access)
- Validation BLOCKED BY Dapr installation (need all components)

---

## Risk Management

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| Oracle Free Tier quota unavailable | High (can't create cluster) | Low | Try alternate region, contact Oracle support |
| ARM64 image compatibility issues | Medium (deployment fails) | Medium | Test builds early, verify with docker manifest inspect |
| kubectl token expiration during work | Low (interruption) | High | Document refresh command prominently, set reminders |
| Accidental paid resource creation | High (unexpected costs) | Low | Configure budget alerts, document Always Free limits clearly |
| Dapr HA resource exhaustion | Medium (pods crash) | Low | Monitor resources during install, reduce replicas if needed |
| Corporate firewall blocks OCI | High (can't access cluster) | Medium | Use personal network, document network requirements |
| Node provisioning fails | Medium (cluster unusable) | Low | Verify quota before creation, retry with different AD |

**Contingency Plans**:
- **Budget exceeded**: Delete cluster immediately, review Cost Analysis, contact Oracle
- **Cluster creation timeout**: Check OCI Console Events, retry in different region
- **Dapr installation fails**: Uninstall (`helm uninstall dapr -n dapr-system`), verify cluster resources, reinstall

---

## Acceptance Criteria (Traceability)

**From Spec User Stories**:

**User Story 1 (Priority P1): Oracle Cloud Account Setup & OKE Cluster Provisioning**
- AS-1.1: Oracle account created with Always Free access ✅ (SC-001)
- AS-1.2: Upgraded to Pay As You Go, Always Free resources retained ✅ (SC-008)
- AS-1.3: Cluster provisions within 15 minutes with specified config ✅ (SC-001, SC-002)
- AS-1.4: Kubeconfig generated and kubectl can connect ✅ (SC-005)
- AS-1.5: 2 nodes in Ready status with ARM64 architecture ✅ (SC-002)

**User Story 2 (Priority P2): Dapr Control Plane Installation in HA Mode**
- AS-2.1: Dapr installs successfully via Helm with HA enabled ✅ (SC-003)
- AS-2.2: All 4 control plane components running in dapr-system namespace ✅ (SC-003)
- AS-2.3: Each component has 3 replicas (HA mode) ✅ (SC-003)
- AS-2.4: Dapr sidecar injection works on test deployment ✅ (SC-004)
- AS-2.5: `dapr status -k` shows all components healthy ✅ (SC-003)

**User Story 3 (Priority P3): Cluster Health Verification & Documentation**
- AS-3.1: Node resource utilization within expected limits ✅ (SC-007)
- AS-3.2: Test application starts with Dapr sidecar ✅ (SC-004)
- AS-3.3: Pod-to-pod communication works via Dapr ✅ (SC-007)
- AS-3.4: Security configuration verified (RBAC, security lists) ✅ (SC-009)
- AS-3.5: Complete documentation in README.md with all required sections ✅ (SC-006)
- AS-3.6: Setup reproducible by team member following guide ✅ (SC-006)

**All acceptance scenarios mapped to success criteria and validation procedures.**

---

## Definition of Done

### MVP Criteria (Constitution Lines 905-922)

- ✅ OKE cluster provisioned and running on Always Free tier (2 nodes, 4 vCPUs, 24GB RAM)
- ✅ Dapr installed on OKE with HA mode enabled (`--enable-ha=true`)
- ✅ All Dapr control plane components (4) running with 3 replicas each (12 pods total)
- ✅ kubectl configured with OIDC token authentication, can execute all basic operations
- ✅ Docker buildx configured for ARM64 image builds
- ✅ Health checks passing: cluster health endpoint, node status, Dapr status
- ✅ Resource limits verified: within Always Free quota (0% oversubscription)
- ✅ Basic security validation: RBAC enabled, security lists reviewed, assumptions documented
- ✅ README.md with complete setup instructions (quickstart.md)
- ✅ Verification logs captured to files (phase-5-cloud-deployment/logs/)
- ✅ Zero cost incurred (confirmed via OCI Cost Analysis dashboard: $0.00)

### Production-Ready Enhancements (Future Stages)

- [ ] Redpanda Cloud integration (Stage 2)
- [ ] Dapr Pub/Sub component configured (Stage 2)
- [ ] Application deployed to cluster (Stage 3)
- [ ] GitHub Actions CI/CD with OIDC (Stage 4)
- [ ] OpenTelemetry + Grafana Cloud observability (Stage 5)
- [ ] NetworkPolicies for pod isolation (Production hardening)
- [ ] Pod Security Standards enforced (Production hardening)
- [ ] Horizontal Pod Autoscaling configured (Production hardening)

---

## Next Steps

**After Plan Approval**:

1. **User reviews plan.md** (this document)
2. **User approves plan** in conversation
3. **Run** `/sp.tasks` to generate tasks.md
4. **User reviews tasks.md**
5. **User approves tasks**
6. **Run** `/sp.implement` OR **Manual execution**:
   - Follow quickstart.md step-by-step
   - Execute commands from cli-commands.md
   - Validate with verification-checklist.md
   - Capture logs per FR-018
7. **Document completion** in CLAUDE.md
8. **Proceed to Stage 2**: Redpanda Pub/Sub Integration (branch: 011-redpanda-pubsub)

---

## Appendix: Quick Reference

**Essential Commands**:

```bash
# Cluster access
oci ce cluster create-kubeconfig --cluster-id <ocid> --file ~/.kube/config --region <region> --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT

# Verify cluster
kubectl get nodes
dapr status -k

# Build ARM64 images
docker buildx build --platform linux/arm64 -t <image>:arm64 -f <Dockerfile> --load <context>

# Check costs
# OCI Console → Billing & Cost Management → Cost Analysis
```

**Key Files**:
- [quickstart.md](./quickstart.md) - Complete setup guide
- [cli-commands.md](./contracts/cli-commands.md) - All CLI commands
- [verification-checklist.md](./contracts/verification-checklist.md) - Validation procedures
- [data-model.md](./data-model.md) - Infrastructure entities

**Time Estimates**:
- Oracle Cloud setup: 15 minutes
- OCI CLI configuration: 10 minutes
- OKE cluster provisioning: 20 minutes
- kubectl + Dapr setup: 15 minutes
- Verification & documentation: 10 minutes
- **Total**: 60-70 minutes

---

**Plan Status**: ✅ Complete and ready for task generation
**Next Command**: `/sp.tasks`
