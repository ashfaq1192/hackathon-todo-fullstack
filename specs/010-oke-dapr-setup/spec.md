# Feature Specification: OKE Cluster & Basic Dapr Setup

**Feature Branch**: `010-oke-dapr-setup`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "Stage 1: OKE Cluster & Basic Dapr Setup - Provision Oracle Kubernetes Engine cluster on Always Free tier, configure kubectl access, install Dapr control plane with HA mode, and verify cluster health. This is the foundation stage for Phase V Advanced Cloud Deployment."

## Clarifications

### Session 2026-01-25

- Q: What level of logging and observability should be implemented for Stage 1 infrastructure setup, given that full observability stack is planned for Stage 5? → A: Basic verification logs only (console output from kubectl/dapr commands saved to files for troubleshooting)
- Q: What level of security validation should be performed for Stage 1, given that production-grade security hardening is out-of-scope? → A: Basic security validation (verify RBAC is enabled, check default security lists, document security assumptions)
- Q: How should Always Free tier quota constraints be handled when multiple developers might work on the same Oracle Cloud tenancy? → A: Document quota as single-developer constraint; multi-dev requires separate tenancies

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Oracle Cloud Account Setup & OKE Cluster Provisioning (Priority: P1)

As a developer completing Phase IV (Local Kubernetes Deployment), I need to provision a production-grade Kubernetes cluster on Oracle Cloud's Always Free tier so that I can deploy my Todo Chatbot application to a real cloud environment without incurring costs.

**Why this priority**: This is the foundational requirement for all subsequent Phase V stages. Without a functioning OKE cluster, no other cloud deployment activities can proceed. The Always Free tier provides perpetual free resources (4 vCPUs, 24GB RAM), making it ideal for learning and portfolio projects.

**Independent Test**: Can be fully tested by verifying the OKE cluster is running, accessible via kubectl, and has the expected node configuration (2 nodes, ARM architecture, correct resource allocation). Delivers a production Kubernetes environment ready for application deployment.

**Acceptance Scenarios**:

1. **Given** I have no Oracle Cloud account, **When** I sign up and verify my identity, **Then** I receive access to the Always Free tier with $300 initial credits for 30 days
2. **Given** I have an Oracle Cloud account on the Free tier, **When** I upgrade to "Pay As You Go", **Then** I keep my Always Free resources and can create OKE clusters
3. **Given** I'm creating an OKE cluster via the Console, **When** I select "Quick Create" with VM.Standard.A1.Flex nodes (2 nodes, 2 OCPUs each, 12GB RAM each), **Then** the cluster provisions successfully within 15 minutes
4. **Given** the OKE cluster is provisioned, **When** I download the kubeconfig file, **Then** I can connect to the cluster using kubectl
5. **Given** I run `kubectl get nodes`, **When** the cluster is healthy, **Then** I see 2 nodes in "Ready" status with ARM architecture

---

### User Story 2 - Dapr Control Plane Installation in HA Mode (Priority: P2)

As a developer with a functioning OKE cluster, I need to install the Dapr control plane in High Availability mode so that my distributed application runtime is production-ready with fault tolerance and reliability.

**Why this priority**: Dapr is the core distributed application runtime for Phase V. HA mode ensures production-grade reliability with multiple replicas of control plane components. This must be configured correctly from the start to avoid rework later when adding Dapr components (Pub/Sub, State, Bindings).

**Independent Test**: Can be fully tested by verifying all Dapr control plane pods are running in the dapr-system namespace, each component has multiple replicas (HA mode), and the Dapr sidecar can be injected into test deployments. Delivers a production-ready Dapr environment.

**Acceptance Scenarios**:

1. **Given** I have kubectl access to OKE, **When** I run `dapr init -k --enable-ha=true`, **Then** Dapr installs successfully in HA mode
2. **Given** Dapr is installed, **When** I check the dapr-system namespace, **Then** I see all control plane components running (Placement, Operator, Sentry, Sidecar Injector)
3. **Given** Dapr is in HA mode, **When** I inspect deployments, **Then** each component has multiple replicas (typically 3 for HA)
4. **Given** Dapr control plane is running, **When** I deploy a test pod with Dapr annotations, **Then** the Dapr sidecar is automatically injected
5. **Given** Dapr is installed, **When** I run `dapr status -k`, **Then** all components show healthy status

---

### User Story 3 - Cluster Health Verification & Documentation (Priority: P3)

As a developer with OKE and Dapr deployed, I need to verify the entire cluster is healthy and document the setup process so that I can confidently proceed to Stage 2 (Kafka integration) and help others reproduce this environment.

**Why this priority**: Verification ensures the foundation is solid before building upon it. Documentation captures the exact steps, configurations, and decisions made, which is critical for the hackathon judging process and future reference. This is lower priority because the cluster can function without perfect documentation, but it's still essential for completeness.

**Independent Test**: Can be fully tested by running a suite of health checks (node status, pod health, resource allocation, network connectivity) and producing a deployment guide. Delivers confidence that the infrastructure is production-ready and reproducible.

**Acceptance Scenarios**:

1. **Given** OKE cluster is running, **When** I check node resource utilization, **Then** CPU and memory usage are within expected limits (not over-provisioned)
2. **Given** Dapr is installed, **When** I deploy a test application with Dapr enabled, **Then** the application starts successfully with sidecar injection
3. **Given** cluster and Dapr are operational, **When** I test connectivity between pods, **Then** pod-to-pod communication works via Dapr service invocation
4. **Given** OKE cluster is provisioned, **When** I verify basic security configuration, **Then** RBAC is enabled, default security lists are reviewed and documented, and security assumptions are clearly stated
5. **Given** all components are verified, **When** I document the setup in README.md, **Then** the guide includes: Oracle Cloud account setup, OKE cluster creation steps, kubectl configuration, Dapr installation commands, verification procedures, security validation steps, and troubleshooting tips
6. **Given** the setup is documented, **When** a team member follows the guide, **Then** they can reproduce the environment successfully

---

### Edge Cases

- **What happens when the OKE cluster creation fails?**
  - Check Oracle Cloud quota limits (Always Free tier has specific limits: 4 OCPUs total, 24GB RAM total)
  - Verify region selection (some regions may have capacity constraints)
  - Ensure "Pay As You Go" upgrade is complete (Free tier cannot create OKE clusters)
  - Review error messages in OCI Console Events for specific failures

- **What happens when Dapr installation times out or fails?**
  - Check cluster connectivity (kubectl can reach API server)
  - Verify sufficient cluster resources (Dapr control plane requires ~500MB memory total)
  - Check for conflicting Dapr installations (`dapr uninstall -k` to clean up)
  - Review Dapr pods logs for specific errors (`kubectl logs -n dapr-system`)

- **What happens when kubectl cannot connect to the cluster?**
  - Verify kubeconfig file is correctly configured (check $HOME/.kube/config)
  - Ensure OCI CLI is authenticated (`oci setup config`)
  - Check cluster OCID is correct in kubeconfig command
  - Verify network connectivity to Oracle Cloud endpoints
  - Re-download kubeconfig if corrupted (`oci ce cluster create-kubeconfig --overwrite`)

- **What happens when OKE nodes fail to reach "Ready" status?**
  - Check node events (`kubectl describe node <node-name>`)
  - Verify subnet and security list configurations in OCI Console
  - Ensure worker nodes have internet access for pulling images
  - Check for resource exhaustion (disk space, memory)

- **What happens if we exceed Always Free tier limits?**
  - System will warn before exceeding limits
  - Configure budget alerts in OCI Console to monitor usage
  - Always Free resources are separate from trial credits ($300 for 30 days)
  - If limits exceeded, cluster creation will fail with quota error

