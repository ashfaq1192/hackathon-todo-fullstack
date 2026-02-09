// Task types matching backend SQLModel schema

export type TaskPriority = 'low' | 'medium' | 'high';

export type RecurringType = 'none' | 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface Task {
  id: number;                    // Unique task identifier (auto-increment from backend)
  user_id: string;               // Owner's user ID (foreign key to User.id)
  title: string;                 // Task title (required)
  description: string | null;    // Task description (optional)
  complete: boolean;             // Completion status
  priority: TaskPriority;        // Task priority (low/medium/high)
  due_date: string | null;       // ISO 8601 timestamp of deadline (optional)
  recurring: RecurringType;      // Recurring schedule type
  recurring_end_date: string | null; // ISO 8601 timestamp of recurring end (optional)
  tags: string[];                // Task tags/categories
  created_at: string;            // ISO 8601 timestamp of creation
  updated_at: string;            // ISO 8601 timestamp of last update
}

// Payload for creating a new task
export interface TaskCreate {
  title: string;                 // Required task title
  description?: string;          // Optional task description
  priority?: TaskPriority;       // Optional task priority (defaults to 'medium' on backend)
  due_date?: string;             // Optional due date (ISO 8601)
  recurring?: RecurringType;     // Optional recurring type (defaults to 'none')
  recurring_end_date?: string;   // Optional recurring end date
  tags?: string[];               // Optional tags
}

// Payload for full task update (PUT)
export interface TaskUpdate {
  title: string;                 // Updated title
  description: string | null;    // Updated description
  complete: boolean;             // Updated completion status
  priority: TaskPriority;        // Updated priority
  due_date?: string | null;      // Updated due date
  recurring?: RecurringType;     // Updated recurring type
  recurring_end_date?: string | null; // Updated recurring end date
  tags?: string[];               // Updated tags
}

// Payload for partial task update (PATCH)
export interface TaskPatch {
  title?: string;                // Partial update: title only
  description?: string | null;   // Partial update: description only
  complete?: boolean;            // Partial update: completion status only
  priority?: TaskPriority;       // Partial update: priority only
  due_date?: string | null;      // Partial update: due date
  recurring?: RecurringType;     // Partial update: recurring type
  recurring_end_date?: string | null; // Partial update: recurring end date
  tags?: string[];               // Partial update: tags
}

// Response from backend when fetching tasks
export interface TaskListResponse {
  tasks: Task[];                 // Array of task objects
  count: number;                 // Total number of tasks
}

// Single task response (same as Task)
export interface TaskResponse extends Task {}

// Query parameters for search/filter/sort
export interface TaskQueryParams {
  search?: string;
  status?: 'all' | 'pending' | 'completed';
  priority?: TaskPriority;
  tags?: string[];
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
}
