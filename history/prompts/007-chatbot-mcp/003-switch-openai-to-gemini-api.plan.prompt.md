---
id: 003
title: Switch OpenAI to Gemini API
stage: plan
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: 007-chatbot-mcp
branch: phase-3-chatbot
user: ashfaq
command: manual-update
labels: ["plan", "api-decision", "gemini", "cost-optimization", "chatbot", "phase-3"]
links:
  spec: specs/features/007-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/features/007-chatbot-mcp/spec.md
  - specs/features/007-chatbot-mcp/plan.md
  - specs/features/007-chatbot-mcp/research.md
  - CLAUDE.md
tests:
  - (none - planning decision)
---

## Prompt

User requested switching from OpenAI API (paid) to Google Gemini API (free tier) to minimize costs while maintaining all chatbot functionality.

**User Input**:
> "Before we run /sp.tasks i will tell you one thing that is 'We will not use OpenAI API (paid) key. Rather we will set Gemini API key (Free limit) for chatbot. You can update the spec and plan accordingly so that we will have a smooth working with clarity."

## Response snapshot

**Decision**: Switch from OpenAI ecosystem to Google Gemini API (free tier)

### Changes Made

**Specification Updates** (`spec.md`):
- **FR-003**: Changed from "OpenAI Agents SDK" to "Google Generative AI SDK (Gemini API) with function calling"
- **FR-007**: Changed from "OpenAI ChatKit" to "custom conversational UI with React components"
- **FR-012**: Removed ChatKit domain allowlist requirement, replaced with "responsive and accessible custom chat UI"
- **FR-013**: Updated Urdu support to specify Gemini native support
- **TC-001**: MUST use Google Generative AI SDK (Gemini API free tier)
- **TC-002**: Implement MCP tools as Python functions compatible with Gemini function calling schema
- **TC-003**: MUST implement custom chat UI (not paid third-party services)
- **TC-010**: NEW - MUST use free-tier Gemini API only (no paid AI services)
- **Out of Scope**: Updated to exclude paid third-party chat libraries and paid AI APIs
- **Dependencies**: Changed from "OpenAI API" to "Google Gemini API (free tier)"
- **Assumptions**: Updated rate limits (1500 req/day, 15 req/min for Gemini 2.0 Flash)
- **References**: Replaced OpenAI links with Gemini documentation links

**Implementation Plan Updates** (`plan.md`):
- **Summary**: Updated to reference Gemini API and custom React chat UI
- **Primary Dependencies**: Replaced `openai`, `OpenAI Agents SDK`, `OpenAI ChatKit` with `google-generativeai`, `tiktoken`, `tenacity`, `TailwindCSS`
- **Performance Goals**: Updated API retry strategy to reference Gemini API, added free tier limits
- **Constraints**: All 3 OpenAI-specific constraints (TC-001, TC-002, TC-003) updated to Gemini equivalents
- **API Decision Change Section**: Added detailed rationale for API switch with impact analysis

**Research Findings Updates** (`research.md`):
- **Complete rewrite** of all 7 research sections to reflect Gemini integration
- **Section 1**: Gemini SDK Integration with function calling (replaces OpenAI Swarm)
  - Installation: `uv add google-generativeai`
  - Model: `gemini-2.0-flash-exp` (recommended) or `gemini-1.5-pro`
  - Function Declarations pattern with `FunctionDeclaration` and `Tool` classes
  - Message handling with Gemini's function calling API
- **Section 2**: MCP Tools with Gemini Function Calling
  - Python functions with Gemini-compatible function declarations
  - Same tool signatures, different registration pattern
- **Section 3**: Custom Chat UI (React)
  - Full custom implementation with message bubbles, input field, auto-scroll
  - TailwindCSS styling
  - JWT integration for Better Auth
  - No dependency on OpenAI ChatKit
- **Section 4**: Context Management (updated for Gemini)
  - Gemini-specific message format: `{"role": "user|model", "parts": ["text"]}`
  - Use `gemini-1.5-flash` for summarization
  - Sliding window same (15 messages), summary same (500 tokens)
- **Section 5**: Retry + Circuit Breaker (updated for Gemini exceptions)
  - `google_exceptions.ServiceUnavailable`, `DeadlineExceeded`, `ResourceExhausted`
  - Same tenacity pattern, different exception types
- **Section 6**: Web Speech API (unchanged, AI-agnostic)
- **Section 7**: Urdu Support (updated for Gemini)
  - Gemini native multilingual support
  - System instruction pattern for language detection

**CLAUDE.md Updates**:
- Updated "Active Technologies" to reflect Gemini API, custom React chat UI
- Updated "Recent Changes" for planning phase with Gemini decision
- Documented cost optimization benefit

### Rationale for Switch

