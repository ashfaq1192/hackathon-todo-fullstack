---
id: "0002"
title: chat-widget-overlay-plan
stage: plan
date: 2026-01-20
surface: cli
model: claude-opus-4-5
feature: 001-chat-widget-overlay
branch: 001-chat-widget-overlay
user: architect
command: /sp.plan
labels: [planning, chat-widget, frontend, react-context]
links:
  spec: specs/001-chat-widget-overlay/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/001-chat-widget-overlay/plan.md
    action: created
  - path: specs/001-chat-widget-overlay/research.md
    action: created
  - path: specs/001-chat-widget-overlay/data-model.md
    action: created
  - path: specs/001-chat-widget-overlay/quickstart.md
    action: created
  - path: CLAUDE.md
    action: modified
tests:
  - none (planning phase)
---

## Prompt

/sp.plan

Execute implementation planning workflow for the Chat Widget Overlay feature (001-chat-widget-overlay).

## Response snapshot

Created comprehensive implementation plan for Chat Widget Overlay:

1. **Technical Context**: TypeScript 5.6.0, Next.js 16.1.3, React 19.0.0, TailwindCSS
2. **Constitution Check**: All 8 principles PASS
3. **Phase 0 Research**: 10 research topics resolved including:
   - React Context vs state management library → Context chosen
   - Widget positioning → Fixed + Portal
   - Real-time sync → SSE tool_call detection + API refetch
   - State persistence → localStorage
   - Component extraction strategy → Incremental
4. **Phase 1 Data Model**: 6 TypeScript interfaces defined for widget and chat state
5. **Quickstart Guide**: Step-by-step implementation order with verification checklist

**Implementation Phases**:
- Phase 1: Core Infrastructure (TaskContext, ChatWidgetContext)
- Phase 2: Widget Components (FAB, Container, Portal)
- Phase 3: Chat Component Extraction (from 729-line ChatInterface)
- Phase 4: Real-Time Task Sync (SSE event detection)
- Phase 5: Polish & Responsive (minimize, persistence, mobile)

**Key Architecture Decisions**:
- Two React Contexts for state separation (tasks + widget visibility)
- Portal rendering for z-index isolation
- SSE tool_call event detection triggers task refetch
- localStorage for widget state persistence

## Outcome

- Impact: Complete implementation plan ready for task generation
- Tests: N/A (planning phase)
- Files: 4 created (plan.md, research.md, data-model.md, quickstart.md), 1 modified (CLAUDE.md)
- Next prompts: /sp.tasks to generate atomic task list
- Reflection: Thorough codebase exploration enabled accurate technical context

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check PASS (8/8 principles)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
