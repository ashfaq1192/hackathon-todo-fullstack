---
id: 0002
title: Frontend tasks generated
stage: tasks
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-frontend-nextjs
branch: 002-database-setup
user: ashfaq
command: /sp.tasks
labels: ["tasks", "frontend", "nextjs", "implementation", "user-stories"]
links:
  spec: specs/004-frontend-nextjs/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-frontend-nextjs/tasks.md
tests:
  - (none - task planning phase, no code written)
---

## Prompt

Command: `/sp.tasks`

User triggered task generation workflow after completing `/sp.plan`.

Context: Frontend planning complete with all design artifacts (plan.md, research.md, data-model.md, contracts/backend-api.md, quickstart.md). The task generation workflow organizes implementation tasks by user story from spec.md to enable independent development and testing.

## Response snapshot

**Task Generation Complete: 132 Tasks Across 12 Phases**

### Task Organization by User Story

**Phase 1: Setup (13 tasks)**
- Project initialization, Next.js 16+ setup, dependencies, configuration
- TypeScript, Tailwind, Vitest, Playwright configuration
- Directory structure creation per plan.md

**Phase 2: Foundational (17 tasks)**
- TypeScript types for User, Task, API payloads, Auth payloads, Errors, UI state
- Zod validation schemas for all forms
- API client with retry logic (exponential backoff per NFR-011)
- Better Auth configuration and API routes
- Reusable UI components (Button, Input, Spinner)
- Navigation component and root layout

**Phase 3: User Story 1 - User Registration (9 tasks, Priority P0)**
- 3 test tasks: Unit test for SignupForm, E2E test for signup flow
- 6 implementation tasks: SignupForm component, React Hook Form + Zod integration, validation, error handling, signup page

**Phase 4: User Story 2 - User Login (9 tasks, Priority P0)**
- 3 test tasks: Unit test for LoginForm, E2E test for login flow
- 6 implementation tasks: LoginForm component, React Hook Form + Zod integration, validation, error handling, login page

**Phase 5: User Story 3 - View Task List (12 tasks, Priority P1)**
- 3 test tasks: Unit test for TaskList, API client test, E2E test
- 9 implementation tasks: TaskList component, TaskItem component, API integration, visual styling, dashboard layout/page, auth guard

**Phase 6: User Story 4 - Create New Task (11 tasks, Priority P1)**
- 3 test tasks: Unit test for CreateTaskForm, API client test, E2E test
- 8 implementation tasks: CreateTaskForm component, React Hook Form + Zod, validation, character counters, submission handler, error handling

**Phase 7: User Story 5 - Mark Complete/Incomplete (8 tasks, Priority P1)**
- 3 test tasks: Unit test for checkbox toggle, API client test, E2E test
- 5 implementation tasks: Checkbox UI, optimistic update, API integration, error handling (revert on failure)

**Phase 8: User Story 8 - Responsive Design (8 tasks, Priority P1)**
- 1 test task: E2E responsive test at multiple viewports
- 7 implementation tasks: Mobile-first responsive classes for all components, test at breakpoints

**Phase 9: User Story 6 - Edit Task (11 tasks, Priority P2)**
- 3 test tasks: Unit test for edit mode, API client test, E2E test
- 8 implementation tasks: Edit mode state, Edit button, editable UI, save/cancel handlers, validation

**Phase 10: User Story 7 - Delete Task (10 tasks, Priority P2)**
- 3 test tasks: Unit test for delete confirmation, API client test, E2E test
- 7 implementation tasks: Delete button, confirmation dialog, confirm/cancel handlers, error handling

**Phase 11: Polish & Cross-Cutting (14 tasks)**
- Logout functionality, 401 error handler, accessibility (ARIA), Lighthouse audit
- Loading skeletons, toast notifications, TypeScript/ESLint validation
- Test coverage verification (70%+), E2E test suite, README, documentation

**Phase 12: Deployment to Vercel (9 tasks)**
- Vercel project configuration, environment variables, deployment
- Production testing (auth, CRUD, responsive, HTTPS), CORS configuration
- Demo video recording

### Task Format Validation

✅ All 132 tasks follow checklist format:
- `- [ ]` checkbox prefix
- Sequential Task IDs (T001-T132)
- `[P]` marker for parallelizable tasks (54 tasks)
- `[US#]` label for user story tasks (US1-US8)
- Exact file paths in descriptions
- References to design docs (spec.md, plan.md, data-model.md, contracts/, quickstart.md)

