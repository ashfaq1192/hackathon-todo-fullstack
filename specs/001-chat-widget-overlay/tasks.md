# Tasks: Chat Widget Overlay

**Input**: Design documents from `/specs/001-chat-widget-overlay/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No explicit test requirements in spec. Tests included for critical integration points.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- All file paths are relative to `/mnt/e/projects/hackathon-todo-fullstack/phase-3-chatbot/frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create type definitions and project structure for the widget feature

- [x] T001 [P] Create widget state types in types/chat-widget.ts (WidgetMode, WidgetState, WidgetPersistedState)
- [x] T002 [P] Create chat types in types/chat.ts (ChatMessage, MessageRole, ToolCallEvent, TaskToolName)
- [x] T003 Create contexts directory structure at contexts/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contexts and hooks that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement TaskContext provider in contexts/TaskContext.tsx with tasks[], isLoading, error state
- [x] T005 Add TaskContext actions: fetchTasks, addTask, updateTask, deleteTask, triggerRefresh
- [x] T006 Implement ChatWidgetContext provider in contexts/ChatWidgetContext.tsx with mode, threadId, hasUnreadMessages
- [x] T007 Add ChatWidgetContext actions: open, close, minimize, restore, setThreadId, markMessagesRead
- [x] T008 Add localStorage persistence for ChatWidgetContext (save/restore on mount)
- [x] T009 Create Portal component in components/ui/Portal.tsx for widget DOM rendering
- [x] T010 Create useChatWidget hook in hooks/useChatWidget.ts wrapping ChatWidgetContext

**Checkpoint**: Foundation ready - contexts provide shared state, Portal enables overlay rendering

---

## Phase 3: User Story 1 - Open Chat Widget from Dashboard (Priority: P1) - MVP

**Goal**: Click FAB to open chat widget overlay while dashboard remains visible

**Independent Test**: Click chat button on dashboard, verify widget appears as overlay without navigation

### Implementation for User Story 1

- [x] T011 [P] [US1] Create ChatWidgetFAB component in components/chat/ChatWidgetFAB.tsx with chat icon
- [x] T012 [P] [US1] Style FAB with fixed positioning (bottom-right, z-index 9998) in ChatWidgetFAB.tsx
- [x] T013 [US1] Create ChatWidget container in components/chat/ChatWidget.tsx with header (title, buttons)
- [x] T014 [US1] Style ChatWidget with fixed positioning (bottom-right, z-index 9999, 380px width) in ChatWidget.tsx
- [x] T015 [US1] Add open/close animation transitions (opacity, scale) to ChatWidget.tsx
- [x] T016 [US1] Integrate FAB click handler with ChatWidgetContext.open() in ChatWidgetFAB.tsx
- [x] T017 [US1] Render ChatWidget conditionally based on context mode in ChatWidget.tsx
- [x] T018 [US1] Modify dashboard layout in app/dashboard/layout.tsx to wrap with ChatWidgetProvider
- [x] T019 [US1] Modify dashboard page in app/dashboard/page.tsx to wrap with TaskProvider
- [x] T020 [US1] Add ChatWidgetFAB and ChatWidget (via Portal) to app/dashboard/page.tsx

**Checkpoint**: FAB visible on dashboard, clicking opens empty widget container, dashboard remains visible

---

## Phase 4: User Story 2 - Send Messages and Receive Responses (Priority: P1)

**Goal**: Send messages to AI assistant, receive streaming responses in widget

**Independent Test**: Open widget, type message, send, verify AI response streams back

### Implementation for User Story 2

- [x] T021 [US2] Extract message content rendering logic from ChatInterface.tsx to lib/chat/messageUtils.ts
- [x] T022 [US2] Create ChatMessages component in components/chat/ChatMessages.tsx with message list display
- [x] T023 [US2] Add MessageContent, FormattedTaskList, TaskCard sub-components to ChatMessages.tsx
- [x] T024 [US2] Add auto-scroll behavior to ChatMessages.tsx (scroll to bottom on new messages)
- [x] T025 [US2] Create ChatInput component in components/chat/ChatInput.tsx with textarea and send button
- [x] T026 [US2] Add Enter key submit and loading state to ChatInput.tsx
- [x] T027 [US2] Integrate existing VoiceInput component into ChatInput.tsx
- [x] T028 [US2] Create useChatMessages hook in hooks/useChatMessages.ts for thread and message management
- [x] T029 [US2] Implement SSE streaming in useChatMessages.ts (POST to /api/chatkit/threads/{id}/messages)
- [x] T030 [US2] Parse SSE events (start, delta, tool_call, done) in useChatMessages.ts
- [x] T031 [US2] Add thread creation logic to useChatMessages.ts (create thread on first message)
- [x] T032 [US2] Integrate ChatMessages and ChatInput into ChatWidget.tsx body
- [x] T033 [US2] Connect useChatMessages hook to ChatWidget.tsx and pass to child components

