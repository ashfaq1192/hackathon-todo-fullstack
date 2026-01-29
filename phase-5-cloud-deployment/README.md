# Phase V - Oracle Cloud Deployment (Stage 1: OKE & Dapr Setup)

**Branch**: `010-oke-dapr-setup`
**Created**: 2026-01-25
**Status**: 🚧 In Progress - Prerequisites Installation

---

## Overview

Stage 1 establishes the foundation infrastructure for Phase V Advanced Cloud Deployment:
- Oracle Kubernetes Engine (OKE) cluster on Always Free tier
- Dapr distributed runtime in High Availability mode
- kubectl configured for local cluster access
- Docker buildx for ARM64 image builds
- Zero ongoing costs (100% within Always Free limits)

**Estimated Time**: 45-60 minutes (including cluster provisioning)

---

## Current Status

### ✅ Completed Steps

- [x] Oracle Cloud account created
- [x] Project directory structure created (`phase-5-cloud-deployment/`, `logs/`, `scripts/`)
- [x] Prerequisites verification script created
- [x] Installation guide documented

### 🚧 In Progress

- [ ] Install missing CLI tools (OCI CLI, Dapr CLI, Docker WSL 2 integration)
- [ ] Configure OCI CLI authentication
- [ ] Upgrade Oracle account to "Pay As You Go"

### ⏳ Pending

- [ ] Create OKE cluster
- [ ] Configure kubectl access
- [ ] Install Dapr control plane
- [ ] Verify complete setup

---

## Quick Start

### Step 1: Install Prerequisites (Current Step)

You have kubectl and Helm installed. Still need:

1. **OCI CLI** (Oracle Cloud CLI)
   ```bash
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
   ```

2. **Dapr CLI**
   ```bash
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
   ```

3. **Docker Desktop WSL 2 Integration**
   - Open Docker Desktop on Windows
   - Settings → Resources → WSL Integration
   - Enable integration with your WSL distro
   - Apply & Restart

**Detailed instructions**: See [SETUP_PREREQUISITES.md](./SETUP_PREREQUISITES.md)

**Verify all tools**:
```bash
./phase-5-cloud-deployment/scripts/verify-prerequisites.sh
```

---

### Step 2: Configure OCI CLI (After Installation)

```bash
# Run interactive setup
oci setup config
```

**You'll need from OCI Console**:
1. User OCID (Profile → User Settings → copy OCID)
2. Tenancy OCID (Profile → Tenancy → copy OCID)
3. Region (e.g., us-ashburn-1)

**Post-configuration**:
- Upload public key to OCI Console → User Settings → API Keys
- Verify: `oci iam region list`

---

### Step 3: Follow Complete Setup Guide

Once prerequisites are installed, follow the comprehensive step-by-step guide:

📖 **[specs/010-oke-dapr-setup/quickstart.md](../specs/010-oke-dapr-setup/quickstart.md)**

This guide covers:
- Oracle Cloud account upgrade to "Pay As You Go"
- Budget alert configuration
- OKE cluster creation
- kubectl configuration
- Docker buildx setup
- Dapr installation
- Complete verification

---

## Key Resources

### Documentation

- **Specification**: [specs/010-oke-dapr-setup/spec.md](../specs/010-oke-dapr-setup/spec.md)
- **Implementation Plan**: [specs/010-oke-dapr-setup/plan.md](../specs/010-oke-dapr-setup/plan.md)
- **Tasks Breakdown**: [specs/010-oke-dapr-setup/tasks.md](../specs/010-oke-dapr-setup/tasks.md)
- **Quickstart Guide**: [specs/010-oke-dapr-setup/quickstart.md](../specs/010-oke-dapr-setup/quickstart.md)
- **CLI Commands Reference**: [specs/010-oke-dapr-setup/contracts/cli-commands.md](../specs/010-oke-dapr-setup/contracts/cli-commands.md)
- **Verification Checklist**: [specs/010-oke-dapr-setup/contracts/verification-checklist.md](../specs/010-oke-dapr-setup/contracts/verification-checklist.md)

### Scripts

- **Prerequisites Verification**: `./scripts/verify-prerequisites.sh`
- **Stage 1 Verification**: (Will be created after cluster setup)

### Logs

Verification outputs will be saved to `./logs/`:
- `cluster-nodes.txt` - Node status
- `dapr-status.txt` - Dapr control plane status
- `resource-utilization.txt` - CPU/memory usage
- Additional verification logs as setup progresses

