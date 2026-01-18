# Feature Specification: Next.js Frontend Application (Phase II - Stage 3)

**Feature Branch**: `004-frontend-nextjs`
**Created**: 2025-12-23
**Status**: Draft
**Phase**: Phase II - Stage 3 (Frontend Development)

## Overview

Build a modern, responsive web frontend using Next.js 16+ (App Router) that provides a complete user interface for the todo application. This stage integrates with the completed backend API (Stage 2) and implements Better Auth for user authentication, delivering a production-ready full-stack web application.

### Context
- **Depends On**:
  - Stage 1 (Database & Models Setup) - `002-database-setup` ✅
  - Stage 2 (Backend API) - `003-backend-api` ✅
- **Enables**: Phase III (AI Chatbot Integration)
- **Technology Stack**:
  - Next.js 16+ (App Router)
  - TypeScript 5+
  - Better Auth (authentication)
  - Tailwind CSS 4+ (styling)
  - React 19+ (UI framework)
  - Vercel (deployment platform)

### Success Criteria
- ✅ All 5 Basic Level features accessible via web UI
- ✅ Better Auth integration with signup/signin flows
- ✅ Responsive design works on mobile, tablet, desktop
- ✅ Full integration with backend API endpoints
- ✅ JWT token management and authentication
- ✅ Deployed to Vercel with environment configuration
- ✅ Accessible at public URL with demo credentials

---

## Clarifications

### Session 2025-12-24

- Q: How should JWT tokens be stored on the client-side? → A: httpOnly cookies (prevents XSS attacks, aligns with Better Auth defaults)
- Q: When the backend API is unreachable, what retry strategy should be implemented? → A: Retry 3 times with exponential backoff (1s, 2s, 4s), then show error banner

---

## User Stories

### US-1: User Registration (Priority: P0)

**As a** new user
**I want to** create an account via signup form
**So that** I can access my personal todo list

**Why this priority**: Authentication is the entry point - nothing else works without user accounts.

**Independent Test**: Can be tested by filling out signup form with valid data and verifying account is created and user can log in.

**Acceptance Scenarios**:

1. **Given** signup page is loaded, **When** user enters email and password, **Then** account is created and user is redirected to dashboard
2. **Given** user enters existing email, **When** submitting signup form, **Then** error message "Email already exists" is displayed
3. **Given** user enters weak password (< 8 chars), **When** submitting form, **Then** validation error is shown
4. **Given** signup succeeds, **When** account is created, **Then** JWT token is stored and user is authenticated

---

### US-2: User Login (Priority: P0)

**As a** returning user
**I want to** sign in with my credentials
**So that** I can access my existing todo list

**Why this priority**: Users must be able to return to their data.

**Independent Test**: Can be tested by entering valid credentials and verifying successful login and redirect to dashboard.

**Acceptance Scenarios**:

1. **Given** login page is loaded, **When** user enters valid credentials, **Then** user is authenticated and redirected to dashboard
2. **Given** user enters invalid password, **When** submitting login form, **Then** error message "Invalid credentials" is displayed
3. **Given** user enters non-existent email, **When** submitting form, **Then** error message "Account not found" is displayed
4. **Given** login succeeds, **When** JWT token is received, **Then** token is stored in secure storage and used for API requests

---

### US-3: View Task List (Priority: P1)

**As a** logged-in user
**I want to** see all my tasks in a list view
**So that** I can review my todos at a glance

**Why this priority**: Core functionality - users need to see their tasks.

**Independent Test**: Can be tested by logging in and verifying task list displays all user's tasks from the backend.

**Acceptance Scenarios**:

1. **Given** user is logged in, **When** dashboard loads, **Then** all user's tasks are fetched and displayed
2. **Given** user has no tasks, **When** dashboard loads, **Then** empty state message is shown
3. **Given** task list is loaded, **When** viewing tasks, **Then** each task shows title, description, completion status, and timestamps
4. **Given** tasks exist, **When** list is rendered, **Then** completed tasks are visually distinct (strikethrough, different color)

---

### US-4: Create New Task (Priority: P1)

**As a** logged-in user
**I want to** add a new task via a form
**So that** I can capture new todos

**Why this priority**: Primary action - users must be able to add tasks.

**Independent Test**: Can be tested by submitting create task form and verifying task appears in list and backend database.