**Checkpoint**: Can send messages in widget, AI responses stream back progressively, voice input works

---

## Phase 5: User Story 3 - Real-Time Task List Updates (Priority: P1)

**Goal**: Dashboard task list updates automatically when AI creates/updates/deletes tasks

**Independent Test**: Open widget, ask AI to create task, verify task appears in dashboard list without refresh

### Implementation for User Story 3

- [x] T034 [US3] Create useTaskSync hook in hooks/useTaskSync.ts to detect tool_call SSE events
- [x] T035 [US3] Add tool_call event callback registration to useChatMessages.ts (onToolCall)
- [x] T036 [US3] Implement debounced TaskContext.triggerRefresh() in useTaskSync.ts (300ms debounce)
- [x] T037 [US3] Modify TodoList.tsx to consume tasks from TaskContext instead of props
- [x] T038 [US3] Remove internal fetch logic from TodoList.tsx (now handled by TaskContext)
- [x] T039 [US3] Preserve existing filter/search functionality in TodoList.tsx
- [x] T040 [US3] Modify AddTodoForm.tsx to use TaskContext.addTask() instead of direct API call
- [x] T041 [US3] Integrate useTaskSync hook into ChatWidget.tsx to trigger refresh on tool_call
- [x] T042 [US3] Add loading indicator to TodoList.tsx when TaskContext.isLoading changes

**Checkpoint**: Create/update/delete task via chat → dashboard updates within 2 seconds

---

## Phase 6: User Story 4 - Minimize and Restore Chat Widget (Priority: P2)

**Goal**: Minimize widget to FAB without losing conversation, restore with history intact

**Independent Test**: Open widget, send message, minimize, restore, verify conversation preserved

### Implementation for User Story 4

- [x] T043 [US4] Add minimize button to ChatWidget.tsx header
- [x] T044 [US4] Implement minimize animation (slide down, fade out) in ChatWidget.tsx
- [x] T045 [US4] Update ChatWidgetContext to handle minimized → open transition
- [x] T046 [US4] Add unread message badge logic to ChatWidgetFAB.tsx (show when minimized with new messages)
- [x] T047 [US4] Update useChatMessages.ts to notify context of new messages while minimized
- [x] T048 [US4] Clear unread badge when widget is restored (call markMessagesRead)

**Checkpoint**: Minimize collapses widget, badge shows unread count, restore shows full conversation

---

## Phase 7: User Story 5 - Close Chat Widget (Priority: P2)

**Goal**: Close widget completely, reopen preserves conversation history

**Independent Test**: Open widget, send messages, close, reopen, verify history preserved

### Implementation for User Story 5

- [x] T049 [US5] Add close (X) button to ChatWidget.tsx header
- [x] T050 [US5] Implement close animation (scale down, fade out) in ChatWidget.tsx
- [x] T051 [US5] Ensure threadId is preserved in ChatWidgetContext on close
- [x] T052 [US5] Load previous messages from thread when widget reopens in useChatMessages.ts
- [x] T053 [US5] Add GET request to /api/chatkit/threads/{id}/messages in useChatMessages.ts for history

**Checkpoint**: Close hides widget, FAB remains, reopen loads conversation history from thread

---

## Phase 8: User Story 6 - Responsive Widget Behavior (Priority: P3)

**Goal**: Widget adapts to mobile/tablet screens while remaining usable

**Independent Test**: Open widget at various viewport sizes (320px, 768px, 1024px+), verify usability

### Implementation for User Story 6

