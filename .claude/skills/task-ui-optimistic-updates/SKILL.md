---
name: task-ui-optimistic-updates
description: Optimistic UI patterns for instant feedback with automatic rollback on errors. Use when building responsive user interfaces in React, specifically for (1) Implementing optimistic updates for checkboxes, toggles, and form submissions, (2) Creating instant UI feedback before API responses, (3) Building responsive task lists with checkbox toggles, (4) Handling automatic rollback when API calls fail, (5) Improving perceived performance with immediate UI changes, (6) Creating smooth UX with loading states and toast notifications
---

# Optimistic UI Updates

Production-ready optimistic UI patterns with automatic rollback on API errors.

## Overview

Optimistic UI provides instant feedback by updating the interface immediately before waiting for server responses. If the API call fails, the UI automatically reverts to its previous state.

**Benefits:**
- Instant visual feedback (feels faster)
- Better perceived performance
- Smooth user experience
- Automatic error recovery (rollback)

## Quick Start

### Basic Pattern

```typescript
const [value, setValue] = useState(initialValue);

const handleChange = async () => {
  const originalValue = value;
  setValue(newValue); // 1. Update UI immediately

  try {
    await api.update(newValue); // 2. Make API call
    toast.success('Updated!');
  } catch (error) {
    setValue(originalValue); // 3. Rollback on error
    toast.error('Failed. Please try again.');
  }
};
```

### Example: Toggle Complete

Copy `assets/optimistic-toggle.tsx` for a complete checkbox toggle implementation:

```typescript
const [isComplete, setIsComplete] = useState(task.complete);

const handleToggle = async () => {
  const original = isComplete;
  setIsComplete(!isComplete); // Optimistic update

  try {
    await apiClient.patch(`/tasks/${task.id}`, { complete: !isComplete });
    toast.success('Task updated!');
  } catch (error) {
    setIsComplete(original); // Rollback
    toast.error('Update failed');
  }
};
```

## Visual Feedback

### Strikethrough for Completed Tasks

```typescript
<span className={isComplete ? 'line-through text-gray-500' : ''}>
  {task.title}
</span>
```

### Background Color Changes

```typescript
<div className={`p-4 ${isComplete ? 'bg-green-50 border-green-200' : 'bg-white'}`}>
  {/* Task content */}
</div>
```

### Loading States

```typescript
const [isLoading, setIsLoading] = useState(false);

<Button disabled={isLoading}>
  {isLoading ? 'Saving...' : 'Save'}
</Button>
```

## When to Use Optimistic Updates

✅ **Good for:**
- Checkboxes and toggles (mark complete/incomplete)
- Like/favorite buttons
- Simple form submissions
- Delete operations with confirmation

❌ **Avoid for:**
- Complex forms with validation
- Operations that need server-generated data (IDs, timestamps)
- Critical financial transactions
- Operations where rollback is confusing

## Conversational Optimistic Updates

In a conversational UI (like a chatbot), the principle of optimistic updates still applies, but the implementation is different. Instead of changing a UI element's state, you provide immediate *linguistic* feedback.

**Core Concept:** The AI agent immediately confirms the action was successful in its chat response, while the actual backend operation (e.g., an MCP tool call) runs asynchronously. If the operation fails, the agent sends a *new, corrective* message.

**Benefits:**
-   **Instant Feedback:** The user receives immediate confirmation, making the chatbot feel highly responsive.
-   **Natural Interaction:** Mirrors human conversation, where we often confirm an action before it's technically complete.
-   **Graceful Error Handling:** Failures are handled through conversation, which is a natural way to manage exceptions.

### Example: Conversational Flow

1.  **User:** "Mark 'buy milk' as complete."
2.  **Chatbot (Optimistic Response):** "Done! I've marked 'buy milk' as complete."
    -   *At this point, the response is sent to the UI immediately.*
    -   *In the background, the AI agent invokes the `complete_task` MCP tool.*
3.  **Scenario A: Success**
    -   The `complete_task` tool succeeds.
    -   No further action is needed. The optimistic response was correct.
4.  **Scenario B: Failure**
    -   The `complete_task` tool fails (e.g., database error, task not found).
    -   The AI agent receives the error from the tool.
    -   **Chatbot (Corrective Response):** "Apologies, it seems I wasn't able to mark 'buy milk' as complete due to a network issue. Please try again in a moment."
    -   *This new message is sent to the UI, correcting the previous optimistic statement.*

### Implementation Pattern

This pattern is typically implemented within the AI agent's orchestration logic on the backend.

```python
# Simplified example within an agent's response generation logic

async def handle_user_message(message: str):
    intent = detect_intent(message) # e.g., 'complete_task'
    entities = extract_entities(message) # e.g., task_title='buy milk'

    if intent == 'complete_task':
        # 1. Immediately generate and send the optimistic response
        yield "Okay, I've marked that task as complete!"

        # 2. In the background, perform the actual operation
        try:
            await complete_task_tool(title=entities['task_title'])
            # 3a. If successful, do nothing. The optimistic response holds true.
        except Exception as e:
            # 3b. If it fails, send a new, corrective message.
            yield f"My apologies, I ran into an error: {e}. The task was not marked as complete."
```

## Error Handling

### Toast Notifications

```typescript
import toast from 'react-hot-toast';

try {
  await api.update();
  toast.success('Updated successfully!');
} catch (error) {
  toast.error('Failed to update. Please try again.');
}
```

### Visual Error States

```typescript
const [error, setError] = useState<string | null>(null);

{error && (
  <p className="text-red-600 text-sm" role="alert">
    {error}
  </p>
)}
```

## Complete Example

```typescript
function TaskItem({ task }: { task: Task }) {
  const [isComplete, setIsComplete] = useState(task.complete);

  const handleToggle = async () => {
    const original = isComplete;
    setIsComplete(!isComplete);

    try {
      await fetch(`/api/tasks/${task.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ complete: !isComplete }),
      });
      toast.success(`Task marked as ${!isComplete ? 'complete' : 'incomplete'}`);
    } catch {
      setIsComplete(original);
      toast.error('Update failed');
    }
  };

  return (
    <div className={isComplete ? 'bg-green-50' : 'bg-white'}>
      <label>
        <input type="checkbox" checked={isComplete} onChange={handleToggle} />
        <span className={isComplete ? 'line-through text-gray-500' : ''}>
          {task.title}
        </span>
      </label>
    </div>
  );
}
```
