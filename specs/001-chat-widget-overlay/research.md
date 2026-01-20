# Research: Chat Widget Overlay

**Feature**: 001-chat-widget-overlay
**Date**: 2026-01-20
**Status**: Complete

## Research Tasks

This document consolidates research findings for implementing the chat widget overlay feature.

---

## 1. React Context vs State Management Library

**Decision**: Use React Context API

**Rationale**:
- Feature scope is limited to dashboard page only
- Two contexts needed: TaskContext (task state), ChatWidgetContext (widget visibility)
- No complex state mutations or middleware requirements
- Project already uses React 19 which has improved context performance
- Avoids adding new dependencies (Redux, Zustand) to existing stack

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| React Context | Native, no deps, simple | Re-renders on any context change | CHOSEN |
| Zustand | Minimal, selective subscriptions | New dependency, overkill for scope | Rejected |
| Redux Toolkit | Powerful, DevTools | Heavy, boilerplate, overkill | Rejected |
| Jotai | Atomic state | New paradigm, learning curve | Rejected |

**Implementation Notes**:
- Split into two contexts to minimize re-renders
- Use `useMemo` for context values
- Consider `useContextSelector` pattern if performance issues arise

---

## 2. Widget Positioning Strategy

**Decision**: CSS `position: fixed` with Portal

**Rationale**:
- Fixed positioning ensures widget stays bottom-right regardless of scroll
- Portal renders widget at document body level, avoiding z-index stacking context issues
- Standard pattern used by Intercom, Drift, and other chat widgets

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Fixed + Portal | Reliable, industry standard | Requires portal component | CHOSEN |
| Fixed in-place | Simpler | Z-index conflicts with modals | Rejected |
| Absolute positioning | No portal needed | Scroll issues, complex calc | Rejected |

**CSS Values**:
```css
.chat-widget {
  position: fixed;
  bottom: 24px;  /* 1.5rem */
  right: 24px;   /* 1.5rem */
  z-index: 9999;
  width: 380px;
  height: 500px;
}

.chat-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9998;  /* Below widget when open */
}
```

---

## 3. Real-Time Task Synchronization Approach

**Decision**: SSE event detection + API refetch

**Rationale**:
- Backend already streams SSE with `event: tool_call` for MCP operations
- Parsing tool_call events identifies when AI modified tasks
- Refetching task list ensures consistency with database state
- Simpler than optimistic updates which require rollback logic

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| SSE detection + refetch | Consistent, simple | Extra API call | CHOSEN |
| Optimistic updates | Instant UI | Complex rollback, state sync | Rejected |
| WebSocket push | True real-time | Backend changes required | Rejected |
| Polling | Simple | Wasteful, delayed | Rejected |

**SSE Event Format (from existing backend)**:
```
event: tool_call
data: {"name": "add_task", "result": {"task_id": 123, "status": "success"}}

event: tool_call
data: {"name": "complete_task", "result": {"task_id": 45, "status": "success"}}
```

**Implementation**:
1. Hook into SSE stream in `useChatMessages`
2. Detect `event: tool_call` with task-related tool names
3. Call `TaskContext.fetchTasks()` after tool_call processed
4. Debounce if multiple operations in quick succession (300ms)

---

## 4. Widget State Persistence

**Decision**: localStorage with JSON serialization

**Rationale**:
- Spec requires: "Widget state (open/closed) persists across page refreshes" (SC-008)
- localStorage is synchronous and reliable for small data
- No expiration needed (session-based persistence)

**Stored Data**:
```typescript
interface WidgetPersistedState {
  isOpen: boolean;
  isMinimized: boolean;
  threadId: string | null;
}

// localStorage key: 'chat-widget-state'
```

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| localStorage | Persistent, sync | 5MB limit (not an issue) | CHOSEN |
| sessionStorage | Auto-clears | Doesn't survive refresh | Rejected |
| IndexedDB | Large storage | Async, overkill | Rejected |
| URL state | Shareable | Clutters URL | Rejected |

---

## 5. Component Extraction Strategy from ChatInterface

**Decision**: Incremental extraction preserving original

**Rationale**:
- ChatInterface.tsx is 729 lines - too large to refactor safely in one pass
- Keep original functional for `/chat` fallback route
- Extract pieces one at a time with tests