- [x] T054 [US6] Add responsive breakpoints to ChatWidget.tsx (mobile <768px: calc(100vw-32px))
- [x] T055 [US6] Add tablet breakpoint to ChatWidget.tsx (768-1024px: 400px width)
- [x] T056 [US6] Ensure ChatWidget height is responsive (60vh on mobile, 500px on desktop)
- [x] T057 [US6] Adjust FAB position for mobile (smaller offset from edge)
- [x] T058 [US6] Test and adjust ChatInput.tsx for mobile keyboard handling
- [x] T059 [US6] Add viewport meta handling to prevent zoom on input focus

**Checkpoint**: Widget fully functional on 320px to 1920px screens, remains within viewport

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [x] T060 Add error handling for network failures in useChatMessages.ts (toast notification, retry)
- [x] T061 Add error handling for auth expiration (401) in useChatMessages.ts (redirect to login)
- [x] T062 Add loading state UI to ChatWidget.tsx while waiting for AI response
- [x] T063 Add cancel request functionality for long-running AI responses
- [x] T064 Add keyboard accessibility to ChatWidgetFAB.tsx and ChatWidget.tsx (ARIA labels, focus trap)
- [x] T065 Add Escape key handler to close/minimize widget
- [x] T066 Verify all existing chat features work in widget (task cards, markdown, code highlighting)
- [x] T067 Run quickstart.md validation checklist
- [x] T068 Clean up any unused code from ChatInterface.tsx refactoring

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-8 (User Stories)**: All depend on Phase 2 completion
- **Phase 9 (Polish)**: Depends on Phases 3-5 minimum (core P1 stories)

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Open Widget | P1 | Phase 2 only | None (first) |
| US2 - Send Messages | P1 | US1 (needs widget container) | None |
| US3 - Real-Time Sync | P1 | US2 (needs message sending) | None |
| US4 - Minimize | P2 | US1 (needs widget container) | US5, US6 |
| US5 - Close | P2 | US1 (needs widget container) | US4, US6 |
| US6 - Responsive | P3 | US1 (needs widget container) | US4, US5 |

### Within Each User Story

- Tasks marked [P] within same story can run in parallel
- Follow task number order for sequential dependencies
- Complete story before moving to next priority level

### Parallel Opportunities

**Phase 1**: T001, T002, T003 (all parallel - different files)

**Phase 3 (US1)**: T011, T012 can parallel (same component but independent additions)

**Phase 4 (US2)**: T021, T022, T025 can start parallel (different components)

**Phases 6-8**: US4, US5, US6 can run in parallel after US3 completes (if team capacity)

---

## Parallel Example: User Story 2

```bash
# Launch component creation in parallel:
Task T022: "Create ChatMessages component"
Task T025: "Create ChatInput component"

# After both complete, integrate:
Task T032: "Integrate ChatMessages and ChatInput into ChatWidget.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup (3 tasks)
2. Complete Phase 2: Foundational (7 tasks) - CRITICAL
3. Complete Phase 3: US1 - Open Widget (10 tasks)
4. **VALIDATE**: FAB visible, widget opens, dashboard visible
5. Complete Phase 4: US2 - Send Messages (13 tasks)
6. **VALIDATE**: Can send messages, AI responds via SSE
7. Complete Phase 5: US3 - Real-Time Sync (9 tasks)
8. **VALIDATE**: Dashboard updates when AI modifies tasks
9. **MVP COMPLETE** - Core value delivered

### Incremental Delivery (P2/P3 Stories)

10. Add US4 - Minimize/Restore (6 tasks)
11. Add US5 - Close/Reopen (5 tasks)
12. Add US6 - Responsive (6 tasks)
13. Complete Phase 9: Polish (9 tasks)

### Total Task Count

| Phase | Tasks | Cumulative |
|-------|-------|------------|
| Phase 1: Setup | 3 | 3 |
| Phase 2: Foundational | 7 | 10 |
| Phase 3: US1 | 10 | 20 |
| Phase 4: US2 | 13 | 33 |
| Phase 5: US3 | 9 | 42 |
| Phase 6: US4 | 6 | 48 |
| Phase 7: US5 | 5 | 53 |
| Phase 8: US6 | 6 | 59 |
| Phase 9: Polish | 9 | **68** |

**Total**: 68 tasks
**MVP (P1 stories)**: 42 tasks
**Full feature**: 68 tasks

---

## Notes

- [P] tasks = different files, no dependencies within that phase
- [Story] label maps task to user story for traceability
- Each user story independently completable after Phase 2
- All file paths relative to `/phase-3-chatbot/frontend/`
- Backend requires NO changes - all frontend work
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
