---
id: 001
title: Clarify chatbot specification ambiguities
stage: spec
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: 007-chatbot-mcp
branch: phase-3-chatbot
user: ashfaq
command: /sp.clarify
labels: ["spec", "clarification", "chatbot", "mcp", "phase-3", "conversation-management", "security", "voice-input"]
links:
  spec: specs/features/007-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/features/007-chatbot-mcp/spec.md
tests:
  - (none - specification clarification only)
---

## Prompt

User invoked `/sp.clarify` to identify and resolve ambiguities in the AI-Powered Todo Chatbot feature specification (007-chatbot-mcp).

## Response snapshot

**Clarification Session Summary**:

Asked and integrated 5 critical clarification questions to resolve specification ambiguities:

**Q1: Conversation Context Management Strategy**
- **Question**: How should the system manage conversation context when history exceeds model token limits (4000-8000 tokens for GPT-4)?
- **Answer**: Sliding window + summarization - Keep recent 10-15 messages verbatim, summarize older messages into compact "conversation summary" field (max 500 tokens). Balances context retention with token limits.
- **Impact**: Added NFR-007, updated Edge Cases, added Conversation.summary field to data model

**Q2: API Failure Retry Strategy**
- **Question**: What retry strategy should the system implement when OpenAI API calls fail?
- **Answer**: Exponential backoff with circuit breaker - Retry up to 3 times with increasing delays (1s, 2s, 4s). After 5 consecutive failures, open circuit for 60s.
- **Impact**: Added NFR-008, updated Edge Cases for rate limiting/API failures

**Q3: JWT Token Validation in Chat Endpoint**
- **Question**: How should the chat endpoint validate the user_id parameter in `POST /api/{user_id}/chat` to prevent spoofing?
- **Answer**: Extract from JWT token - Validate JWT from Authorization header, extract user_id from token claims. URL parameter only for routing; actual user_id from authenticated token.
- **Impact**: Updated FR-006, added Edge Case for user_id mismatch (403 Forbidden)

**Q4: Voice Input Implementation Strategy**
- **Question**: Which voice input strategy should be used for the bonus voice commands feature (+200 points) given hackathon time constraints?
- **Answer**: Browser Web Speech API - Use built-in `webkitSpeechRecognition`/`SpeechRecognition`. Free, low-latency, works in Chrome/Edge/Safari, supports English and Urdu.
- **Impact**: Updated FR-014, TC-009, User Story 8 acceptance scenarios (clarified no audio output in MVP)

**Q5: Conversation Summary Storage**
- **Question**: Where should the conversation summary be stored in the database schema for the sliding window + summarization strategy?
- **Answer**: Conversation table field - Add `summary` TEXT field to Conversation model. Single query for summary + metadata, regenerate every ~20 messages.
- **Impact**: Updated Conversation entity with summary field and regeneration logic, added FR-011a for context window management

**Sections Updated**:
- Added "Clarifications" section with Session 2026-01-03
- Updated Edge Cases (5 items)
- Updated Functional Requirements (FR-006, FR-011a, FR-014)
- Updated Key Entities (Conversation model with summary field)
- Updated Non-Functional Requirements (NFR-007, NFR-008)
- Updated Technical Constraints (TC-009)
- Updated User Story 8 acceptance scenarios
- Marked Open Question Q2 as resolved

**Coverage Summary**: All 10 taxonomy categories resolved. Observability details deferred to planning phase (low impact).

**Recommendation**: Proceed to `/sp.plan` - all critical ambiguities resolved.

## Outcome

- ✅ Impact: Resolved 5 critical specification ambiguities across security, performance, data model, and bonus features. Added 2 NFRs, 1 technical constraint, updated 3 functional requirements, enhanced data model.
- 🧪 Tests: No tests run (specification phase)
- 📁 Files: Modified 1 file (specs/features/007-chatbot-mcp/spec.md) - added Clarifications section, updated 8 specification sections
- 🔁 Next prompts: Run `/sp.plan` to create architectural plan based on clarified specification
- 🧠 Reflection: Systematic ambiguity analysis using 10-category taxonomy effectively identified high-impact clarification opportunities. Sequential questioning with recommended options streamlined decision-making. Incremental spec updates after each answer prevented context loss and ensured atomicity.

## Evaluation notes (flywheel)

- Failure modes observed: Initial script failure due to non-standard feature path (specs/features/007-chatbot-mcp vs specs/007-chatbot-mcp). Recovered with agent-native PHR creation.
- Graders run and results (PASS/FAIL): N/A (specification phase)
- Prompt variant (if applicable): Standard /sp.clarify workflow with 10-category taxonomy
- Next experiment (smallest change to try): Test whether providing recommended options with rationale reduces clarification rounds compared to open-ended questions
