# Tasks: Next.js Frontend Application

**Input**: Design documents from `/specs/004-frontend-nextjs/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/backend-api.md, quickstart.md

**Tests**: Included per Phase II constitution (70%+ coverage for MVP, 75%+ for production-ready)

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (frontend)**: `frontend/` at repository root
- Paths use Next.js 16 App Router structure: `app/`, `components/`, `lib/`, `types/`

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic Next.js structure

- [X] T001 Create frontend directory and initialize Next.js 16+ project with TypeScript, Tailwind CSS, ESLint per quickstart.md
- [X] T002 [P] Install core dependencies (better-auth, react-hook-form, zod, @hookform/resolvers, axios) per quickstart.md
- [X] T003 [P] Install dev dependencies (vitest, @vitejs/plugin-react, @testing-library/react, playwright) per quickstart.md
- [X] T004 [P] Configure TypeScript (tsconfig.json) with strict mode and path aliases per quickstart.md
- [X] T005 [P] Configure Tailwind CSS (tailwind.config.ts) with custom colors and breakpoints per quickstart.md
- [X] T006 [P] Configure Vitest (vitest.config.ts) with jsdom environment and coverage settings per quickstart.md
- [X] T007 [P] Configure Playwright (playwright.config.ts) for E2E tests per quickstart.md
- [X] T008 [P] Create environment variables template (.env.example) with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET per quickstart.md
- [X] T009 Create .env.local with development environment variables per quickstart.md
- [X] T010 [P] Create directory structure (app/, components/, lib/, types/, __tests__/, e2e/) per plan.md
- [X] T011 [P] Update package.json scripts (dev, build, test, test:e2e, type-check) per quickstart.md
- [X] T012 [P] Create __tests__/setup.ts with testing-library configuration per quickstart.md
- [X] T013 [P] Create app/globals.css with Tailwind imports and custom styles per quickstart.md

**Checkpoint**: Frontend project initialized - can run `pnpm dev`, `pnpm type-check`, `pnpm test`

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T014 Create TypeScript types for User (id, email, createdAt) in types/user.ts per data-model.md
- [X] T015 [P] Create TypeScript types for Task (id, user_id, title, description, complete, created_at, updated_at) in types/task.ts per data-model.md
- [X] T016 [P] Create TypeScript types for API payloads (TaskCreate, TaskUpdate, TaskPatch, TaskListResponse) in types/task.ts per data-model.md
- [X] T017 [P] Create TypeScript types for Auth payloads (SignupPayload, LoginPayload, AuthResponse) in types/auth.ts per data-model.md
- [X] T018 [P] Create TypeScript types for API errors (APIError, ValidationError) in types/api.ts per data-model.md
- [X] T019 [P] Create TypeScript types for UI state (LoadingState, FormState, TaskItemState) in types/ui.ts per data-model.md
- [X] T020 Create Zod validation schemas (signupSchema, loginSchema) in lib/validation/schemas.ts per data-model.md
- [X] T021 [P] Create Zod validation schemas (createTaskSchema, updateTaskSchema, patchTaskSchema) in lib/validation/schemas.ts per data-model.md
- [X] T022 Create API client class with retry logic (3 attempts, exponential backoff) in lib/api/client.ts per contracts/backend-api.md and NFR-011
- [X] T023 [P] Add API client methods (getTasks, createTask, updateTask, patchTask, deleteTask) in lib/api/client.ts per contracts/backend-api.md
- [X] T024 [P] Create Better Auth configuration in lib/auth/better-auth.ts per research.md
- [X] T025 [P] Create Better Auth API route in app/api/auth/[...betterauth]/route.ts per research.md
- [X] T026 [P] Create session management utilities in lib/auth/session.ts (getSession, useSession hooks) per research.md
- [X] T027 [P] Create reusable UI components (Button, Input, Spinner) in components/ui/ per spec.md Component Architecture
- [X] T028 [P] Create Navigation component with user email and logout in components/layout/Navigation.tsx per spec.md Component Architecture
- [X] T029 [P] Create root layout in app/layout.tsx with global styles and metadata per plan.md
- [X] T030 [P] Create landing page in app/page.tsx with links to login/signup per plan.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P0) 🎯 AUTH MVP ✅ COMPLETE

**Goal**: New users can create accounts via signup form with Better Auth integration

**Independent Test**: Fill out signup form with valid email/password, verify account created and user redirected to dashboard with JWT stored

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T031 [P] [US1] Unit test for SignupForm component validation in __tests__/components/SignupForm.test.tsx
- [X] T032 [P] [US1] E2E test for signup flow (success, duplicate email, weak password) in e2e/auth.spec.ts

### Implementation for User Story 1

- [X] T033 [P] [US1] Create SignupForm component with email/password/confirmPassword fields in components/auth/SignupForm.tsx per spec.md US-1
- [X] T034 [US1] Integrate React Hook Form with Zod signupSchema in SignupForm component per data-model.md
- [X] T035 [US1] Add signup form validation (email format, password min 8 chars, password match) per spec.md US-1 Acceptance Scenarios
- [X] T036 [US1] Add signup form submission handler (call Better Auth signup API, store JWT, redirect to /dashboard) per spec.md US-1
- [X] T037 [US1] Add error handling for signup (duplicate email, weak password) per spec.md US-1 Acceptance Scenarios
- [X] T038 [P] [US1] Create signup page in app/(auth)/signup/page.tsx with SignupForm component per plan.md
- [X] T039 [US1] Add loading state and error display to signup page per NFR-004

**Checkpoint**: User Story 1 complete - users can sign up, JWT stored, redirected to dashboard

---

## Phase 4: User Story 2 - User Login (Priority: P0) 🎯 AUTH MVP ✅ COMPLETE

**Goal**: Returning users can sign in with credentials via Better Auth

**Independent Test**: Enter valid credentials on login form, verify successful authentication, JWT stored, redirect to dashboard

### Tests for User Story 2

- [X] T040 [P] [US2] Unit test for LoginForm component validation in __tests__/components/LoginForm.test.tsx
- [X] T041 [P] [US2] E2E test for login flow (success, invalid password, non-existent email) in e2e/auth.spec.ts

### Implementation for User Story 2

- [X] T042 [P] [US2] Create LoginForm component with email/password fields in components/auth/LoginForm.tsx per spec.md US-2
- [X] T043 [US2] Integrate React Hook Form with Zod loginSchema in LoginForm component per data-model.md
- [X] T044 [US2] Add login form validation (email format, password required) per spec.md US-2 Acceptance Scenarios
- [X] T045 [US2] Add login form submission handler (call Better Auth signin API, store JWT, redirect to /dashboard) per spec.md US-2
- [X] T046 [US2] Add error handling for login (invalid credentials, account not found) per spec.md US-2 Acceptance Scenarios
- [X] T047 [P] [US2] Create login page in app/(auth)/login/page.tsx with LoginForm component per plan.md
- [X] T048 [US2] Add loading state and error display to login page per NFR-004
- [X] T049 [US2] Update landing page (app/page.tsx) with links to login and signup pages

**Checkpoint**: User Stories 1 AND 2 complete - users can sign up OR login, authentication working

---

## Phase 5: User Story 3 - View Task List (Priority: P1) 🎯 CORE MVP

**Goal**: Logged-in users can see all their tasks in a list view

**Independent Test**: Login as user, verify dashboard loads with all user's tasks displayed (or empty state if no tasks)

### Tests for User Story 3

- [ ] T050 [P] [US3] Unit test for TaskList component (empty state, task display, loading) in __tests__/components/TaskList.test.tsx
- [ ] T051 [P] [US3] Unit test for API client getTasks method in __tests__/lib/api-client.test.ts
- [ ] T052 [P] [US3] E2E test for view tasks flow (login, see tasks, empty state) in e2e/tasks.spec.ts

### Implementation for User Story 3

- [ ] T053 [P] [US3] Create TaskList component with loading state and empty state in components/tasks/TaskList.tsx per spec.md US-3
- [ ] T054 [P] [US3] Create TaskItem component (read-only view) displaying title, description, complete status in components/tasks/TaskItem.tsx per spec.md US-3
- [ ] T055 [US3] Integrate TaskList with API client getTasks method per contracts/backend-api.md GET /api/{user_id}/tasks
- [ ] T056 [US3] Add visual distinction for completed tasks (strikethrough, gray color) per spec.md US-3 Acceptance Scenario 4
- [ ] T057 [US3] Add timestamp display (created_at, updated_at) to TaskItem per spec.md US-3
- [ ] T058 [P] [US3] Create dashboard layout with Navigation component in app/(dashboard)/layout.tsx per plan.md
- [ ] T059 [US3] Create dashboard page with TaskList component in app/(dashboard)/page.tsx per plan.md
- [ ] T060 [US3] Add authentication guard to dashboard layout (redirect to /login if not authenticated) per FR-006
- [ ] T061 [US3] Add error handling for API failures (show error message, retry logic already in API client) per NFR-011

**Checkpoint**: User Stories 1, 2, AND 3 complete - users can sign up, login, and view their tasks

---

## Phase 6: User Story 4 - Create New Task (Priority: P1) 🎯 CORE MVP

**Goal**: Logged-in users can add new tasks via a form

**Independent Test**: Click "Add Task" button, fill title and description, submit, verify task appears in list and persists in backend

### Tests for User Story 4

- [ ] T062 [P] [US4] Unit test for CreateTaskForm component (validation, submission, character counter) in __tests__/components/CreateTaskForm.test.tsx
- [ ] T063 [P] [US4] Unit test for API client createTask method in __tests__/lib/api-client.test.ts
- [ ] T064 [P] [US4] E2E test for create task flow (success, empty title, max length) in e2e/tasks.spec.ts

### Implementation for User Story 4

- [ ] T065 [P] [US4] Create CreateTaskForm component with title and description fields in components/tasks/CreateTaskForm.tsx per spec.md US-4
- [ ] T066 [US4] Integrate React Hook Form with Zod createTaskSchema in CreateTaskForm per data-model.md
- [ ] T067 [US4] Add form validation (title required, title max 200 chars, description max 1000 chars) per spec.md US-4 Acceptance Scenarios
- [ ] T068 [US4] Add character counters for title (200) and description (1000) per spec.md US-4 Acceptance Scenario 4
- [ ] T069 [US4] Add form submission handler (call API client createTask, refresh task list) per spec.md US-4 Acceptance Scenario 5
- [ ] T070 [US4] Add form clearing after successful submission per spec.md US-4 Acceptance Scenario 5
- [ ] T071 [US4] Add error handling for create failures (show error message) per NFR-013
- [ ] T072 [US4] Integrate CreateTaskForm into dashboard page above TaskList per spec.md Component Architecture

**Checkpoint**: User Stories 1-4 complete - users can create tasks and see them in the list

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P1) 🎯 CORE MVP

**Goal**: Logged-in users can toggle task completion status with a checkbox

**Independent Test**: Click checkbox on incomplete task, verify UI updates immediately, backend state changes, checkbox can be unchecked

### Tests for User Story 5

- [ ] T073 [P] [US5] Unit test for TaskItem checkbox toggle (optimistic update, revert on error) in __tests__/components/TaskItem.test.tsx
- [ ] T074 [P] [US5] Unit test for API client patchTask method in __tests__/lib/api-client.test.ts
- [ ] T075 [P] [US5] E2E test for toggle complete flow (mark complete, mark incomplete, error handling) in e2e/tasks.spec.ts

### Implementation for User Story 5

- [ ] T076 [P] [US5] Add checkbox to TaskItem component for completion toggle per spec.md US-5
- [ ] T077 [US5] Implement optimistic UI update (update UI immediately on checkbox click) per spec.md US-5 Acceptance Scenario 1
- [ ] T078 [US5] Add API call to patchTask with {complete: true/false} per contracts/backend-api.md PATCH /api/{user_id}/tasks/{id}
- [ ] T079 [US5] Add error handling (revert checkbox state if API fails, show error message) per spec.md US-5 Acceptance Scenario 3
- [ ] T080 [US5] Update visual styling based on completion status (already implemented in US3 T056, verify integration)

**Checkpoint**: User Stories 1-5 complete - core todo functionality working (create, view, complete tasks)

---

## Phase 8: User Story 8 - Responsive Design (Priority: P1) 🎯 CORE MVP

**Goal**: App works on mobile, tablet, desktop with responsive layout

**Independent Test**: View app at 320px (mobile), 768px (tablet), 1440px (desktop), verify layout adapts without horizontal scroll

### Tests for User Story 8

- [ ] T081 [P] [US8] E2E test for responsive design at multiple viewports (320px, 768px, 1440px) in e2e/responsive.spec.ts

### Implementation for User Story 8

- [ ] T082 [P] [US8] Add mobile-first responsive classes to TaskList (stack on mobile, grid on desktop) per spec.md US-8 and research.md
- [ ] T083 [P] [US8] Add mobile-first responsive classes to CreateTaskForm (full-width on mobile, constrained on desktop) per spec.md US-8
- [ ] T084 [P] [US8] Add mobile-first responsive classes to Navigation (hamburger menu on mobile, full nav on desktop) per spec.md US-8
- [ ] T085 [P] [US8] Add mobile-first responsive classes to TaskItem (touch-friendly buttons on mobile) per spec.md US-8 and WCAG 44x44px touch targets
- [ ] T086 [P] [US8] Add mobile-first responsive classes to auth forms (full-width on mobile, centered card on desktop) per spec.md US-8
- [ ] T087 [US8] Test responsive layout at breakpoints (320px, 768px, 1024px, 1440px) per spec.md US-8 Acceptance Scenarios
- [ ] T088 [US8] Verify no horizontal scroll at any breakpoint per spec.md US-8 Acceptance Scenario 4

**Checkpoint**: CORE MVP complete (US1-5, US8) - users can sign up, login, view tasks, create tasks, mark complete, responsive design

---

## Phase 9: User Story 6 - Edit Task (Priority: P2)

**Goal**: Logged-in users can edit task title and description

**Independent Test**: Click "Edit" button on task, modify title/description, save, verify changes persist to backend

### Tests for User Story 6

- [ ] T089 [P] [US6] Unit test for TaskItem edit mode (enter edit, save, cancel) in __tests__/components/TaskItem.test.tsx
- [ ] T090 [P] [US6] Unit test for API client updateTask method in __tests__/lib/api-client.test.ts
- [ ] T091 [P] [US6] E2E test for edit task flow (edit and save, cancel edit, validation error) in e2e/tasks.spec.ts

### Implementation for User Story 6

- [ ] T092 [P] [US6] Add edit mode state to TaskItem component (isEditing boolean) per spec.md US-6
- [ ] T093 [US6] Add "Edit" button to TaskItem component per spec.md US-6
- [ ] T094 [US6] Implement edit mode UI (title and description become editable inputs) per spec.md US-6 Acceptance Scenario 1
- [ ] T095 [US6] Integrate React Hook Form with Zod updateTaskSchema in edit mode per data-model.md
- [ ] T096 [US6] Add save button with API call to updateTask (PUT /api/{user_id}/tasks/{id}) per contracts/backend-api.md
- [ ] T097 [US6] Add cancel button to discard changes and exit edit mode per spec.md US-6 Acceptance Scenario 3
- [ ] T098 [US6] Add validation (title required, max lengths) per spec.md US-6 Acceptance Scenario 4
- [ ] T099 [US6] Add error handling for update failures (show error message, keep in edit mode)

**Checkpoint**: User Stories 1-6 complete - edit functionality added

---

## Phase 10: User Story 7 - Delete Task (Priority: P2)

**Goal**: Logged-in users can delete tasks with confirmation

**Independent Test**: Click "Delete" button, confirm in dialog, verify task removed from UI and backend

### Tests for User Story 7

- [ ] T100 [P] [US7] Unit test for TaskItem delete confirmation (show dialog, confirm, cancel) in __tests__/components/TaskItem.test.tsx
- [ ] T101 [P] [US7] Unit test for API client deleteTask method in __tests__/lib/api-client.test.ts
- [ ] T102 [P] [US7] E2E test for delete task flow (confirm delete, cancel delete, error handling) in e2e/tasks.spec.ts

### Implementation for User Story 7

- [ ] T103 [P] [US7] Add delete button to TaskItem component per spec.md US-7
- [ ] T104 [US7] Add confirmation dialog state to TaskItem component (isDeleting boolean) per spec.md US-7
- [ ] T105 [US7] Implement confirmation dialog UI (confirm/cancel buttons) per spec.md US-7 Acceptance Scenario 1
- [ ] T106 [US7] Add confirm handler with API call to deleteTask (DELETE /api/{user_id}/tasks/{id}) per contracts/backend-api.md
- [ ] T107 [US7] Remove task from UI on successful deletion per spec.md US-7 Acceptance Scenario 2
- [ ] T108 [US7] Add cancel handler to close dialog without deleting per spec.md US-7 Acceptance Scenario 3
- [ ] T109 [US7] Add error handling for deletion failures (show error message, keep task in list) per spec.md US-7 Acceptance Scenario 4

**Checkpoint**: All User Stories (1-8) complete - full todo app functionality implemented

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T110 [P] Add logout functionality to Navigation component (clear JWT, redirect to /login) per FR-019
- [ ] T111 [P] Add 401 error handler to API client (redirect to /login on unauthorized) per contracts/backend-api.md
- [ ] T112 [P] Add accessibility attributes (ARIA labels, roles) to all interactive components per NFR-003
- [ ] T113 [P] Run Lighthouse audit and optimize to score > 90 per SC-009
- [ ] T114 [P] Add loading skeletons to TaskList while fetching per NFR-004
- [ ] T115 [P] Add toast notifications for success/error messages across all operations
- [ ] T116 [P] Verify TypeScript strict mode has zero errors (`pnpm type-check`) per TC-003
- [ ] T117 [P] Verify ESLint passes with zero errors (`pnpm lint`) per quickstart.md
- [ ] T118 Run full test suite and verify 70%+ coverage (`pnpm test:coverage`) per Development Standards
- [ ] T119 Run E2E test suite and verify all scenarios pass (`pnpm test:e2e`) per Development Standards
- [ ] T120 [P] Create frontend README.md with setup instructions, demo credentials, deployed URL per Definition of Done
- [ ] T121 [P] Create .env.example documentation with all required variables per quickstart.md
- [ ] T122 [P] Update root CLAUDE.md with frontend implementation session notes per Principle V
- [ ] T123 Build production bundle and verify no errors (`pnpm build`) per Definition of Done

**Checkpoint**: All polish tasks complete - ready for deployment

---

## Phase 12: Deployment to Vercel

**Purpose**: Deploy frontend to production

- [ ] T124 Configure Vercel project with GitHub integration per quickstart.md
- [ ] T125 [P] Set environment variables in Vercel dashboard (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, etc.) per quickstart.md
- [ ] T126 Deploy to Vercel and verify build succeeds per Definition of Done
- [ ] T127 Test authentication flow on deployed URL (signup, login, logout) per Definition of Done
- [ ] T128 Test all CRUD operations on deployed URL per Definition of Done
- [ ] T129 Test responsive design on real devices (mobile, tablet) per Definition of Done
- [ ] T130 [P] Verify HTTPS enabled and no console errors per NFR-008 and SC-008
- [ ] T131 [P] Update backend CORS settings to allow production frontend URL per contracts/backend-api.md
- [ ] T132 [P] Record demo video (<90 seconds) showing signup, login, create task, view tasks, edit task, delete task, mark complete per Definition of Done

**Checkpoint**: Frontend deployed to Vercel, all features working in production

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - **P0 stories (US1, US2)**: Authentication foundation - MUST complete before other stories
  - **P1 stories (US3, US4, US5, US8)**: Core MVP features - can proceed in parallel after US1+US2 complete
  - **P2 stories (US6, US7)**: Enhancement features - can proceed in parallel after P1 stories
- **Polish (Phase 11)**: Depends on all desired user stories being complete
- **Deployment (Phase 12)**: Depends on Polish completion

### User Story Dependencies

**Critical Path (MUST follow this order)**:
1. **Setup + Foundational (Phase 1-2)**: Foundation for all work
2. **Auth Stories (US1, US2)**: BLOCKS all other stories (need authentication)
3. **Core MVP Stories (US3, US4, US5, US8)**: Can proceed in parallel after auth complete
4. **Enhancement Stories (US6, US7)**: Can proceed in parallel after Core MVP

**Recommended Implementation Order**:
- Phase 1-2: Setup + Foundational
- Phase 3-4: US1 + US2 (Authentication) - SEQUENTIAL (US1 first, then US2)
- Phase 5-8: US3, US4, US5, US8 (Core MVP) - CAN BE PARALLEL
- Phase 9-10: US6, US7 (Enhancements) - CAN BE PARALLEL
- Phase 11-12: Polish + Deployment

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Types/schemas before components
- Components before page integration
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks marked [P] can run in parallel (8 parallel tasks)

**Phase 2 (Foundational)**: All tasks marked [P] can run in parallel after types are created (14 parallel tasks)

**After Foundational Complete**:
- US3, US4, US5, US8 can all start in parallel (different components/pages)
- US6 and US7 can start in parallel (both modify TaskItem but different features)

**Within Each Story**:
- All tests for a story marked [P] can run in parallel (typically 2-3 tests)
- Components within a story marked [P] can run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all type definitions together:
Task: "Create TypeScript types for User in types/user.ts"
Task: "Create TypeScript types for Task in types/task.ts"
Task: "Create TypeScript types for API payloads in types/task.ts"
Task: "Create TypeScript types for Auth payloads in types/auth.ts"
Task: "Create TypeScript types for API errors in types/api.ts"
Task: "Create TypeScript types for UI state in types/ui.ts"

# After types complete, launch all other foundational tasks:
Task: "Create Zod validation schemas in lib/validation/schemas.ts"
Task: "Create API client class in lib/api/client.ts"
Task: "Create Better Auth configuration in lib/auth/better-auth.ts"
Task: "Create reusable UI components in components/ui/"
Task: "Create Navigation component in components/layout/Navigation.tsx"
```