**Acceptance Scenarios**:

1. **Given** user clicks "Add Task" button, **When** form is shown, **Then** title and description fields are displayed
2. **Given** user enters title, **When** submitting form, **Then** task is created via API and appears in list
3. **Given** user submits empty title, **When** form validation runs, **Then** error message is displayed
4. **Given** title exceeds 200 chars, **When** user types, **Then** character counter is shown and submission is blocked
5. **Given** task creation succeeds, **When** response is received, **Then** form is cleared and task list is refreshed

---

### US-5: Mark Task Complete/Incomplete (Priority: P1)

**As a** logged-in user
**I want to** toggle task completion status with a checkbox
**So that** I can track task progress

**Why this priority**: Core functionality for todo management.

**Independent Test**: Can be tested by clicking checkbox and verifying UI updates and backend state changes.

**Acceptance Scenarios**:

1. **Given** task is incomplete, **When** user clicks checkbox, **Then** task is marked complete via API and UI updates
2. **Given** task is complete, **When** user clicks checkbox, **Then** task is marked incomplete via API and UI updates
3. **Given** checkbox is clicked, **When** API call fails, **Then** checkbox reverts to original state and error is shown
4. **Given** task status changes, **When** UI updates, **Then** visual styling reflects completion status

---

### US-6: Edit Task (Priority: P2)

**As a** logged-in user
**I want to** edit task title and description
**So that** I can update task details

**Why this priority**: Users need to modify tasks.

**Independent Test**: Can be tested by clicking edit button, modifying fields, and verifying changes persist to backend.

**Acceptance Scenarios**:

1. **Given** user clicks "Edit" on a task, **When** edit mode activates, **Then** title and description become editable
2. **Given** user modifies title, **When** saving changes, **Then** task is updated via API and UI reflects changes
3. **Given** user cancels edit, **When** cancel button is clicked, **Then** changes are discarded and view mode is restored
4. **Given** user clears title, **When** attempting to save, **Then** validation error prevents empty title

---

### US-7: Delete Task (Priority: P2)

**As a** logged-in user
**I want to** delete tasks I no longer need
**So that** I can keep my list clean

**Why this priority**: Task management requires deletion capability.

**Independent Test**: Can be tested by clicking delete button, confirming action, and verifying task is removed from UI and backend.

**Acceptance Scenarios**:

1. **Given** user clicks "Delete" on a task, **When** confirmation dialog appears, **Then** user can confirm or cancel
2. **Given** user confirms deletion, **When** API call succeeds, **Then** task is removed from list
3. **Given** user cancels deletion, **When** cancel is clicked, **Then** task remains in list unchanged
4. **Given** deletion fails, **When** API returns error, **Then** task remains and error message is shown

---

### US-8: Responsive Design (Priority: P1)

**As a** user on any device
**I want to** use the app on mobile, tablet, or desktop
**So that** I can manage tasks from any device

**Why this priority**: Modern web apps must work on all screen sizes.

**Independent Test**: Can be tested by viewing app at different viewport sizes and verifying layout adapts.

**Acceptance Scenarios**:

1. **Given** user accesses app on mobile (< 640px), **When** page loads, **Then** layout stacks vertically with touch-friendly buttons
2. **Given** user accesses app on tablet (640-1024px), **When** page loads, **Then** layout uses medium breakpoints
3. **Given** user accesses app on desktop (> 1024px), **When** page loads, **Then** layout uses full-width design with sidebar
4. **Given** viewport changes, **When** window is resized, **Then** layout adapts smoothly without horizontal scroll

---

### Edge Cases