**Cost**:
- OpenAI GPT-4: Paid API, requires credit card, costs per token
- Gemini API: Free tier (1500 req/day, 15 req/min), no credit card required
- **Savings**: $0 vs. estimated $50-100 for development + demo

**Functionality Preservation**:
- ✅ Function Calling: Both support native function calling for MCP tools
- ✅ Multilingual: Both support Urdu natively
- ✅ Context Management: Both have large context windows (Gemini: 1M tokens)
- ✅ Stateless Architecture: Implementation pattern identical

**Performance**:
- Gemini 2.0 Flash: 15 requests/minute (sufficient for demo)
- Gemini 1.5 Pro: 2 requests/minute (backup option)
- Latency: Comparable to OpenAI (<2s response time)

**Simplification**:
- No ChatKit domain verification needed
- No OpenAI platform account setup
- Custom chat UI gives full control
- Fewer external dependencies

**Trade-offs Accepted**:
- Need to build custom chat UI (vs. ChatKit pre-built)
  - Mitigation: Simple React component, ~100 lines of code
- Gemini SDK less mature than OpenAI SDK
  - Mitigation: Function calling well-documented, similar to OpenAI pattern
- Rate limits (15 req/min vs. OpenAI's higher limits)
  - Mitigation: Sufficient for demo + development, can upgrade if needed

### Technical Compatibility

| Aspect | OpenAI | Gemini | Compatible? |
|--------|--------|--------|-------------|
| Function Calling | ✅ Yes | ✅ Yes | ✅ |
| Multilingual (Urdu) | ✅ Yes | ✅ Yes | ✅ |
| Stateless Architecture | ✅ Yes | ✅ Yes | ✅ |
| Conversation History | ✅ Yes | ✅ Yes | ✅ |
| Context Window | 128K tokens | 1M tokens | ✅ Better |
| Free Tier | ❌ No | ✅ Yes | ✅ |
| Chat UI | ChatKit (pre-built) | Custom (build) | ⚠️ Trade-off |

### Implementation Impact

**No changes required**:
- Database schema (Conversation, Message models)
- MCP tool function signatures (same input/output)
- Sliding window strategy (same 15 messages + 500 token summary)
- Retry + circuit breaker pattern (same delays, thresholds)
- Web Speech API integration (AI-agnostic)
- JWT authentication (AI-agnostic)

**Changes required**:
- Backend: Replace `openai` SDK with `google-generativeai`
- Backend: Rewrite agent initialization for Gemini
- Backend: Update function calling handler for Gemini's API format
- Frontend: Build custom chat UI component (~100 LOC)
- Environment: `GEMINI_API_KEY` instead of `OPENAI_API_KEY`

**Effort estimation**:
- Original plan: ~8 hours (OpenAI integration + ChatKit setup)
- Updated plan: ~8 hours (Gemini integration + custom UI)
- **Net change**: ~0 hours (comparable complexity)

### Next Steps

All planning documents updated and synchronized:
- ✅ spec.md (14 FRs, 10 TCs updated)
- ✅ plan.md (Summary, Technical Context, Constraints updated)
- ✅ research.md (All 7 sections rewritten for Gemini)
- ✅ CLAUDE.md (Active Technologies, Recent Changes updated)

Ready to proceed with `/sp.tasks` to break down into implementation tasks using Gemini API architecture.

## Outcome

- ✅ Impact: Successfully migrated all planning documents from OpenAI API to Google Gemini API (free tier). Preserved all functionality (function calling, Urdu support, stateless architecture) while eliminating costs. Simplified deployment (no ChatKit domain verification). Zero net effort increase.
- 🧪 Tests: No tests run (planning decision)
- 📁 Files: Updated 4 planning documents (spec.md, plan.md, research.md, CLAUDE.md)
- 🔁 Next prompts: Run `/sp.tasks` with Gemini-based architecture
- 🧠 Reflection: Gemini API's free tier with function calling support makes it an ideal choice for cost-sensitive hackathon projects. The switch required comprehensive document updates but no fundamental architecture changes. Custom chat UI provides more control than ChatKit while adding minimal implementation effort. Free tier rate limits (15 req/min) are sufficient for demo + development use cases.

## Evaluation notes (flywheel)

- Failure modes observed: None - API switch was straightforward due to similar function calling patterns between OpenAI and Gemini
- Graders run and results (PASS/FAIL): N/A (planning decision)
- Prompt variant (if applicable): User-driven API decision change mid-planning
- Next experiment (smallest change to try): Compare actual Gemini 2.0 Flash vs. 1.5 Pro response quality for function calling accuracy. 2.0 Flash is faster (15 req/min) but less tested than 1.5 Pro (2 req/min). May need fallback strategy if 2.0 Flash function calling proves less reliable.
