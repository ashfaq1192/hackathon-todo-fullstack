# Evolution of Todo Constitution

<!--
Sync Impact Report:
Version: 1.6.0 → 1.7.0 (MINOR: Phase V Advanced Cloud Deployment Specifications)

Changes:
- Expanded Phase V section with production-ready cloud deployment patterns
- Added OIDC Workload Identity for secure CI/CD authentication
- Specified OpenTelemetry + Grafana Cloud observability stack
- Added Dapr HA configuration requirements
- Specified Redpanda Cloud for Kafka-compatible messaging (14-day $100 credit trial)
- Added External Secrets Operator (ESO) for advanced secret management
- Added GitOps deployment pattern with Argo CD/Flux CD (optional but recommended)
- Defined 5-stage gradual implementation strategy with clear checkpoints
- Updated Definition of Done with comprehensive observability and security requirements
- Added advanced features: recurring tasks, due dates, reminders, priorities, tags, search, filter, sort
- Included production best practices checklist

New Sections Added/Enhanced:
1. Phase V: Advanced Cloud Deployment including:
   - Oracle Kubernetes Engine (OKE) Always Free tier deployment (4 vCPUs, 24GB RAM perpetual)
   - Dapr HA integration (Pub/Sub, State Management, Bindings, Secrets, Service Invocation)
   - Event-driven architecture with Kafka/Redpanda
   - OIDC-based CI/CD pipeline with GitHub Actions (eliminates static credentials)
   - Zero-code observability with OpenTelemetry + Grafana Cloud Free Tier
   - Advanced application features implementation
   - 5-stage implementation strategy (OKE setup → Kafka → Dapr → CI/CD → Observability)
   - GitOps deployment as production enhancement (optional)
   - Comprehensive security practices (RBAC, Network Policies, ESO)
   - Infrastructure as Code with Terraform (optional)

Modified Sections:
- Phase V: Expanded from basic outline to comprehensive production-ready specifications (~150 lines)
- Added modern cloud-native best practices (OIDC, OpenTelemetry, GitOps)
- Enhanced security requirements with ESO and network policies
- Updated deliverables to include observability dashboards and security scanning

Templates Requiring Updates:
✅ Existing templates support Phase V features
⚠️ May need cloud infrastructure templates (Terraform for OKE provisioning)
⚠️ CI/CD workflow templates for OIDC authentication
⚠️ Dapr component YAML templates
⚠️ OpenTelemetry Collector configuration templates

Rationale for MINOR version bump:
- Significant Phase V material added (from outline to production-ready actionable spec)
- Non-breaking: Phases I-IV remain unchanged, Phase V is additive
- Enables Phase V execution with complete modern cloud-native requirements
- Incorporates latest 2026 best practices (OIDC, OpenTelemetry, GitOps)
- Aligns with hackathon PDF requirements for Advanced Cloud Deployment
- Based on combined research (Claude + Gemini) validated against industry standards
- Provides first-time cloud deployment guidance with free-tier platform focus

Follow-up TODOs:
- Set up Oracle Cloud account and enable "Pay As You Go" (keeps Always Free resources)
- Install OCI CLI: `bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"`
- Sign up for Redpanda Cloud free trial ($100 credits, 14 days)
- Configure GitHub repository secrets for OIDC workload identity
- Set up Grafana Cloud free tier account (10k metrics, 50GB logs, 50GB traces)
- Install Dapr CLI: `curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash`
- Create /specs/features/012-advanced-cloud-deployment/ when starting Phase V
- Review IMPLEMENTATION_GUIDE.md in phase-5-cloud-deployment/ directory for detailed guidance
- Install kubectl-ai if not already available: `kubectl krew install ai`
-->
-->

## Overview

This constitution governs the development of the "Evolution of Todo" project for Hackathon II. It enforces Spec-Driven Development (SDD) using Claude Code and Spec-Kit Plus, shifting the role from syntax writer to system architect. The project evolves a Todo app from a simple CLI to a cloud-native AI system, incorporating Reusable Intelligence through skills and subagents.

## Core Principles

### I. Spec-Driven Development (SDD)

All features MUST start with a Markdown spec. Refine specs iteratively until Claude Code generates correct implementations. No manual coding is allowed—only spec refinement and prompt engineering.

**Rationale**: SDD ensures requirements are clear, testable, and auditable before implementation. It eliminates ambiguity and provides a documented decision trail for judges. Manual coding violates the hackathon's agentic development philosophy.

**Requirements**:
- Every feature MUST have a spec in `/specs/[###-feature-name]/spec.md`
- Specs MUST be refined through Claude Code iterations before implementation
- All spec iterations MUST be tracked in `/specs/[###-feature-name]/history/`
- No code may be written manually—all code MUST be generated by Claude Code

### II. Agentic Dev Stack Workflow

Follow the strict workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. Use Spec-Kit Plus for spec management (e.g., init, generate plan, validate).

**Rationale**: This workflow enforces systematic development and leverages Claude Code's strengths. It ensures planning precedes implementation and maintains traceability from requirements to code.

**Requirements**:
- ALL features MUST follow: `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`
- Plans MUST be approved before task generation
- Tasks MUST be approved before implementation
- Document all Claude sessions and prompts in `CLAUDE.md`

### III. Reusable Intelligence

Design modular skills and subagents using the P+Q+P framework (Problem + Query + Plan). Create reusable components like "TaskManagerSkill" for CRUD operations to maximize bonus points.

**Rationale**: Reusable Intelligence demonstrates mastery of agentic patterns and earns +200 bonus points. Modular skills improve maintainability and enable composition of complex behaviors.

**Requirements**:
- Skills MUST follow the P+Q+P framework
- Each skill MUST have clear problem definition, query interface, and execution plan
- Skills MUST be independently testable and reusable across features
- Document skill architecture in `/specs/skills/` for bonus point validation

### IV. Clean Code and Structure

Adhere to Python best practices (PEP8), modular design, and proper project structure. Use UV for dependency management.

**Rationale**: Clean code ensures maintainability, readability, and professional quality expected in hackathon submissions. Proper structure supports scaling from CLI to cloud-native architecture.