- What happens when **JWT token expires** during use? (Should redirect to login with message "Session expired")
- What happens when **backend API is unreachable**? (Should retry 3 times with exponential backoff: 1s, 2s, 4s, then show persistent error banner "Unable to connect to server")
- What happens when **user creates 100+ tasks**? (Should implement virtual scrolling or pagination)
- What happens when **task title contains special characters** (emoji, unicode)? (Should display correctly)
- What happens when **user has two browser tabs** open? (Should sync state or warn about stale data)
- What happens when **network is slow** (3G connection)? (Should show loading indicators)

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide signup page with email and password fields
- **FR-002**: System MUST provide login page with email and password fields
- **FR-003**: System MUST integrate Better Auth for authentication
- **FR-004**: System MUST store JWT token securely after successful login
- **FR-005**: System MUST attach JWT token to all API requests in Authorization header
- **FR-006**: System MUST redirect unauthenticated users to login page
- **FR-007**: System MUST display dashboard with task list for authenticated users
- **FR-008**: System MUST provide form to create new tasks (title required, description optional)
- **FR-009**: System MUST provide checkbox to toggle task completion status
- **FR-010**: System MUST provide edit functionality to modify task title and description
- **FR-011**: System MUST provide delete functionality with confirmation dialog
- **FR-012**: System MUST show loading states during API calls
- **FR-013**: System MUST display error messages for failed operations
- **FR-014**: System MUST refresh task list after create/update/delete operations
- **FR-015**: System MUST implement responsive design for mobile, tablet, desktop
- **FR-016**: System MUST validate form inputs client-side before API submission
- **FR-017**: System MUST handle 401 errors by redirecting to login
- **FR-018**: System MUST handle 403 errors by showing "Access denied" message
- **FR-019**: System MUST provide logout functionality that clears JWT token
- **FR-020**: System MUST show user email/identifier in navigation

### Non-Functional Requirements

- **NFR-001**: UI MUST follow responsive design principles (mobile-first approach)
- **NFR-002**: Pages MUST load within 2 seconds on 4G connection
- **NFR-003**: UI MUST be accessible (WCAG 2.1 AA compliance for forms and navigation)
- **NFR-004**: All API calls MUST include loading indicators
- **NFR-005**: Form validation MUST provide immediate feedback (< 100ms)
- **NFR-006**: JWT tokens MUST be stored in httpOnly cookies (prevents XSS attacks, not localStorage or sessionStorage)
- **NFR-007**: Application MUST work offline with cached data (optional enhancement)
- **NFR-008**: Application MUST be deployed to Vercel with HTTPS
- **NFR-009**: Environment variables MUST be used for API URL and auth configuration
- **NFR-010**: Application MUST use TypeScript with strict mode enabled
- **NFR-011**: Failed API calls MUST retry 3 times with exponential backoff (1s, 2s, 4s) before showing error

### Key Entities (Frontend Models)

- **User**: Authenticated user with session
  - Attributes: id, email, JWT token
  - Behavior: Login, logout, signup, session management

- **Task (Frontend)**: Client-side task representation
  - Attributes: id, user_id, title, description, complete, created_at, updated_at
  - Behavior: Create, update, toggle complete, delete
  - State: loading, error, success

- **API Client**: Manages backend communication
  - Attributes: base_url, jwt_token
  - Behavior: Fetch tasks, create task, update task, delete task, handle errors

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Signup flow completes successfully within 5 seconds
- **SC-002**: Login flow completes successfully within 3 seconds
- **SC-003**: Task list loads within 2 seconds after authentication
- **SC-004**: All CRUD operations complete within 1 second (excluding network latency)
- **SC-005**: UI is responsive at 320px (mobile), 768px (tablet), 1440px (desktop) viewports
- **SC-006**: 100% of form validations work client-side
- **SC-007**: Application is deployed to Vercel and accessible via public URL
- **SC-008**: Zero console errors in browser devtools
- **SC-009**: Lighthouse score > 90 for Performance, Accessibility, Best Practices

---

## Technical Constraints

- **TC-001**: MUST use Next.js 16+ with App Router (as specified in Phase II)
- **TC-002**: MUST use Better Auth for authentication (Phase II requirement)
- **TC-003**: MUST use TypeScript 5+ with strict mode
- **TC-004**: MUST use Tailwind CSS 4+ for styling
- **TC-005**: MUST integrate with backend API at `http://localhost:8000` (dev) or production URL
- **TC-006**: MUST deploy to Vercel (Phase II requirement)
- **TC-007**: MUST follow Next.js App Router conventions (app directory structure)
- **TC-008**: MUST store configuration in environment variables (.env.local)
- **TC-009**: Frontend code MUST reside in `/frontend/` directory (monorepo structure)
- **TC-010**: MUST use React Server Components where appropriate

---

## Out of Scope (For This Stage)