- **What happens when x86/amd64 Docker images are deployed to ARM64 cluster nodes?** ⚠️ CRITICAL
  - Pods fail to start with "Exec format error" in container logs
  - This error appears AFTER deployment, making it confusing to debug
  - Symptom: `kubectl describe pod` shows CrashLoopBackOff or ImagePullBackOff status
  - Root cause: Binary incompatibility between x86 images and ARM64 processor architecture
  - Solution: Rebuild all Docker images for ARM64 using `docker buildx build --platform linux/arm64` or multi-arch builds with `--platform linux/amd64,linux/arm64`
  - Prevention: Verify image architecture before deployment (`docker manifest inspect <image>` to check supported platforms)
  - Dapr sidecar images are already multi-arch (supports both amd64 and arm64), so Dapr itself won't have this issue

- **What happens when multiple developers try to create OKE clusters in the same Oracle Cloud tenancy?**
  - Always Free tier quota is per-tenancy: 4 OCPUs and 24GB RAM total (exactly consumed by this Stage 1 cluster: 2 nodes × 2 OCPUs × 12GB)
  - No headroom for resource sharing; second cluster creation will fail with quota exceeded error
  - Solution: Each developer must use their own separate Oracle Cloud tenancy/account for learning purposes
  - Multi-developer team scenarios require paid tier with higher quotas or separate Always Free accounts
  - Documentation must clearly state this is a single-developer-per-tenancy setup for learning/portfolio projects

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provision an OKE cluster with exactly 2 worker nodes using VM.Standard.A1.Flex shape (ARM architecture)
- **FR-002**: Each worker node MUST be configured with 2 OCPUs and 12GB RAM (total cluster: 4 OCPUs, 24GB RAM within Always Free limits)
- **FR-003**: System MUST configure kubectl to connect to the OKE cluster using OIDC token authentication
- **FR-004**: System MUST install Dapr control plane version 1.12+ (latest stable) using Helm charts
- **FR-005**: Dapr MUST be deployed in High Availability mode with `--enable-ha=true` flag
- **FR-006**: Dapr control plane components (Placement, Operator, Sentry, Sidecar Injector) MUST run in a dedicated `dapr-system` namespace
- **FR-007**: System MUST verify all Dapr control plane pods reach "Running" status within 5 minutes of installation
- **FR-008**: System MUST enable automatic Dapr sidecar injection for pods with appropriate annotations
- **FR-009**: System MUST document the complete setup process in phase-5-cloud-deployment/README.md including Oracle Cloud account setup, cluster creation, kubectl configuration, Dapr installation, and the single-developer-per-tenancy constraint (Always Free tier quota is fully consumed by this cluster)
- **FR-010**: System MUST provide troubleshooting steps for common failures (cluster creation, kubectl connection, Dapr installation, quota exceeded errors)
- **FR-011**: OKE cluster MUST use the "Quick Create" workflow to automatically configure VCN, subnets, security lists, and load balancer
- **FR-012**: System MUST configure OCI CLI for authenticated access to Oracle Cloud resources
- **FR-013**: Dapr installation MUST include all core components required for Phase V: Pub/Sub, State Management, Bindings, Secrets, and Service Invocation capabilities
- **FR-014**: System MUST validate cluster health by checking: node status, pod health, resource allocation, and network connectivity
- **FR-015**: System MUST configure cluster access credentials with appropriate token expiration (default: 8 hours, renewable)
- **FR-016**: All Docker images deployed to the cluster MUST be built for ARM64 (aarch64) architecture to prevent "Exec format error" on ARM-based worker nodes
- **FR-017**: System MUST document the requirement for multi-architecture Docker builds using `docker buildx` or equivalent cross-platform build tools
- **FR-018**: System MUST save basic verification logs (console output from kubectl and dapr commands) to files for troubleshooting purposes, without implementing full structured logging or centralized collection
- **FR-019**: System MUST verify basic security configuration: RBAC is enabled on the cluster, default security lists allow only necessary traffic, and document security assumptions for the learning/development environment

