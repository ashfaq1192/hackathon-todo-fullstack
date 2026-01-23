# Quickstart: Local Kubernetes Deployment

**Feature**: 008-local-k8s-deployment
**Date**: 2026-01-22

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop 4.53+ (or Docker Engine)
- [ ] Minikube installed
- [ ] Helm 3.x installed
- [ ] kubectl installed
- [ ] Phase III chatbot code in `phase-3-chatbot/`
- [ ] Environment variables configured

## Step 1: Build Docker Images

```bash
# Navigate to project root
cd /mnt/e/projects/hackathon-todo-fullstack

# Build backend image
docker build \
  -t todo-backend:latest \
  -f phase-4-k8s/docker/backend/Dockerfile \
  phase-3-chatbot/backend

# Build frontend image
docker build \
  -t todo-frontend:latest \
  -f phase-4-k8s/docker/frontend/Dockerfile \
  phase-3-chatbot/frontend

# Verify images
docker images | grep todo
```

**Expected Output**:
```
todo-frontend   latest   abc123   <5 min ago   <500MB
todo-backend    latest   def456   <5 min ago   <500MB
```

## Step 2: Start Minikube

```bash
# Start Minikube with recommended settings
minikube start --driver=docker --memory=4096 --cpus=2

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
Kubernetes control plane is running at https://...
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.x
```

## Step 3: Load Images into Minikube

```bash
# Load local images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify images are loaded
minikube image list | grep todo
```

## Step 4: Configure Secrets

Create `phase-4-k8s/helm/todo-chatbot/values-minikube.yaml` with your secrets:

```yaml
backend:
  env:
    DATABASE_URL: "postgresql://user:pass@host/db"
    OPENAI_API_KEY: "sk-your-key"
    BETTER_AUTH_SECRET: "your-secret"

frontend:
  env:
    NEXT_PUBLIC_BACKEND_URL: "http://todo.local/api"
```

## Step 5: Deploy with Helm

```bash
# Validate chart
helm lint phase-4-k8s/helm/todo-chatbot

# Install the application
helm install todo-chatbot phase-4-k8s/helm/todo-chatbot \
  -f phase-4-k8s/helm/todo-chatbot/values-minikube.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/instance=todo-chatbot \
  --timeout=120s

# Check status
kubectl get pods
kubectl get services
kubectl get ingress
```

**Expected Output**:
```
NAME                                READY   STATUS    RESTARTS   AGE
todo-chatbot-backend-xxx            1/1     Running   0          1m
todo-chatbot-frontend-xxx           1/1     Running   0          1m
```

## Step 6: Configure Local DNS

```bash
# Get Minikube IP
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

## Step 7: Access Application

Open browser and navigate to: **http://todo.local**

Or use Minikube tunnel:
```bash
minikube tunnel
# Then access http://localhost
```

## Verification Checklist

- [ ] Backend pod is Running and Ready (1/1)
- [ ] Frontend pod is Running and Ready (1/1)
- [ ] Both services show endpoints
- [ ] Ingress shows ADDRESS
- [ ] http://todo.local loads the chatbot UI
- [ ] Chat message "Add task test" creates a task
- [ ] Tasks persist after page refresh

## Troubleshooting

### Pods stuck in Pending

```bash
kubectl describe pod <pod-name>
# Check for resource constraints or image pull issues
```

### Image pull errors

```bash
# Verify images are loaded
minikube image list | grep todo

# Re-load if needed
minikube image load todo-backend:latest
```

### Ingress not working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Verify ingress resource
kubectl describe ingress todo-chatbot
```

### Database connection issues

```bash
# Check backend logs
kubectl logs -l app=backend

# Verify secret
kubectl get secret todo-chatbot-secrets -o yaml
```

## Cleanup

```bash
# Remove Helm release
helm uninstall todo-chatbot

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete

# Remove Docker images (optional)
docker rmi todo-backend:latest todo-frontend:latest
```

## Using AI DevOps Tools

### kubectl-ai

```bash
# Install
kubectl krew install ai

# Check cluster status
kubectl ai "what pods are running"

# Diagnose issues
kubectl ai "why is the backend pod failing"

# Scale application
kubectl ai "scale frontend to 2 replicas"
```

### Docker AI (Gordon)

```bash
# Enable in Docker Desktop: Settings > Beta features > Enable

# Generate Dockerfile
docker ai "create Dockerfile for FastAPI app"

# Troubleshoot build
docker ai "why is my build failing"
```

## Next Steps

After successful deployment:

1. Run `/sp.tasks` to generate implementation tasks
2. Follow tasks.md to implement each component
3. Document AI tool usage in `phase-4-k8s/CLAUDE.md`
4. Record demo video showing deployment process