- ❌ AI chatbot integration (Phase III)
- ❌ Real-time collaboration (future enhancement)
- ❌ Task sharing between users (future enhancement)
- ❌ Email notifications (future enhancement)
- ❌ Task categories/tags (beyond basic level)
- ❌ Due dates and reminders (Phase II Advanced Level)
- ❌ File attachments to tasks (future enhancement)
- ❌ Task search functionality (enhancement)
- ❌ Dark mode theme (enhancement)
- ❌ Offline-first architecture (future enhancement)

---

## Better Auth Integration

### Authentication Flow

1. **Signup Flow**:
   ```
   User → Signup Form → Better Auth API → JWT Token → Store Token → Redirect to Dashboard
   ```

2. **Login Flow**:
   ```
   User → Login Form → Better Auth API → JWT Token → Store Token → Redirect to Dashboard
   ```

3. **Protected Routes**:
   ```
   User → Access Dashboard → Check JWT → Valid? → Allow Access
                                      → Invalid? → Redirect to Login
   ```

4. **API Requests**:
   ```
   Frontend → API Call → Attach JWT in Header → Backend Validates → Response → Update UI
   ```

### Better Auth Configuration

**Required Environment Variables** (`.env.local`):
```bash
NEXT_PUBLIC_BETTER_AUTH_URL=https://auth.hackathon-todo.com
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
```

**Auth Endpoints**:
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout
- `GET /api/auth/session` - Get current session
- `POST /api/auth/refresh` - Refresh JWT token

**JWT Token Structure** (from Better Auth):
```json
{
  "sub": "user_abc123",
  "user_id": "user_abc123",
  "email": "user@example.com",
  "exp": 1703088000,
  "iat": 1703084400
}
```

### Token Management

- **Storage**: Use httpOnly cookies exclusively (Better Auth default, XSS protection)
- **Expiration**: Handle 401 responses by refreshing token or redirecting to login
- **Refresh**: Implement automatic token refresh before expiration
- **Logout**: Clear token and redirect to login page

---

## Component Architecture

### Page Structure (App Router)

```
frontend/app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx              # Login page
│   └── signup/
│       └── page.tsx              # Signup page
├── (dashboard)/
│   ├── layout.tsx                # Dashboard layout with nav
│   └── page.tsx                  # Task list dashboard
├── layout.tsx                    # Root layout
├── page.tsx                      # Landing/home page
└── api/
    └── auth/
        └── [...betterauth]/
            └── route.ts          # Better Auth API routes
```

### Component Hierarchy

```
App
├── RootLayout
│   ├── Navigation (user email, logout button)
│   └── Children
│       ├── LoginPage
│       │   └── LoginForm
│       ├── SignupPage
│       │   └── SignupForm
│       └── DashboardPage
│           ├── TaskList
│           │   ├── TaskItem (multiple)
│           │   │   ├── TaskCheckbox
│           │   │   ├── TaskContent
│           │   │   └── TaskActions (Edit, Delete)
│           │   └── EmptyState
│           └── CreateTaskForm
```

### Core Components

#### 1. LoginForm Component
```tsx
interface LoginFormProps {}

// Features:
// - Email and password inputs
// - Form validation
// - Submit handler that calls Better Auth
// - Error display
// - Link to signup page
// - Loading state during authentication
```

#### 2. SignupForm Component
```tsx
interface SignupFormProps {}

// Features:
// - Email and password inputs
// - Password confirmation field
// - Form validation (password strength, email format)
// - Submit handler that calls Better Auth
// - Error display
// - Link to login page
// - Loading state during registration
```

#### 3. TaskList Component
```tsx
interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: number) => Promise<void>;
  onDeleteTask: (taskId: number) => Promise<void>;
  onUpdateTask: (taskId: number, updates: Partial<Task>) => Promise<void>;
  loading: boolean;
}

// Features:
// - Renders list of TaskItem components
// - Shows loading skeleton
// - Shows empty state when no tasks
// - Handles optimistic UI updates
// - Scrollable container for many tasks
```

#### 4. TaskItem Component
```tsx
interface TaskItemProps {
  task: Task;
  onToggleComplete: () => Promise<void>;
  onDelete: () => Promise<void>;
  onUpdate: (updates: Partial<Task>) => Promise<void>;
}

// Features:
// - Displays task title, description, timestamps
// - Checkbox for completion toggle
// - Edit and delete buttons
// - Inline edit mode
// - Visual distinction for completed tasks
// - Confirmation dialog for delete
```

