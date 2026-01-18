/**
 * TodoItem Component
 *
 * Individual todo item with inline edit, toggle complete, and delete functionality.
 */

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import type { Task, TaskPatch, TaskPriority } from '@/types/task';

// Helper function to get priority badge styles
const getPriorityBadge = (priority: TaskPriority) => {
  const styles = {
    low: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      icon: '🟢',
      label: 'Low'
    },
    medium: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      icon: '🟡',
      label: 'Medium'
    },
    high: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      icon: '🔴',
      label: 'High'
    }
  };
  return styles[priority] || styles.medium;
};

interface TodoItemProps {
  todo: Task;
  taskNumber: number; // Actual database ID (consistent with chatbot)
  onUpdate: (todoId: number, updates: TaskPatch) => Promise<void>;
  onDelete: (todoId: number) => Promise<void>;
  isUpdating?: boolean;
  isDeleting?: boolean;
}

export function TodoItem({ todo, taskNumber, onUpdate, onDelete, isUpdating = false, isDeleting = false }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');
  const [editPriority, setEditPriority] = useState<TaskPriority>(todo.priority);
  const [error, setError] = useState<string | null>(null);
  const [showCompleteConfirm, setShowCompleteConfirm] = useState(false);

  const handleCheckboxClick = () => {
    // Show confirmation instead of immediately toggling
    setShowCompleteConfirm(true);
  };

  const handleConfirmComplete = async (complete: boolean) => {
    setError(null);
    setShowCompleteConfirm(false);
    try {
      await onUpdate(todo.id, { complete });
    } catch (err) {
      setError('Failed to update todo');
    }
  };

  const handleCancelComplete = () => {
    setShowCompleteConfirm(false);
  };

  const handleSaveEdit = async () => {
    setError(null);

    if (!editTitle.trim()) {
      setError('Title cannot be empty');
      return;
    }

    try {
      await onUpdate(todo.id, {
        title: editTitle,
        description: editDescription || null,
        priority: editPriority,
      });
      setIsEditing(false);
    } catch (err) {
      setError('Failed to update todo');
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
    setEditPriority(todo.priority);
    setIsEditing(false);
    setError(null);
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this todo?')) {
      setError(null);
      try {
        await onDelete(todo.id);
      } catch (err) {
        setError('Failed to delete todo');
      }
    }
  };

  const isLoading = isUpdating || isDeleting;

  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-all duration-200 ${todo.complete ? 'bg-green-50/50 border-green-200' : ''} ${isLoading ? 'opacity-50' : ''}`}>
      {/* Error Message */}
      {error && (
        <div className="mb-3 p-3 bg-red-50 border-l-4 border-red-500 rounded text-red-700 text-sm flex items-start space-x-2">
          <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {isEditing ? (
        /* Edit Mode */
        <div className="space-y-3 bg-blue-50/50 p-4 rounded-lg border-2 border-blue-200">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
            placeholder="Todo title"
            disabled={isLoading}
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
            placeholder="Description (optional)"
            rows={2}
            disabled={isLoading}
          />
          <select
            value={editPriority}
            onChange={(e) => setEditPriority(e.target.value as TaskPriority)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
            disabled={isLoading}
          >
            <option value="low">🟢 Low Priority</option>
            <option value="medium">🟡 Medium Priority</option>
            <option value="high">🔴 High Priority</option>
          </select>
          <div className="flex space-x-2">
            <Button
              variant="primary"
              size="sm"
              onClick={handleSaveEdit}
              disabled={isLoading}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Save
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCancelEdit}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        /* View Mode */
        <div>
          <div className="flex items-start space-x-4">
            {/* Checkbox */}
            <div className="flex-shrink-0 mt-1">
              <input
                type="checkbox"
                checked={todo.complete}
                onChange={handleCheckboxClick}
                disabled={isLoading}
                className="h-5 w-5 rounded border-gray-300 text-green-600 focus:ring-green-500 cursor-pointer transition-colors"
              />
            </div>

            {/* Todo Content */}
            <div className="flex-1 min-w-0">
              {/* Task ID and Priority Badges */}
              <div className="mb-2 flex items-center gap-2">
                <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-sm">
                  <svg className="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                  </svg>
                  ID: {taskNumber}
                </span>
                {(() => {
                  const priorityBadge = getPriorityBadge(todo.priority);
                  return (
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityBadge.bg} ${priorityBadge.text}`}>
                      <span className="mr-1">{priorityBadge.icon}</span>
                      {priorityBadge.label}
                    </span>
                  );
                })()}
              </div>

              <h3 className={`text-lg font-semibold ${todo.complete ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {todo.title}
              </h3>
              {todo.description && (
                <p className={`mt-2 text-sm leading-relaxed ${todo.complete ? 'text-gray-400 line-through' : 'text-gray-600'}`}>
                  {todo.description}
                </p>
              )}

              {/* Completion Confirmation */}
              {showCompleteConfirm && (
                <div className="mt-3 p-3 bg-amber-50 border-l-4 border-amber-400 rounded-lg">
                  <div className="flex items-start">
                    <svg className="w-5 h-5 text-amber-400 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-amber-800">
                        {todo.complete ? 'Mark as incomplete?' : 'Mark as complete?'}
                      </p>
                      <div className="mt-2 flex space-x-2">
                        <button
                          onClick={() => handleConfirmComplete(!todo.complete)}
                          disabled={isLoading}
                          className="px-3 py-1.5 bg-amber-600 text-white rounded-md text-sm font-medium hover:bg-amber-700 transition-colors disabled:opacity-50"
                        >
                          Yes, {todo.complete ? 'mark incomplete' : 'mark complete'}
                        </button>
                        <button
                          onClick={handleCancelComplete}
                          disabled={isLoading}
                          className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-3 flex items-center space-x-4 text-xs text-gray-400">
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Created {new Date(todo.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-2 flex-shrink-0">
              <button
                onClick={() => setIsEditing(true)}
                disabled={isLoading}
                className="flex items-center px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="flex items-center px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
