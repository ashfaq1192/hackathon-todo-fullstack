// components/tasks/TaskItem.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Task, TaskPriority, RecurringType } from '@/types/task';
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

  const formatDueDate = (dateString: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const isOverdue = (dateString: string | null) => {
    if (!dateString) return false;
    return new Date(dateString) < new Date() && !isComplete;
  };

  const handleToggleComplete = async () => {
    const originalIsComplete = isComplete;
    setIsComplete(!isComplete);

    const userId = getUserId();
    if (!userId) {
      toast.error('User not found');
      setIsComplete(originalIsComplete);
      return;
    }

    try {
      await apiClient.patchTask(userId, task.id, { complete: !isComplete });
      toast.success(`Task marked as ${!isComplete ? 'complete' : 'incomplete'}`);
      if (onTaskUpdated) {
        onTaskUpdated({ ...task, complete: !isComplete });
      }
    } catch (err: any) {
      toast.error('Failed to update task. Please try again.');
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
      if (onTaskUpdated) {
        onTaskUpdated(updatedTask);
      }
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
            />
            {errors.title && (
              <p className="text-xs text-red-500 mt-1" role="alert">{errors.title.message}</p>
            )}
          </div>

          <div className="mb-3">
            <label htmlFor={`edit-description-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              {...register('description')}
              id={`edit-description-${task.id}`}
              rows={3}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
            />
          </div>

          <div className="mb-3">
            <label htmlFor={`edit-priority-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              {...register('priority')}
              id={`edit-priority-${task.id}`}
              className="w-full px-3 py-2 border rounded-md border-gray-300"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
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
          Are you sure you want to delete &quot;{task.title}&quot;? This action cannot be undone.
        </p>
        <div className="flex gap-2">
          <Button variant="danger" size="sm" onClick={handleConfirmDelete}>Delete</Button>
          <Button variant="outline" size="sm" onClick={handleCancelDelete}>Cancel</Button>
        </div>
      </div>
    );
  }

  // Priority badge styles
  const getPriorityBadge = (priority: TaskPriority) => {
    const styles = {
      low: { bg: 'bg-green-100', text: 'text-green-800', label: 'Low' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Medium' },
      high: { bg: 'bg-red-100', text: 'text-red-800', label: 'High' }
    };
    return styles[priority] || styles.medium;
  };

  const recurringLabels: Record<RecurringType, string> = {
    none: '',
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    yearly: 'Yearly',
  };

  const priorityBadge = getPriorityBadge(task.priority);
  const dueDate = formatDueDate(task.due_date);
  const overdue = isOverdue(task.due_date);

  // Render normal view mode
  return (
    <div className={`p-4 border rounded-md shadow-sm transition-colors ${isComplete ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'} task-item ${isComplete ? 'task-complete' : ''}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex-grow">
          {/* Badges row */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityBadge.bg} ${priorityBadge.text}`}>
              {priorityBadge.label}
            </span>
            {task.recurring && task.recurring !== 'none' && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                {recurringLabels[task.recurring]}
              </span>
            )}
            {dueDate && (
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                overdue ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
              }`}>
                {overdue ? 'Overdue: ' : 'Due: '}{dueDate}
              </span>
            )}
          </div>

          <h3 className={`text-lg font-medium ${isComplete ? 'line-through text-gray-500' : 'text-gray-900'}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`text-sm text-gray-600 mt-1 ${isComplete ? 'line-through' : ''}`}>
              {task.description}
            </p>
          )}

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {task.tags.map(tag => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

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
        <Button variant="outline" size="sm" onClick={handleEdit} aria-label="Edit task">Edit</Button>
        <Button variant="danger" size="sm" onClick={handleDeleteClick} aria-label="Delete task">Delete</Button>
      </div>

      <div className="flex justify-between text-xs text-gray-400">
        <span>Created: {formatDate(task.created_at)}</span>
        <span>Updated: {formatDate(task.updated_at)}</span>
      </div>
    </div>
  );
};