---

## Parallel Example: Core MVP (Phase 5-8)

```bash
# After US1+US2 complete, launch all core MVP stories in parallel:

# Developer A: User Story 3 (View Tasks)
Task: "[US3] Create TaskList component"
Task: "[US3] Create TaskItem component"
Task: "[US3] Create dashboard layout and page"

# Developer B: User Story 4 (Create Task)
Task: "[US4] Create CreateTaskForm component"
Task: "[US4] Integrate form into dashboard"

# Developer C: User Story 5 (Toggle Complete)
Task: "[US5] Add checkbox to TaskItem"
Task: "[US5] Implement optimistic update"

# Developer D: User Story 8 (Responsive Design)
Task: "[US8] Add responsive classes to all components"
Task: "[US8] Test at multiple breakpoints"
```

---

## Implementation Strategy

### MVP First (Core Features Only)

**Recommended MVP Scope**: User Stories 1, 2, 3, 4, 5, 8 (Authentication + Core CRUD + Responsive)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3-4: US1 + US2 (Authentication)
4. Complete Phase 5-8: US3, US4, US5, US8 (Core MVP)
5. Complete Phase 11: Polish
6. Complete Phase 12: Deployment
7. **STOP and VALIDATE**: Test full user journey (signup → login → create task → view → mark complete) on deployed URL
8. **MVP COMPLETE**: Deliverable app with core functionality

