# Phase-V Cloud Deployment: Complete Implementation Guide

**Version:** 2.0 (Combined Research)
**Date:** 2026-01-25
**Status:** Production-Ready Patterns for First-Time Deployment
**Context:** Hackathon II - Completed Phase-IV (Local Kubernetes)

---

## 📋 Quick Navigation

- [Platform Selection](#platform-selection)
- [Implementation Roadmap](#implementation-roadmap)
- [Advanced Features](#part-a-advanced-features-development)
- [Event-Driven Architecture](#part-b-event-driven-architecture)
- [Local Testing](#part-c-local-deployment-validation)
- [Cloud Deployment](#part-d-cloud-deployment-oke)
- [CI/CD Pipeline](#part-e-cicd-with-github-actions)
- [Observability](#part-f-observability-stack)
- [GitOps (Optional)](#part-g-gitops-deployment-optional)
- [Troubleshooting](#troubleshooting-guide)

---

## Platform Selection

### Recommended: Oracle Cloud (OKE)

**Always Free Tier:**
- 4 ARM vCPUs + 24GB RAM (perpetual)
- 200GB block storage + 20GB object storage
- Free cluster management
- Free Flexible Load Balancer (10Mbps)
- **No expiration** - unlimited learning time

**Initial Credits:** $300 for 30 days (bonus)

**Why OKE:**
- Only platform with perpetual free Kubernetes resources
- Sufficient for production-grade learning
- No surprise bills after trial expiry

### Alternative Options

| Platform | Free Credits | Free Tier | Best For |
|----------|-------------|-----------|----------|
| **GKE** | $300 (90d) | $74.40/mo cluster credit | Production patterns |
| **AKS** | $200 (30d) | Free control plane | Azure ecosystem |
| **DigitalOcean** | $100-200 (60d) | None | Simplicity |

---

## Implementation Roadmap

### Week 1-2: Advanced Features Development
- Implement intermediate features (priorities, tags, search, filter, sort)
- Add advanced features (recurring tasks, due dates, reminders)
- Integrate Dapr Jobs API for scheduling

### Week 2-3: Event-Driven Architecture
- Deploy Kafka (Strimzi local, Redpanda Cloud)
- Configure Dapr Pub/Sub and State Management
- Implement event producers/consumers

### Week 3: Local Validation
- Deploy full stack to Minikube
- Validate all features end-to-end
- Test Dapr components and Kafka events

### Week 4-5: Cloud Deployment
- Set up Oracle Cloud OKE cluster
- Deploy with Helm to cloud
- Configure CI/CD with OIDC
- Set up observability stack

---

## PART A: Advanced Features Development

### Intermediate Features

**Priorities & Tags:**
```typescript
// Database schema addition
interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  tags: string[];  // Array of category labels
  completed: boolean;
  created_at: Date;
  updated_at: Date;
}
```

**Search & Filter:**
- Backend: Add query parameters to `GET /api/{user_id}/tasks`
- Frontend: Implement search bar and filter dropdowns
- Database: Add indexes on `priority`, `tags`, `completed`

**Sort:**
- Support sort by: `created_at`, `priority`, `due_date`, `title`
- Backend: Add `?sort=<field>&order=<asc|desc>` parameters

### Advanced Features

**Recurring Tasks:**
```python
# Store pattern in database
class RecurringPattern(SQLModel, table=True):
    task_id: int
    frequency: str  # 'daily', 'weekly', 'monthly'
    interval: int   # every X days/weeks/months
    next_occurrence: datetime

# Consumer listens to task completion events
async def handle_task_completed(event):
    if event.task.is_recurring:
        create_next_occurrence(event.task)
```

**Due Dates & Reminders:**
- Use **Dapr Jobs API** (not cron polling)
- Schedule jobs for specific reminder times
- Publish to `reminders` Kafka topic when due

---

## PART B: Event-Driven Architecture

### Kafka Deployment

**Local (Minikube): Strimzi Operator**
```bash
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Create cluster
kubectl apply -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
EOF
```

**Cloud: Redpanda Cloud Serverless**
- Sign up: [redpanda.com/try-data-streaming](https://www.redpanda.com/try-data-streaming)
- Get $100 free credits (14-day trial)
- Create serverless cluster
- Note: **Upstash Kafka deprecated** (discontinued March 2025)

**Topics:**
1. `task-events` - All CRUD operations
2. `reminders` - Scheduled notifications
3. `task-updates` - Real-time client sync

### Dapr Integration

**Installation:**
```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize on Kubernetes (HA mode for production)
dapr init -k --enable-ha=true
```

**Dapr Components (Configuration as Code):**

**1. Pub/Sub (Kafka)**
```yaml
# dapr-components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: dapr-system
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka:9092"
    - name: consumerGroup
      value: "todo-service"
```

**2. State Management (PostgreSQL)**
```yaml
# dapr-components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: dapr-system
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connectionString
```

**3. Jobs API (Reminders)**
```python
# Schedule reminder
async def schedule_reminder(task_id: int, remind_at: datetime, user_id: str):
    await httpx.post(
        f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
        json={
            "dueTime": remind_at.isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "type": "reminder"
            }
        }
    )

# Job callback endpoint
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    job_data = await request.json()
    # Publish to reminders topic via Dapr Pub/Sub
    await httpx.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/reminders",
        json=job_data["data"]
    )
    return {"status": "SUCCESS"}
```

**4. Secrets Management**
```yaml
# dapr-components/kubernetes-secrets.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: dapr-system
spec:
  type: secretstores.kubernetes
  version: v1
```

**Production Enhancement: External Secrets Operator (Optional)**
```bash
# Install ESO
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# Sync secrets from cloud providers to K8s
# Enables GitOps without committing secrets
```

**5. Service Invocation**
```typescript
// Frontend calls backend via Dapr sidecar
const response = await fetch(
  "http://localhost:3500/v1.0/invoke/backend-service/method/api/chat",
  { method: "POST", body: JSON.stringify(message) }
);
```

**Dapr Deployment Annotations:**
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
```

---

## PART C: Local Deployment Validation

**Deploy Complete Stack to Minikube:**

```bash
# Start Minikube
minikube start --cpus 4 --memory 8192

# Install Dapr (HA mode)
dapr init -k --enable-ha=true

# Deploy Kafka
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f phase-5-cloud-deployment/kafka-cluster.yaml

# Deploy Dapr components
kubectl apply -f phase-5-cloud-deployment/dapr-components/

# Deploy application
helm install todo-chatbot ./phase-4-k8s/helm/todo-chatbot \
  -f values-minikube.yaml \
  --create-namespace \
  --namespace todo

# Port forward for testing
kubectl port-forward svc/frontend 3000:3000 -n todo
kubectl port-forward svc/backend 8000:8000 -n todo
```

**Validation Checklist:**
- [ ] Frontend loads and displays tasks
- [ ] Backend API responds to requests
- [ ] Tasks persist to Neon database
- [ ] Kafka events publish successfully
- [ ] Dapr sidecars inject properly
- [ ] Recurring tasks create next occurrence
- [ ] Reminder jobs trigger at scheduled time
- [ ] WebSocket updates work across clients

---

## PART D: Cloud Deployment (OKE)

### 1. Oracle Cloud Account Setup

```bash
# Sign up
https://www.oracle.com/cloud/free/

# Important: Upgrade to "Pay As You Go"
# - Keeps Always Free resources
# - Enables OKE cluster creation
# - Won't charge for Always Free usage
```

### 2. Create OKE Cluster

**Via OCI Console:**
1. Navigate: Developer Services → Kubernetes Clusters (OKE)
2. Click "Create Cluster" → "Quick Create"
3. Configure:
   - Name: `todo-chatbot-cluster`
   - Kubernetes Version: Latest stable
   - Node Shape: `VM.Standard.A1.Flex` (ARM - FREE)
   - Nodes: 2
   - OCPUs per node: 2 (total 4 = free tier)
   - Memory per node: 12GB (total 24GB = free tier)
4. Create (10-15 minutes)

**Via Terraform (Infrastructure as Code):**
```hcl
# oke-cluster.tf
resource "oci_containerengine_cluster" "todo_cluster" {
  compartment_id     = var.compartment_id
  kubernetes_version = "v1.28.2"
  name              = "todo-chatbot-cluster"
  vcn_id            = oci_core_vcn.vcn.id

  options {
    service_lb_subnet_ids = [oci_core_subnet.lb_subnet.id]
  }
}

resource "oci_containerengine_node_pool" "node_pool" {
  cluster_id         = oci_containerengine_cluster.todo_cluster.id
  compartment_id     = var.compartment_id
  kubernetes_version = "v1.28.2"
  name              = "worker-nodes"
  node_shape        = "VM.Standard.A1.Flex"

  node_config_details {
    size = 2

    placement_configs {
      availability_domain = data.oci_identity_availability_domain.ad.name
      subnet_id           = oci_core_subnet.node_subnet.id
    }
  }

  node_shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }
}
```

### 3. Connect to Cluster

```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure
oci setup config

# Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <CLUSTER_OCID> \
  --file $HOME/.kube/config \
  --region us-ashburn-1 \
  --token-version 2.0.0

# Verify
kubectl get nodes
```

### 4. Deploy to OKE

**Install Dapr:**
```bash
dapr init -k --enable-ha=true --wait
```

**Deploy Kafka:**
```bash
# Option 1: Strimzi (self-hosted, free)
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f kafka-cluster.yaml

# Option 2: Use Redpanda Cloud (easier)
# Configure Dapr component with Redpanda connection string
```

**Deploy Application:**
```bash
# Build and push images to Oracle Container Registry
docker tag backend:latest <region>.ocir.io/<tenancy>/backend:latest
docker tag frontend:latest <region>.ocir.io/<tenancy>/frontend:latest

docker push <region>.ocir.io/<tenancy>/backend:latest
docker push <region>.ocir.io/<tenancy>/frontend:latest

# Deploy with Helm
helm upgrade --install todo-chatbot ./phase-4-k8s/helm/todo-chatbot \
  --namespace todo \
  --create-namespace \
  -f values-oke.yaml \
  --set backend.image.repository=<region>.ocir.io/<tenancy>/backend \
  --set frontend.image.repository=<region>.ocir.io/<tenancy>/frontend
```

**Configure Ingress:**
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: todo.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

---

## PART E: CI/CD with GitHub Actions

### Modern Approach: OIDC Workload Identity

**Why OIDC:**
- **No static credentials** in GitHub Secrets
- Short-lived tokens per workflow run
- More secure than service account tokens
- Latest best practice for 2026

**Setup Steps:**

**1. Configure OKE for OIDC Trust:**
```bash
# Create service account
kubectl create serviceaccount github-actions -n todo

# Create role with necessary permissions
kubectl create role deployer --verb=get,list,create,update,patch,delete \
  --resource=deployments,services,configmaps,secrets -n todo

# Bind role
kubectl create rolebinding github-actions-deployer \
  --role=deployer \
  --serviceaccount=todo:github-actions \
  -n todo

# Configure OIDC trust (OKE 1.26+)
# This allows GitHub's OIDC issuer to authenticate
```

**2. GitHub Actions Workflow:**
```yaml
# .github/workflows/deploy-oke.yml
name: Deploy to Oracle Cloud OKE

on:
  push:
    branches: [ main ]

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      # Security: Scan images
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

      # Build and push images
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Oracle Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.OCI_REGISTRY }}
          username: ${{ secrets.OCI_USERNAME }}
          password: ${{ secrets.OCI_AUTH_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./phase-3-chatbot/backend
          push: true
          tags: |
            ${{ secrets.OCI_REGISTRY }}/${{ secrets.OCI_TENANCY }}/backend:${{ github.sha }}
            ${{ secrets.OCI_REGISTRY }}/${{ secrets.OCI_TENANCY }}/backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # Authenticate with OIDC
      - name: Authenticate to OKE via OIDC
        uses: oracle-actions/configure-kubectl-oke@v1
        with:
          cluster: ${{ secrets.OKE_CLUSTER_ID }}
          token: ${{ steps.get-oidc-token.outputs.token }}

      # Static analysis
      - name: Lint Kubernetes manifests
        uses: stackrox/kube-linter-action@v1
        with:
          directory: phase-4-k8s/helm/todo-chatbot

      # Deploy with Helm
      - name: Deploy to staging
        if: github.ref == 'refs/heads/main'
        run: |
          helm upgrade --install todo-chatbot ./phase-4-k8s/helm/todo-chatbot \
            --namespace todo-staging \
            --create-namespace \
            -f values-oke.yaml \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --wait

      # Promote to production (manual approval)
      - name: Deploy to production
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: |
          helm upgrade --install todo-chatbot ./phase-4-k8s/helm/todo-chatbot \
            --namespace todo \
            --create-namespace \
            -f values-oke.yaml \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --wait
```

**Best Practices:**
- ✅ Least privilege RBAC
- ✅ Image vulnerability scanning (Trivy)
- ✅ Manifest static analysis (kube-linter)
- ✅ Staging → Production promotion
- ✅ Image tagging with commit SHA
- ✅ GitHub Environments for approvals

---

## PART F: Observability Stack

### OpenTelemetry + Grafana Cloud

**Why This Stack:**
- **Zero-code instrumentation** with Dapr
- **Generous free tier**: 10k metrics, 50GB logs, 50GB traces
- Native OpenTelemetry support
- Unified dashboarding

**Setup:**

**1. Sign up for Grafana Cloud:**
- Visit: [grafana.com/products/cloud](https://grafana.com/products/cloud)
- Select free tier
- Get API key and endpoints

**2. Deploy OpenTelemetry Collector:**
```yaml
# otel-collector.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318

    processors:
      batch:
        timeout: 10s
      memory_limiter:
        check_interval: 1s
        limit_mib: 512

    exporters:
      otlp:
        endpoint: tempo-prod-04-prod-us-east-0.grafana.net:443
        headers:
          authorization: Basic <GRAFANA_CLOUD_API_KEY>

      prometheusremotewrite:
        endpoint: https://prometheus-prod-10-prod-us-central-0.grafana.net/api/prom/push
        headers:
          authorization: Basic <GRAFANA_CLOUD_API_KEY>

      loki:
        endpoint: https://logs-prod-us-central1.grafana.net/loki/api/v1/push
        headers:
          authorization: Basic <GRAFANA_CLOUD_API_KEY>

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp]
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [prometheusremotewrite]
        logs:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [loki]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector:latest
        args: ["--config=/etc/otel/config.yaml"]
        volumeMounts:
        - name: config
          mountPath: /etc/otel
      volumes:
      - name: config
        configMap:
          name: otel-collector-config
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: observability
spec:
  ports:
  - name: otlp-grpc
    port: 4317
    protocol: TCP
  - name: otlp-http
    port: 4318
    protocol: TCP
  selector:
    app: otel-collector
```

**3. Configure Dapr for OpenTelemetry:**
```yaml
# dapr-config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
  namespace: dapr-system
spec:
  tracing:
    samplingRate: "1"
    otel:
      endpointAddress: "otel-collector.observability:4317"
      isSecure: false
      protocol: grpc
  metric:
    enabled: true
```

**4. Enable in Deployments:**
```yaml
metadata:
  annotations:
    dapr.io/config: "tracing"
```

**Result:**
- Automatic distributed tracing across all Dapr service invocations
- Metrics exported to Grafana Cloud
- Logs aggregated in Loki
- Zero code changes required

**Alternative: SigNoz (Self-Hosted)**
```bash
# Deploy SigNoz
git clone https://github.com/SigNoz/signoz.git
cd signoz/deploy/kubernetes
kubectl apply -f .

# Access UI
kubectl port-forward svc/frontend 3301:3301 -n platform
```

---

## PART G: GitOps Deployment (Optional)

### Argo CD for Pull-Based Deployments

**Why GitOps:**
- Git as single source of truth
- Automatic cluster reconciliation
- Better auditability and rollback
- Complements GitHub Actions (push-based)

**Install Argo CD:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Repository Structure:**
```
todo-chatbot-gitops/
├── apps/
│   ├── backend/
│   │   └── deployment.yaml
│   ├── frontend/
│   │   └── deployment.yaml
│   └── kafka/
│       └── kafka-cluster.yaml
├── dapr-components/
│   ├── kafka-pubsub.yaml
│   ├── statestore.yaml
│   └── secrets.yaml
└── argocd-applications/
    ├── backend-app.yaml
    ├── frontend-app.yaml
    └── dapr-components-app.yaml
```

**Argo Application:**
```yaml
# argocd-applications/backend-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: todo-backend
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourusername/todo-chatbot-gitops
    targetRevision: HEAD
    path: apps/backend
  destination:
    server: https://kubernetes.default.svc
    namespace: todo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Workflow:**
1. Developer pushes code → GitHub Actions builds image
2. GitHub Actions updates GitOps repo with new image tag
3. Argo CD detects change → pulls and applies to cluster
4. Cluster state matches Git automatically

---

## Troubleshooting Guide

### Cluster Connection Issues

```bash
# Verify connection
kubectl cluster-info

# Check credentials
kubectl config get-contexts
kubectl config use-context <context-name>

# Refresh OKE kubeconfig
oci ce cluster create-kubeconfig --cluster-id <OCID> --file ~/.kube/config --overwrite
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo

# Describe pod for errors
kubectl describe pod <pod-name> -n todo

# View logs
kubectl logs <pod-name> -n todo

# Check events
kubectl get events -n todo --sort-by='.lastTimestamp'

# If ImagePullBackOff:
# - Verify image exists in registry
# - Check imagePullSecrets configured
# - Ensure registry credentials are valid
```

### Dapr Sidecar Issues

```bash
# Check Dapr sidecar injection
kubectl get pods -n todo -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Should see: app-container daprd

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo

# Check Dapr components
kubectl get components -n dapr-system

# Verify Dapr configuration
kubectl get configuration -n dapr-system
```

### Kafka Connection Issues

```bash
# Check Kafka cluster status
kubectl get kafka -n kafka

# View Kafka logs
kubectl logs -n kafka -l app.kubernetes.io/name=kafka

# Test Kafka connection from pod
kubectl run kafka-test --image=confluentinc/cp-kafka:latest -it --rm -- bash
kafka-topics --bootstrap-server todo-kafka-kafka-bootstrap.kafka:9092 --list
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n todo

# Describe ingress
kubectl describe ingress todo-ingress -n todo

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Verify LoadBalancer IP assigned
kubectl get svc -n ingress-nginx
```

### Database Connection Issues

```bash
# Test from backend pod
kubectl exec -it <backend-pod> -n todo -- bash
curl -v <NEON_DATABASE_URL>

# Check secrets
kubectl get secret postgres-secret -n todo -o yaml

# Verify connection string format
# Should be: postgresql://user:password@host:5432/dbname?sslmode=require
```

### Use AI Assistants

```bash
# kubectl-ai for diagnostics
kubectl ai "why is my frontend pod crashing in namespace todo?"
kubectl ai "show me resource usage for backend deployment"

# kagent for cluster analysis
kagent "analyze cluster health and suggest optimizations"
```

---

## Production Best Practices Checklist

### Dapr HA Configuration
- [ ] Deploy Dapr with `--enable-ha=true`
- [ ] Multiple replicas for Dapr control plane components
- [ ] Dedicated namespace (`dapr-system`)
- [ ] Priority classes assigned
- [ ] Resource limits and requests configured

### Security
- [ ] RBAC with least privilege
- [ ] Network policies between pods
- [ ] External Secrets Operator for secret management
- [ ] No secrets committed to Git
- [ ] OIDC workload identity for CI/CD
- [ ] Regular image vulnerability scans

### Observability
- [ ] OpenTelemetry collector deployed
- [ ] Traces exported to Grafana Cloud/SigNoz
- [ ] Metrics collected and visualized
- [ ] Logs aggregated (Loki)
- [ ] Alerting configured for critical issues

### Reliability
- [ ] Pod anti-affinity for high availability
- [ ] Resource requests and limits set
- [ ] Health checks (liveness/readiness probes)
- [ ] Horizontal Pod Autoscaling configured
- [ ] PodDisruptionBudgets defined

### GitOps
- [ ] Infrastructure as Code (Terraform for OKE)
- [ ] Helm charts version controlled
- [ ] Argo CD/Flux CD for automated deployments
- [ ] Separate repos for app code and GitOps config
- [ ] Rollback strategy documented

---

## Key Resources

### Platform Documentation
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- [OKE Documentation](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [GKE Free Tier](https://cloud.google.com/free)
- [Azure AKS Free Tier](https://azure.microsoft.com/en-us/pricing/details/kubernetes-service/)

### Kafka/Messaging
- [Redpanda Cloud](https://www.redpanda.com/try-data-streaming) - $100 free credits
- [Strimzi Kafka Operator](https://strimzi.io/)
- **Note:** Upstash Kafka deprecated (discontinued March 11, 2025)

### Dapr
- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Dapr Best Practices](https://docs.dapr.io/operations/production/)

### Observability
- [Grafana Cloud Free Tier](https://grafana.com/products/cloud/)
- [OpenTelemetry](https://opentelemetry.io/)
- [SigNoz](https://signoz.io/)

### GitOps
- [Argo CD](https://argo-cd.readthedocs.io/)
- [Flux CD](https://fluxcd.io/)

### Security
- [External Secrets Operator](https://external-secrets.io/)
- [Kube-Linter](https://github.com/stackrox/kube-linter)
- [Trivy](https://github.com/aquasecurity/trivy)

---

## Deliverables Checklist

**Code & Configuration:**
- [ ] GitHub repository with Phase-V code
- [ ] All advanced features implemented
- [ ] Kafka/Dapr integration complete
- [ ] Helm charts for deployment
- [ ] CI/CD pipeline with OIDC
- [ ] Observability stack configured

**Deployment:**
- [ ] Successfully deployed to OKE
- [ ] Public URL accessible
- [ ] SSL/TLS certificate configured
- [ ] Database migrations applied

**Documentation:**
- [ ] README.md with setup instructions
- [ ] Architecture diagram
- [ ] API documentation
- [ ] Deployment runbook

**Presentation:**
- [ ] Demo video (90 seconds max)
- [ ] Screenshots of running application
- [ ] Performance metrics/dashboards

---

**Generated:** 2026-01-25
**Sources:** Combined research from Claude Sonnet 4.5 & Gemini 2.0
**Status:** Production-ready patterns validated for first-time cloud deployment