### Key Entities *(infrastructure components)*

- **OKE Cluster**: Oracle Kubernetes Engine cluster resource with control plane (managed by Oracle) and worker nodes (managed by user). Key attributes: cluster OCID, Kubernetes version, node pool configuration, network settings (VCN, subnets)

- **Worker Node**: Compute instance running as Kubernetes node. Key attributes: shape (VM.Standard.A1.Flex), OCPU count (2), memory (12GB), availability domain, operating system (Oracle Linux)

- **Dapr Control Plane**: Distributed application runtime management layer. Key attributes: namespace (dapr-system), deployment mode (HA), component pods (Placement, Operator, Sentry, Sidecar Injector), version (1.12+)

- **Kubeconfig**: Configuration file for kubectl access. Key attributes: cluster endpoint, authentication method (OIDC token), user credentials, context name

- **OCI CLI Configuration**: Oracle Cloud Infrastructure command-line tool settings. Key attributes: user OCID, tenancy OCID, region, API key fingerprint, private key path

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: OKE cluster is provisioned and accessible via kubectl within 20 minutes of starting the creation process (15 minutes cluster provisioning + 5 minutes kubectl setup)

- **SC-002**: All cluster nodes report "Ready" status with correct resource allocation (2 nodes × 2 OCPUs × 12GB RAM each = 4 OCPUs, 24GB RAM total)

- **SC-003**: Dapr control plane components are installed and running in HA mode with 100% of pods in "Running" state within 5 minutes of installation command

- **SC-004**: Automatic Dapr sidecar injection works successfully on first test deployment (pod starts with daprd sidecar container)

- **SC-005**: Developer can execute all basic cluster operations (kubectl get nodes/pods/deployments, kubectl logs, kubectl describe) without authentication errors

- **SC-006**: Complete setup documentation is created and validated by having a team member successfully reproduce the environment following the written guide (100% success rate on reproduction)

- **SC-007**: All verification commands execute successfully showing healthy cluster state: node status check, Dapr status check, pod network connectivity test, resource utilization check

- **SC-008**: Zero cost incurred for cluster operation (all resources within Always Free tier limits, confirmed via OCI Cost Analysis dashboard showing $0.00 charges for compute/networking)

- **SC-009**: Basic security configuration is verified and documented: RBAC enabled check passes, default OCI security list rules are reviewed and understood, security assumptions are explicitly documented in README.md

## Assumptions

- Oracle Cloud account can be created with standard email verification (no special approval needed)
- Always Free tier resources (4 OCPUs ARM, 24GB RAM) are available in at least one Oracle Cloud region (us-ashburn-1, us-phoenix-1, or eu-frankfurt-1)
- Developer has local machine with Internet access and ability to install CLI tools (OCI CLI, kubectl, Helm, Dapr CLI)
- Developer is working on Linux, macOS, or Windows with WSL2 (all support required CLI tools)
- Kubernetes version 1.26+ is available on OKE (required for Dapr 1.12+ compatibility)
- Dapr 1.12 or later is stable and production-ready (current stable version as of Jan 2026)
- Developer has completed Phase IV (Local Kubernetes Deployment with Minikube) and is familiar with Kubernetes concepts
- This is a single-developer-per-tenancy setup for learning/portfolio purposes; Always Free tier quota (4 OCPUs, 24GB RAM) is fully consumed by this cluster, leaving no headroom for additional clusters or multi-developer scenarios
- Developer has administrative access to Oracle Cloud account (can create clusters, configure IAM)
- Network connectivity to Oracle Cloud endpoints is not blocked by corporate firewalls
- Standard OKE "Quick Create" workflow produces a secure default configuration suitable for learning/development (not production-hardened)

## Dependencies