#### 5. CreateTaskForm Component
```tsx
interface CreateTaskFormProps {
  onCreateTask: (task: { title: string; description?: string }) => Promise<void>;
}

// Features:
// - Title input (required, max 200 chars)
// - Description textarea (optional, max 1000 chars)
// - Character counters
// - Submit and cancel buttons
// - Form validation
// - Loading state during creation
// - Auto-focus on title field
// - Clear form after successful creation
```

#### 6. Navigation Component
```tsx
interface NavigationProps {
  user: { email: string };
  onLogout: () => Promise<void>;
}

// Features:
// - Displays app logo/title
// - Shows user email
// - Logout button
// - Responsive (hamburger menu on mobile)
```

---

## API Integration

### API Client Module

**Location**: `frontend/lib/api/client.ts`

```typescript
class APIClient {
  private baseURL: string;
  private getAuthToken: () => string | null;

  constructor(baseURL: string, getAuthToken: () => string | null) {
    this.baseURL = baseURL;
    this.getAuthToken = getAuthToken;
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const token = this.getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    };

    // Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
    const maxRetries = 3;
    const retryDelays = [1000, 2000, 4000]; // milliseconds

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers,
        });

        if (response.status === 401) {
          // Redirect to login on unauthorized
          window.location.href = '/login';
          throw new Error('Unauthorized');
        }

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'API request failed');
        }

        if (response.status === 204) {
          return null as T;
        }

        return response.json();
      } catch (error) {
        // Retry on network errors, but not on 4xx/5xx responses
        if (attempt < maxRetries && error.message === 'Failed to fetch') {
          await new Promise(resolve => setTimeout(resolve, retryDelays[attempt]));
          continue;
        }
        throw error;
      }
    }
  }

  // Task API methods
  async getTasks(userId: string): Promise<TaskListResponse> {
    return this.request(`/api/${userId}/tasks`);
  }

  async createTask(userId: string, task: TaskCreate): Promise<TaskResponse> {
    return this.request(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async updateTask(userId: string, taskId: number, updates: TaskUpdate): Promise<TaskResponse> {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async patchTask(userId: string, taskId: number, updates: Partial<TaskPatch>): Promise<TaskResponse> {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  async deleteTask(userId: string, taskId: number): Promise<void> {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new APIClient(
  process.env.NEXT_PUBLIC_API_URL!,
  () => getAuthToken() // Function to retrieve JWT from storage
);
```

### TypeScript Types

**Location**: `frontend/types/task.ts`

```typescript
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  complete: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title: string;
  description: string | null;
  complete: boolean;
}

export interface TaskPatch {
  title?: string;
  description?: string | null;
  complete?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export interface TaskResponse extends Task {}
```

---

## Styling with Tailwind CSS

### Design System

**Colors**:
```css
/* Primary palette */
--primary: #3b82f6;      /* Blue for primary actions */
--primary-dark: #2563eb; /* Hover state */
--secondary: #8b5cf6;    /* Purple for secondary actions */
--success: #10b981;      /* Green for completed tasks */
--danger: #ef4444;       /* Red for delete actions */
--warning: #f59e0b;      /* Yellow for warnings */
--gray-50: #f9fafb;      /* Light backgrounds */
--gray-900: #111827;     /* Dark text */
```

**Typography**:
```css
/* Font family */
font-family: 'Inter', system-ui, sans-serif;

/* Sizes */
--text-xs: 0.75rem;    /* 12px - timestamps */
--text-sm: 0.875rem;   /* 14px - descriptions */
--text-base: 1rem;     /* 16px - body text */
--text-lg: 1.125rem;   /* 18px - task titles */
--text-xl: 1.25rem;    /* 20px - page headings */
--text-2xl: 1.5rem;    /* 24px - main headings */
```

**Spacing**:
```css
/* Consistent spacing scale */
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-4: 1rem;     /* 16px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
```

### Component Styling Examples

**TaskItem Component**:
```tsx
<div className="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
  <input
    type="checkbox"
    className="w-5 h-5 text-primary rounded focus:ring-2 focus:ring-primary"
    checked={task.complete}
  />
  <div className="flex-1">
    <h3 className={`text-lg font-medium ${task.complete ? 'line-through text-gray-400' : 'text-gray-900'}`}>
      {task.title}
    </h3>
    {task.description && (
      <p className="text-sm text-gray-600 mt-1">{task.description}</p>
    )}
  </div>
  <div className="flex gap-2">
    <button className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded">Edit</button>
    <button className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded">Delete</button>
  </div>
</div>
```

