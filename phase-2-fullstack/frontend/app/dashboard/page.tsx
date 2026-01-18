/**
 * Dashboard Page
 *
 * Main dashboard view for authenticated users.
 * Shows task list, create task form, and task management.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useSession } from '@/lib/auth/client';
import { useRouter } from 'next/navigation';
import { apiClient, initializeApiToken, getUserId } from '@/lib/api/client';
import { AddTodoForm } from '@/components/todos/AddTodoForm';
import { TodoList } from '@/components/todos/TodoList';
import type { Task, TaskCreate, TaskPatch } from '@/types/task';

export default function DashboardPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  const [todos, setTodos] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  // Initialize API token and fetch todos on mount
  useEffect(() => {
    const initialize = async () => {
      if (!session) return;

      try {
        // Get or initialize API token
        let storedUserId = getUserId();

        if (!storedUserId) {
          const tokenData = await initializeApiToken();
          if (tokenData) {
            storedUserId = tokenData.user_id;
          }
        }

        if (storedUserId) {
          setUserId(storedUserId);
          await fetchTodos(storedUserId);
        } else {
          setError('Failed to initialize authentication. Please try logging in again.');
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setError('Failed to initialize application. Please refresh the page or log in again.');
      } finally {
        setIsLoading(false);
      }
    };

    // Set timeout to prevent infinite loading (10 seconds)
    const timeout = setTimeout(() => {
      if (isLoading && !session) {
        setIsLoading(false);
        setError('Session loading timeout. Please refresh the page or log in again.');
      }
    }, 10000);

    if (session) {
      initialize();
    } else if (!isPending) {
      // Session is null and not pending - user not logged in
      setIsLoading(false);
    }

    return () => clearTimeout(timeout);
  }, [session, isPending]);

  // Fetch todos from API
  const fetchTodos = useCallback(async (uid: string) => {
    try {
      setError(null);
      const response = await apiClient.getTasks(uid);
      setTodos(response.tasks);
    } catch (err) {
      console.error('Failed to fetch todos:', err);
      setError('Failed to load todos');
    }
  }, []);

  // Create new todo
  const handleCreateTodo = async (data: TaskCreate) => {
    if (!userId) {
      setError('User not authenticated');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const newTodo = await apiClient.createTask(userId, data);
      setTodos((prev) => [newTodo, ...prev]);
    } catch (err) {
      console.error('Failed to create todo:', err);
      throw err; // Re-throw to let form handle error
    } finally {
      setIsCreating(false);
    }
  };

  // Update todo
  const handleUpdateTodo = async (todoId: number, updates: TaskPatch) => {
    if (!userId) return;

    try {
      const updatedTodo = await apiClient.patchTask(userId, todoId, updates);
      setTodos((prev) =>
        prev.map((todo) => (todo.id === todoId ? updatedTodo : todo))
      );
    } catch (err) {
      console.error('Failed to update todo:', err);
      throw err;
    }
  };

  // Delete todo
  const handleDeleteTodo = async (todoId: number) => {
    if (!userId) return;

    try {
      await apiClient.deleteTask(userId, todoId);
      setTodos((prev) => prev.filter((todo) => todo.id !== todoId));
    } catch (err) {
      console.error('Failed to delete todo:', err);
      throw err;
    }
  };

  // Loading state
  if (isPending || isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!session) {
    if (typeof window !== 'undefined') {
      router.push('/login');
    }
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl shadow-lg px-8 py-8 text-white">
        <div className="flex items-center space-x-3 mb-3">
          <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h1 className="text-4xl font-bold">My Todos</h1>
        </div>
        <p className="text-blue-50 text-lg">
          Welcome back, <span className="font-semibold text-white">{session.user.name || session.user.email}</span>
        </p>
        <p className="mt-2 text-blue-100 text-sm">
          Stay organized and productive with your task list
        </p>
      </div>

      {/* Global Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg px-6 py-4 flex items-start space-x-3">
          <svg className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-700 font-medium">{error}</p>
        </div>
      )}

      {/* Create Todo Section */}
      <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 px-8 py-6 border border-gray-100">
        <div className="flex items-center space-x-2 mb-5">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900">
            Create New Todo
          </h2>
        </div>
        <AddTodoForm onSubmit={handleCreateTodo} isLoading={isCreating} />
      </div>

      {/* Todo List Section */}
      <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 px-8 py-6 border border-gray-100">
        <div className="flex items-center space-x-2 mb-5">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900">
            Your Todos
          </h2>
        </div>
        <TodoList
          todos={todos}
          onUpdate={handleUpdateTodo}
          onDelete={handleDeleteTodo}
          isLoading={isLoading && !session}
        />
      </div>
    </div>
  );
}
