# System Architecture - Evolution of Todo

## Architecture Evolution Summary

This document shows how the system architecture evolves across all 5 phases.

## Phase I: CLI Console App

```
┌─────────────────────────────────────┐
│          User Terminal              │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      Python CLI Application         │
│  ┌─────────────────────────────┐    │
│  │      main.py (Entry)        │    │
│  └─────────────────┬───────────┘    │
│                    │                │
│  ┌─────────────────▼───────────┐    │
│  │    TodoService (Logic)      │    │
│  └─────────────────┬───────────┘    │
│                    │                │
│  ┌─────────────────▼───────────┐    │
│  │  In-Memory List (Storage)   │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Key Components:**
- CLI entry point with menu-driven interface
- TodoService with 5 basic operations
- In-memory storage (data lost on exit)

---

## Phase II: Full-Stack Web Application

```
┌───────────────────────────────────────────────────────────────────┐
│                          Vercel                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   Next.js Frontend                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │  Auth Pages │  │  Task Pages │  │  API Client         │  │  │
│  │  │  (Better    │  │  (CRUD UI)  │  │  (Axios + JWT)      │  │  │
│  │  │   Auth)     │  │             │  │                     │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │  │
│  └─────────┼────────────────┼────────────────────┼─────────────┘  │
│            │                │                    │                 │
│            │                │         ┌──────────▼──────────┐     │
│            │                │         │  JWT Token (Cookie) │     │
│            │                │         └──────────┬──────────┘     │
└────────────┼────────────────┼────────────────────┼─────────────────┘
             │                │                    │
             │                │      Authorization: Bearer <token>
             │                │                    │
┌────────────┼────────────────┼────────────────────┼─────────────────┐
│            │                │                    │   Vercel        │
│  ┌─────────▼────────────────▼────────────────────▼─────────────┐  │
│  │                   FastAPI Backend                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │ JWT Verify  │  │  Task API   │  │  SQLModel ORM       │  │  │
│  │  │ Middleware  │──▶│  Routes     │──▶│  (Task Model)       │  │  │
│  │  └─────────────┘  └─────────────┘  └──────────┬──────────┘  │  │
│  └───────────────────────────────────────────────┼──────────────┘  │
└──────────────────────────────────────────────────┼─────────────────┘
                                                   │
                                                   ▼
                                    ┌──────────────────────────┐
                                    │  Neon Serverless         │
                                    │  PostgreSQL              │
                                    │  ┌────────────────────┐  │
                                    │  │ tasks              │  │
                                    │  │ users (Better Auth)│  │
                                    │  │ sessions           │  │
                                    │  └────────────────────┘  │
                                    └──────────────────────────┘
```

**Key Components:**
- **Frontend**: Next.js 16+ with Better Auth, React 19, Tailwind CSS
- **Backend**: FastAPI with SQLModel, JWT verification middleware
- **Database**: Neon Serverless PostgreSQL
- **Auth Flow**: Better Auth → JWT → FastAPI verification

---

## Phase III: AI-Powered Chatbot

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              Vercel (Frontend)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Next.js Frontend                                  │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │  │
│  │  │  Task Dashboard │  │  ChatKit UI     │  │  Voice Input        │  │  │
│  │  │  (Existing)     │  │  (OpenAI)       │  │  (Web Speech API)   │  │  │
│  │  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │  │
│  └───────────┼────────────────────┼──────────────────────┼─────────────┘  │
└──────────────┼────────────────────┼──────────────────────┼─────────────────┘
               │                    │                      │
               │              POST /api/{user_id}/chat     │
               │                    │                      │
┌──────────────┼────────────────────┼──────────────────────┼─────────────────┐
│              │                    ▼                      │   Vercel        │
│  ┌───────────┼────────────────────────────────────────────────────────┐   │
│  │           │         FastAPI Backend                                │   │
│  │           │  ┌─────────────────────────────────────────────────┐   │   │
│  │           │  │              Chat Endpoint                       │   │   │
│  │           │  │  POST /api/{user_id}/chat                        │   │   │
│  │           │  └────────────────────┬────────────────────────────┘   │   │
│  │           │                       │                                │   │
│  │           │                       ▼                                │   │
│  │           │  ┌─────────────────────────────────────────────────┐   │   │
│  │           │  │           OpenAI Agents SDK (Swarm)              │   │   │
│  │           │  │  ┌─────────────────┐  ┌─────────────────────┐   │   │   │
│  │           │  │  │  Agent (System  │  │  Runner              │   │   │   │
│  │           │  │  │  Prompt + Tools)│  │  (Orchestration)     │   │   │   │
│  │           │  │  └────────┬────────┘  └──────────┬──────────┘   │   │   │
│  │           │  └───────────┼─────────────────────┼───────────────┘   │   │
│  │           │              │                     │                   │   │
│  │           │              │  Tool Calls         │                   │   │
│  │           │              ▼                     │                   │   │
│  │           │  ┌──────────────────────────┐      │                   │   │
│  │           │  │    MCP Tools (Python)    │      │                   │   │
│  │           │  │  ┌────────────────────┐  │      │                   │   │
│  │           │  │  │ add_task           │  │      │                   │   │
│  │           │  │  │ list_tasks         │──┼──────┼───────┐           │   │
│  │           │  │  │ complete_task      │  │      │       │           │   │
│  │           │  │  │ delete_task        │  │      │       │           │   │
│  │  ┌────────┼──│  │ update_task        │  │      │       │           │   │
│  │  │        │  │  └────────────────────┘  │      │       │           │   │
│  │  │        │  └──────────────────────────┘      │       │           │   │
│  │  │  REST  │               │                    │       │           │   │
│  │  │  API   │◀──────────────┘                    │       │           │   │
│  │  │        │                                    │       │           │   │
│  │  └────────┼────────────────────────────────────┼───────┼───────────┘   │
│  └───────────┼────────────────────────────────────┼───────┼───────────────┘
└──────────────┼────────────────────────────────────┼───────┼────────────────┘
               │                                    │       │
               │            LLM API Call            │       │
               │    ┌───────────────────────────────┘       │
               │    │                                       │
               │    ▼                                       ▼
               │  ┌───────────────────┐      ┌──────────────────────────┐
               │  │  Google Gemini    │      │  Neon Serverless         │
               │  │  API (Free Tier)  │      │  PostgreSQL              │
               │  │  via OpenAI-      │      │  ┌────────────────────┐  │
               │  │  compatible       │      │  │ tasks              │  │
               │  │  endpoint         │      │  │ users              │  │
               │  └───────────────────┘      │  │ conversations      │  │
               │                             │  │ messages           │  │
               │                             │  └────────────────────┘  │
               │                             └──────────────────────────┘
               │
               └──────────────────────────────────────────┘
```