- **External**: Oracle Cloud Infrastructure (OCI) service availability and Always Free tier program continuation
- **External**: Dapr project stability and compatibility with Kubernetes 1.26+
- **Internal**: Completed Phase IV with working knowledge of Kubernetes, kubectl, and Helm
- **Internal**: Constitution v1.7.0 specifications for Phase V implementation strategy
- **Internal**: IMPLEMENTATION_GUIDE.md in phase-5-cloud-deployment/ directory for detailed technical guidance
- **Tool**: OCI CLI installed and configured (bash script for Linux/macOS, manual installation for Windows)
- **Tool**: kubectl installed (version 1.26+ to match Kubernetes server version)
- **Tool**: Helm 3.x installed (for Dapr installation)
- **Tool**: Dapr CLI installed (version 1.12+)
- **Tool**: Docker with buildx plugin (for multi-architecture image builds targeting ARM64)

## Out of Scope

- **Production-grade security hardening**: Network policies, pod security policies, secrets encryption at rest (addressed in later stages)
- **Multi-region or multi-cluster setup**: Single cluster in one region is sufficient for Phase V
- **Custom Kubernetes configurations**: Using OKE "Quick Create" defaults; custom CNI, CSI, or ingress controllers not configured
- **Dapr component configuration**: Pub/Sub, State, Bindings, Secrets components are installed but not configured (Stage 2: Redpanda Pub/Sub)
- **Application deployment**: No Todo Chatbot application deployed yet (deferred to later stages after infrastructure is fully configured)
- **Monitoring and observability setup**: Prometheus, Grafana, OpenTelemetry configured in Stage 5 (Observability)
- **CI/CD pipeline setup**: GitHub Actions workflows configured in Stage 4 (CI/CD)
- **Cost optimization beyond Always Free tier**: No analysis of paid tier pricing or cost reduction strategies
- **Disaster recovery or backup procedures**: Cluster recreation from documentation is sufficient for Phase V learning objectives
- **Load balancer or ingress configuration**: Configured when deploying applications in later stages
- **Custom domain or DNS setup**: Using cluster IP addresses; custom domains configured when needed
- **SSL/TLS certificate management**: Configured with application ingress in later stages
- **Database migration or data seeding**: Neon PostgreSQL remains external and unchanged from Phase IV

## Notes

- **⚠️ CRITICAL - ARM64 Architecture**: OKE Always Free tier nodes are ARM64 (aarch64), NOT x86/amd64. All Docker images must be built for ARM64 or as multi-architecture builds. Deploying x86 images will result in "Exec format error" which is difficult to debug. Use `docker buildx build --platform linux/arm64` or `--platform linux/amd64,linux/arm64` for all custom images. Verify with `docker manifest inspect <image>` before deploying.
- This is Stage 1 of a 5-stage Phase V implementation (per constitution branch sequence: 010-oke-dapr-setup → 011-redpanda-pubsub → 012-dapr-advanced-features → 013-github-actions-cicd → 014-observability)
- Always Free tier is perpetual (no expiration) unlike the $300 trial credits (30 days)
- OKE control plane is fully managed by Oracle (no cost, no user access needed)
- Worker nodes consume the Always Free tier compute allocation (4 OCPUs, 24GB RAM total)
- Dapr in HA mode typically deploys 3 replicas per component; verify cluster resources can support this (~1.5GB total memory for Dapr control plane)
- Dapr CLI is optional for installation (can use Helm directly) but recommended for easier management (`dapr status -k`, `dapr dashboard -k`)
- Kubeconfig token-based authentication expires after 8 hours by default; re-run `oci ce cluster create-kubeconfig` to refresh
- "Quick Create" workflow is beginner-friendly but less customizable than "Custom Create"; sufficient for Phase V objectives
- All infrastructure-as-code (Terraform) is optional for Stage 1; manual Console setup is acceptable for learning purposes
