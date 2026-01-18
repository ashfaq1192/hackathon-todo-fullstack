# Todo App Overview - Hackathon II

## Purpose

This project implements **"The Evolution of Todo"** - a full-featured web application that evolves from a simple CLI app to a cloud-native AI chatbot deployed on Kubernetes, using **Spec-Driven Development (SDD)** methodology.

## Project Information

| Attribute | Value |
|-----------|-------|
| **Hackathon** | Hackathon II - Spec-Driven Development |
| **Total Points** | 1,000 base + 600 bonus = 1,600 |
| **Methodology** | Spec-Driven Development with Claude Code + Spec-Kit Plus |
| **Repository** | Public GitHub |

## Phase Evolution

| Phase | Name | Points | Due Date | Status | Key Features |
|-------|------|--------|----------|--------|--------------|
| **I** | In-Memory Python Console App | 100 | Dec 7, 2025 | Complete | Basic CRUD (5 features) |
| **II** | Full-Stack Web Application | 150 | Dec 14, 2025 | Complete | Web UI, REST API, Auth, PostgreSQL |
| **III** | AI-Powered Todo Chatbot | 200 | Dec 21, 2025 | **In Progress** | Natural language, MCP, OpenAI ChatKit |
| **IV** | Local Kubernetes Deployment | 250 | Jan 4, 2026 | Pending | Docker, Minikube, Helm |
| **V** | Advanced Cloud Deployment | 300 | Jan 18, 2026 | Pending | Kafka, Dapr, DOKS |

## Feature Progression

### Basic Level (Core Essentials) - Phase I+
- Add Task - Create new todo items
- Delete Task - Remove tasks from the list
- Update Task - Modify existing task details
- View Task List - Display all tasks
- Mark as Complete - Toggle task completion status

### Web Application Features - Phase II+
- User authentication (Better Auth with JWT)
- Persistent storage (Neon Serverless PostgreSQL)
- Responsive frontend (Next.js 16+ with Tailwind CSS)
- RESTful API (FastAPI with SQLModel)

### AI Chatbot Features - Phase III+
- Natural language task management
- MCP server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Conversation persistence with stateless architecture
- Voice input support (bonus)
- Urdu language support (bonus)

### Intermediate Level (Organization & Usability) - Phase V
- Priorities & Tags/Categories
- Search & Filter
- Sort Tasks

### Advanced Level (Intelligent Features) - Phase V
- Recurring Tasks
- Due Dates & Time Reminders

## Technology Stack by Phase

### Phase I: CLI Console App
- Python 3.13+
- UV package manager
- pytest (testing)
- ruff (linting)

### Phase II: Full-Stack Web App
- **Frontend**: Next.js 16+ (App Router), React 19, TypeScript 5+, Tailwind CSS 4+
- **Backend**: Python FastAPI, SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Auth**: Better Auth with JWT
- **Deployment**: Vercel

### Phase III: AI Chatbot
- **Frontend**: OpenAI ChatKit
- **AI Framework**: OpenAI Agents SDK (Swarm)
- **LLM Backend**: Google Gemini API (free tier via OpenAI-compatible interface)
- **MCP**: Official MCP SDK (Python)
- **Voice**: Web Speech API

### Phase IV: Local Kubernetes
- Docker (Docker Desktop)
- Docker AI Agent (Gordon)
- Kubernetes (Minikube)
- Helm Charts
- kubectl-ai, Kagent

### Phase V: Cloud Native
- Kafka/Redpanda Cloud
- Dapr (Distributed Application Runtime)
- Azure AKS / Google GKE / Oracle OKE
- GitHub Actions CI/CD

## Specification Structure

```
specs/
├── overview.md              # This file - Phase progression summary
├── architecture.md          # System architecture evolution
├── features/                # Feature specifications
│   ├── task-crud.md         # Core CRUD (Phases I-V)
│   ├── authentication.md    # Auth (Phases II-V)
│   ├── chatbot.md           # AI Chatbot (Phases III-V)
│   ├── k8s-deployment.md    # Kubernetes (Phase IV-V)
│   └── cloud-native.md      # Advanced cloud (Phase V)
├── api/                     # API specifications
│   ├── rest-endpoints.md    # REST API contracts
│   └── mcp-tools.md         # MCP tool signatures
├── database/                # Database specifications
│   └── schema.md            # Schema evolution
├── ui/                      # UI specifications
│   ├── components.md        # React components
│   └── pages.md             # Page layouts
└── archive/                 # Detailed SDD artifacts per phase
    ├── phase-1/             # Original 001-cli-todo-app specs
    ├── phase-2/             # Original 002, 003, 004 specs
    └── phase-3/             # Original 007-chatbot-mcp specs
```

## Prompt History Records (PHRs)

All SDD workflow artifacts are preserved in `history/prompts/`:
- `constitution/` - Project constitution amendments
- `001-cli-todo-app/` - Phase I SDD workflow
- `002-database-setup/` - Phase II database SDD
- `003-backend-api/` - Phase II backend SDD
- `004-frontend-nextjs/` - Phase II frontend SDD
- `007-chatbot-mcp/` - Phase III chatbot SDD
- `general/` - General prompts and context

## Git Tags for Phase Review

```bash
# View specific phase state
git checkout phase-1-complete  # Phase I final state
git checkout phase-2-complete  # Phase II final state
git checkout phase-3-complete  # Phase III final state (after completion)
```

## Deployed Links

| Component | URL | Status |
|-----------|-----|--------|
| Frontend | [Vercel](https://hackathon-todo-fullstack.vercel.app) | Active |
| Backend | [API](https://hackathon-todo-backend.vercel.app) | Active |
| Chatbot | TBD | In Progress |

## Submission Checklist

- [x] Public GitHub Repository
- [x] Constitution file (`.specify/memory/constitution.md`)
- [x] Spec history folder (`specs/`, `history/prompts/`)
- [x] Source code (`/backend`, `/frontend`)
- [x] README.md with setup instructions
- [x] CLAUDE.md with Claude Code instructions
- [x] Phase configuration (`.spec-kit/config.yaml`)
- [ ] Demo video (90 seconds max)
- [ ] Deployed chatbot link (Phase III)
- [ ] Minikube setup instructions (Phase IV)
- [ ] Cloud deployment URL (Phase V)

---

*Last Updated: 2026-01-18*
*Current Phase: III (AI-Powered Todo Chatbot)*