**Key Components:**
- **Frontend**: OpenAI ChatKit + Voice Input (Web Speech API)
- **AI Framework**: OpenAI Agents SDK (Swarm) with Agent + Runner
- **LLM Backend**: Google Gemini API (free tier) via OpenAI-compatible interface
- **MCP Tools**: 5 stateless Python functions for task management
- **Database**: Extended with Conversation and Message models

**Stateless Architecture Flow:**
1. Receive user message
2. Fetch conversation history from database
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)

---

## Phase IV: Local Kubernetes Deployment

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            Minikube Cluster                                    │
│                                                                                │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐           │
│  │     Frontend Deployment     │    │     Backend Deployment      │           │
│  │  ┌───────────────────────┐  │    │  ┌───────────────────────┐  │           │
│  │  │   Next.js Container   │  │    │  │  FastAPI Container    │  │           │
│  │  │   (Built with Gordon) │  │    │  │  + Agents SDK         │  │           │
│  │  │   Replicas: 2         │  │    │  │  + MCP Tools          │  │           │
│  │  └───────────────────────┘  │    │  │  Replicas: 2          │  │           │
│  └───────────────┬─────────────┘    │  └───────────────────────┘  │           │
│                  │                   └──────────────┬──────────────┘           │
│                  │                                  │                          │
│  ┌───────────────▼──────────────────────────────────▼───────────────┐         │
│  │                     Kubernetes Services                           │         │
│  │  ┌─────────────────────┐    ┌─────────────────────┐              │         │
│  │  │  frontend-service   │    │  backend-service    │              │         │
│  │  │  (LoadBalancer)     │    │  (ClusterIP)        │              │         │
│  │  └─────────────────────┘    └─────────────────────┘              │         │
│  └──────────────────────────────────────────────────────────────────┘         │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐         │
│  │                      Helm Chart Structure                         │         │
│  │  todo-chatbot/                                                    │         │
│  │  ├── Chart.yaml                                                   │         │
│  │  ├── values.yaml                                                  │         │
│  │  └── templates/                                                   │         │
│  │      ├── frontend-deployment.yaml                                 │         │
│  │      ├── backend-deployment.yaml                                  │         │
│  │      ├── services.yaml                                            │         │
│  │      └── configmaps.yaml                                          │         │
│  └──────────────────────────────────────────────────────────────────┘         │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐         │
│  │                     AIOps Tools                                   │         │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │         │
│  │  │   kubectl-ai    │  │     Kagent      │  │  Gordon (Docker)│   │         │
│  │  │   (K8s Ops)     │  │   (Cluster Mgmt)│  │  (Container Build│   │         │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │         │
│  └──────────────────────────────────────────────────────────────────┘         │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ External Services
                                      ▼
               ┌──────────────────────────────────────────┐
               │  ┌───────────────────┐  ┌─────────────┐  │
               │  │  Neon PostgreSQL  │  │  Gemini API │  │
               │  │  (External)       │  │  (External) │  │
               │  └───────────────────┘  └─────────────┘  │
               └──────────────────────────────────────────┘
```

**Key Components:**
- **Containerization**: Docker with Gordon AI assistance
- **Orchestration**: Kubernetes on Minikube
- **Package Manager**: Helm Charts
- **AI DevOps**: kubectl-ai, Kagent

---

## Phase V: Advanced Cloud Deployment

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                         Azure AKS / Google GKE / Oracle OKE                             │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              Dapr Sidecar Architecture                           │   │
│  │                                                                                  │   │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────────┐   │   │
│  │  │   Frontend Pod    │  │   Backend Pod     │  │   Notification Pod        │   │   │
│  │  │ ┌───────┐┌──────┐│  │ ┌───────┐┌──────┐ │  │ ┌───────┐ ┌──────────────┐│   │   │
│  │  │ │Next.js││ Dapr ││  │ │FastAPI││ Dapr │ │  │ │Notif  │ │   Dapr       ││   │   │
│  │  │ │  App  ││Sidecar│  │ │+ MCP  ││Sidecar│ │  │ │Service│ │   Sidecar    ││   │   │
│  │  │ └───────┘└──────┘│  │ └───────┘└──────┘ │  │ └───────┘ └──────────────┘│   │   │
│  │  └─────────┬─────────┘  └────────┬──────────┘  └───────────┬──────────────┘   │   │
│  │            │                     │                         │                  │   │
│  │            │                     │ Pub/Sub                 │ Subscribe        │   │
│  │            │                     ▼                         ▼                  │   │
│  │            │          ┌──────────────────────────────────────────────────┐   │   │
│  │            │          │              DAPR COMPONENTS                      │   │   │
│  │            │          │  ┌──────────────────┐  ┌──────────────────────┐   │   │   │
│  │            │          │  │ pubsub.kafka     │  │ state.postgresql     │   │   │   │
│  │            │          │  │ (Redpanda Cloud) │  │ (Neon DB)            │   │   │   │
│  │            │          │  └────────┬─────────┘  └──────────────────────┘   │   │   │
│  │            │          │           │                                       │   │   │
│  │            │          │  ┌────────▼─────────┐  ┌──────────────────────┐   │   │   │
│  │            │          │  │ Jobs API         │  │ secretstores.k8s     │   │   │   │
│  │            │          │  │ (Reminders)      │  │ (API Keys)           │   │   │   │
│  │            │          │  └──────────────────┘  └──────────────────────┘   │   │   │
│  │            │          └──────────────────────────────────────────────────┘   │   │
│  └────────────┼──────────────────────────────────────────────────────────────────┘   │
│               │                                                                      │
│  ┌────────────▼──────────────────────────────────────────────────────────────────┐   │
│  │                            Kafka Topics (Redpanda Cloud)                       │   │
│  │  ┌───────────────┐  ┌───────────────────┐  ┌───────────────────────────────┐  │   │
│  │  │ task-events   │  │ reminders         │  │ task-updates                  │  │   │
│  │  │ (All CRUD ops)│  │ (Scheduled alerts)│  │ (Real-time sync)              │  │   │
│  │  └───────────────┘  └───────────────────┘  └───────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐   │
│  │                         Advanced Feature Services                              │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐    │   │
│  │  │ Recurring Task      │  │ Reminder Service    │  │ Audit Service       │    │   │
│  │  │ Service             │  │ (Notification)      │  │ (Activity Log)      │    │   │
│  │  │ (Auto-reschedule)   │  │                     │  │                     │    │   │
│  │  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘    │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐   │
│  │                              CI/CD Pipeline                                    │   │
│  │  GitHub Actions → Build → Test → Push to Registry → Deploy to K8s             │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Key Components:**
- **Event-Driven**: Kafka/Redpanda Cloud for event streaming
- **Distributed Runtime**: Dapr with Pub/Sub, State, Bindings, Secrets
- **Cloud Platform**: Azure AKS / Google GKE / Oracle OKE
- **CI/CD**: GitHub Actions

**Advanced Features:**
- Recurring Tasks (auto-reschedule)
- Due Dates & Time Reminders
- Priorities & Tags
- Search & Filter
- Real-time multi-client sync

---

## Data Flow Summary

| Phase | Data Flow |
|-------|-----------|
| I | User → CLI → In-Memory List |
| II | User → Next.js → FastAPI → Neon PostgreSQL |
| III | User → ChatKit → FastAPI → Agents SDK → MCP Tools → Neon + Gemini API |
| IV | User → K8s Ingress → Frontend Pod → Backend Pod → External DB/API |
| V | User → K8s → Dapr Sidecars → Kafka Events → Microservices → DB/API |

---

*Last Updated: 2026-01-18*