**Extraction Order**:
1. **Types first** - Message, ToolCall interfaces → `types/chat.ts`
2. **Utilities** - parseTaskList, scrollToBottom → `lib/chat/utils.ts`
3. **Message rendering** - MessageContent, TaskCard → `ChatMessages.tsx`
4. **Input** - Input field, send logic → `ChatInput.tsx`
5. **SSE logic** - Streaming, thread management → `useChatMessages.ts` hook
6. **Voice** - Already separate in `VoiceInput.tsx` (no change)

**Risk Mitigation**:
- Keep ChatInterface.tsx working throughout extraction
- Add unit tests for each extracted component
- Only integrate into widget after all pieces stable

---

## 6. Responsive Breakpoints

**Decision**: Three breakpoints matching existing TailwindCSS config

**Rationale**:
- Project uses TailwindCSS with default breakpoints
- Match existing responsive patterns in dashboard

**Breakpoints**:
| Screen | Width | Widget Size | Behavior |
|--------|-------|-------------|----------|
| Mobile | < 768px | calc(100vw - 32px) x 60vh | Near full-screen overlay |
| Tablet | 768-1024px | 400px x 500px | Right-aligned widget |
| Desktop | > 1024px | 380px x 500px | Right-aligned widget |

**Tailwind Classes**:
```tsx
<div className="
  fixed bottom-4 right-4
  w-[calc(100vw-32px)] h-[60vh]
  md:w-[400px] md:h-[500px]
  lg:w-[380px]
  ...
">
```

---

## 7. Animation Approach

**Decision**: CSS transitions with Tailwind classes

**Rationale**:
- Simple open/close/minimize transitions
- No complex animations requiring Framer Motion
- Tailwind's transition utilities sufficient

**Animations**:
- **Open**: Fade in + scale up (150ms)
- **Close**: Fade out + scale down (100ms)
- **Minimize**: Slide down + fade (200ms)

**Implementation**:
```tsx
// Widget container
className={cn(
  "transition-all duration-150 ease-out",
  isOpen ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
)}
```

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| CSS transitions | Native, fast, simple | Limited complexity | CHOSEN |
| Framer Motion | Powerful, gestures | New dependency | Rejected |
| React Spring | Physics-based | Learning curve | Rejected |

---

## 8. Accessibility Considerations

**Decision**: ARIA landmarks + keyboard navigation

**Requirements**:
- FAB: `aria-label="Open chat assistant"`, `role="button"`
- Widget: `role="dialog"`, `aria-labelledby="chat-widget-title"`
- Focus trap when widget is open
- Escape key closes widget
- Tab navigation through messages and input

**Implementation**:
```tsx
<button
  aria-label={isOpen ? "Close chat" : "Open chat assistant"}
  aria-expanded={isOpen}
  onClick={toggleWidget}
>
  <ChatIcon />
</button>

<div
  role="dialog"
  aria-labelledby="chat-widget-title"
  aria-modal="true"
>
  <h2 id="chat-widget-title">AI Chat Assistant</h2>
  ...
</div>
```

---

## 9. Error Handling Strategy

**Decision**: Toast notifications + inline error states

**Rationale**:
- Project already uses React Hot Toast for notifications
- Consistent with existing dashboard error patterns
- Non-blocking errors for network issues

**Error Types**:
| Error | Handling |
|-------|----------|
| Network failure | Toast + retry button in widget |
| SSE disconnection | Auto-reconnect with exponential backoff |
| Auth expired (401) | Redirect to login (existing behavior) |
| API error (500) | Toast with generic message |
| Message send failure | Keep message in input, show error below |

---

## 10. Testing Strategy

**Decision**: Unit tests for components + hooks, E2E for integration

**Unit Tests (Vitest)**:
- TaskContext: state updates, API calls
- ChatWidgetContext: state transitions
- useChatMessages: SSE parsing, message handling
- ChatWidget: render states, button clicks
- ChatMessages: message formatting

**E2E Tests (Playwright)**:
- Open widget from FAB
- Send message and see response
- Create task via chat, verify in dashboard
- Minimize and restore
- Responsive behavior at breakpoints

**Coverage Target**: 80% for new code

---

## Summary

| Topic | Decision |
|-------|----------|
| State Management | React Context (2 contexts) |
| Positioning | Fixed + Portal at body |
| Real-time Sync | SSE tool_call detection + API refetch |
| Persistence | localStorage |
| Extraction | Incremental, preserve original |
| Responsive | 3 breakpoints (mobile/tablet/desktop) |
| Animation | CSS transitions via Tailwind |
| Accessibility | ARIA + keyboard navigation |
| Errors | Toast + inline states |
| Testing | Vitest + Playwright |

All research questions resolved. Ready for Phase 1 design.
