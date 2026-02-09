# Research Document: OKE Cluster & Basic Dapr Setup

**Feature**: 010-oke-dapr-setup
**Date**: 2026-01-25
**Purpose**: Resolve technical unknowns and document technology choices for Stage 1 of Phase V

---

## Decision 1: Oracle Cloud Account Setup Process

**Decision**: Use "Pay As You Go" upgrade to enable OKE cluster creation while retaining Always Free resources

**Rationale**:
- Oracle Cloud Free Tier alone cannot create OKE clusters (restricted to compute instances only)
- "Pay As You Go" upgrade unlocks OKE service while preserving perpetual Always Free resources
- Always Free resources (4 OCPUs ARM, 24GB RAM) remain free indefinitely post-upgrade
- $300 trial credits (30 days) provided separately for paid services
- No charges if staying within Always Free limits

**Alternatives Considered**:
- Free Tier only: Rejected - cannot provision OKE clusters
- Paid tier immediately: Rejected - unnecessary cost for learning project
- Third-party Kubernetes (GKE, EKS free tiers): Rejected - Hackathon specifies Oracle Cloud

**Implementation**:
1. Sign up at cloud.oracle.com with email verification
2. Complete identity verification (credit card for validation, no charge)
3. Upgrade to "Pay As You Go" in Console → Billing
4. Configure budget alerts to prevent accidental charges

**References**:
- Oracle Cloud Free Tier: https://www.oracle.com/cloud/free/
- OKE Always Free limitations: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

---

## Decision 2: OKE Cluster Configuration Strategy

**Decision**: Use "Quick Create" workflow with VM.Standard.A1.Flex shape (2 nodes × 2 OCPUs × 12GB RAM)

**Rationale**:
- Quick Create automates VCN, subnet, security list, and load balancer setup
- VM.Standard.A1.Flex is ARM64 architecture (Always Free eligible)
- 2 nodes × 2 OCPUs × 12GB RAM = 4 OCPUs, 24GB RAM (exactly matches quota)
- Beginner-friendly for first-time OKE users
- Sufficient resources for Dapr HA mode (~1.5GB memory) + sample applications

**Alternatives Considered**:
- Custom Create: Rejected - too complex for learning objectives, unnecessary for Stage 1
- Single node cluster: Rejected - insufficient for HA Dapr testing
- 3+ nodes: Rejected - exceeds Always Free quota
- x86/amd64 shapes: Rejected - not eligible for Always Free tier

**Configuration Details**:
- Kubernetes Version: 1.26+ (latest supported by OKE)
- Node Pool: 2 nodes in different availability domains (if available in region)
- Network: Public VCN with public/private subnets
- Load Balancer: Flexible shape (Always Free eligible)
- Region: us-ashburn-1 or us-phoenix-1 (confirmed Always Free availability)

**Cluster Sizing Validation**:
- Dapr control plane HA: ~1.5GB RAM total
- System pods (CoreDNS, kube-proxy): ~512MB
- Remaining for applications: ~22GB
- Headroom: Sufficient for sample deployments

---

## Decision 3: ARM64 Docker Image Build Strategy

**Decision**: Use Docker Buildx for multi-architecture builds (amd64 + arm64)

**Rationale**:
- OKE Always Free nodes are ARM64, not x86/amd64
- Deploying x86 images causes "Exec format error" after deployment (difficult to debug)
- Multi-arch builds support both local development (x86) and OKE deployment (ARM64)
- Docker Buildx is standard tool, widely supported
- Official base images (python:3.13-slim, node:22-alpine) are already multi-arch

**Alternatives Considered**:
- ARM64-only builds: Rejected - breaks local x86 development workflow
- Build on ARM64 machine: Rejected - requires separate ARM hardware
- QEMU emulation: Rejected - slower build times, less reliable
- Separate Dockerfiles per architecture: Rejected - maintenance overhead

**Build Commands**:
```bash
# Create buildx builder (one-time setup)
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build for ARM64 only (OKE deployment)
docker buildx build --platform linux/arm64 \
  -t todo-backend:v2-arm64 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --load \
  phase-3-chatbot/backend

# Build for both architectures (production best practice)
docker buildx build --platform linux/amd64,linux/arm64 \
  -t <registry>/todo-backend:v2 \
  -f phase-4-k8s/docker/backend/Dockerfile \
  --push \
  phase-3-chatbot/backend
```

**Verification**:
```bash
# Check supported platforms
docker manifest inspect <image> | grep -A 5 "platform"

# Expected output:
# "architecture": "arm64", "os": "linux"
# "architecture": "amd64", "os": "linux"
```

