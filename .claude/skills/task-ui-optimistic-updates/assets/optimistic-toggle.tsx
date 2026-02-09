// Optimistic UI Pattern: Toggle Complete with Rollback on Error

import { useState } from 'react';
import toast from 'react-hot-toast';

interface Task {
  id: number;
  title: string;
  complete: boolean;
}

interface OptimisticToggleProps {
  task: Task;
  onUpdate?: (updated: Task) => void;
}

export function OptimisticToggle({ task, onUpdate }: OptimisticToggleProps) {
  const [isComplete, setIsComplete] = useState(task.complete);

  const handleToggle = async () => {
    const originalValue = isComplete;

    // 1. Optimistically update UI immediately
    setIsComplete(!isComplete);

    try {
      // 2. Make API call
      await apiClient.patch(`/tasks/${task.id}`, { complete: !isComplete });
      toast.success(`Task marked as ${!isComplete ? 'complete' : 'incomplete'}`);

      // 3. Notify parent component
      if (onUpdate) {
        onUpdate({ ...task, complete: !isComplete });
      }
    } catch (error) {
      // 4. Revert UI on error
      toast.error('Failed to update task. Please try again.');
      setIsComplete(originalValue);
    }
  };

  return (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={isComplete}
        onChange={handleToggle}
        className="h-5 w-5 rounded border-gray-300"
        aria-label={isComplete ? 'Mark as incomplete' : 'Mark as complete'}
      />
      <span className={isComplete ? 'line-through text-gray-500 ml-2' : 'ml-2'}>
        {task.title}
      </span>
    </label>
  );
}
