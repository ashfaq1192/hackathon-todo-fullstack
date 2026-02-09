# Feature Specification: Chat Widget Overlay

**Feature Branch**: `001-chat-widget-overlay`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Chat Widget Overlay - Convert the current full-page chat experience to a floating widget that appears in the bottom-right corner of the dashboard. Users should be able to interact with the AI chatbot while viewing their tasks in real-time. The widget should be toggleable via a floating action button, minimizable, and persist across dashboard navigation. When the AI creates/updates/deletes tasks, the dashboard task list should update in real-time."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open Chat Widget from Dashboard (Priority: P1)

As a user on the dashboard, I want to click a floating action button in the bottom-right corner to open a chat widget overlay, so that I can interact with the AI assistant while keeping my task list visible.

**Why this priority**: This is the core functionality that enables the entire feature. Without the ability to open the chat widget, none of the other features can be used.

**Independent Test**: Can be fully tested by clicking the chat button on the dashboard and verifying the widget appears as an overlay without navigating away from the dashboard.

**Acceptance Scenarios**:

1. **Given** I am authenticated and on the dashboard page, **When** I click the chat floating action button in the bottom-right corner, **Then** a chat widget overlay appears in the bottom-right area of the screen while the dashboard remains visible behind it.
2. **Given** the chat widget is closed, **When** I click the floating action button, **Then** the widget opens with my previous conversation history (if any) preserved.
3. **Given** I am not authenticated, **When** I try to access the dashboard, **Then** I am redirected to the login page (existing behavior).

---

### User Story 2 - Send Messages and Receive Responses in Widget (Priority: P1)

As a user with the chat widget open, I want to send messages to the AI assistant and receive streaming responses, so that I can manage my tasks through natural language while viewing my task list.

**Why this priority**: This is essential functionality - the widget must be able to send and receive messages to be useful.

**Independent Test**: Can be fully tested by opening the widget, typing a message, sending it, and verifying the AI response streams back correctly.

**Acceptance Scenarios**:

1. **Given** the chat widget is open, **When** I type a message and press Enter or click Send, **Then** my message appears in the chat and the AI response streams in progressively.
2. **Given** the chat widget is open, **When** I send a task-related command like "add buy groceries", **Then** the AI processes it and responds with confirmation.
3. **Given** I am typing a message, **When** the AI is still responding to a previous message, **Then** I can see a loading indicator and my input is not blocked.

---

### User Story 3 - Real-Time Task List Updates (Priority: P1)

As a user interacting with the chatbot, I want my dashboard task list to update automatically when the AI creates, updates, or deletes tasks, so that I can see changes reflected immediately without refreshing.

**Why this priority**: This is the key differentiator from the current full-page approach - seeing real-time updates is the main value proposition of the widget overlay.

**Independent Test**: Can be fully tested by opening the widget, asking the AI to create a task, and verifying the task appears in the dashboard list without page refresh.

**Acceptance Scenarios**:

1. **Given** the chat widget is open and dashboard is visible, **When** I ask the AI to create a new task, **Then** the new task appears in the dashboard task list within 2 seconds without page refresh.
2. **Given** the chat widget is open and dashboard is visible, **When** I ask the AI to mark a task as complete, **Then** the task status updates in the dashboard list within 2 seconds.
3. **Given** the chat widget is open and dashboard is visible, **When** I ask the AI to delete a task, **Then** the task is removed from the dashboard list within 2 seconds.
4. **Given** the chat widget is open and dashboard is visible, **When** I ask the AI to update a task's title or priority, **Then** the changes appear in the dashboard list within 2 seconds.

---

### User Story 4 - Minimize and Restore Chat Widget (Priority: P2)

As a user with the chat widget open, I want to minimize it to just the floating action button without losing my conversation, so that I can focus on my tasks and resume the chat later.

**Why this priority**: Improves usability by allowing users to temporarily hide the widget without losing context, but the feature works without this.

**Independent Test**: Can be fully tested by opening the widget, minimizing it, and then restoring it to verify conversation is preserved.

**Acceptance Scenarios**:

1. **Given** the chat widget is open, **When** I click the minimize button, **Then** the widget collapses to just the floating action button and my conversation is preserved.
2. **Given** the chat widget is minimized, **When** I click the floating action button, **Then** the widget restores to its previous size with all conversation history intact.
3. **Given** the chat widget is minimized and the AI sends a response, **When** I restore the widget, **Then** I can see the response that was received while minimized.

---

### User Story 5 - Close Chat Widget (Priority: P2)

As a user, I want to close the chat widget completely to reclaim screen space, understanding that I can reopen it anytime.

**Why this priority**: Standard widget behavior that users expect, but minimize covers most use cases.

