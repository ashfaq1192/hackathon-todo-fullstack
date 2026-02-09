# Quickstart Guide: Chat Widget Overlay

**Feature**: 001-chat-widget-overlay
**Date**: 2026-01-20

## Prerequisites

- Node.js 18+ installed
- Phase 3 chatbot already deployed and working
- Backend API running (no changes needed)
- Frontend development environment set up

## Development Setup

### 1. Navigate to Frontend Directory

```bash
cd phase-3-chatbot/frontend
```

### 2. Install Dependencies (if needed)

```bash
pnpm install
```

### 3. Start Development Server

```bash
pnpm dev
```

The app runs at `http://localhost:3000`.

### 4. Verify Backend Connection

Ensure the backend is running and `NEXT_PUBLIC_API_URL` is set in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Implementation Order

Follow this order to implement the feature incrementally:

### Phase 1: Core Infrastructure

1. Create `types/chat-widget.ts` - Widget state types
2. Create `types/chat.ts` - Chat message types (if not exists)
3. Create `contexts/TaskContext.tsx` - Task state provider
4. Create `contexts/ChatWidgetContext.tsx` - Widget state provider
5. Test contexts in isolation

### Phase 2: Widget Components

1. Create `components/ui/Portal.tsx` - React portal wrapper
2. Create `components/chat/ChatWidgetFAB.tsx` - Floating action button
3. Create `components/chat/ChatWidget.tsx` - Widget container
4. Add FAB to dashboard page (static, no functionality yet)

### Phase 3: Chat Component Extraction

1. Create `hooks/useChatMessages.ts` - Extract from ChatInterface
2. Create `components/chat/ChatMessages.tsx` - Message display
3. Create `components/chat/ChatInput.tsx` - Input with send
4. Integrate extracted components into ChatWidget
5. Verify SSE streaming works

### Phase 4: Real-Time Task Sync

1. Create `hooks/useTaskSync.ts` - Tool call detection
2. Modify `TodoList.tsx` - Use TaskContext
3. Modify `app/dashboard/page.tsx` - Add providers
4. Test: Create task via chat, verify appears in list

### Phase 5: Polish

1. Implement minimize/restore with animation
2. Add localStorage persistence
3. Add responsive styles
4. Test on mobile viewport

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `types/chat-widget.ts` | Widget state TypeScript types |
| `contexts/TaskContext.tsx` | Shared task state provider |
| `contexts/ChatWidgetContext.tsx` | Widget visibility provider |
| `components/ui/Portal.tsx` | Portal for widget rendering |
| `components/chat/ChatWidgetFAB.tsx` | Floating action button |
| `components/chat/ChatWidget.tsx` | Main widget container |
| `components/chat/ChatMessages.tsx` | Message list component |
| `components/chat/ChatInput.tsx` | Input field component |
| `hooks/useChatMessages.ts` | SSE streaming hook |
| `hooks/useTaskSync.ts` | Task refresh hook |

---

## Key Files to Modify

| File | Change |
|------|--------|
| `app/dashboard/layout.tsx` | Wrap with ChatWidgetProvider |
| `app/dashboard/page.tsx` | Wrap with TaskProvider, add FAB + Widget |
| `components/todos/TodoList.tsx` | Use TaskContext instead of props |

---

## Testing Commands

### Run Unit Tests

```bash
pnpm test
```

### Run E2E Tests

```bash
pnpm test:e2e
```

### Type Check

```bash
pnpm type-check
```

### Lint

```bash
pnpm lint
```

---

## Verification Checklist

After each phase, verify:

- [ ] **Phase 1**: Contexts render without errors, state updates work
- [ ] **Phase 2**: FAB visible on dashboard, widget opens/closes
- [ ] **Phase 3**: Can send message, see streaming response
- [ ] **Phase 4**: Create task via chat → appears in dashboard list
- [ ] **Phase 5**: Minimize works, state persists after refresh

---

## Common Issues

### Widget doesn't appear
- Check z-index conflicts with Navigation (use z-index: 9999)
- Verify Portal is mounted at document.body

### SSE not streaming
- Check CORS configuration in backend
- Verify Authorization header is sent
- Check browser DevTools Network tab for SSE connection

### Tasks not updating
- Verify tool_call events are being parsed correctly
- Check TaskContext.fetchTasks() is called
- Add console.log in useTaskSync to debug event flow

### localStorage not persisting
- Check browser allows localStorage (incognito may block)
- Verify JSON serialization isn't failing

---

## Environment Variables

No new environment variables required. Uses existing:

```env
# .env.local (frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000

# Backend (.env) - no changes
DATABASE_URL=...
JWT_SECRET=...
```

---

## API Endpoints Used

All existing, no changes:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/{user_id}/tasks` | Fetch task list |
| `POST /api/chatkit/session` | Create chat session |
| `POST /api/chatkit/threads` | Create thread |
| `POST /api/chatkit/threads/{id}/messages` | Send message (SSE) |

---

## Next Steps

After completing implementation:

1. Run full test suite
2. Test on mobile devices
3. Deploy to staging
4. Record demo video showing:
   - Open widget from FAB
   - Send message to AI
   - Create task via chat
   - See task appear in dashboard
   - Minimize and restore widget
