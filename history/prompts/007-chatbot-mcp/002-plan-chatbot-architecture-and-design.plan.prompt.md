---
id: 002
title: Plan chatbot architecture and design
stage: plan
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: 007-chatbot-mcp
branch: phase-3-chatbot
user: ashfaq
command: /sp.plan
labels: ["plan", "architecture", "chatbot", "mcp", "phase-3", "design", "contracts", "research"]
links:
  spec: specs/features/007-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/features/007-chatbot-mcp/plan.md
  - specs/features/007-chatbot-mcp/research.md
  - specs/features/007-chatbot-mcp/data-model.md
  - specs/features/007-chatbot-mcp/contracts/chat-api.yaml
  - specs/features/007-chatbot-mcp/contracts/mcp-tools.yaml
  - specs/features/007-chatbot-mcp/quickstart.md
  - CLAUDE.md
tests:
  - (none - planning phase)
---

## Prompt

User invoked `/sp.plan` to create an implementation plan for the AI-Powered Todo Chatbot feature (007-chatbot-mcp) based on the clarified specification.

## Response snapshot

**Planning Session Summary**:

Successfully created comprehensive implementation plan with Phase 0 (Research) and Phase 1 (Design) completed.

### Phase 0: Research & Technology Validation

Investigated and resolved 7 technical unknowns:

**1. OpenAI Agents SDK Integration**
- **Decision**: Use OpenAI Swarm framework (lightweight multi-agent orchestration)
- **Rationale**: Stateless by design, native function calling support, official OpenAI support
- **Installation**: `uv add openai git+https://github.com/openai/swarm.git`

**2. Official MCP SDK Usage**
- **Decision**: Implement MCP tools as Python functions compatible with OpenAI function calling
- **Rationale**: Simplified architecture, no separate server process, stateless, direct integration with Swarm
- **Pattern**: 5 functions (add_task, list_tasks, complete_task, delete_task, update_task) registered with Swarm Agent

**3. OpenAI ChatKit Setup**
- **Decision**: Use OpenAI ChatKit with domain verification (production), localhost (dev)
- **Setup**: Domain allowlist on OpenAI Platform, `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` env var
- **Integration**: React component with JWT injection for backend auth

**4. Conversation Context Management**
- **Decision**: Sliding window (10-15 recent messages) + GPT-3.5-turbo summarization (max 500 tokens)
- **Implementation**: tiktoken for token counting, summary stored in Conversation.summary field
- **Regeneration**: Every ~20 messages to maintain compact context

**5. Exponential Backoff + Circuit Breaker**
- **Decision**: tenacity library + custom circuit breaker decorator
- **Pattern**: 3 retries (1s, 2s, 4s delays), circuit opens for 60s after 5 consecutive failures
- **Exceptions**: Retry on APIError/APIConnectionError/RateLimitError, fail immediately on AuthenticationError/BadRequestError

**6. Browser Web Speech API**
- **Decision**: Native `webkitSpeechRecognition`/`SpeechRecognition` with React hooks
- **Rationale**: Zero cost, low latency, no external dependencies, supports Urdu (TC-009)
- **Browsers**: Chrome/Edge (full support), Safari (iOS 14.5+), Firefox (no support)

**7. Urdu Language Support**
- **Decision**: GPT-4 native multilingual with system prompt engineering
- **Pattern**: Auto-detect user language, respond in same language
- **No Special Config**: GPT-4 handles Urdu natively, Web Speech API supports `ur-PK`

### Phase 1: Design & Contracts

**Data Model** (`data-model.md`):
- **Conversation**: id, user_id, summary (TEXT, nullable), created_at, updated_at
  - Summary field stores compact context (max 500 tokens) for sliding window strategy
  - Regenerated every ~20 messages
- **Message**: id, conversation_id, user_id, role (user/assistant), content, created_at
  - Immutable messages (no UPDATE operations per spec Q4)
  - CASCADE delete when conversation deleted
- **Task**: Existing from Phase II, no changes (accessed via MCP tools)

**Indexes**:
- `idx_conversations_user_id` ON conversations(user_id)
- `idx_conversations_updated_at` ON conversations(updated_at DESC)
- `idx_messages_conversation_created` ON messages(conversation_id, created_at DESC)
- `idx_messages_user_id` ON messages(user_id)

**API Contracts**:

1. **chat-api.yaml** (OpenAPI 3.0.3):
   - `POST /api/{user_id}/chat` - Send message to chatbot
   - Request: `{message: string, conversation_id?: integer}`
   - Response: `{conversation_id: integer, message: string, timestamp: datetime, tools_called?: string[]}`
   - Security: JWT Bearer token, user_id extracted from JWT claims (not URL parameter)
   - Error codes: 400 (bad request), 401 (unauthorized), 403 (JWT mismatch), 404 (conversation not found), 500 (internal error), 503 (circuit breaker open)

