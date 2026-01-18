// Task types matching backend SQLModel schema

export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;                    // Unique task identifier (auto-increment from backend)
  user_id: string;               // Owner's user ID (foreign key to User.id)
  title: string;                 // Task title (required)
  description: string | null;    // Task description (optional)
  complete: boolean;             // Completion status
  priority: TaskPriority;        // Task priority (low/medium/high)
  created_at: string;            // ISO 8601 timestamp of creation
  updated_at: string;            // ISO 8601 timestamp of last update
}

// Payload for creating a new task
export interface TaskCreate {
  title: string;                 // Required task title
  description?: string;          // Optional task description
  priority?: TaskPriority;       // Optional task priority (defaults to 'medium' on backend)
}

// Payload for full task update (PUT)
export interface TaskUpdate {
  title: string;                 // Updated title
  description: string | null;    // Updated description
  complete: boolean;             // Updated completion status
  priority: TaskPriority;        // Updated priority
}

// Payload for partial task update (PATCH)
export interface TaskPatch {
  title?: string;                // Partial update: title only
  description?: string | null;   // Partial update: description only
  complete?: boolean;            // Partial update: completion status only
  priority?: TaskPriority;       // Partial update: priority only
}

// Response from backend when fetching tasks
export interface TaskListResponse {
  tasks: Task[];                 // Array of task objects
  count: number;                 // Total number of tasks
}

// Single task response (same as Task)
export interface TaskResponse extends Task {}