---

## Architecture

### Infrastructure Components

```
Oracle Cloud (Always Free Tier)
└─ OKE Cluster (todo-chatbot-cluster)
   ├─ Control Plane (Managed by Oracle)
   │  └─ Kubernetes API Server (v1.28)
   │
   └─ Worker Nodes (2 nodes)
      ├─ Node 1: VM.Standard.A1.Flex (ARM64)
      │  ├─ 2 vCPUs
      │  └─ 12 GB RAM
      │
      └─ Node 2: VM.Standard.A1.Flex (ARM64)
         ├─ 2 vCPUs
         └─ 12 GB RAM

Dapr Control Plane (HA Mode)
└─ dapr-system namespace
   ├─ dapr-operator (3 replicas)
   ├─ dapr-sidecar-injector (3 replicas)
   ├─ dapr-sentry (3 replicas)
   └─ dapr-placement-server (3 replicas)
```

### Total Resources

- **Compute**: 4 vCPUs (100% of Always Free quota)
- **Memory**: 24 GB (100% of Always Free quota)
- **Architecture**: ARM64/aarch64
- **Cost**: $0.00 perpetual (Always Free tier)

---

## Success Criteria

This stage is complete when:

- ✅ OKE cluster status = ACTIVE in OCI Console
- ✅ `kubectl get nodes` returns 2 nodes in Ready status
- ✅ Both nodes show ARM64 architecture
- ✅ `dapr status -k` shows all 4 components HEALTHY with 3 replicas each
- ✅ Test deployment successfully injects Dapr sidecar
- ✅ All verification commands execute without errors
- ✅ OCI Cost Analysis shows $0.00 charges
- ✅ Complete documentation and logs captured

---

## Important Notes

### ⚠️ ARM64 Architecture

**CRITICAL**: OKE Always Free tier nodes are ARM64, NOT x86/amd64.

All Docker images MUST be built for ARM64:
```bash
docker buildx build --platform linux/arm64 \
  -t <image>:arm64 \
  -f <Dockerfile> \
  --load <context>
```

Deploying x86 images will cause **"Exec format error"** after deployment.

### 💰 Cost Monitoring

- Always Free resources are perpetual (no expiration)
- Budget alerts configured at $10 threshold
- Regular checks: OCI Console → Billing & Cost Management
- Expected cost: **$0.00**

### 🔑 kubectl Token Expiration

- OIDC tokens expire after 8 hours
- Refresh command:
  ```bash
  oci ce cluster create-kubeconfig \
    --cluster-id <ocid> \
    --file ~/.kube/config \
    --region <region> \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT \
    --overwrite
  ```

### 👤 Single-Developer Constraint

- Always Free quota: 4 vCPUs, 24 GB RAM total
- This cluster consumes 100% of quota
- Multiple developers require separate Oracle Cloud tenancies

---

## Troubleshooting

### Common Issues

**"Cluster creation failed - quota exceeded"**
- Check: Governance → Limits & Quotas → Compute
- Solution: Delete existing compute resources or create new account

**"kubectl: connection refused"**
- Cause: Token expired (8-hour limit)
- Solution: Re-run `oci ce cluster create-kubeconfig` with `--overwrite`

**"Docker exec format error"**
- Cause: x86 image on ARM64 node
- Solution: Rebuild with `--platform linux/arm64`

**"Dapr pods CrashLoopBackOff"**
- Check: `kubectl top nodes` (resource utilization)
- Solution: Verify sufficient memory, check pod logs

**Detailed troubleshooting**: See quickstart.md section "Common Issues & Solutions"

---

## Next Steps After Stage 1

Once this stage is complete:

1. **Verify all success criteria** (verification-checklist.md)
2. **Capture logs** to `./logs/` directory
3. **Commit changes** to Git
4. **Proceed to Stage 2**: Redpanda Cloud & Dapr Pub/Sub Integration

---

## External References

- **Oracle Cloud OKE**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Always Free Tier**: https://www.oracle.com/cloud/free/
- **Dapr Documentation**: https://docs.dapr.io/
- **Dapr on Kubernetes**: https://docs.dapr.io/operations/hosting/kubernetes/
- **Docker Buildx**: https://docs.docker.com/build/buildx/

---

**Last Updated**: 2026-01-25
**Next Review**: After prerequisites installation complete