2. **mcp-tools.yaml**:
   - `add_task(user_id, title, description?)` → `{task_id, status, title}`
   - `list_tasks(user_id, status?)` → `{tasks: [...], count}`
   - `complete_task(user_id, task_id)` → `{task_id, status, title}`
   - `delete_task(user_id, task_id)` → `{task_id, status, title}`
   - `update_task(user_id, task_id, title?, description?)` → `{task_id, status, title}`

**Quickstart Guide** (`quickstart.md`):
- Environment setup (backend + frontend env vars)
- Database migration (Alembic script for conversations + messages tables)
- MCP tools implementation (5 Python functions)
- Chat service with Swarm integration
- Chat endpoint with stateless architecture
- ChatKit integration (frontend)
- Voice input component (bonus)
- Testing guide (unit, integration, E2E)
- Deployment guide (OpenAI Platform setup, Vercel)
- Troubleshooting section

**Project Structure**:
- Extends Phase II monorepo (`/backend/`, `/frontend/`)
- Backend adds: `src/mcp/` (tools), `src/services/` (chat_service, context_service), `src/api/chat.py`, `src/models/` (conversation, message), `src/middleware/circuit_breaker.py`
- Frontend adds: `src/components/` (ChatInterface, VoiceInput), `src/app/chat/page.tsx`, `src/services/speech.ts`, `src/lib/chatkit-config.ts`

**Constitution Check** (Re-evaluated):
✅ All principles pass:
- I: SDD ✅ (spec → clarify → plan workflow followed)
- II: Agentic Workflow ✅ (documented in PHRs)
- III: Reusable Intelligence ✅ (MCP tools, +200 bonus potential)
- IV: Clean Code ✅ (extends Phase II structure, PEP8, separation of concerns)
- V: No Manual Interventions ✅ (all via Claude Code)
- VI: Bonus Alignment ✅ (+500 potential: Reusable Intelligence +200, Urdu +100, Voice +200)
- VII: Ethical & Compliant ✅ (JWT validation, user isolation, stateless scaling)
- VIII: Gradual Implementation ✅ (8-stage hierarchy defined)

**No violations detected**. Complexity justified for MCP architecture (hackathon requirement), sliding window (token limits), stateless design (scalability).

### Deliverables Created

1. **plan.md** - Comprehensive implementation plan with Technical Context, Constitution Check, Project Structure, Phase 0-1 execution
2. **research.md** - 7 research findings with decisions, rationale, alternatives, implementation guidance, configuration
3. **data-model.md** - Database schema (Conversation, Message, Task), indexes, migrations, SQLModel definitions
4. **contracts/chat-api.yaml** - OpenAPI 3.0.3 specification for chat endpoint with all response codes
5. **contracts/mcp-tools.yaml** - 5 MCP tool signatures with parameters, returns, examples, implementation notes
6. **quickstart.md** - End-to-end implementation guide with code snippets, testing, deployment

### Technologies Validated

- **AI/Agents**: OpenAI Swarm, OpenAI Agents SDK, GPT-4 (main), GPT-3.5-turbo (summarization)
- **MCP**: Python functions as tools (not separate server process)
- **Context Management**: tiktoken (token counting), sliding window (15 messages), summary field (500 tokens)
- **Resilience**: tenacity (retry), custom circuit breaker (5 failures → 60s open)
- **Frontend**: OpenAI ChatKit, Web Speech API (`ur-PK` for Urdu)
- **Database**: Neon PostgreSQL (existing + Conversation/Message tables)
- **Deployment**: Vercel (serverless functions)

### Next Steps

Run `/sp.tasks` to:
- Break down plan into granular, testable tasks
- Define task dependencies and ordering
- Create acceptance criteria for each task
- Generate tasks.md for `/sp.implement` execution

## Outcome

- ✅ Impact: Completed comprehensive planning for AI-powered chatbot with stateless MCP architecture. Resolved all technical unknowns. Designed database schema, API contracts, and implementation roadmap. Validated 7 technology choices with production-ready patterns.
- 🧪 Tests: No tests run (planning phase)
- 📁 Files: Created 6 planning documents (plan.md, research.md, data-model.md, 2 contracts, quickstart.md), updated CLAUDE.md
- 🔁 Next prompts: Run `/sp.tasks` to break down into implementation tasks
- 🧠 Reflection: Systematic planning workflow (Phase 0 research → Phase 1 design) ensured all unknowns resolved before task breakdown. OpenAI Swarm simplified MCP tool integration vs. separate server process. Sliding window + summarization strategy balances context retention with token efficiency. Stateless architecture enables horizontal scaling on Vercel serverless.

## Evaluation notes (flywheel)

- Failure modes observed: Initial setup-plan.sh failure due to non-standard branch name (`phase-3-chatbot` vs. `007-chatbot-mcp`). Recovered by manual path setup. Background research agents interrupted by user but recovered by synthesizing research findings directly.
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 (Research) + Phase 1 (Design)
- Next experiment (smallest change to try): Test whether breaking Phase 0 research into parallel sub-agents (one per research question) improves efficiency vs. synthesizing findings directly. Current approach (direct synthesis) was faster but may miss edge cases that dedicated research agents would discover.
