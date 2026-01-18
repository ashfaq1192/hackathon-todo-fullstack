// components/tasks/TaskItem.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Task, TaskPriority } from '@/types/task';
import { apiClient, getUserId } from '@/lib/api/client';
import { updateTaskSchema, UpdateTaskInput } from '@/lib/validation/schemas';
import { Button } from '@/components/ui/Button';
import toast from 'react-hot-toast';

interface TaskItemProps {
  task: Task;
  onTaskUpdated?: (updatedTask: Task) => void;
  onTaskDeleted?: (taskId: number) => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({ task, onTaskUpdated, onTaskDeleted }) => {
  const [isComplete, setIsComplete] = useState(task.complete);
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<UpdateTaskInput>({
    resolver: zodResolver(updateTaskSchema),
    defaultValues: {
      title: task.title,
      description: task.description || '',
      complete: task.complete,
      priority: task.priority,
    },
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleToggleComplete = async () => {
    const originalIsComplete = isComplete;
    // Optimistically update the UI
    setIsComplete(!isComplete);

    const userId = getUserId();
    if (!userId) {
      toast.error('User not found');
      setIsComplete(originalIsComplete); // Revert
      return;
    }

    try {
      await apiClient.patchTask(userId, task.id, { complete: !isComplete });
      toast.success(`Task marked as ${!isComplete ? 'complete' : 'incomplete'}`);

      // Update parent if callback provided
      if (onTaskUpdated) {
        onTaskUpdated({ ...task, complete: !isComplete });
      }
    } catch (err: any) {
      toast.error('Failed to update task. Please try again.');
      // Revert the UI change on error
      setIsComplete(originalIsComplete);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    reset({
      title: task.title,
      description: task.description || '',
      complete: isComplete,
      priority: task.priority,
    });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    reset();
  };

  const handleSaveEdit = async (data: UpdateTaskInput) => {
    const userId = getUserId();
    if (!userId) {
      toast.error('User not found');
      return;
    }

    setIsSaving(true);
    try {
      const updatedTask = await apiClient.updateTask(userId, task.id, {
        title: data.title,
        description: data.description || null,
        complete: data.complete,
        priority: data.priority,
      });

      toast.success('Task updated successfully!');
      setIsEditing(false);

      // Update parent if callback provided
      if (onTaskUpdated) {
        onTaskUpdated(updatedTask);
      }

      // Update local state
      setIsComplete(updatedTask.complete);
    } catch (err: any) {
      toast.error(err.message || 'Failed to update task. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteClick = () => {
    setIsDeleting(true);
  };

  const handleCancelDelete = () => {
    setIsDeleting(false);
  };

  const handleConfirmDelete = async () => {
    const userId = getUserId();
    if (!userId) {
      toast.error('User not found');
      return;
    }

    try {
      await apiClient.deleteTask(userId, task.id);
      toast.success('Task deleted successfully!');

      // Notify parent to remove from list
      if (onTaskDeleted) {
        onTaskDeleted(task.id);
      }
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete task. Please try again.');
      setIsDeleting(false);
    }
  };

  // Render edit mode
  if (isEditing) {
    return (
      <div className="p-4 border rounded-md shadow-sm bg-blue-50 border-blue-200">
        <form onSubmit={handleSubmit(handleSaveEdit)}>
          <div className="mb-3">
            <label htmlFor={`edit-title-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              {...register('title')}
              id={`edit-title-${task.id}`}
              type="text"
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
              aria-invalid={errors.title ? 'true' : 'false'}
              aria-describedby={errors.title ? `edit-title-error-${task.id}` : undefined}
            />
            {errors.title && (
              <p id={`edit-title-error-${task.id}`} className="text-xs text-red-500 mt-1" role="alert">
                {errors.title.message}
              </p>
            )}
          </div>

          <div className="mb-3">
            <label htmlFor={`edit-description-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              id={`edit-description-${task.id}`}
              rows={3}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              aria-invalid={errors.description ? 'true' : 'false'}
              aria-describedby={errors.description ? `edit-description-error-${task.id}` : undefined}
            />
            {errors.description && (
              <p id={`edit-description-error-${task.id}`} className="text-xs text-red-500 mt-1" role="alert">
                {errors.description.message}
              </p>
            )}
          </div>

          <div className="mb-3">
            <label htmlFor={`edit-priority-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">
              Priority <span className="text-red-500">*</span>
            </label>
            <select
              {...register('priority')}
              id={`edit-priority-${task.id}`}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent ${
                errors.priority ? 'border-red-500' : 'border-gray-300'
              }`}
              aria-invalid={errors.priority ? 'true' : 'false'}
              aria-describedby={errors.priority ? `edit-priority-error-${task.id}` : undefined}
            >
              <option value="low">🟢 Low Priority</option>
              <option value="medium">🟡 Medium Priority</option>
              <option value="high">🔴 High Priority</option>
            </select>
            {errors.priority && (
              <p id={`edit-priority-error-${task.id}`} className="text-xs text-red-500 mt-1" role="alert">
                {errors.priority.message}
              </p>
            )}
          </div>

          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={isSaving} loading={isSaving}>
              {isSaving ? 'Saving...' : 'Save'}
            </Button>
            <Button type="button" variant="outline" size="sm" onClick={handleCancelEdit} disabled={isSaving}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    );
  }

  // Render delete confirmation dialog
  if (isDeleting) {
    return (
      <div className="p-4 border rounded-md shadow-sm bg-red-50 border-red-300">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Delete Task?</h3>
        <p className="text-sm text-gray-700 mb-4">
          Are you sure you want to delete "{task.title}"? This action cannot be undone.
        </p>
        <div className="flex gap-2">
          <Button variant="danger" size="sm" onClick={handleConfirmDelete}>
            Delete
          </Button>
          <Button variant="outline" size="sm" onClick={handleCancelDelete}>
            Cancel
          </Button>
        </div>
      </div>
    );
  }

  // Helper function to get priority badge styles
  const getPriorityBadge = (priority: TaskPriority) => {
    const styles = {
      low: { bg: 'bg-green-100', text: 'text-green-800', icon: '🟢', label: 'Low' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: '🟡', label: 'Medium' },
      high: { bg: 'bg-red-100', text: 'text-red-800', icon: '🔴', label: 'High' }
    };
    return styles[priority] || styles.medium;
  };

  const priorityBadge = getPriorityBadge(task.priority);

  // Render normal view mode
  return (
    <div className={`p-4 border rounded-md shadow-sm transition-colors ${isComplete ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'} task-item ${isComplete ? 'task-complete' : ''}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex-grow">
          <div className="flex items-center gap-2 mb-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityBadge.bg} ${priorityBadge.text}`}>
              <span className="mr-1">{priorityBadge.icon}</span>
              {priorityBadge.label}
            </span>
          </div>
          <h3 className={`text-lg font-medium ${isComplete ? 'line-through text-gray-500' : 'text-gray-900'}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`text-sm text-gray-600 mt-1 ${isComplete ? 'line-through' : ''}`}>
              {task.description}
            </p>
          )}
        </div>
        {/* Wrap checkbox in a label for increased touch target */}
        <label className="flex items-center justify-center p-2 -mr-2 cursor-pointer">
          <input
            type="checkbox"
            checked={isComplete}
            onChange={handleToggleComplete}
            className="h-5 w-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            aria-label={isComplete ? 'Mark task as incomplete' : 'Mark task as complete'}
          />
        </label>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 mb-2">
        <Button variant="outline" size="sm" onClick={handleEdit} aria-label="Edit task">
          Edit
        </Button>
        <Button variant="danger" size="sm" onClick={handleDeleteClick} aria-label="Delete task">
          Delete
        </Button>
      </div>

      <div className="flex justify-between text-xs text-gray-400">
        <span>Created: {formatDate(task.created_at)}</span>
        <span>Updated: {formatDate(task.updated_at)}</span>
      </div>
    </div>
  );
};