**Skip for MVP**: US6 (Edit Task), US7 (Delete Task) - can be added post-MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 + US2 → Test authentication independently → Deploy (Auth works!)
3. Add US3 + US4 + US5 + US8 → Test core CRUD independently → Deploy (MVP complete!)
4. Add US6 → Test edit independently → Deploy
5. Add US7 → Test delete independently → Deploy (Full feature set!)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Week 1**: Team completes Setup + Foundational together (Phase 1-2)
2. **Week 2**: Team completes Authentication together (Phase 3-4, US1+US2)
3. **Week 3**: Split into parallel streams:
   - Developer A: US3 (View Tasks)
   - Developer B: US4 (Create Task)
   - Developer C: US5 (Toggle Complete)
   - Developer D: US8 (Responsive Design)
4. **Week 4**: Split into parallel streams:
   - Developer A: US6 (Edit Task)
   - Developer B: US7 (Delete Task)
   - Developer C+D: Polish + Deployment
5. **Integration**: Stories merge independently, no conflicts (different files/components)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **CRITICAL**: US1+US2 (Authentication) MUST complete before any other user stories
- Responsive design (US8) is cross-cutting but grouped as separate story for clarity
- MVP scope: US1, US2, US3, US4, US5, US8 (skip US6, US7 for initial release)

---

## Task Count Summary

- **Total Tasks**: 132
- **Setup (Phase 1)**: 13 tasks
- **Foundational (Phase 2)**: 17 tasks
- **US1 (Signup)**: 9 tasks (3 tests + 6 implementation)
- **US2 (Login)**: 9 tasks (3 tests + 6 implementation)
- **US3 (View Tasks)**: 12 tasks (3 tests + 9 implementation)
- **US4 (Create Task)**: 11 tasks (3 tests + 8 implementation)
- **US5 (Toggle Complete)**: 8 tasks (3 tests + 5 implementation)
- **US8 (Responsive)**: 8 tasks (1 test + 7 implementation)
- **US6 (Edit Task)**: 11 tasks (3 tests + 8 implementation)
- **US7 (Delete Task)**: 10 tasks (3 tests + 7 implementation)
- **Polish (Phase 11)**: 14 tasks
- **Deployment (Phase 12)**: 9 tasks

**Parallel Opportunities**: 54 tasks marked [P] can run in parallel within their phases

**MVP Scope**: 101 tasks (excludes US6, US7)

**Test Coverage**: 24 test tasks (unit + E2E) across all user stories for 70%+ coverage target
