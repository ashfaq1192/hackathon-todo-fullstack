Always Read @AGENTS.md for the latest instructions.

## Current Phase
Phase V - Advanced Cloud Deployment (Oracle Cloud OKE Enhanced Cluster)

## Quick Reference
- **Constitution**: `.specify/memory/constitution.md` (v1.7.0 - Phase V Advanced Cloud Deployment)
- **Phase-V Implementation Guide**: `phase-5-cloud-deployment/IMPLEMENTATION_GUIDE.md` (Combined Research - Production Ready)
- **Hackathon PDF**: `Hackathon II - Todo Spec-Driven Development.pdf` (Official Requirements)
- **All technologies and AIOps tools**: See AGENTS.md Section 5
- **Key Resources**: Oracle Cloud **Enhanced Cluster** (~$3/24h), Redpanda Cloud ($100 credits), Grafana Cloud Free Tier

## Important: OKE Cluster Type
- **Basic Cluster**: API not responding (deprecated/limited) - DO NOT USE
- **Enhanced Cluster**: Required for deployment (~$3/day cost)
- **Strategy**: Deploy, demo, delete within 24 hours to minimize cost
- **Architecture**: x86_64 (AMD64) - VM.Standard.E4.Flex shape

## Phase V Requirements (from Hackathon PDF)

### Part A: Advanced Features

**Advanced Level (NEW features):**
- **Recurring Tasks** - Auto-reschedule repeating tasks (e.g., "weekly meeting"). When marked complete, auto-create next occurrence.
- **Due Dates & Time Reminders** - Set deadlines with date/time pickers; browser notifications at scheduled times.

**Intermediate Level (Build on Phase II):**
- **Priorities** - Assign levels: high / medium / low
- **Tags/Categories** - Labels such as work, home, personal
- **Search & Filter** - Search by keyword; filter by status, priority, or date
- **Sort Tasks** - Reorder by due date, priority, or alphabetically

**Event-Driven Architecture:**
- Kafka integration for 3 topics: `task-events`, `reminders`, `task-updates`
- Dapr as distributed application runtime (all 5 building blocks)

### Part B: Local Deployment (Minikube)
- Full Dapr: Pub/Sub, State, Bindings/Jobs, Secrets, Service Invocation
- **Local Kafka options**: Redpanda (Docker, easiest), Bitnami Kafka Helm, or Strimzi Operator

### Part C: Cloud Deployment (OKE / AKS / GKE)
- **Cloud Platform**: Oracle OKE (chosen), alternatives: Azure AKS ($200/30d), Google GKE ($300/90d)
- Full Dapr with Kafka/Redpanda Cloud
- CI/CD with GitHub Actions
- Monitoring and logging (OpenTelemetry + Grafana Cloud)

## Kafka Use Cases & Topics (Required)

### 4 Kafka Use Cases
1. **Reminder/Notification System** - Producer: Chat API → Topic: `reminders` → Consumer: Notification Service → User Device
2. **Recurring Task Engine** - Producer: Chat API → Topic: `task-events` → Consumer: Recurring Task Service (creates next occurrence)
3. **Activity/Audit Log** - Producer: Chat API (all CRUD ops) → Topic: `task-events` → Consumer: Audit Service (stores log)
4. **Real-time Sync Across Clients** - Producer: Chat API → Topic: `task-updates` → Consumer: WebSocket Service → All Connected Clients

### Kafka Topics
| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `task-events` | Chat API (MCP Tools) | Recurring Task Service, Audit Service | All task CRUD operations |
| `reminders` | Chat API (when due date set) | Notification Service | Scheduled reminder triggers |
| `task-updates` | Chat API | WebSocket Service | Real-time client sync |

### Kafka Service Options
- **Cloud**: Redpanda Cloud (recommended, free serverless), Confluent Cloud ($400 credit), CloudKarafka (free "Developer Duck"), Aiven ($300 trial)
- **Local (Minikube)**: Redpanda Docker (easiest, no Zookeeper), Bitnami Kafka Helm, Strimzi Operator

## Submission Requirements (Phase V - 300 points)
1. **Public GitHub repo** with all source code, `/specs` folder, CLAUDE.md, README.md
2. **Deployed application links** (OKE deployment URL + local Minikube instructions)
3. **Demo video** (max 90 seconds) showing: advanced features, Kafka event flow, Dapr integration
4. **WhatsApp number** for presentation invitation
5. **Live Presentation**: Invited top submissions present on Zoom

## Active Technologies
- **Phase V (Cloud)**: OKE Enhanced Cluster, Kafka/Redpanda, Dapr (HA mode), OpenTelemetry, Grafana Cloud, Argo CD (GitOps), GitHub Actions CI/CD
- **Phase IV (Local K8s)**: Minikube, Helm 3.x, kubectl, Docker multi-stage builds
- **Persistent**: External Neon PostgreSQL, Better Auth + JWT
- **Docker Images**: x86_64 (amd64) architecture for both local and OKE deployment

## Dapr Building Blocks (Required)
1. **Pub/Sub** - Kafka abstraction (pubsub.kafka) — publish/subscribe without Kafka client code
2. **State Management** - Conversation state (state.postgresql) — save/retrieve via Dapr HTTP API
3. **Service Invocation** - Frontend → Backend with retries, circuit breakers, mTLS
4. **Bindings/Jobs** - Cron triggers for reminders OR **Dapr Jobs API** (preferred — exact timing, no polling)
5. **Secrets Management** - K8s secrets or Dapr secrets store — API keys, DB credentials

### Dapr Components
| Component | Type | Purpose |
|-----------|------|---------|
| kafka-pubsub | pubsub.kafka | Event streaming (task-events, reminders, task-updates) |
| statestore | state.postgresql | Conversation state, task cache |
| dapr-jobs | Jobs API | Trigger reminder checks at exact times |
| kubernetes-secrets | secretstores.kubernetes | API keys, DB credentials |

## Meta Skills (Never Modify)
The following skills are meta skills and must NEVER be changed/updated:
- skill-creator
- skill-creator-pro
- skill-validator

## Recent Changes
- 2026-02-01: **OKE Basic Cluster API non-functional** - Must use Enhanced Cluster (~$3/day). Updated all docs.
- 2026-02-01: Switched to x86_64 architecture for Docker images (compatible with local + OKE)
- 009-cloud-deployment: Created comprehensive Phase-V implementation guide (merged Claude + Gemini research) with OIDC CI/CD, OpenTelemetry observability, GitOps patterns, and production-grade Dapr deployment
- 008-local-k8s-deployment: Added Dockerfile (multi-stage), YAML (Kubernetes manifests), Bash (scripts) + Docker Desktop 4.53+, Minikube, Helm 3.x, kubectl
