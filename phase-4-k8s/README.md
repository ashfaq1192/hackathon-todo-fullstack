# Phase IV - Local Kubernetes Deployment

## What is this phase about?

In the previous phases, we built a Todo app with a chatbot. It works great on our computers during development, but how do we run it like a "real" production application — one that can be easily started, stopped, scaled up, and managed?

**Phase IV answers that question.** We take our existing app and package it into containers (like shipping containers for software), then deploy it to a mini version of the same system that companies like Google, Netflix, and Spotify use to run their apps at scale.

Think of it like this:
- **Before**: Running the app by manually typing commands in the terminal
- **After**: The app runs itself inside a managed system that monitors its health, restarts it if it crashes, and can scale it up when needed

---

## Technology Stack (Explained Simply)

### Docker — "The Shipping Container"

**What it is**: A tool that packages your app and everything it needs (code, libraries, settings) into a single box called a "container."

**Why we use it**: Just like a shipping container can be loaded onto any ship regardless of what's inside, a Docker container can run on any computer regardless of what OS or software is installed. No more "it works on my machine" problems.

**What we did**: Created two containers — one for the backend (Python API) and one for the frontend (Next.js website).

---

### Minikube — "The Mini Data Center on Your Laptop"

**What it is**: A tool that creates a tiny Kubernetes cluster on your own computer for learning and testing.

**Why we use it**: Real Kubernetes runs on massive cloud servers. Minikube lets us practice the same concepts locally without paying for cloud services. It's like having a flight simulator before flying a real plane.

---

### Kubernetes (K8s) — "The Container Manager"

**What it is**: A system that manages containers — it decides where to run them, monitors their health, restarts them if they fail, and can spin up more copies when traffic increases.

**Why we use it**: Instead of manually starting containers and watching them, Kubernetes does it automatically. You tell it "I want 2 copies of my backend running" and it makes it happen, forever keeping that promise.

**Key concepts we use**:
- **Pod**: The smallest unit — one running instance of your app
- **Deployment**: A declaration of "I want X copies of this container running"
- **Service**: A stable address to reach your pods (pods come and go, services stay)
- **Ingress**: The front door — routes external traffic to the right service
- **ConfigMap**: Non-secret settings (like log levels)
- **Secret**: Sensitive settings (like database passwords)

---

### Helm — "The App Store for Kubernetes"

**What it is**: A package manager for Kubernetes. Instead of writing dozens of YAML config files and applying them one by one, Helm bundles them into a single "chart" that you install with one command.

**Why we use it**: Imagine installing an app on your phone by manually copying 15 files to specific folders vs. just tapping "Install" in the app store. Helm is the "Install" button for Kubernetes apps.

**What we did**: Created a Helm chart that contains all the Kubernetes configuration (deployments, services, ingress, secrets, configmaps) in one package.

---

### Nginx Ingress — "The Traffic Cop"

**What it is**: A reverse proxy that sits at the entrance of our cluster and routes incoming requests to the right service.

**Why we use it**: When someone visits `todo.local/api/tasks`, Ingress knows to send that to the backend. When they visit `todo.local/`, it sends them to the frontend. One domain, multiple services.

---

### External Database (Neon PostgreSQL) — "The Cloud Database"

**What it is**: Our database lives outside the Kubernetes cluster, hosted by Neon (a cloud PostgreSQL provider).

**Why**: Databases need persistent storage and careful management. Running a database inside a local cluster adds complexity. By keeping it external, our containers stay simple and stateless — they can be destroyed and recreated without losing data.

---

## How It All Fits Together

```
You (browser)
    │
    ▼
┌─────────────────────────────────────────────┐
│  Minikube Cluster                           │
│                                             │
│  ┌─────────┐                                │
│  │ Ingress │  ← Routes /api to backend      │
│  │ (nginx) │  ← Routes / to frontend        │
│  └────┬────┘                                │
│       │                                     │
│  ┌────┴─────────────────────┐               │
│  │            │              │               │
│  ▼            ▼              │               │
│  ┌────────┐  ┌─────────┐    │               │
│  │Backend │  │Frontend  │    │               │
│  │(FastAPI)│  │(Next.js) │    │               │
│  └───┬────┘  └──────────┘    │               │
│      │                       │               │
└──────┼───────────────────────┘               │
       │                                       │
       ▼                                       │
  ┌──────────┐                                 │
  │  Neon DB │  (External PostgreSQL)          │
  └──────────┘
```

---

## Quick Commands

```bash
# Start everything
./scripts/deploy-minikube.sh

# Access the app
kubectl port-forward svc/todo-chatbot-frontend 3000:3000
# Then open http://localhost:3000

# Check status
kubectl get pods

# View logs
kubectl logs -f deploy/todo-chatbot-backend

# Stop everything
./scripts/cleanup.sh
```

---

## What We Learned

1. **Containerization** — How to package apps into portable, reproducible containers
2. **Orchestration** — How Kubernetes manages containers automatically
3. **Infrastructure as Code** — All our deployment config is in version-controlled YAML files
4. **Helm Charts** — How to bundle complex deployments into reusable packages
5. **Health Checks** — How Kubernetes knows if your app is alive and ready
6. **Ingress Routing** — How to expose multiple services under one domain
7. **Secrets Management** — How to handle sensitive configuration in Kubernetes