### Dependencies & Execution Order

**Critical Path**:
1. Setup (Phase 1) → Foundational (Phase 2) → BLOCKS all user stories
2. Authentication (US1, US2) → BLOCKS all other user stories (need auth)
3. Core MVP (US3, US4, US5, US8) → Can proceed in parallel after auth
4. Enhancements (US6, US7) → Can proceed in parallel after Core MVP
5. Polish → Deployment

**Parallel Opportunities**:
- Phase 1: 8 tasks marked [P] can run in parallel
- Phase 2: 14 tasks marked [P] can run in parallel
- After Foundational: US3, US4, US5, US8 can all start in parallel (different components)
- Within each story: Tests marked [P], components marked [P] can run in parallel
- Total: 54 tasks marked [P] for parallel execution

### MVP Scope

**Recommended MVP**: User Stories 1, 2, 3, 4, 5, 8 (Authentication + Core CRUD + Responsive)
- **MVP Tasks**: 101 tasks (excludes US6, US7)
- **MVP Deliverable**: Users can sign up, login, view tasks, create tasks, mark complete, responsive design
- **Post-MVP**: Add US6 (Edit) and US7 (Delete) as enhancements

### Test Coverage

**24 test tasks** distributed across all user stories:
- Unit tests: 18 tasks (component tests, API client tests)
- E2E tests: 6 tasks (user journey tests)
- Coverage target: 70%+ for MVP, 75%+ for production-ready per Phase II constitution

### Entity-to-Story Mapping

- **User types** (types/user.ts) → US1, US2
- **Task types** (types/task.ts) → US3, US4, US5, US6, US7
- **API Client** (lib/api/client.ts) → All CRUD stories (US3-US7)
- **Better Auth** (lib/auth/) → US1, US2
- **Zod schemas** (lib/validation/schemas.ts) → All form stories (US1, US2, US4, US6)
- **Responsive utilities** (Tailwind CSS) → US8 (cross-cutting)

### Endpoint-to-Story Mapping

- `POST /api/auth/signup` → US1 (User Registration)
- `POST /api/auth/signin` → US2 (User Login)
- `GET /api/{user_id}/tasks` → US3 (View Task List)
- `POST /api/{user_id}/tasks` → US4 (Create New Task)
- `PATCH /api/{user_id}/tasks/{id}` → US5 (Mark Complete)
- `PUT /api/{user_id}/tasks/{id}` → US6 (Edit Task)
- `DELETE /api/{user_id}/tasks/{id}` → US7 (Delete Task)

## Outcome

- ✅ Impact: Complete implementation roadmap for Next.js frontend with 132 granular, executable tasks. Each user story is independently implementable and testable. Clear MVP path (101 tasks) and parallel execution strategy (54 tasks marked [P]).
- 🧪 Tests: 24 test tasks included (18 unit, 6 E2E) across all user stories. TDD approach: tests written FIRST, must FAIL before implementation. Coverage target 70%+ for MVP.
- 📁 Files: 1 file created (tasks.md, 501 lines)
- 🔁 Next prompts: `/sp.implement` to execute tasks in dependency order (Setup → Foundational → US1+US2 → Core MVP → Enhancements → Polish → Deploy)
- 🧠 Reflection: Task organization by user story enables true independent development. Authentication stories (US1, US2) correctly identified as blocking prerequisites. Responsive design (US8) grouped as P1 story despite being cross-cutting for clarity. 54 tasks marked [P] provide significant parallelization opportunities within phases. MVP scope (US1-5, US8) delivers core value with 101 tasks while deferring edit/delete to post-MVP.

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.sh returned wrong feature directory (002-database-setup instead of 004-frontend-nextjs), handled by directly loading design docs from specs/004-frontend-nextjs/.
- Graders run and results (PASS/FAIL): PASS - All 132 tasks follow required checklist format (verified with grep). Task IDs sequential (T001-T132). Story labels present on all user story tasks ([US1]-[US8]). File paths included in all implementation tasks. Dependencies documented clearly with critical path. Parallel opportunities identified (54 tasks).
- Prompt variant (if applicable): Standard /sp.tasks workflow with user story organization
- Next experiment (smallest change to try): Consider separating responsive design tasks into each user story phase instead of dedicated US8 phase (e.g., "Make SignupForm responsive" as part of US1). Current approach groups all responsive work for visibility but may delay responsive implementation until Phase 8. Trade-off: centralized vs distributed responsive development.