**Requirements**:
- ALL Python code MUST conform to PEP8 standards
- MUST use UV for dependency management (Python 3.13+)
- Project structure MUST follow monorepo pattern: `/src/`, `/specs/`, `/tests/`, `/frontend/`, `/backend/` (as phases evolve)
- MUST maintain separation of concerns: models, services, CLI, API layers
- Configuration MUST use environment variables (`.env` files)

### V. No Manual Interventions

Code MUST be generated by Claude Code. Document all Claude sessions, prompts, and iterations in `CLAUDE.md` for judging transparency.

**Rationale**: Manual coding disqualifies the submission per hackathon rules. Complete documentation proves authentic agentic development and helps judges evaluate prompt engineering skill.

**Requirements**:
- Zero manual code writing permitted
- EVERY Claude Code session MUST be documented in `CLAUDE.md`
- MUST record: prompt text, generated code, iteration count, refinements made
- Document failures and how specs were adjusted to achieve success
- Violations invalidate the submission

### VI. Bonus Alignment

Incorporate features that earn bonus points: Reusable Intelligence (+200), Cloud-Native Blueprints (+200), Multi-language Support (Urdu chatbot, +100), Voice Commands (+200).

**Rationale**: Bonus features differentiate submissions and demonstrate advanced capabilities. Strategic alignment maximizes scoring potential (up to +700 points).

**Requirements**:
- Plan bonus features explicitly in spec and plan documents
- Reusable Intelligence: document skills in `/specs/skills/`
- Cloud-Native: implement in Phase IV/V with Docker, K8s, Kafka, Dapr
- Multi-language: add Urdu support in Phase III chatbot
- Voice Commands: integrate voice interface in Phase III or later
- MUST document bonus feature implementation for judge validation

### VII. Ethical and Compliant Development

Ensure user data isolation (e.g., via authentication in later phases), scalability, and alignment with cloud-native principles.

**Rationale**: Professional applications require security, privacy, and scalability. Demonstrating these principles shows production-readiness and responsible engineering.

**Requirements**:
- User data MUST be isolated per user (implement auth in Phase II+)
- MUST follow principle of least privilege for access control
- Sensitive data (passwords, tokens) MUST use secure storage (env vars, secrets managers)
- MUST implement proper error handling without leaking sensitive information
- Design MUST support horizontal scaling (stateless services in cloud phases)

### VIII. Gradual Feature Implementation

Features MUST be implemented in logical, hierarchical order. Each stage MUST be fully functional and testable before proceeding to the next. Build complexity incrementally—foundation before dependent features.

**Rationale**: Gradual implementation reduces risk, enables early validation, and ensures a working application at every stage. This approach prevents big-bang integration failures and allows course correction after each milestone. It aligns with agile principles and provides judges with clear progression evidence.

**Requirements**:
- Features MUST be ordered by dependency (e.g., database setup before API, API before frontend)
- Each feature stage MUST have independent acceptance criteria
- MUST validate and test each stage before starting the next
- Document the feature hierarchy in plan.md with explicit stage ordering
- Each stage MUST be committable and deployable independently
- Integration between stages MUST be testable in isolation

## Development Standards

### Testing Requirements
- **TDD Mandatory**: Write tests BEFORE implementation for all features
- **Phase I Coverage**: Minimum 70% for MVP, 80% for production-ready
- **Phase II Coverage**: Minimum 75% for MVP, 85% for production-ready
- **Test Structure**: Mirror src/ in tests/ (e.g., `src/models/task.py` → `tests/unit/models/test_task.py`)
- **Test Categories**: Unit tests in `tests/unit/`, integration tests in `tests/integration/`, e2e tests in `tests/e2e/`
- **Test Execution**: Run `pytest` (backend) and test framework (frontend) before marking any task complete

### Version Control & Branching
- **Branch Naming**: `###-feature-name` format (e.g., `001-cli-todo-app`, `002-database-setup`)
- **Feature Numbering**: Start at 001, increment sequentially per feature
- **Commit Frequency**: Commit after each completed task from tasks.md
- **Commit Format**: `feat(scope): description` for features, `fix(scope): description` for bugs
- **Example**: `git checkout -b 002-database-setup` then `git commit -m "feat(db): configure neon postgresql connection"`

### Environment Setup
- **Virtual Environment**: Use `uv venv` to create, `source .venv/bin/activate` to activate
- **Environment Variables**: Create `.env` files for each service (root, backend, frontend)
- **Phase I Variables**: `LOG_LEVEL=DEBUG`, `APP_NAME=evolution-todo`
- **Phase II Variables**: Add `DATABASE_URL`, `BETTER_AUTH_SECRET`, `JWT_SECRET`, `FRONTEND_URL`, `BACKEND_URL`
- **Dependencies**: Manage via `uv add <package>` and `uv pip compile` for lock files

### Approval Process
- **Spec Approval**: User reviews and confirms spec.md in chat before running `/sp.plan`
- **Plan Approval**: User reviews and confirms plan.md in chat before running `/sp.tasks`
- **Task Approval**: User reviews and confirms tasks.md in chat before running `/sp.implement`
- **Mechanism**: Claude Code will pause and request explicit approval at each transition

### Code Documentation
- **Docstrings**: All public functions MUST have Google-style docstrings
- **Required Sections**: Description, Args, Returns, Raises (if applicable)
- **Example**:
  ```python
  def add_task(title: str, description: str) -> dict:
      """Add a new task to the task list.

      Args:
          title: Task title (required, non-empty)
          description: Task description (optional)

      Returns:
          dict: Created task with id, title, description, complete fields

      Raises:
          ValueError: If title is empty
      """
  ```

### Logging Standards
- **Library**: Python standard `logging` module
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Levels**: DEBUG for development, INFO for production, ERROR for failures
- **Requirement**: Log all CRUD operations at INFO level

## Phase-Specific Guidelines

### Phase I: In-Memory Python Console App

**Scope**: Implement Basic Level features (Add Task, Delete Task, Update Task, View Task List, Mark as Complete) in a CLI app with in-memory storage.

**Data Structure**: Use a list of dictionaries (e.g., `{'id': int, 'title': str, 'description': str, 'complete': bool}`).

**Interface**: Menu-driven CLI with user prompts.

**Technology**: Python 3.13+, UV, Claude Code, Spec-Kit Plus.

**Deliverables**:
- Specs in `/specs/` (with history tracking)
- Source in `/src/`
- `CLAUDE.md` with all sessions documented
- `README.md` with setup and usage instructions