**CreateTaskForm Component**:
```tsx
<form className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      Title <span className="text-red-500">*</span>
    </label>
    <input
      type="text"
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
      maxLength={200}
    />
    <p className="text-xs text-gray-500 mt-1">{charCount}/200</p>
  </div>
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      Description
    </label>
    <textarea
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
      rows={4}
      maxLength={1000}
    />
  </div>
  <button
    type="submit"
    className="w-full bg-primary text-white py-2 px-4 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50"
  >
    Add Task
  </button>
</form>
```

### Responsive Design

**Breakpoints**:
```typescript
const breakpoints = {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
};
```

**Mobile-First Approach**:
```tsx
// Stack layout on mobile, grid on desktop
<div className="flex flex-col gap-4 md:grid md:grid-cols-2 lg:grid-cols-3">
  {tasks.map(task => <TaskItem key={task.id} task={task} />)}
</div>

// Full-width buttons on mobile, inline on desktop
<div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
  <button className="w-full sm:w-auto">Cancel</button>
  <button className="w-full sm:w-auto">Save</button>
</div>
```

---

## Testing Requirements

### Unit Tests (Vitest + React Testing Library)

**Test Files**:
```
frontend/__tests__/
├── components/
│   ├── LoginForm.test.tsx
│   ├── SignupForm.test.tsx
│   ├── TaskList.test.tsx
│   ├── TaskItem.test.tsx
│   └── CreateTaskForm.test.tsx
├── lib/
│   └── api-client.test.ts
└── utils/
    └── validation.test.ts
```

**Test Coverage Requirements**:
- All components: 70%+ coverage
- API client: 90%+ coverage
- Validation logic: 100% coverage

**Example Unit Test**:
```typescript
describe('CreateTaskForm', () => {
  it('should validate required title', async () => {
    const onSubmit = vi.fn();
    render(<CreateTaskForm onCreateTask={onSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: /add task/i }));

    expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should enforce title max length', () => {
    render(<CreateTaskForm onCreateTask={vi.fn()} />);

    const input = screen.getByLabelText(/title/i);
    fireEvent.change(input, { target: { value: 'a'.repeat(201) } });

    expect(input).toHaveValue('a'.repeat(200));
  });
});
```

### Integration Tests (Playwright)

**Test Files**:
```
frontend/e2e/
├── auth.spec.ts          # Signup, login, logout flows
├── tasks.spec.ts         # CRUD operations on tasks
└── responsive.spec.ts    # Mobile, tablet, desktop views
```

**Example Integration Test**:
```typescript
test('user can create and complete a task', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Create task
  await page.waitForURL('/dashboard');
  await page.fill('[name="title"]', 'Test Task');
  await page.click('button:has-text("Add Task")');

  // Verify task appears
  await expect(page.locator('text=Test Task')).toBeVisible();

  // Mark complete
  await page.click('[aria-label="Mark task complete"]');
  await expect(page.locator('text=Test Task')).toHaveClass(/line-through/);
});
```

### Manual Testing Checklist

- [ ] Signup flow with valid credentials
- [ ] Signup flow with duplicate email (error handling)
- [ ] Login flow with valid credentials
- [ ] Login flow with invalid credentials (error handling)
- [ ] Create task with title only
- [ ] Create task with title and description
- [ ] Create task with empty title (validation error)
- [ ] Mark task as complete
- [ ] Mark task as incomplete
- [ ] Edit task title
- [ ] Edit task description
- [ ] Delete task with confirmation
- [ ] Cancel task deletion
- [ ] Logout and verify JWT cleared
- [ ] Responsive layout on mobile (320px width)
- [ ] Responsive layout on tablet (768px width)
- [ ] Responsive layout on desktop (1440px width)
- [ ] Expired JWT handling (redirect to login)
- [ ] Backend API unreachable (error message shown)

---

## Acceptance Criteria

### AC-1: Authentication Working ✅
**Given**: Better Auth is configured
**When**: User signs up or logs in
**Then**:
- Signup creates new account and returns JWT
- Login authenticates existing user and returns JWT
- JWT is stored securely
- User is redirected to dashboard
- Logout clears JWT and redirects to login

