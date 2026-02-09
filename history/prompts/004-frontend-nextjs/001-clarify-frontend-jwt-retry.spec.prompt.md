---
id: 001
title: Clarify frontend spec JWT and retry strategy
stage: spec
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-frontend-nextjs
branch: 002-database-setup
user: ashfaq
command: /sp.clarify
labels: ["clarification", "spec", "frontend", "jwt", "retry-strategy", "security", "resilience"]
links:
  spec: specs/004-frontend-nextjs/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-frontend-nextjs/spec.md
tests:
  - (none - specification clarification session)
---

## Prompt

Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.

Command: `/sp.clarify`

Context: Frontend specification for Phase II (Next.js 16+ with Better Auth, full-stack todo application) was already comprehensive (1235 lines) but needed clarification on security and resilience implementation details.

## Response snapshot

**Clarification Session Completed: 2 of 5 questions answered**

### Question 1: JWT Token Storage
**Asked:** How should JWT tokens be stored on the client-side for optimal security?

**Options Presented:**
- A: localStorage (simple but vulnerable to XSS)
- B: httpOnly cookies (prevents XSS attacks) [RECOMMENDED]
- C: sessionStorage (cleared on tab close)
- D: In-memory only (lost on page refresh)

**User Answer:** B (httpOnly cookies)

**Integration Actions:**
- Added clarification to spec.md Clarifications section (line 36-41)
- Updated NFR-006 to mandate httpOnly cookies exclusively (line 242)
- Updated Token Management section to specify Better Auth default (line 365)

**Rationale:** httpOnly cookies prevent XSS attacks by making tokens inaccessible to JavaScript, aligning with Better Auth defaults and security best practices.

---

### Question 2: API Retry Strategy
**Asked:** When the backend API is unreachable, what retry strategy should be implemented?

**Options Presented:**
- A: No retry, immediate error (fast feedback but poor UX)
- B: Retry once with 2s delay (simple but limited)
- C: Retry 3 times with exponential backoff (1s, 2s, 4s) [RECOMMENDED]
- D: Retry indefinitely until success (may hang app)

**User Answer:** C (3 retries with exponential backoff)

**Integration Actions:**
- Added clarification to spec.md Clarifications section (line 41)
- Updated Edge Cases section to specify retry behavior (line 203)
- Added NFR-011 for retry requirement (line 248)
- Implemented retry logic in API Client request method (lines 539-575) with complete TypeScript code

**Rationale:** Exponential backoff (1s, 2s, 4s) handles transient network issues gracefully without overwhelming the server, balancing user experience with system stability.

---

### Questions 3-5: Not Asked
User requested to conclude clarification workflow after 2 questions, which is acceptable per `/sp.clarify` design (up to 5 questions maximum).

**Remaining ambiguities identified but not prioritized:**
- Virtual scrolling strategy for 100+ tasks
- Conflict resolution for simultaneous edits
- Session timeout behavior (idle vs absolute)

**Coverage Assessment:**
- Functional Scope: ✅ Clear (8 user stories, acceptance criteria)
- Domain & Data Model: ✅ Clear (task schema, user model)
- Interaction & UX Flow: ⚠️ Partial (loading states specified, offline mode not detailed)
- Non-Functional Quality: ✅ Improved (security and resilience clarified)
- Integration & Dependencies: ✅ Improved (failure mode handling specified)
- Edge Cases: ⚠️ Partial (API failures addressed, conflict resolution pending)

## Outcome

- ✅ Impact: Security posture strengthened (httpOnly cookies), resilience improved (exponential backoff retry)
- 🧪 Tests: No tests modified (specification phase)
- 📁 Files: 1 file modified (specs/004-frontend-nextjs/spec.md) across 7 distinct edits
- 🔁 Next prompts: `/sp.plan` to generate architectural plan based on clarified spec
- 🧠 Reflection: 2 high-impact clarifications successfully integrated. JWT storage and API retry strategy are foundational decisions affecting security and user experience across all features. Remaining ambiguities (virtual scrolling, conflict resolution, session timeout) are lower priority and can be addressed during planning/implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Prerequisites check returned incorrect feature paths (002-database-setup instead of 004-frontend-nextjs) but was handled transparently by directly reading correct spec file.
- Graders run and results (PASS/FAIL): PASS - All clarifications successfully integrated into spec with proper cross-referencing (Clarifications section, NFRs, Edge Cases, Component Architecture)
- Prompt variant (if applicable): Standard /sp.clarify workflow
- Next experiment (smallest change to try): Consider front-loading ambiguity analysis summary before question workflow to set user expectations on total questions and coverage areas.