**Independent Test**: Can be fully tested by opening the widget, closing it, and reopening to verify it works correctly.

**Acceptance Scenarios**:

1. **Given** the chat widget is open, **When** I click the close (X) button, **Then** the widget closes completely and only the floating action button remains visible.
2. **Given** the chat widget is closed, **When** I click the floating action button, **Then** the widget opens with my conversation history preserved.

---

### User Story 6 - Responsive Widget Behavior (Priority: P3)

As a user on a mobile or tablet device, I want the chat widget to adapt appropriately to smaller screens, so that I can still use the chat functionality effectively.

**Why this priority**: Mobile usability is important but secondary to core desktop functionality.

**Independent Test**: Can be fully tested by opening the widget on various screen sizes and verifying it remains usable.

**Acceptance Scenarios**:

1. **Given** I am on a screen width below 768px (mobile), **When** I open the chat widget, **Then** the widget expands to use most of the screen width for better usability.
2. **Given** I am on a screen width between 768px and 1024px (tablet), **When** I open the chat widget, **Then** the widget uses an appropriately sized overlay that doesn't obstruct the entire dashboard.
3. **Given** I am on any screen size, **When** I open the chat widget, **Then** it remains within the viewport boundaries and is fully usable.

---

### Edge Cases

- What happens when the user's session expires while the chat widget is open?
  - The widget should detect authentication failure and prompt the user to re-login.
- How does the system handle network disconnection during a chat?
  - The widget should display an error message and allow retry when connection is restored.
- What happens if the AI response takes longer than expected (>30 seconds)?
  - The widget should show a loading state and allow the user to cancel the request.
- What happens when the user manually modifies a task on the dashboard while the widget shows it?
  - The widget's task references should remain valid; the dashboard is the source of truth.
- What happens if multiple browser tabs are open with the same dashboard?
  - Each tab operates independently; real-time updates apply to the active tab's widget session.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a floating action button (FAB) in the bottom-right corner of the dashboard page.
- **FR-002**: System MUST open a chat widget overlay when the FAB is clicked.
- **FR-003**: Chat widget MUST remain visible while the dashboard content is still accessible and visible.
- **FR-004**: Chat widget MUST support sending messages to the AI assistant.
- **FR-005**: Chat widget MUST display streaming AI responses progressively as they are received.
- **FR-006**: System MUST update the dashboard task list in real-time when the AI creates, updates, or deletes tasks.
- **FR-007**: Chat widget MUST preserve conversation history when minimized or closed within the same session.
- **FR-008**: Chat widget MUST provide a minimize button to collapse it to just the FAB.
- **FR-009**: Chat widget MUST provide a close button to hide the widget entirely.
- **FR-010**: Chat widget MUST support all existing chat features (voice input, message formatting, task card display).
- **FR-011**: System MUST maintain authentication state between the widget and dashboard.
- **FR-012**: Chat widget MUST be responsive and usable on mobile devices (screen width < 768px).
- **FR-013**: System MUST handle errors gracefully with user-friendly messages.
- **FR-014**: FAB MUST remain visible at all times on the dashboard, regardless of scroll position.

### Key Entities

- **ChatWidget**: The overlay component containing the chat interface, with states (open, minimized, closed) and position (bottom-right).
- **FloatingActionButton**: The persistent button that toggles the chat widget, displaying a chat icon and optional notification badge.
- **WidgetState**: Tracks the widget's current state (open/minimized/closed), conversation thread ID, and any pending messages.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the chat widget and send their first message within 3 seconds of clicking the FAB.
- **SC-002**: Task list updates appear on the dashboard within 2 seconds of the AI completing a task operation.
- **SC-003**: Chat widget occupies no more than 40% of viewport width on desktop screens (>1024px).
- **SC-004**: Users can minimize and restore the widget without losing any conversation context.
- **SC-005**: The widget remains fully functional on screens as small as 320px width.
- **SC-006**: Users can see both the chat widget and at least 50% of the dashboard content simultaneously on desktop.
- **SC-007**: All existing chat functionality (voice input, message formatting, task cards) works identically in the widget.
- **SC-008**: Widget state (open/closed) persists across page refreshes within the same browser session.

## Assumptions

- The existing backend chat API (ChatKit endpoints) will work without modification - only frontend changes are needed.
- The existing SSE streaming mechanism is sufficient for real-time communication.
- Real-time task updates will be achieved by refreshing the task list after AI operations, not through WebSocket push.
- The current authentication system (Better Auth + JWT) remains unchanged.
- Voice input functionality will be preserved and work within the widget context.
- The `/chat` full-page route may be retained for users who prefer the full-screen experience (optional).
