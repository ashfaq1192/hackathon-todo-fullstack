// components/tasks/TaskList.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { Task, TaskPriority, TaskQueryParams } from '@/types/task';
import { TaskItem } from '@/components/tasks/TaskItem';
import { apiClient, getUserId } from '@/lib/api/client';
import { TaskItemSkeleton } from './TaskItemSkeleton';

export const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  // Search/Filter/Sort state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | ''>('');
  const [tagFilter, setTagFilter] = useState('');
  const [sortBy, setSortBy] = useState<'created_at' | 'due_date' | 'priority' | 'title'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const fetchTasks = useCallback(async () => {
    const userId = getUserId();
    if (!userId) {
      setError(new Error('User not authenticated. Please log in.'));
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      // Build query params
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (statusFilter && statusFilter !== 'all') params.append('status', statusFilter);
      if (priorityFilter) params.append('priority', priorityFilter);
      if (tagFilter) {
        tagFilter.split(',').map(t => t.trim()).filter(Boolean).forEach(t => params.append('tags', t));
      }
      if (sortBy !== 'created_at') params.append('sort_by', sortBy);
      if (sortOrder !== 'desc') params.append('sort_order', sortOrder);

      const queryString = params.toString();
      const response = await apiClient.getTasks(userId, queryString ? `?${queryString}` : '');
      setTasks(response.tasks);
    } catch (err: any) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, statusFilter, priorityFilter, tagFilter, sortBy, sortOrder]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(prevTasks =>
      prevTasks.map(task => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleTaskDeleted = (taskId: number) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
  };

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div>
      {/* Search and Filter Controls */}
      <div className="mb-6 space-y-3">
        {/* Search bar */}
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tasks..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* Filter row */}
        <div className="flex flex-wrap gap-3 items-center">
          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>

          {/* Priority filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value as any)}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* Tag filter */}
          <input
            type="text"
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value)}
            placeholder="Filter by tags (comma-separated)"
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 min-w-[200px]"
          />

          {/* Sort controls */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="created_at">Sort by Date</option>
            <option value="due_date">Sort by Due Date</option>
            <option value="priority">Sort by Priority</option>
            <option value="title">Sort by Title</option>
          </select>

          <button
            onClick={toggleSortOrder}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm hover:bg-gray-50 focus:ring-2 focus:ring-blue-500"
            title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
          >
            {sortOrder === 'asc' ? '↑ Asc' : '↓ Desc'}
          </button>
        </div>
      </div>

      {/* Task list */}
      {isLoading ? (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <TaskItemSkeleton key={index} />
          ))}
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-32 text-red-500">
          <p>Error: {error.message}</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="flex justify-center items-center h-32 text-gray-500">
          <p className="text-lg">
            {searchQuery || statusFilter !== 'all' || priorityFilter || tagFilter
              ? 'No tasks match your filters.'
              : 'No tasks yet. Start by adding a new one!'}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onTaskUpdated={handleTaskUpdated}
              onTaskDeleted={handleTaskDeleted}
            />
          ))}
        </div>
      )}
    </div>
  );
};
