/**
 * TodoList Component
 *
 * Displays a list of todos with filtering and empty states.
 */

'use client';

import { useState } from 'react';
import { TodoItem } from './TodoItem';
import type { Task, TaskPatch, TaskPriority } from '@/types/task';

interface TodoListProps {
  todos: Task[];
  onUpdate: (todoId: number, updates: TaskPatch) => Promise<void>;
  onDelete: (todoId: number) => Promise<void>;
  isLoading?: boolean;
}

type FilterType = 'all' | 'active' | 'completed';
type PriorityFilterType = 'all' | 'low' | 'medium' | 'high';

export function TodoList({ todos, onUpdate, onDelete, isLoading = false }: TodoListProps) {
  const [filter, setFilter] = useState<FilterType>('all');
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter todos based on selected filter, priority filter, and search query
  const filteredTodos = todos.filter((todo) => {
    // Filter by status
    if (filter === 'active' && todo.complete) return false;
    if (filter === 'completed' && !todo.complete) return false;

    // Filter by priority
    if (priorityFilter !== 'all' && todo.priority !== priorityFilter) return false;

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const matchesTitle = todo.title.toLowerCase().includes(query);
      const matchesDescription = todo.description?.toLowerCase().includes(query);

      // Match by actual database ID (consistent with chatbot)
      const matchesTaskId = todo.id.toString().includes(query.replace('#', ''));

      return matchesTitle || matchesDescription || matchesTaskId;
    }

    return true;
  });

  // Stats
  const totalCount = todos.length;
  const activeCount = todos.filter((t) => !t.complete).length;
  const completedCount = todos.filter((t) => t.complete).length;
  const lowCount = todos.filter((t) => t.priority === 'low').length;
  const mediumCount = todos.filter((t) => t.priority === 'medium').length;
  const highCount = todos.filter((t) => t.priority === 'high').length;

  return (
    <div className="space-y-5">
      {/* Search Bar */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by title, description, or task number (e.g., #1)..."
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm text-gray-900 placeholder-gray-400"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Filter Tabs and Stats */}
      <div className="space-y-3">
        {/* Status Filters */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="inline-flex bg-gray-100 rounded-lg p-1 space-x-1">
            <button
              onClick={() => setFilter('all')}
              className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${
                filter === 'all'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              All
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
                filter === 'all' ? 'bg-white/20' : 'bg-gray-300'
              }`}>
                {totalCount}
              </span>
            </button>
            <button
              onClick={() => setFilter('active')}
              className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${
                filter === 'active'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              Active
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
                filter === 'active' ? 'bg-white/20' : 'bg-gray-300'
              }`}>
                {activeCount}
              </span>
            </button>
            <button
              onClick={() => setFilter('completed')}
              className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${
                filter === 'completed'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              Completed
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
                filter === 'completed' ? 'bg-white/20' : 'bg-gray-300'
              }`}>
                {completedCount}
              </span>
            </button>
          </div>
        </div>

        {/* Priority Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-gray-700">Priority:</span>
          <div className="inline-flex bg-gray-100 rounded-lg p-1 space-x-1">
            <button
              onClick={() => setPriorityFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                priorityFilter === 'all'
                  ? 'bg-gray-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setPriorityFilter('low')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                priorityFilter === 'low'
                  ? 'bg-green-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              🟢 Low
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
                priorityFilter === 'low' ? 'bg-white/20' : 'bg-gray-300'
              }`}>
                {lowCount}
              </span>
            </button>
            <button
              onClick={() => setPriorityFilter('medium')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                priorityFilter === 'medium'
                  ? 'bg-yellow-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              🟡 Medium
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
                priorityFilter === 'medium' ? 'bg-white/20' : 'bg-gray-300'
              }`}>
                {mediumCount}
              </span>
            </button>
            <button
              onClick={() => setPriorityFilter('high')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                priorityFilter === 'high'
                  ? 'bg-red-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              🔴 High
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
                priorityFilter === 'high' ? 'bg-white/20' : 'bg-gray-300'
              }`}>
                {highCount}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-16 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200"></div>
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-t-blue-600 absolute top-0 left-0"></div>
          </div>
          <p className="mt-4 text-blue-600 font-medium">Loading your todos...</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredTodos.length === 0 && (
        <div className="text-center py-16 bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="flex justify-center">
            <div className="bg-blue-100 p-4 rounded-full">
              <svg
                className="h-16 w-16 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
          </div>
          <h3 className="mt-4 text-lg font-semibold text-gray-900">
            {filter === 'all' && 'No todos yet'}
            {filter === 'active' && 'No active todos'}
            {filter === 'completed' && 'No completed todos'}
          </h3>
          <p className="mt-2 text-sm text-gray-600 max-w-sm mx-auto">
            {filter === 'all' && 'Get started by creating your first todo using the form above'}
            {filter === 'active' && 'Awesome! All your todos are completed 🎉'}
            {filter === 'completed' && 'Complete some todos to see them appear here'}
          </p>
        </div>
      )}

      {/* Todo Items */}
      {!isLoading && filteredTodos.length > 0 && (
        <div className="space-y-3">
          {filteredTodos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              taskNumber={todo.id}  // Use actual database ID for consistency with chatbot
              onUpdate={onUpdate}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