**Definition of Done (MVP)**:
- ✅ All 5 basic features implemented and working (Add, Delete, Update, View, Mark Complete)
- ✅ In-memory storage functional with proper data structure
- ✅ Menu-driven CLI with user prompts and error handling
- ✅ 70%+ test coverage (verified with `pytest --cov`)
- ✅ All code PEP8 compliant (verified with `ruff check`)
- ✅ README.md with setup and usage instructions
- ✅ CLAUDE.md with all sessions documented
- ✅ All tests passing (`pytest` exits with 0)

**Definition of Done (Production-Ready)**:
- All MVP criteria PLUS:
- ✅ 80%+ test coverage
- ✅ Input validation for all edge cases
- ✅ Comprehensive error handling with user-friendly messages
- ✅ All functions have Google-style docstrings
- ✅ Logging implemented for all CRUD operations

**Phase I Feature Requirements** (implementation order):
- **High (Must Have for MVP)**: Add Task, View Task List, Mark Complete
- **Medium (Should Have)**: Update Task, Delete Task
- **Normal (Nice to Have)**: Input validation enhancements, colored CLI output

**Note**: The High/Medium/Low terminology above refers to which features must be implemented for MVP. This is separate from the task priority field (High/Medium/Low) that users set when adding tasks to their todo list.

**Branch**: `001-cli-todo-app`

### Phase II: Full-Stack Web Application

**Scope**: Transform the Phase I CLI application into a multi-user full-stack web application with persistent storage. Implement all Basic Level features (Add, Delete, Update, View, Mark Complete) as a web app supporting multiple users with authentication and database persistence. Features MUST be implemented gradually in hierarchical order per Principle VIII.

**Gradual Implementation Strategy**: Build features in ordered stages, each independently functional and testable. Start with foundational infrastructure (database, models), then backend API, then authentication, then frontend, finally integration. Each stage MUST be validated before proceeding.

**Technology Stack**:
- **Frontend**: Next.js 16+ (App Router), React 19+, TailwindCSS 3+
- **Backend**: FastAPI 0.115+, Python 3.13+
- **ORM**: SQLModel 0.0.22+
- **Database**: Neon Serverless PostgreSQL (cloud-hosted)
- **Authentication**: Better Auth (frontend), JWT validation (backend)
- **Development Tools**: UV (Python dependencies), pnpm (Node dependencies)
- **Deployment**: Vercel (frontend + backend as serverless functions)
- **Spec-Driven**: Claude Code + Spec-Kit Plus

**Monorepo Structure**:
```text
/
├── .spec-kit/
│   └── config.yaml          # Define specs_dir: specs, features_dir: specs/features
├── specs/
│   ├── overview.md          # High-level Phase II architecture
│   ├── architecture.md      # System design and component interactions
│   ├── features/
│   │   ├── [002-database-setup]/
│   │   ├── [003-task-crud-api]/
│   │   ├── [004-authentication]/
│   │   ├── [005-frontend-ui]/
│   │   └── [006-integration]/
│   ├── api/
│   │   └── rest-endpoints.md     # API contracts and schemas
│   ├── database/
│   │   └── schema.md             # Database models and relationships
│   └── ui/
│       ├── components.md         # Frontend component specifications
│       └── pages.md              # Page-level requirements
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel database models
│   │   ├── services/        # Business logic layer
│   │   ├── api/             # FastAPI routes and endpoints
│   │   ├── middleware/      # JWT validation, CORS, logging
│   │   └── main.py          # FastAPI application entry
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── .env                 # Backend environment variables
│   ├── pyproject.toml       # UV dependencies
│   └── CLAUDE.md            # Backend development sessions
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components (UI, forms, layouts)
│   │   ├── services/        # API client, auth utilities
│   │   └── lib/             # Shared utilities
│   ├── tests/
│   ├── .env.local           # Frontend environment variables
│   ├── package.json         # pnpm dependencies
│   └── CLAUDE.md            # Frontend development sessions
├── CLAUDE.md                # Root project sessions
├── docker-compose.yml       # Local development environment (optional)
└── README.md                # Complete setup instructions
```

**API Endpoints** (RESTful):
- `GET /api/{user_id}/tasks` - List all tasks for authenticated user
- `POST /api/{user_id}/tasks` - Create new task with title and description
- `GET /api/{user_id}/tasks/{id}` - Retrieve single task details by ID
- `PUT /api/{user_id}/tasks/{id}` - Update task title, description, or status
- `DELETE /api/{user_id}/tasks/{id}` - Delete task by ID
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

**Request/Response Format**:
```json
// POST /api/{user_id}/tasks
{
  "title": "Task title",
  "description": "Task description"
}

// Response (201 Created)
{
  "id": 1,
  "user_id": "user-uuid",
  "title": "Task title",
  "description": "Task description",
  "complete": false,
  "created_at": "2025-12-18T10:00:00Z",
  "updated_at": "2025-12-18T10:00:00Z"
}
```

**Authentication & Security Architecture**:
- **Frontend (Better Auth)**:
  - User signup/signin with email and password
  - Better Auth issues JWT tokens on successful authentication
  - Store JWT in secure HttpOnly cookies or localStorage
  - Attach JWT in `Authorization: Bearer <token>` header for all API calls
  - Implement protected routes (redirect to login if not authenticated)

- **Backend (JWT Validation)**:
  - Add middleware to verify JWT signature using shared secret
  - Extract `user_id` from validated JWT payload
  - Filter all database queries by authenticated `user_id`
  - Return 401 Unauthorized for missing or invalid tokens
  - Enforce task ownership (users can only access their own tasks)

- **Shared Secret**: Set `BETTER_AUTH_SECRET` environment variable in both frontend and backend

- **Security Requirements**:
  - MUST validate JWT on every backend request
  - MUST filter all data by authenticated user_id
  - MUST use HTTPS in production (Vercel provides this)
  - MUST NOT expose user data across accounts
  - MUST implement rate limiting on authentication endpoints

**Data Models**:

**Task Model** (SQLModel):
```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None, max_length=1000)
    complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**User Model** (Better Auth handles user storage, backend only needs user_id):
- Backend does NOT store user credentials
- Better Auth manages user table (email, hashed password, etc.)
- Backend receives user_id from validated JWT
- Backend Task model references user_id as foreign key concept

**Definition of Done (MVP)**:
- ✅ Database schema created in Neon PostgreSQL with Task model
- ✅ All 6 API endpoints implemented and functional
- ✅ Authentication: signup, signin, JWT validation working
- ✅ Backend enforces user data isolation (tasks filtered by user_id)
- ✅ Frontend: signup/signin pages, task list, add/edit/delete forms
- ✅ Frontend: responsive design with TailwindCSS
- ✅ Integration: frontend successfully calls backend API with JWT
- ✅ 75%+ test coverage for backend (verified with `pytest --cov`)
- ✅ All backend code PEP8 compliant (verified with `ruff check`)
- ✅ All backend tests passing (`pytest` exits with 0)
- ✅ Frontend builds successfully (`npm run build` succeeds)
- ✅ Both services documented in respective CLAUDE.md files
- ✅ README.md with complete setup instructions (database, env vars, running locally)
- ✅ Deployed to Vercel and publicly accessible
- ✅ Demo video (<90 seconds) showing: signup, signin, add task, view tasks, edit task, delete task, mark complete

**Definition of Done (Production-Ready)**:
- All MVP criteria PLUS:
- ✅ 85%+ test coverage for backend
- ✅ Frontend unit tests for components and services
- ✅ E2E tests covering critical user journeys
- ✅ Comprehensive error handling (network failures, validation errors, auth errors)
- ✅ Input validation on both frontend and backend
- ✅ Loading states and user feedback for all async operations
- ✅ Proper CORS configuration for production domains
- ✅ Database connection pooling and retry logic
- ✅ Logging for all API requests and errors
- ✅ Rate limiting on authentication endpoints
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ All functions have Google-style docstrings

**Phase II Feature Implementation Hierarchy** (MUST follow this order):

**Stage 1: Foundation - Database & Models** (Branch: `002-database-setup`)
- Set up Neon PostgreSQL database
- Configure DATABASE_URL environment variable
- Implement SQLModel Task model
- Create database migration scripts
- Write unit tests for model validation
- **Acceptance**: Can create/read Task records programmatically

**Stage 2: Backend API - CRUD Operations** (Branch: `003-task-crud-api`)
- Implement FastAPI application structure
- Create all 6 API endpoints (GET, POST, PUT, DELETE, PATCH)
- Add request/response validation with Pydantic
- Implement service layer for business logic
- Write integration tests for all endpoints
- **Acceptance**: API endpoints work with curl/Postman (no auth yet)

**Stage 3: Authentication & Security** (Branch: `004-authentication`)
- Set up Better Auth on frontend for user management
- Implement JWT validation middleware in backend
- Add user_id filtering to all database queries
- Configure BETTER_AUTH_SECRET in both services
- Implement protected API routes
- Write tests for authentication flow
- **Acceptance**: Only authenticated users can access their tasks

**Stage 4: Frontend UI** (Branch: `005-frontend-ui`)
- Set up Next.js 16 with App Router
- Create signup/signin pages with Better Auth integration
- Implement task list page with CRUD forms
- Add TailwindCSS styling and responsive design
- Implement API client service with JWT header injection
- Add loading states and error handling
- **Acceptance**: Full UI works with mock API data

**Stage 5: Integration & Deployment** (Branch: `006-integration`)
- Connect frontend to backend API
- Configure CORS for Vercel deployment
- Set up environment variables in Vercel
- Deploy both services to Vercel
- Run E2E tests against deployed application
- Record demo video showing all features
- **Acceptance**: Deployed app fully functional, demo video complete

**Branch Sequence**: `002-database-setup` → `003-task-crud-api` → `004-authentication` → `005-frontend-ui` → `006-integration`

**Deliverables**:
- GitHub repository with complete Phase II implementation
- Constitution file (this document) at `.specify/memory/constitution.md`
- Specs in `/specs/` with history tracking for each feature
- Source code split into `/backend/` and `/frontend/` directories
- CLAUDE.md files in root, backend, and frontend (all sessions documented)
- README.md with comprehensive setup instructions
- Deployed application on Vercel (provide URL)
- Demo video (<90 seconds) demonstrating:
  1. User signup and signin
  2. Adding a new task
  3. Viewing task list
  4. Editing a task
  5. Deleting a task
  6. Marking task as complete
  7. Data isolation (create second user, verify separate task lists)

**Constitution Compliance**:
- MUST maintain SDD workflow with separate specs for each feature stage
- MUST follow gradual implementation per Principle VIII
- MUST implement authentication per Principle VII (user data isolation)
- MUST document API contracts in `/specs/api/rest-endpoints.md`
- MUST use monorepo structure per Principle IV
- MUST achieve Definition of Done before claiming Phase II complete

### Phase III: AI-Powered Todo Chatbot

**Scope**: Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture. Users interact via conversational UI instead of traditional forms. All Basic Level features (Add, Delete, Update, View, Mark Complete) accessible through natural language commands.

**Core Architecture**: Stateless chat endpoint + OpenAI Agents SDK + MCP Tools + Database persistence
- Chat endpoint: POST /api/{user_id}/chat (receives message, returns AI response)
- Conversation state stored in database (conversations, messages tables)
- Server holds NO state between requests (horizontally scalable)
- MCP server exposes 5 tools: add_task, list_tasks, complete_task, delete_task, update_task

**Technology Stack**:
- **Frontend**: OpenAI ChatKit (conversational UI)
- **Backend**: FastAPI (chat endpoint + MCP server)
- **AI Framework**: OpenAI Agents SDK (agent orchestration)
- **MCP**: Official MCP SDK (tool server)
- **Database**: Neon PostgreSQL (tasks + conversations + messages)
- **Authentication**: Better Auth + JWT (same as Phase II)

**Database Models**:
- Task: (existing from Phase II)
- Conversation: user_id, id, created_at, updated_at
- Message: user_id, conversation_id, role (user/assistant), content, created_at

**MCP Tools Specification** (each tool stateless, stores to DB):
- `add_task(user_id, title, description)` → Returns task_id, status, title
- `list_tasks(user_id, status)` → Returns array of task objects
- `complete_task(user_id, task_id)` → Returns task_id, status, title
- `delete_task(user_id, task_id)` → Returns task_id, status, title
- `update_task(user_id, task_id, title?, description?)` → Returns task_id, status, title

**Natural Language Examples**:
- "Add a task to buy groceries" → calls add_task
- "Show me pending tasks" → calls list_tasks with status="pending"
- "Mark task 3 as done" → calls complete_task
- "Delete the meeting task" → calls list_tasks then delete_task

**Stateless Request Cycle** (critical for scalability):
1. Receive user message
2. Fetch conversation history from database
3. Build message array (history + new message)
4. Store user message in database
5. Run OpenAI Agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server ready for next request (no state held)

**OpenAI ChatKit Setup**:
- Domain allowlist: Add deployed frontend URL to OpenAI platform
- Domain key: Configure NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- Required for hosted ChatKit (localhost works without)

**Definition of Done**:
- ✅ MCP server with all 5 tools functional
- ✅ OpenAI Agent successfully calls tools based on natural language
- ✅ Chat endpoint persists conversations to database
- ✅ ChatKit UI integrated and functional
- ✅ Stateless architecture (server restarts don't lose conversations)
- ✅ All Phase II features accessible via chatbot
- ✅ Agent behavior handles errors gracefully
- ✅ Authentication enforces user isolation
- ✅ Deployed chatbot URL functional
- ✅ Demo video (<90 seconds) showing natural language interactions

**Deliverables**:
- `/frontend` - ChatKit-based UI
- `/backend` - FastAPI + Agents SDK + MCP server
- `/specs/features/007-chatbot-mcp/` - Spec, plan, tasks
- Database migration for conversations and messages
- README with MCP server setup instructions
- Deployed application with chatbot interface

**Branch**: `007-chatbot-mcp`

**Constitution Compliance**:
- Design chatbot as Reusable Intelligence component (Principle III)
- MCP tools follow stateless pattern (Principle VII - scalability)
- Multi-language support (Urdu) earns +100 bonus (Principle VI)
- Voice command integration earns +200 bonus (Principle VI)
- Follow SDD workflow: spec → plan → tasks → implement (Principle II)

### Phase IV: Local Kubernetes Deployment

**Scope**: Deploy the Phase III Todo Chatbot on a local Kubernetes cluster using Minikube, Helm Charts, and AI-assisted DevOps tools. Containerize both frontend and backend applications. Features MUST be implemented gradually following the SDD workflow.

**Objective**: Demonstrate cloud-native deployment skills by containerizing the chatbot application, creating Helm charts, and deploying to a local Kubernetes cluster with AI-assisted tooling.

**Core Architecture**: Docker containers + Kubernetes (Minikube) + Helm Charts + AI DevOps tools
- Frontend: Next.js application containerized and deployed as Kubernetes Deployment/Service
- Backend: FastAPI + MCP server containerized and deployed as Kubernetes Deployment/Service
- Database: Neon PostgreSQL (external, cloud-hosted - no change from Phase III)
- Container Registry: Local Minikube registry or Docker Hub

**Technology Stack**:
- **Containerization**: Docker (Docker Desktop)
- **Docker AI**: Docker AI Agent (Gordon) - requires Docker Desktop 4.53+
- **Orchestration**: Kubernetes (Minikube)
- **Package Manager**: Helm Charts
- **AI DevOps**: kubectl-ai (Google Cloud Platform), Kagent (CNCF sandbox project)
- **Application**: Phase III Todo Chatbot (frontend + backend)

**AIOps Tools Specification**:

**Docker AI Agent (Gordon)**:
- Embedded AI assistant in Docker Desktop and CLI
- Enable in Docker Desktop 4.53+: Settings > Beta features > toggle on
- Commands: `docker ai "What can you do?"`, `docker ai "containerize this app"`
- Uses LLMs to generate Dockerfiles, troubleshoot container issues, manage resources
- Supports MCP integration for connecting to external tools
- Note: If Gordon is unavailable in your region, use standard Docker CLI or ask Claude Code to generate docker commands

**kubectl-ai** (Google Cloud Platform):
- Natural language interface to Kubernetes
- Install via krew: `kubectl krew install ai`, then use as `kubectl ai`
- Supports multiple LLMs: Gemini, OpenAI, Grok, local models via Ollama
- Read-only by default, requests permission before modifying resources
- Example: `kubectl ai "deploy the todo frontend with 2 replicas"`
- Example: `kubectl ai "scale the backend to handle more load"`
- Example: `kubectl ai "check why the pods are failing"`

**Kagent** (CNCF Sandbox Project):
- Open-source framework for AI agents in Kubernetes
- Built on A2A protocol, Agent Development Kit (ADK), and MCP
- Provides MCP server with tools for K8s, Helm, Prometheus, Grafana
- Supports multiple LLM providers: OpenAI, Anthropic, Azure, Ollama
- Agents are Kubernetes custom resources
- Example: `kagent "analyze the cluster health"`
- Example: `kagent "optimize resource allocation"`

**Requirements**:
- Containerize frontend and backend applications using Docker/Gordon
- Create multi-stage Dockerfiles for optimized image sizes
- Create Helm charts for deployment (use kubectl-ai and/or kagent to generate)
- Deploy to Minikube locally with proper resource limits
- Configure environment variables via Kubernetes Secrets/ConfigMaps
- Implement health checks (liveness/readiness probes)
- Set up Kubernetes Services for internal communication

**Gradual Implementation Strategy**:

**Stage 1: Docker Containerization** (Branch: `008-docker-containerization`)
- Create Dockerfile for backend (FastAPI + MCP server)
- Create Dockerfile for frontend (Next.js)
- Use multi-stage builds for optimized images
- Test containers locally with docker-compose
- Use Gordon for AI-assisted Dockerfile generation and troubleshooting
- **Acceptance**: Both containers run locally and communicate successfully

**Stage 2: Minikube Setup** (Branch: `009-minikube-setup`)
- Install and configure Minikube locally
- Enable required addons (ingress, registry, metrics-server)
- Configure kubectl context for Minikube
- Verify cluster health with kubectl-ai
- **Acceptance**: Minikube cluster running with addons enabled

**Stage 3: Helm Charts Creation** (Branch: `010-helm-charts`)
- Create Helm chart structure for todo-chatbot
- Define templates for Deployments, Services, ConfigMaps, Secrets
- Use kubectl-ai/kagent to assist with manifest generation
- Configure values.yaml for environment-specific settings
- Implement Ingress for external access
- **Acceptance**: `helm lint` passes, charts are well-structured

**Stage 4: Local Deployment** (Branch: `011-local-k8s-deploy`)
- Deploy Helm charts to Minikube
- Verify all pods are running and healthy
- Test application functionality through Ingress
- Configure horizontal pod autoscaling (optional)
- Document deployment process in README
- **Acceptance**: Application fully functional on Minikube

**Project Structure for Phase IV**:
```text
/
├── phase-4-k8s/
│   ├── docker/
│   │   ├── backend/
│   │   │   └── Dockerfile
│   │   └── frontend/
│   │       └── Dockerfile
│   ├── helm/
│   │   └── todo-chatbot/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-minikube.yaml
│   │       └── templates/
│   │           ├── backend-deployment.yaml
│   │           ├── backend-service.yaml
│   │           ├── frontend-deployment.yaml
│   │           ├── frontend-service.yaml
│   │           ├── configmap.yaml
│   │           ├── secrets.yaml
│   │           └── ingress.yaml
│   ├── scripts/
│   │   ├── build-images.sh
│   │   ├── deploy-minikube.sh
│   │   └── cleanup.sh
│   └── CLAUDE.md
├── specs/
│   └── features/
│       └── 008-local-k8s-deployment/
│           ├── spec.md
│           ├── plan.md
│           └── tasks.md
└── README.md (updated with Phase IV instructions)
```

**Definition of Done (MVP)**:
- ✅ Backend Dockerfile created and builds successfully
- ✅ Frontend Dockerfile created and builds successfully
- ✅ Docker images optimized with multi-stage builds (<500MB each)
- ✅ docker-compose.yml for local testing works
- ✅ Minikube cluster running with required addons
- ✅ Helm chart created with proper structure
- ✅ All Kubernetes manifests valid (`kubectl apply --dry-run=client`)
- ✅ Application deployed to Minikube and accessible
- ✅ Health checks (liveness/readiness probes) implemented
- ✅ Environment variables properly configured via ConfigMaps/Secrets
- ✅ AI tools (Gordon, kubectl-ai, or kagent) used and documented
- ✅ README with local Minikube deployment instructions
- ✅ Demo showing: container builds, Minikube deployment, app functionality

**Definition of Done (Production-Ready)**:
- All MVP criteria PLUS:
- ✅ Horizontal Pod Autoscaler configured
- ✅ Resource limits and requests defined for all containers
- ✅ Network policies for pod-to-pod communication
- ✅ Persistent volume claims for any stateful data
- ✅ Helm chart passes `helm lint` with no warnings
- ✅ Rollback strategy documented and tested
- ✅ Monitoring with Prometheus metrics endpoint
- ✅ Logging aggregation configured

**Branch Sequence**: `008-docker-containerization` → `009-minikube-setup` → `010-helm-charts` → `011-local-k8s-deploy`

**Deliverables**:
- GitHub repository with Phase IV implementation
- Dockerfiles for frontend and backend
- Helm charts in `/phase-4-k8s/helm/`
- Deployment scripts for Minikube
- CLAUDE.md documenting AI tool usage (Gordon, kubectl-ai, kagent)
- README with comprehensive local deployment instructions
- Demo video (<90 seconds) showing:
  1. Docker image builds
  2. Minikube cluster setup
  3. Helm deployment process
  4. Application running on Kubernetes
  5. AI tool usage (at least one: Gordon, kubectl-ai, or kagent)

**Constitution Compliance**:
- Cloud-Native Blueprints (+200 bonus, Principle VI)
- Demonstrate scalability (Principle VII)
- Document infrastructure as code in `/specs/infrastructure/`
- Follow SDD workflow: spec → plan → tasks → implement (Principle II)
- Use AI-assisted tools for DevOps automation
- No manual Kubernetes manifest writing without AI assistance

### Phase V: Advanced Cloud Deployment

**Scope**: Deploy the Dapr-enabled Todo Chatbot to a production-grade Kubernetes cluster (OKE Always Free), integrate with a managed Kafka-compatible service (Redpanda Cloud), set up robust CI/CD with GitHub Actions and OIDC, and implement comprehensive observability using Grafana Cloud and OpenTelemetry. This phase includes implementing advanced features like recurring tasks and reminders using Dapr.

**Objective**: Master advanced cloud-native deployment practices, leveraging free-tier services to build a resilient, scalable, and observable event-driven microservices architecture on Kubernetes.

**Core Architecture**: Kubernetes (OKE) + Dapr + Managed Kafka (Redpanda Cloud) + GitHub Actions (CI/CD) + Grafana Cloud (Observability)
- **Frontend/Backend**: Existing Next.js and FastAPI applications (containerized from Phase IV).
- **Orchestration**: Oracle Kubernetes Engine (OKE) Always Free tier.
- **Event Bus**: Redpanda Cloud (Kafka-compatible) for Pub/Sub.
- **Distributed Application Runtime**: Dapr for state management, pub/sub, secrets, and scheduled jobs (bindings).
- **Database**: Neon Serverless PostgreSQL (external, cloud-hosted - no change from Phase IV).
- **CI/CD**: GitHub Actions with OIDC Workload Identity for secure, automated deployments.
- **Observability**: Grafana Cloud Free Tier (Prometheus, Loki, Tempo) integrated with OpenTelemetry Collector.

**Technology Stack**:
- **Kubernetes**: Oracle Kubernetes Engine (OKE) Always Free
- **Dapr**: Latest stable version
- **Kafka-compatible Service**: Redpanda Cloud (Serverless)
- **CI/CD**: GitHub Actions, Helm
- **Container Registry**: Oracle Container Registry (OCIR) or Docker Hub
- **Observability**: Grafana Cloud Free Tier, OpenTelemetry Collector
- **Infrastructure as Code (Optional but Recommended)**: Terraform (for OKE cluster provisioning, if not manual)
- **Application**: Phase III Todo Chatbot (frontend + backend)

**Requirements**:
- Deploy Dapr control plane and components to OKE in HA mode (`--enable-ha=true`).
- Configure Dapr Pub/Sub component to use Redpanda Cloud (Kafka-compatible serverless).
- Implement Dapr state management for conversation state (optional, or continue with PostgreSQL).
- Implement Dapr Bindings (Jobs API) for scheduling recurring tasks/reminders (not cron polling).
- Utilize Dapr Secrets building block for secure credential management.
- **Advanced Security (Production)**: Deploy External Secrets Operator (ESO) to sync secrets from cloud providers to Kubernetes without committing to Git.
- Set up a GitHub Actions workflow for building, pushing (to OCIR/Docker Hub), and deploying Helm charts to OKE.
- Implement OIDC Workload Identity in GitHub Actions for secure authentication to OKE (eliminates static credentials).
- Integrate security scanning: Trivy for image vulnerabilities, Kube-Linter for manifest static analysis.
- Configure Dapr to emit OpenTelemetry traces, metrics, and logs (zero-code instrumentation).
- Deploy an OpenTelemetry Collector to forward telemetry data to Grafana Cloud Free Tier.
- Configure Grafana Cloud to visualize application metrics, logs, and distributed traces.
- **Optional but Recommended**: Set up GitOps with Argo CD or Flux CD for pull-based deployments (Git as single source of truth).
- Implement advanced application features: Recurring Tasks, Due Dates & Reminders, Priorities, Tags, Search, Filter, Sort.

**Gradual Implementation Strategy**:

**Stage 1: OKE Cluster & Basic Dapr Setup** (Branch: `012-oke-dapr-setup`)
- Provision OKE cluster using the Oracle Cloud Always Free tier.
- Configure `kubectl` to connect to the OKE cluster.
- Install Dapr on OKE using Helm.
- Verify Dapr control plane health.
- **Acceptance**: OKE cluster provisioned, Dapr installed and healthy.

**Stage 2: Redpanda Cloud & Dapr Pub/Sub** (Branch: `013-redpanda-pubsub`)
- Sign up for Redpanda Cloud and create a serverless cluster (or alternative free-tier Kafka).
- Create required topics (e.g., `task-events`, `reminders`).
- Configure Dapr Pub/Sub component to connect to Redpanda Cloud.
- Modify backend to publish/subscribe events via Dapr Pub/Sub API.
- **Acceptance**: Backend successfully publishes and consumes messages via Dapr/Redpanda.

**Stage 3: Advanced Dapr Features & App Integration** (Branch: `014-dapr-advanced-features`)
- Implement Dapr bindings for scheduling (e.g., cron bindings for recurring tasks).
- Integrate Dapr state management or continue using PostgreSQL for conversation state (review trade-offs).
- Utilize Dapr Secrets for database credentials and API keys.
- Develop/refactor application logic for advanced features (recurring tasks, reminders).
- Update Helm charts to include Dapr component definitions.
- **Acceptance**: Advanced features functional locally on Minikube with Dapr components.

**Stage 4: CI/CD with GitHub Actions & OIDC** (Branch: `015-github-actions-cicd`)
- Configure OIDC Workload Identity for GitHub Actions to authenticate with OKE.
- Create GitHub Actions workflows for:
    - Building and pushing Docker images to OCIR/Docker Hub.
    - Deploying Helm charts to OKE.
- Implement environment-specific deployments.
- **Acceptance**: Automated deployments to OKE triggered by Git pushes.

**Stage 5: Observability with Grafana Cloud** (Branch: `016-observability`)
- Configure Dapr to emit OpenTelemetry telemetry data (automatic with Dapr config).
- Deploy OpenTelemetry Collector on OKE.
- Set up Grafana Cloud free tier account (10k metrics, 50GB logs, 50GB traces).
- Configure OpenTelemetry Collector to export data to Grafana Cloud (Prometheus, Loki, Tempo).
- Create Grafana dashboards for Dapr and application metrics, logs, and distributed traces.
- Set up alerts for critical application and infrastructure issues.
- **Acceptance**: Comprehensive monitoring and logging visible in Grafana Cloud, distributed tracing working end-to-end.

**Stage 6 (Optional): GitOps Deployment** (Branch: `017-gitops-argocd`)
- Install Argo CD or Flux CD on OKE cluster.
- Create GitOps repository with application manifests and Dapr components.
- Configure Argo CD applications for automated sync from Git.
- Implement sync policies (automated pruning, self-healing).
- Update GitHub Actions to commit manifest changes to GitOps repo (not direct deployment).
- **Acceptance**: Changes to GitOps repo automatically reconciled to cluster, rollback working via Git revert.

**Project Structure for Phase V**:
```text
/
├── phase-5-cloud-deployment/
│   ├── IMPLEMENTATION_GUIDE.md    # Combined research guide (Claude + Gemini)
│   ├── oci-setup/                 # Terraform/CLI scripts for OKE provisioning (optional)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── dapr-components/           # Dapr component YAMLs (pubsub, state, secrets, bindings)
│   │   ├── kafka-pubsub.yaml
│   │   ├── statestore.yaml
│   │   ├── kubernetes-secrets.yaml
│   │   └── dapr-config.yaml
│   ├── observability/             # OpenTelemetry and Grafana Cloud configs
│   │   ├── otel-collector.yaml
│   │   └── grafana-dashboards/
│   ├── gitops/ (optional)         # GitOps repository structure
│   │   ├── apps/
│   │   ├── dapr-components/
│   │   └── argocd-applications/
│   ├── .github/
│   │   └── workflows/             # GitHub Actions workflows with OIDC
│   │       ├── build-and-deploy.yaml
│   │       ├── security-scan.yaml
│   │       └── ...
│   ├── kafka/                     # Kafka cluster manifests (Strimzi)
│   │   └── kafka-cluster.yaml
│   └── CLAUDE.md
├── specs/
│   └── features/
│       └── 012-advanced-cloud-deployment/
│           ├── spec.md
│           ├── plan.md
│           └── tasks.md
└── README.md (updated with Phase V instructions)
```

**Definition of Done (MVP)**:
- ✅ OKE cluster provisioned and running on Always Free tier (2 nodes, 4 vCPUs total, 24GB RAM total).
- ✅ Dapr installed on OKE with HA mode enabled (`--enable-ha=true`).
- ✅ Redpanda Cloud serverless cluster configured and integrated with Dapr Pub/Sub component.
- ✅ Kafka topics created: `task-events`, `reminders`, `task-updates`.
- ✅ Backend application publishes/subscribes messages via Dapr Pub/Sub API.
- ✅ Advanced features implemented: Recurring Tasks (with Dapr Jobs API), Due Dates, Reminders.
- ✅ Intermediate features implemented: Priorities, Tags, Search, Filter, Sort.
- ✅ GitHub Actions workflow with OIDC Workload Identity deploys to OKE using Helm (no static credentials).
- ✅ Security scanning integrated: Trivy for images, Kube-Linter for manifests.
- ✅ Application deployed and accessible via Ingress with LoadBalancer.
- ✅ OpenTelemetry Collector deployed and forwarding data to Grafana Cloud.
- ✅ Basic Grafana dashboards showing: application metrics, logs, distributed traces.
- ✅ Health checks (liveness/readiness probes) configured for all pods.
- ✅ Resource limits and requests defined for all containers.
- ✅ README with complete OKE setup, deployment, and troubleshooting instructions.
- ✅ Demo video (<90 seconds) showcasing: OKE deployment, Dapr features (recurring task triggering), CI/CD pipeline with OIDC, observability in Grafana.

**Definition of Done (Production-Ready)**:
- All MVP criteria PLUS:
- ✅ Full Dapr integration with HA mode (Pub/Sub, State Management, Bindings/Jobs, Secrets, Service Invocation).
- ✅ Dapr control plane: multiple replicas, dedicated namespace, priority classes, resource limits.
- ✅ All advanced features fully functional: Recurring Tasks, Due Dates, Reminders, Priorities, Tags, Search, Filter, Sort.
- ✅ External Secrets Operator (ESO) deployed for advanced secret management (optional enhancement).
- ✅ Automated CI/CD pipeline with comprehensive testing: unit tests, integration tests, E2E tests.
- ✅ Security pipeline: vulnerability scanning (Trivy), manifest linting (Kube-Linter), SBOM generation.
- ✅ Comprehensive observability: distributed tracing across all services, custom dashboards, log aggregation, alerting rules.
- ✅ Horizontal Pod Autoscaling (HPA) configured based on CPU/memory metrics.
- ✅ Advanced security: RBAC with least privilege, Network Policies, Pod Security Standards, secrets rotation strategy.
- ✅ Infrastructure as Code: Terraform/CLI scripts for OKE cluster provisioning and configuration.
- ✅ GitOps deployment: Argo CD or Flux CD configured with automated sync and self-healing (optional but recommended).
- ✅ Pod anti-affinity rules for high availability.
- ✅ PodDisruptionBudgets defined for critical services.
- ✅ Documented disaster recovery, backup strategy, and rollback procedures.
- ✅ Performance testing and optimization completed.
- ✅ Cost monitoring dashboard configured (Oracle Cloud Cost Analysis).

**Branch Sequence**: `012-oke-dapr-setup` → `013-redpanda-pubsub` → `014-dapr-advanced-features` → `015-github-actions-cicd` → `016-observability` → `017-gitops-argocd` (optional)

**Deliverables**:
- GitHub repository with complete Phase V implementation.
- IMPLEMENTATION_GUIDE.md in phase-5-cloud-deployment/ (combined research from Claude + Gemini).
- Terraform/CLI scripts for OKE provisioning (optional but recommended for IaC).
- Dapr component YAMLs: Pub/Sub, State, Secrets, Config (all as configuration-as-code).
- OpenTelemetry Collector configuration and deployment manifests.
- GitHub Actions workflows with OIDC authentication (no static credentials stored).
- Security scanning reports: Trivy vulnerability scans, Kube-Linter manifest analysis.
- GitOps repository with application manifests and Argo CD applications (if implemented).
- CLAUDE.md documenting AI tool usage and all development sessions.
- README.md with comprehensive setup instructions:
  - Oracle Cloud account setup
  - OKE cluster provisioning
  - Redpanda Cloud configuration
  - GitHub OIDC setup
  - Grafana Cloud integration
  - Local testing with Minikube
  - Troubleshooting guide
- Publicly accessible application on OKE with custom domain/ingress.
- Grafana Cloud dashboards showing:
  - Application performance metrics
  - Infrastructure health (node CPU, memory, pod status)
  - Distributed traces across Dapr service invocations
  - Log aggregation and search
  - Alert rules configured
- Demo video (<90 seconds) demonstrating:
  1. OKE cluster with deployed application
  2. Advanced features: adding recurring task, reminder triggering, priority/tag filtering
  3. Event-driven flow: task created → Kafka event → consumer processing
  4. GitHub Actions CI/CD with OIDC deploying a change
  5. Real-time observability in Grafana: metrics dashboard, distributed trace, logs
  6. (Optional) GitOps: Git commit → Argo CD sync → automatic deployment

**Constitution Compliance**:
- Complete Cloud-Native transformation with production-ready patterns (Principle VI - Cloud-Native Blueprints +200 bonus).
- Full observability with zero-code instrumentation (Principle VII - professional quality and scalability).
- Demonstrate all advanced features including event-driven architecture (Principle VI - maximum bonus points).
- Strict adherence to SDD workflow for all stages (Principle I & II - spec → plan → tasks → implement).
- Gradual implementation per Principle VIII (5-6 stages, each independently testable).
- Use AI-assisted tools for DevOps automation (kubectl-ai, Docker AI if available).
- Modern security practices: OIDC for CI/CD, ESO for secrets, RBAC with least privilege (Principle VII).
- Infrastructure as Code with Terraform (optional) for reproducibility (Principle IV - clean structure).
- GitOps for declarative deployments (optional) aligns with Principle V (no manual interventions).
- Document all implementation decisions and AI tool usage in CLAUDE.md (Principle V).
- Reference IMPLEMENTATION_GUIDE.md for detailed step-by-step guidance.

## Governance

This constitution supersedes all other practices. Amendments require:
1. Documented rationale for change
2. Approval from project lead or team consensus
3. Migration plan for impacted specs and code
4. Version increment per semantic versioning

All pull requests and reviews MUST verify compliance with this constitution. Complexity MUST be justified (reference Principle IV and plan-template.md Complexity Tracking section). Any code generated by Claude Code MUST be traced to its originating spec.

Use `CLAUDE.md` for runtime development guidance and session tracking.

**Version**: 1.7.0 | **Ratified**: 2026-01-25 | **Last Amended**: 2026-01-25
