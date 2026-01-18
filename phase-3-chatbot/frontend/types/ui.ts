// UI state management types

import { Task } from './task';

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface FormState<T> {
  data: T;                       // Form data
  loading: LoadingState;         // Current loading state
  error: string | null;          // Error message if any
}

export interface TaskItemState {
  task: Task;
  isEditing: boolean;            // Whether task is in edit mode
  isDeleting: boolean;           // Whether delete confirmation is shown
  optimisticUpdate: boolean;     // Whether UI updated optimistically
}
