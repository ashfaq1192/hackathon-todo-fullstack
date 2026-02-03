# Phase V - Advanced Cloud Deployment (Oracle Kubernetes Engine)

**Branch**: `main`
**Last Updated**: 2026-02-03
**Status**: ✅ Ready for Deployment

---

## Overview

Phase V deploys the Todo Chatbot application to Oracle Kubernetes Engine (OKE) with:
- **OKE Enhanced Cluster** (required - Basic Cluster API is non-functional)
- **Docker Hub** images for easy deployment
- **NGINX Ingress Controller** for external access
- **Neon PostgreSQL** as external database
- **Gemini AI** for chatbot functionality

**Estimated Cost**: ~$3/day (delete cluster after demo to minimize costs)

---

## Quick Start

### Option 1: Complete Beginner Guide

📖 **[oracle_guide.md](./oracle_guide.md)** - Step-by-step guide from account creation to deployment

### Option 2: Experienced Users

If you're familiar with Kubernetes:

```bash
# 1. Create OKE Enhanced Cluster via OCI Console
# 2. Configure kubectl (use OCI Cloud Shell)
# 3. Install Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# 4. Create secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="your-neon-url" \
  --from-literal=GEMINI_API_KEY="your-key" \
  --from-literal=BETTER_AUTH_SECRET="your-secret" \
  --from-literal=JWT_SECRET_KEY="your-jwt-secret"

# 5. Deploy application
kubectl apply -f k8s/

# 6. Get external IP
kubectl get svc -n ingress-nginx
```

---

## Docker Hub Images

All images are built for `linux/amd64` and publicly available:

| Image | Tag | Size | Description |
|-------|-----|------|-------------|
| `ashfaq1192/todo-backend` | v2 | ~600MB | FastAPI + MCP Tools + Gemini |
| `ashfaq1192/todo-frontend` | v3 | ~350MB | Next.js + Better Auth |
| `ashfaq1192/todo-audit` | v2 | ~200MB | Audit logging service |
| `ashfaq1192/todo-notification` | v2 | ~200MB | Notification service |
| `ashfaq1192/todo-recurring` | v2 | ~200MB | Recurring task service |

### Pull Images

```bash
docker pull ashfaq1192/todo-backend:v2
docker pull ashfaq1192/todo-frontend:v3
```

---

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         Oracle Cloud (OKE)              │
                    │                                         │
┌──────────┐        │  ┌─────────────────────────────────┐   │
│  Users   │───────▶│  │      NGINX Ingress Controller   │   │
└──────────┘        │  │         (LoadBalancer)          │   │
                    │  └──────────────┬──────────────────┘   │
                    │                 │                       │
                    │    ┌────────────┴────────────┐         │
                    │    │                         │         │
                    │    ▼                         ▼         │
                    │  ┌───────────┐       ┌─────────────┐   │
                    │  │  Backend  │       │  Frontend   │   │
                    │  │  (2 pods) │◀─────▶│  (2 pods)   │   │
                    │  │  FastAPI  │       │   Next.js   │   │
                    │  └─────┬─────┘       └─────────────┘   │
                    │        │                               │
                    └────────┼───────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Neon PostgreSQL │
                    │  (External DB)   │
                    └─────────────────┘
```

---

## Important Notes

### ⚠️ Enhanced Cluster Required

**CRITICAL**: You MUST create an **Enhanced Cluster**, not a Basic Cluster.

- Basic Cluster API is non-functional (returns errors)
- Enhanced Cluster costs ~$3/day
- **Strategy**: Deploy → Demo → Delete within 24 hours

### 💰 Cost Management

| Resource | Daily Cost |
|----------|------------|
| OKE Enhanced Control Plane | ~$2.40 |
| Worker Nodes (2x VM.Standard.E4.Flex) | ~$0.50 |
| Load Balancer | ~$0.10 |
| **Total** | **~$3.00/day** |

**Recommendation**: Delete cluster immediately after recording demo video.

### 🏗️ Architecture

- **Platform**: `linux/amd64` (x86_64)
- **Node Shape**: VM.Standard.E4.Flex (1 OCPU, 8GB RAM each)
- **Compatible with**: Local Docker, Minikube, and OKE

---

## Directory Structure

```
phase-5-cloud-deployment/
├── README.md                    # This file
├── oracle_guide.md              # Complete beginner deployment guide
├── IMPLEMENTATION_GUIDE.md      # Detailed implementation reference
├── SETUP_PREREQUISITES.md       # Prerequisites installation
├── NEXT_STEPS.md               # Future enhancements
├── k8s/                        # Kubernetes manifests
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   └── secrets.yaml (template)
├── dapr/                       # Dapr components (future)
│   └── components/
├── scripts/                    # Deployment scripts
│   └── verify-prerequisites.sh
└── docs.md                     # Additional documentation
```

---

## Local Testing (Minikube)

Before deploying to OKE, test locally with Minikube:

```bash
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Enable Ingress
minikube addons enable ingress

# Deploy using Helm
cd phase-4-k8s
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-minikube.yaml

# Access via port-forward
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Open http://localhost:3000
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Oracle Cloud account created
- [ ] Docker Hub images verified
- [ ] Environment variables ready (DATABASE_URL, GEMINI_API_KEY, etc.)

### Deployment
- [ ] OKE Enhanced Cluster created (~15 min)
- [ ] kubectl configured via Cloud Shell
- [ ] NGINX Ingress Controller installed
- [ ] Kubernetes secrets created
- [ ] Application deployed
- [ ] External IP obtained

### Verification
- [ ] Health endpoint responds: `curl http://<IP>/health`
- [ ] Frontend loads in browser
- [ ] User can sign up and log in
- [ ] Tasks can be created
- [ ] Chatbot responds to queries

### Post-Demo Cleanup
- [ ] Delete Kubernetes resources
- [ ] Delete OKE cluster
- [ ] Verify no resources remain (Compute, Load Balancers, Block Storage)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Pods in "Pending" | Check node resources: `kubectl describe nodes` |
| ImagePullBackOff | Verify Docker Hub images are public |
| 502 Bad Gateway | Check pod logs: `kubectl logs deploy/todo-backend` |
| CORS errors | Verify FRONTEND_URL matches access URL |
| Database connection failed | Check DATABASE_URL and Neon IP allowlist |

**Full troubleshooting guide**: See [oracle_guide.md](./oracle_guide.md#12-troubleshooting)

---

## Related Documentation

- **Phase IV (Local K8s)**: [../phase-4-k8s/README.md](../phase-4-k8s/README.md)
- **Phase III (Chatbot)**: [../phase-3-chatbot/README.md](../phase-3-chatbot/README.md)
- **Hackathon Requirements**: [../Hackathon II - Todo Spec-Driven Development.pdf](../Hackathon%20II%20-%20Todo%20Spec-Driven%20Development.pdf)
- **Project Constitution**: [../.specify/memory/constitution.md](../.specify/memory/constitution.md)

---

## External Resources

- [Oracle OKE Documentation](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

---

**Maintained by**: AI-Assisted Development (Claude Code)
**Last Updated**: 2026-02-03