**Impact on Existing Dockerfiles**:
- Backend (Python): python:3.13-slim is multi-arch ✅
- Frontend (Node.js): node:22-alpine is multi-arch ✅
- No changes needed to Dockerfile content, only build process

---

## Decision 4: Dapr Installation Method & HA Configuration

**Decision**: Use Helm chart installation with `--enable-ha=true` for production-ready HA mode

**Rationale**:
- Helm provides declarative configuration, version control, easy upgrades/rollbacks
- `dapr init -k --enable-ha=true` is simpler but less flexible for customization
- HA mode ensures fault tolerance with 3 replicas per control plane component
- Helm chart allows fine-grained resource limits and scheduling constraints
- Aligns with Phase V GitOps patterns (Helm charts as source of truth)

**Alternatives Considered**:
- Dapr CLI `init -k`: Rejected - harder to customize, less GitOps-friendly
- Standard mode (no HA): Rejected - not production-ready for Phase V objectives
- Operator-based installation: Rejected - overkill for Stage 1 learning

**Dapr Components (HA Mode)**:
- Placement Service: 3 replicas (state distribution)
- Operator: 3 replicas (component management)
- Sentry: 3 replicas (certificate authority for mTLS)
- Sidecar Injector: 3 replicas (webhook for pod injection)

**Helm Installation**:
```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr control plane in HA mode
helm install dapr dapr/dapr \
  --version=1.14 \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --wait

# Verify installation
kubectl get pods -n dapr-system
dapr status -k
```

**Resource Requirements**:
- Total memory for Dapr HA: ~1.5GB (validated against cluster capacity)
- CPU requests: minimal (~0.1 core per component)
- Fits comfortably within Always Free tier allocation

---

## Decision 5: kubectl Configuration & Authentication

**Decision**: Use OCI CLI to generate kubeconfig with OIDC token authentication (8-hour expiration)

**Rationale**:
- OIDC tokens are short-lived, more secure than static certificates
- OCI CLI automates kubeconfig generation with correct cluster endpoint
- Standard approach for OKE access, documented in Oracle docs
- Token refresh requires re-running command (acceptable for learning environment)

**Alternatives Considered**:
- Manual kubeconfig creation: Rejected - error-prone, requires cluster OCID/endpoint lookup
- Long-lived certificates: Rejected - less secure, not OKE default
- Cloud Shell only: Rejected - limits local development workflow

**Setup Process**:
```bash
# Install OCI CLI (Linux/macOS)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure OCI CLI with user credentials
oci setup config
# Prompts for: User OCID, Tenancy OCID, Region, API Key

# Generate kubeconfig for cluster
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Test connectivity
kubectl get nodes
```

**Token Refresh** (every 8 hours):
```bash
# Simply re-run the create-kubeconfig command with --overwrite
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT \
  --overwrite
```

---

## Decision 6: Basic Security Validation Strategy

**Decision**: Verify RBAC enabled, review default security lists, document security assumptions (per FR-019)

