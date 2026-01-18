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

type CreateTaskFormInputs = z.infer<typeof createTaskSchema>;

interface CreateTaskFormProps {
  onTaskCreated: () => void;
}

export const CreateTaskForm: React.FC<CreateTaskFormProps> = ({ onTaskCreated }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const onSubmit: SubmitHandler<CreateTaskFormInputs> = async (data) => {
    setIsSubmitting(true);
    const userId = getUserId();
    if (!userId) {
      toast.error('You must be logged in to create a task.');
      setIsSubmitting(false);
      return;
    }

    try {
      await apiClient.createTask(userId, data);
      toast.success('Task created successfully!');
      reset(); // Clear form on success
      onTaskCreated(); // Notify parent to refresh task list
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
          rows={4}
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

      <div className="mb-4">
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700">Priority</label>
        <select
          {...register('priority')}
          id="priority"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          aria-invalid={errors.priority ? 'true' : 'false'}
        >
          <option value="low">🟢 Low Priority</option>
          <option value="medium">🟡 Medium Priority</option>
          <option value="high">🔴 High Priority</option>
        </select>
        {errors.priority && (
          <p className="mt-1 text-sm text-red-600" role="alert">{errors.priority.message}</p>
        )}
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Adding Task...' : 'Add Task'}
      </Button>
    </form>
  );
};
