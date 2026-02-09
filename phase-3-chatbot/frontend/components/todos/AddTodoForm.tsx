/**
 * AddTodoForm Component
 *
 * Form for creating new todos.
 * Includes title and description fields with validation.
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import type { TaskCreate, TaskPriority } from '../../types/task';
import { useTaskContext } from '../../contexts/TaskContext';

// Validation schema
const todoSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be 200 characters or less'),
  description: z.string().max(1000, 'Description must be 1000 characters or less').optional(),
  priority: z.enum(['low', 'medium', 'high']).optional(),
  due_date: z.string().optional(),
  recurring: z.enum(['none', 'daily', 'weekly', 'monthly', 'yearly']).optional(),
});

interface AddTodoFormProps {}

export function AddTodoForm({}: AddTodoFormProps) {
  const { addTask, isLoading } = useTaskContext();
  const [apiError, setApiError] = useState<string | null>(null);
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TaskCreate>({
    resolver: zodResolver(todoSchema),
  });

  const handleAddTag = () => {
    const trimmed = tagInput.trim().toLowerCase();
    if (trimmed && !tags.includes(trimmed) && tags.length < 10) {
      setTags([...tags, trimmed]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter(t => t !== tag));
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleFormSubmit = async (data: TaskCreate) => {
    setApiError(null);

    try {
      const payload: TaskCreate = { ...data };
      if (tags.length > 0) {
        payload.tags = tags;
      }
      if (!payload.due_date) {
        delete payload.due_date;
      }
      if (payload.recurring === 'none') {
        delete payload.recurring;
      }
      await addTask(payload);
      reset();
      setTags([]);
      setTagInput('');
    } catch (error) {
      if (error instanceof Error) {
        setApiError(error.message);
      } else {
        setApiError('Failed to create todo');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
      {/* Title Field */}
      <div>
        <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          type="text"
          {...register('title')}
          disabled={isLoading}
          placeholder="e.g., Buy groceries, Finish project report..."
          className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
            errors.title ? 'border-red-500 bg-red-50' : 'border-gray-300'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.title && (
          <p className="mt-2 text-sm text-red-600 flex items-start">
            <svg className="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Description Field */}
      <div>
        <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2">
          Description (optional)
        </label>
        <textarea
          id="description"
          {...register('description')}
          disabled={isLoading}
          placeholder="Add more details about this task..."
          rows={3}
          className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none ${
            errors.description ? 'border-red-500 bg-red-50' : 'border-gray-300'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.description && (
          <p className="mt-2 text-sm text-red-600 flex items-start">
            <svg className="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {errors.description.message}
          </p>
        )}
      </div>

      {/* Priority Field */}
      <div>
        <label htmlFor="priority" className="block text-sm font-semibold text-gray-700 mb-2">
          Priority
        </label>
        <select
          id="priority"
          defaultValue="medium"
          {...register('priority')}
          disabled={isLoading}
          className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
            errors.priority ? 'border-red-500 bg-red-50' : 'border-gray-300'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        >
          <option value="low">🟢 Low Priority</option>
          <option value="medium">🟡 Medium Priority</option>
          <option value="high">🔴 High Priority</option>
        </select>
        {errors.priority && (
          <p className="mt-2 text-sm text-red-600 flex items-start">
            <svg className="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {errors.priority.message}
          </p>
        )}
      </div>

      {/* Due Date and Recurring */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="due_date" className="block text-sm font-semibold text-gray-700 mb-2">
            Due Date (optional)
          </label>
          <input
            id="due_date"
            type="datetime-local"
            {...register('due_date')}
            disabled={isLoading}
            className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 ${
              isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
            }`}
          />
        </div>

        <div>
          <label htmlFor="recurring" className="block text-sm font-semibold text-gray-700 mb-2">
            Recurring Schedule
          </label>
          <select
            id="recurring"
            defaultValue="none"
            {...register('recurring')}
            disabled={isLoading}
            className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 ${
              isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
            }`}
          >
            <option value="none">None (one-time task)</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Tags (optional)
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagKeyDown}
            placeholder="Type a tag and press Enter"
            disabled={isLoading}
            className={`flex-1 px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 ${
              isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
            }`}
          />
          <button
            type="button"
            onClick={handleAddTag}
            disabled={isLoading || !tagInput.trim()}
            className="px-4 py-3 bg-gray-100 border-2 border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-1 inline-flex items-center justify-center w-4 h-4 text-blue-400 hover:text-blue-600"
                  aria-label={`Remove tag ${tag}`}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* API Error Display */}
      {apiError && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start space-x-3">
          <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-700 text-sm font-medium">{apiError}</p>
        </div>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        loading={isLoading}
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Adding...
          </>
        ) : (
          <>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Todo
          </>
        )}
      </Button>
    </form>
  );
}
