// components/tasks/CreateTaskForm.tsx
import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { createTaskSchema } from '@/lib/validation/schemas';
import { apiClient, getUserId } from '@/lib/api/client';
import { RecurringType } from '@/types/task';

type CreateTaskFormInputs = z.infer<typeof createTaskSchema>;

interface CreateTaskFormProps {
  onTaskCreated: () => void;
}

export const CreateTaskForm: React.FC<CreateTaskFormProps> = ({ onTaskCreated }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<CreateTaskFormInputs>({
    resolver: zodResolver(createTaskSchema),
  });

  const titleLength = watch('title')?.length || 0;
  const descriptionLength = watch('description')?.length || 0;

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

  const onSubmit: SubmitHandler<CreateTaskFormInputs> = async (data) => {
    setIsSubmitting(true);
    const userId = getUserId();
    if (!userId) {
      toast.error('You must be logged in to create a task.');
      setIsSubmitting(false);
      return;
    }

    try {
      const payload: any = { ...data };
      if (tags.length > 0) {
        payload.tags = tags;
      }
      // Convert empty due_date to undefined
      if (!payload.due_date) {
        delete payload.due_date;
      }
      if (payload.recurring === 'none') {
        delete payload.recurring;
      }

      await apiClient.createTask(userId, payload);
      toast.success('Task created successfully!');
      reset();
      setTags([]);
      setTagInput('');
      onTaskCreated();
    } catch (err: any) {
      toast.error(err.message || 'An unexpected error occurred.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="p-4 bg-white rounded-md shadow-md border border-gray-200 max-w-xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Add a New Task</h2>

      <div className="mb-4">
        <Input
          {...register('title')}
          label="Title"
          placeholder="e.g., Buy groceries"
          error={errors.title?.message}
          required
          aria-describedby="title-counter"
        />
        <p id="title-counter" className="text-xs text-gray-500 mt-1 text-right" aria-live="polite">{titleLength} / 200</p>
      </div>

      <div className="mb-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description (Optional)</label>
        <textarea
          {...register('description')}
          id="description"
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          placeholder="e.g., Milk, eggs, bread"
          aria-describedby="description-counter"
          aria-invalid={errors.description ? 'true' : 'false'}
        />
        <p id="description-counter" className="text-xs text-gray-500 mt-1 text-right" aria-live="polite">{descriptionLength} / 1000</p>
        {errors.description && (
          <p className="mt-1 text-sm text-red-600" role="alert">{errors.description.message}</p>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700">Priority</label>
          <select
            {...register('priority')}
            id="priority"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="low">Low Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="high">High Priority</option>
          </select>
        </div>

        <div>
          <label htmlFor="due_date" className="block text-sm font-medium text-gray-700">Due Date (Optional)</label>
          <input
            {...register('due_date')}
            id="due_date"
            type="datetime-local"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="mb-4">
        <label htmlFor="recurring" className="block text-sm font-medium text-gray-700">Recurring Schedule</label>
        <select
          {...register('recurring')}
          id="recurring"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="none">None (one-time task)</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Tags (Optional)</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagKeyDown}
            placeholder="Type tag and press Enter"
            className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
          <Button type="button" variant="outline" size="sm" onClick={handleAddTag}>
            Add
          </Button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
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

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Adding Task...' : 'Add Task'}
      </Button>
    </form>
  );
};