**Rationale**:
- OKE "Quick Create" enables RBAC by default (verify, don't assume)
- Default security lists allow necessary traffic but should be reviewed
- Security assumptions must be documented for stakeholders
- Production-grade hardening is out-of-scope (Stage 1 focus: infrastructure foundation)
- Balances learning objectives with responsible cloud practices

**Validation Checks**:
1. **RBAC Verification**:
   ```bash
   # Check RBAC is enabled
   kubectl api-resources | grep rbac
   kubectl get clusterroles

   # Verify current user has appropriate permissions
   kubectl auth can-i create deployments
   kubectl auth can-i create pods
   ```

2. **Security List Review** (OCI Console):
   - Ingress rules: Only required ports open (443 for ingress, 6443 for API server)
   - Egress rules: Allow outbound traffic for image pulls, package updates
   - Document any overly permissive rules (e.g., 0.0.0.0/0 on all ports)

3. **Security Assumptions Documentation**:
   - This is a learning/portfolio environment, not production
   - Network policies NOT configured (Stage 1 scope limit)
   - Pod security standards NOT enforced (Stage 1 scope limit)
   - Secrets stored in Kubernetes Secrets (basic, not encrypted at rest yet)
   - Public ingress for demo purposes (acceptable for Always Free tier)
   - No compliance requirements (GDPR, HIPAA, etc.)

**Validation Output**:
- Create `security-validation.md` in specs/010-oke-dapr-setup/
- Document findings: RBAC status, security list rules, assumptions
- Include in README.md setup guide

---

## Decision 7: Logging & Verification Strategy

**Decision**: Save kubectl/dapr command outputs to files for troubleshooting (per FR-018)

**Rationale**:
- Full observability stack comes in Stage 5 (OpenTelemetry + Grafana Cloud)
- Stage 1 needs basic logs for debugging during setup
- File-based logs are simple, version-controllable, no infrastructure needed
- Satisfies success criteria SC-007 (verification commands execute successfully)

**Logging Approach**:
```bash
# Create logs directory
mkdir -p phase-5-cloud-deployment/logs/

# Capture cluster setup logs
kubectl get nodes > logs/cluster-nodes.txt
kubectl get pods --all-namespaces > logs/all-pods.txt
kubectl describe nodes > logs/nodes-detailed.txt

# Capture Dapr installation logs
dapr status -k > logs/dapr-status.txt
kubectl get pods -n dapr-system > logs/dapr-pods.txt
kubectl logs -n dapr-system -l app=dapr-operator > logs/dapr-operator.log

# Capture health check outputs
kubectl get --raw /healthz > logs/cluster-health.txt
kubectl top nodes > logs/resource-utilization.txt
```

**Log Organization**:
```text
phase-5-cloud-deployment/
└── logs/
    ├── cluster-nodes.txt         # Node status
    ├── all-pods.txt               # All pods across namespaces
    ├── nodes-detailed.txt         # Detailed node info
    ├── dapr-status.txt            # Dapr control plane status
    ├── dapr-pods.txt              # Dapr system pods
    ├── dapr-operator.log          # Dapr operator logs
    ├── cluster-health.txt         # Kubernetes health endpoint
    └── resource-utilization.txt   # CPU/memory usage
```

**Usage in Documentation**:
- Include log outputs in README troubleshooting section
- Reference logs in setup verification steps
- Commit representative logs to Git for reproducibility

---

## Best Practices Summary

**Oracle Cloud Configuration**:
- Always use budget alerts to prevent unexpected charges
- Bookmark OCI Console → Governance → Limits & Quotas for quota monitoring
- Enable MFA on Oracle Cloud account for security
- Use separate compartments for different projects (optional for Always Free)

**Kubernetes Operations**:
- Always verify cluster connectivity before operations: `kubectl cluster-info`
- Use `--dry-run=client -o yaml` to preview manifests before applying
- Label resources consistently: `app.kubernetes.io/name`, `app.kubernetes.io/instance`
- Check pod events when troubleshooting: `kubectl describe pod <name>`

**Dapr Best Practices**:
- Use `dapr dashboard -k` to visualize control plane (localhost:8080)
- Test sidecar injection with simple deployment before complex apps
- Monitor Dapr sidecar logs: `kubectl logs <pod> -c daprd`
- Reference official docs: https://docs.dapr.io/operations/hosting/kubernetes/

**Docker ARM64 Workflow**:
- Always build multi-arch images from the start (avoid rework later)
- Verify image architecture BEFORE pushing to registry
- Test ARM64 images on actual ARM hardware or OKE (QEMU emulation not reliable)
- Document platform requirements in Dockerfile comments

**Documentation Standards**:
- Keep README.md updated with each stage completion
- Include "Prerequisites", "Setup Steps", "Verification", "Troubleshooting" sections
- Capture screenshots of OCI Console steps for future reference
- Document all environment variables and their purposes

---

## References

**Oracle Cloud**:
- OKE Documentation: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- Always Free Services: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- OCI CLI Installation: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm

**Dapr**:
- Dapr on Kubernetes: https://docs.dapr.io/operations/hosting/kubernetes/
- Dapr HA Deployment: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-production/
- Helm Chart Configuration: https://github.com/dapr/dapr/tree/master/charts/dapr

**Docker & ARM64**:
- Buildx Documentation: https://docs.docker.com/build/buildx/
- Multi-platform builds: https://docs.docker.com/build/building/multi-platform/
- Official Images Platform Support: https://github.com/docker-library/official-images

**Kubernetes**:
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- RBAC Authorization: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Exceed Always Free quota | Medium | High (unexpected charges) | Configure budget alerts, monitor OCI Cost Analysis dashboard daily |
| Token expiration during work | High | Low (interruption) | Document refresh command in README, set calendar reminder for 7-hour mark |
| ARM64 image compatibility issues | Medium | Medium (deployment failure) | Test images immediately after build, verify with docker manifest inspect |
| OKE cluster creation fails | Low | Medium (timeline delay) | Verify quota before creation, try alternate region if first fails |
| Dapr HA resource exhaustion | Low | Medium (pods crash) | Monitor kubectl top nodes/pods during installation, reduce replicas if needed |
| Security misconfiguration | Low | High (exposure) | Follow security validation checklist, document all assumptions |

---

**Research Complete**: All technical unknowns resolved. Ready for Phase 1 (Data Model & Contracts).