**Test**: Auth integration tests + manual verification

---

### AC-2: Task List Display ✅
**Given**: User is authenticated
**When**: Dashboard loads
**Then**:
- All user's tasks are fetched from backend API
- Tasks display title, description, completion status
- Completed tasks have visual distinction (strikethrough)
- Empty state shown when no tasks exist
- Loading indicator shown during fetch

**Test**: Component tests + API mocking

---

### AC-3: Create Task Functionality ✅
**Given**: User clicks "Add Task" button
**When**: Form is displayed
**Then**:
- Title and description fields are shown
- Form validates required title
- Character counters display for both fields
- Submission creates task via API
- New task appears in list immediately
- Form clears after successful creation

**Test**: Integration test with backend API

---

### AC-4: Toggle Task Completion ✅
**Given**: Task exists in list
**When**: User clicks checkbox
**Then**:
- API PATCH request sent to toggle complete status
- UI updates optimistically
- If API fails, checkbox reverts and error shown
- Visual styling changes based on completion status

**Test**: Component test with API mocking

---

### AC-5: Edit Task Functionality ✅
**Given**: User clicks "Edit" on a task
**When**: Edit mode activates
**Then**:
- Title and description become editable
- Changes can be saved or cancelled
- Save triggers API PUT request
- UI updates with new values
- Validation prevents empty title

**Test**: Component test with API integration

---

### AC-6: Delete Task Functionality ✅
**Given**: User clicks "Delete" on a task
**When**: Confirmation dialog appears
**Then**:
- User can confirm or cancel deletion
- Confirm triggers API DELETE request
- Task removed from UI on success
- Error message shown on failure

**Test**: Integration test with backend API

---

### AC-7: Responsive Design ✅
**Given**: Application is accessed on different devices
**When**: Viewport width changes
**Then**:
- Mobile (< 640px): Stacked layout, full-width buttons
- Tablet (640-1024px): Medium breakpoint layout
- Desktop (> 1024px): Full-width with sidebar/grid
- No horizontal scrolling on any breakpoint
- Touch-friendly tap targets on mobile (min 44x44px)

**Test**: Playwright responsive tests + manual verification

---

### AC-8: Error Handling ✅
**Given**: Errors occur during use
**When**: API calls fail or validation errors occur
**Then**:
- 401 errors redirect to login
- 403 errors show "Access denied" message
- 404 errors show "Not found" message
- Network errors show "Unable to connect" message
- Form validation shows field-specific errors
- All errors are user-friendly (no stack traces)

**Test**: Error scenario tests with mocked API failures

---

### AC-9: Deployment to Vercel ✅
**Given**: Application is ready for production
**When**: Deploying to Vercel
**Then**:
- Application builds successfully
- Environment variables configured
- HTTPS enabled
- Accessible at public URL
- Demo credentials provided in README
- No console errors in production

**Test**: Manual verification of deployed app

---

## Implementation Dependencies

### New Dependencies to Add

```bash
# Core framework
npm install next@16 react@19 react-dom@19

# TypeScript
npm install -D typescript @types/react @types/node

# Better Auth
npm install better-auth

# Styling
npm install tailwindcss@4 postcss autoprefixer

# Forms and validation
npm install react-hook-form zod

# API client
npm install axios

# Testing
npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom
npm install -D playwright @playwright/test
```

