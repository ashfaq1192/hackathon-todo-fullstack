# Feature Specification: CLI Todo App with Basic CRUD Operations

**Feature Branch**: `001-cli-todo-app`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "Phase I: CLI Todo App with Basic CRUD Operations - Implement a menu-driven CLI todo application with in-memory storage supporting: Add Task (title, description, priority), View Task List (show all tasks with status and priority), Mark Task as Complete, Update Task (edit title/description/priority), Delete Task. Tasks include priority field (High/Medium/Low) set by user."

## Clarifications

### Session 2025-12-17

- Q: When a task is marked as complete, should users be able to mark it as incomplete again (toggle), or is completion a permanent one-way state? → A: Allow toggling - users can mark complete tasks back to incomplete
- Q: After deleting a task (e.g., task ID 2), should the next new task reuse that ID (2), or should IDs always increment and never be reused? → A: Never reuse IDs - always increment, even after deletions
- Q: When viewing the task list, should tasks be displayed in a specific order (e.g., by priority, creation order, completion status), or in any order? → A: By priority - High, then Medium, then Low (incomplete tasks first)
- Q: How should users select operations in the menu-driven interface? → A: Numbered menu - users enter numbers (1, 2, 3, etc.) to select operations
- Q: When updating a task, can users update individual fields (only title, or only description, or only priority), or must they provide all three fields every time? → A: Update individual fields - users can update only title, or only description, or only priority, or any combination

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and View Tasks (Priority: High)

As a user, I want to add new tasks with titles, descriptions, and priority levels (High/Medium/Low), then view them in a list so I can track what I need to do and understand task urgency.

**Why this feature is High priority**: Core functionality - without the ability to create and view tasks, the application has no value. This is the foundation of any todo app.

**Independent Test**: Can be fully tested by launching the app, adding 2-3 tasks with different titles/descriptions, viewing the task list, and verifying all tasks appear with correct information and completion status (initially incomplete).

**Acceptance Scenarios**:

1. **Given** the app is running and task list is empty, **When** I choose to add a task with title "Buy groceries", description "Milk, bread, eggs", and priority "High", **Then** the task is created with a unique ID, stored with complete=false and priority=High, and I see a confirmation message
2. **Given** I have added 3 tasks with different priorities (High, Medium, Low), **When** I choose to view the task list, **Then** I see all 3 tasks displayed with their ID, title, description, priority level, and completion status in a readable format, ordered by priority (High first, then Medium, then Low), with incomplete tasks appearing before completed tasks within each priority group
3. **Given** the task list is empty, **When** I choose to view the task list, **Then** I see a message indicating no tasks exist

---

### User Story 2 - Mark Tasks Complete (Priority: High)

As a user, I want to mark tasks as complete or incomplete so I can track my progress, distinguish finished work from pending work, and reopen tasks if needed.

**Why this feature is High priority**: Essential for basic task management - users need to track what's done. Without this, the app is just a list with no state tracking.

**Independent Test**: Can be fully tested by adding 2 tasks, marking one as complete, viewing the list, verifying the completed task shows complete=true, then marking it incomplete again and verifying it returns to complete=false.

**Acceptance Scenarios**:

1. **Given** I have 3 tasks and one has ID 2, **When** I choose to mark task ID 2 as complete, **Then** task 2's complete status changes to true and I see a confirmation message
2. **Given** I have marked task ID 2 as complete, **When** I view the task list, **Then** task ID 2 displays with complete=true and all other tasks show complete=false
3. **Given** I have a completed task with ID 2 (complete=true), **When** I choose to mark task ID 2 as incomplete, **Then** task 2's complete status changes to false and I see a confirmation message
4. **Given** I attempt to mark a non-existent task ID 999 as complete, **When** I submit the request, **Then** I see an error message indicating the task was not found

---

### User Story 3 - Update Task Details (Priority: Medium)

As a user, I want to edit a task's title, description, or priority level individually or in combination so I can correct mistakes, refine task details, or adjust urgency as situations change.

**Why this feature is Medium priority**: Important for usability - users make mistakes or need to clarify tasks. This is a "should have" feature but not critical for MVP.

**Independent Test**: Can be fully tested by adding a task, updating only its title from "Old Title" to "New Title", viewing the list, and verifying the updated title appears while description and priority remain unchanged.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 1, title "Buy milk", description "Whole milk", and priority "Low", **When** I choose to update task ID 1 with only a new title "Buy organic milk", **Then** only the task's title is updated, description and priority remain unchanged, and I see a confirmation message
2. **Given** I have a task with ID 1, **When** I choose to update task ID 1 with new title "Buy organic milk", new description "Organic whole milk", and new priority "High", **Then** the task's title, description, and priority are all updated and I see a confirmation message
3. **Given** I have updated a task, **When** I view the task list, **Then** I see the updated field values for that task, and its complete status remains unchanged
4. **Given** I attempt to update non-existent task ID 999, **When** I submit the update, **Then** I see an error message indicating the task was not found

---

### User Story 4 - Delete Tasks (Priority: Medium)

As a user, I want to delete tasks I no longer need so I can keep my task list clean and relevant.

**Why this feature is Medium priority**: Important for list management but not essential for MVP. Users can work around this by ignoring unwanted tasks.

**Independent Test**: Can be fully tested by adding 3 tasks, deleting task ID 2, viewing the list, and verifying only 2 tasks remain (IDs 1 and 3).

**Acceptance Scenarios**:

1. **Given** I have 3 tasks with IDs 1, 2, and 3, **When** I choose to delete task ID 2, **Then** task ID 2 is removed from storage and I see a confirmation message
2. **Given** I have deleted task ID 2, **When** I view the task list, **Then** I see only tasks with IDs 1 and 3, and task ID 2 is not present
3. **Given** I attempt to delete non-existent task ID 999, **When** I submit the delete request, **Then** I see an error message indicating the task was not found

---

### Edge Cases

- What happens when a user enters an empty title when adding a task? (Task creation should fail with validation error message)
- What happens when a user enters an invalid task ID (non-numeric, negative, zero)? (Show error message indicating invalid input)
- What happens when a user tries to add a task with only whitespace in the title? (Treat as empty and reject)
- What happens when the description is left empty/blank? (Allowed - description is optional, title and priority are required)
- What happens when a user enters an invalid priority (not High/Medium/Low, e.g., "Urgent", "low", "HIGH")? (Show error message indicating priority must be exactly "High", "Medium", or "Low" - case-sensitive)
- What happens when a user tries to update a task but provides the same values? (Update succeeds, no change in data)
- What happens when a user updates only the title field of a task? (Only title is changed, description and priority remain unchanged)
- What happens when a user updates a task but provides an empty title? (Update fails with validation error message - title cannot be empty)
- What happens when a user updates only the priority field with an invalid value? (Update fails with validation error message - priority must be High, Medium, or Low)
- What happens when multiple tasks are created in sequence? (Each gets a unique, incrementing ID; IDs never reuse deleted values)
- What happens when tasks with IDs 1, 2, 3 exist, then task 2 is deleted, then a new task is added? (New task gets ID 4, not ID 2; deleted IDs are never reused)
- What happens when a user doesn't provide a priority when adding a task? (Show error message indicating priority is required)
- What happens when multiple tasks have the same priority and completion status? (Tasks within the same priority/completion group are displayed by ID ascending - oldest first)
- What happens when a user enters an invalid menu choice (non-numeric, out of range, negative)? (Show error message indicating invalid selection and re-display menu)
- What happens when a user enters a valid menu number with extra text (e.g., "1 add task")? (Parse the numeric part; if valid, accept it; otherwise show error)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a numbered menu-driven interface that displays available operations with corresponding numbers (e.g., 1=Add, 2=View, 3=Mark Complete/Incomplete, 4=Update, 5=Delete, 6=Exit) and accepts numeric input to select operations
- **FR-002**: System MUST allow users to add a new task by providing a title (required), description (optional), and priority level (required, one of: High, Medium, Low)
- **FR-003**: System MUST assign a unique numeric ID to each task automatically upon creation, starting from 1 and always incrementing (IDs are never reused, even after task deletion)
- **FR-004**: System MUST store each task as a dictionary with keys: id (int), title (str), description (str), priority (str), complete (bool, default false)
- **FR-005**: System MUST maintain all tasks in a list data structure during the session (in-memory storage, data lost on exit)
- **FR-006**: System MUST display all tasks in the list with their ID, title, description, priority level, and completion status when user chooses to view, sorted by priority (High, then Medium, then Low) with incomplete tasks appearing before completed tasks within each priority group
- **FR-007**: System MUST allow users to toggle a task's completion status by specifying its ID, changing complete status from false to true or from true to false
- **FR-008**: System MUST allow users to update a task's title, description, and/or priority individually or in combination by specifying its ID (partial updates allowed - only provided fields are changed, others remain unchanged)
- **FR-009**: System MUST allow users to delete a task by specifying its ID, removing it from the list
- **FR-010**: System MUST validate that task titles are non-empty (after trimming whitespace) before creation or update
- **FR-011**: System MUST display error messages when users attempt operations on non-existent task IDs
- **FR-012**: System MUST display error messages when users provide invalid input (empty title, invalid ID format, invalid priority level)
- **FR-013**: System MUST validate that priority is one of the allowed values (High, Medium, Low) before creation or update
- **FR-014**: System MUST allow users to exit the application gracefully
- **FR-015**: System MUST persist the menu loop until user explicitly chooses to exit
- **FR-016**: System MUST display confirmation messages after successful operations (task added, updated, deleted, marked complete)

### Key Entities

- **Task**: Represents a single todo item with attributes:
  - id: Unique numeric identifier (integer, auto-generated, starting from 1, always increments and never reused after deletion)
  - title: Short description of what needs to be done (string, required, non-empty)
  - description: Detailed information about the task (string, optional, can be empty)
  - priority: Urgency level set by user (string, required, one of: "High", "Medium", "Low")
    - **High**: Critical tasks crucial for main goals, must be completed immediately
    - **Medium**: Important tasks without immediate urgency, scheduled after High priority work
    - **Low**: Tasks that can be postponed or delegated, minimal impact if left undone
  - complete: Completion status flag (boolean, defaults to false, can be toggled between true and false)

  **Example**: `{'id': 1, 'title': 'Buy groceries', 'description': 'Milk, bread, eggs', 'priority': 'High', 'complete': False}`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task in under 15 seconds from menu selection to confirmation
- **SC-002**: Users can view their complete task list in under 3 seconds from menu selection
- **SC-003**: 100% of valid task operations (add, view, mark, update, delete) complete successfully without errors
- **SC-004**: Users see clear error messages for 100% of invalid operations (bad IDs, empty titles) without application crashes
- **SC-005**: Users can complete all 5 core operations (add, view, mark, update, delete) in a single session without restarting the application
- **SC-006**: Task data persists correctly within a session - tasks created remain viewable until the app exits
- **SC-007**: Users can navigate the menu and perform operations without consulting external documentation (self-evident interface)