### package.json Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:e2e": "playwright test",
    "test:coverage": "vitest --coverage"
  }
}
```

### Environment Variables (.env.local)

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
NEXT_PUBLIC_BETTER_AUTH_URL=https://auth.hackathon-todo.com
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## File Structure

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── api/
│   │   └── auth/
│   │       └── [...betterauth]/
│   │           └── route.ts
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   ├── tasks/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   └── CreateTaskForm.tsx
│   ├── layout/
│   │   ├── Navigation.tsx
│   │   └── Footer.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Spinner.tsx
├── lib/
│   ├── api/
│   │   └── client.ts
│   ├── auth/
│   │   ├── better-auth.ts
│   │   └── session.ts
│   └── utils/
│       └── validation.ts
├── types/
│   ├── task.ts
│   └── user.ts
├── __tests__/
│   ├── components/
│   └── lib/
├── e2e/
│   ├── auth.spec.ts
│   └── tasks.spec.ts
├── public/
│   └── favicon.ico
├── .env.local
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## Out of Scope (Deferred to Later Phases)

- ❌ AI chatbot integration (Phase III)
- ❌ Task due dates and reminders (Phase II Advanced Level)
- ❌ Task categories/labels (Phase II Advanced Level)
- ❌ Real-time sync between tabs (future enhancement)
- ❌ Offline mode with service workers (future enhancement)
- ❌ Task search and filtering (enhancement)
- ❌ Email verification for signup (future enhancement)
- ❌ Password reset flow (future enhancement)
- ❌ Social login (Google, GitHub) (future enhancement)
- ❌ Dark mode toggle (enhancement)

---

## Risks and Mitigations

### Risk 1: Better Auth Setup Complexity
**Impact**: High - Authentication is critical for all features
**Probability**: Medium
**Mitigation**:
- Follow Better Auth Next.js integration guide closely
- Test auth flows early in development
- Use Better Auth demo/examples as reference
- Document any configuration issues for team

### Risk 2: CORS Issues with Backend API
**Impact**: High - Frontend can't communicate with backend
**Probability**: Medium
**Mitigation**:
- Configure CORS in FastAPI backend to allow frontend origin
- Test API integration early
- Use proxy in next.config.ts for development if needed
- Document CORS setup in README

### Risk 3: Responsive Design Not Working on All Devices
**Impact**: Medium - Poor UX on some devices
**Probability**: Low (Tailwind handles this well)
**Mitigation**:
- Use Tailwind's responsive utilities
- Test on real devices (mobile, tablet)
- Use browser DevTools device emulation
- Follow mobile-first design approach

### Risk 4: JWT Token Expiration Handling
**Impact**: Medium - Users get logged out unexpectedly
**Probability**: Medium
**Mitigation**:
- Implement token refresh before expiration
- Show clear "Session expired" message
- Store intended route for redirect after re-login
- Test expiration scenarios

---

## Success Metrics

- ✅ Signup flow working with Better Auth
- ✅ Login flow working with Better Auth
- ✅ All 5 Basic Level features functional via UI
- ✅ Responsive design verified at 3 breakpoints
- ✅ JWT authentication integrated with backend API
- ✅ All CRUD operations working end-to-end
- ✅ 70%+ test coverage
- ✅ Deployed to Vercel with public URL
- ✅ Lighthouse score > 90
- ✅ Zero TypeScript errors
- ✅ Zero console errors in production

---

## Definition of Done

- [ ] Next.js 16+ project initialized with App Router
- [ ] Better Auth configured and integrated
- [ ] TypeScript configured with strict mode
- [ ] Tailwind CSS 4+ set up and working
- [ ] Signup page implemented with form validation
- [ ] Login page implemented with form validation
- [ ] Dashboard page displays task list
- [ ] Create task form functional
- [ ] Task item component with checkbox, edit, delete
- [ ] Responsive design verified on mobile, tablet, desktop
- [ ] API client integrated with backend endpoints
- [ ] JWT token management implemented
- [ ] Error handling for 401, 403, 404, 500 responses
- [ ] Loading states for all async operations
- [ ] Unit tests for all components (70%+ coverage)
- [ ] Integration tests for critical user flows
- [ ] Deployed to Vercel with HTTPS
- [ ] Environment variables documented in .env.example
- [ ] README updated with setup instructions and demo URL
- [ ] No TypeScript errors (`npm run type-check` passes)
- [ ] No linting errors (`npm run lint` passes)
- [ ] Lighthouse audit score > 90

---

## References

- [Next.js 16 Documentation (App Router)](https://nextjs.org/docs)
- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Tailwind CSS 4 Documentation](https://tailwindcss.com/docs)
- [React 19 Documentation](https://react.dev/)
- [Vercel Deployment Guide](https://vercel.com/docs)
- [Vitest Testing Framework](https://vitest.dev/)
- [Playwright E2E Testing](https://playwright.dev/)
- Phase II Hackathon Specification (PDF pages 7-8)
- Stage 2 Backend API Specification: `specs/003-backend-api/spec.md`
- Backend CRUD API Skill: `.claude/skills/backend-crud-api/SKILL.md`

---

**Next Stage**: Phase III - AI Chatbot Integration (OpenAI ChatKit)
