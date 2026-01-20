/**
 * Dashboard Page
 *
 * Main dashboard view for authenticated users.
 * Shows task list, create task form, task management, and chat widget.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useSession } from '../../lib/auth/client';
import { useRouter } from 'next/navigation';
import { apiClient, initializeApiToken, getUserId } from '../../lib/api/client';
import { AddTodoForm } from '../../components/todos/AddTodoForm';
import { TodoList } from '../../components/todos/TodoList';
import { ChatWidgetFAB } from '../../components/chat/ChatWidgetFAB';
import { ChatWidget } from '../../components/chat/ChatWidget';
import { TaskProvider, useTaskContext } from '../../contexts/TaskContext';
import type { Task, TaskCreate, TaskPatch } from '../../types/task';

export default function DashboardPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const { fetchTasks, isLoading, error } = useTaskContext();

  // Initialize API token and fetch todos on mount
  useEffect(() => {
    const initializeSessionAndTasks = async () => {
      if (!session) return;

      try {
        let currentUserId = getUserId();
        if (!currentUserId) {
          const tokenData = await initializeApiToken();
          if (tokenData && tokenData.user_id) {
            currentUserId = tokenData.user_id;
          } else {
            throw new Error('Failed to get user ID after token initialization.');
          }
        }
        await fetchTasks(); // Fetch tasks using TaskContext
      } catch (err) {
        console.error('Initialization error:', err);
        // Optionally, display a global error or redirect to login if initialization fails
        if (err instanceof Error && err.message === 'Unauthorized') {
          router.push('/login');
        } else {
          // Handle other initialization errors
        }
      }
    };

    if (session && !isLoading) { // Only initialize if session exists and TaskContext isn't already loading
      initializeSessionAndTasks();
    } else if (!isPending && !session) {
      router.push('/login');
    }
  }, [session, isPending, fetchTasks, isLoading, router]);


  // Redirect if not authenticated (handled by useEffect above, but this provides a visual loading state)
  if (isPending || !session) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // The rest of the component will consume tasks and state from TaskContext directly
  return (
    <TaskProvider>
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
        <AddTodoForm />
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
        <TodoList />
      </div>

      {/* Chat Widget */}
      <ChatWidgetFAB />
      <ChatWidget />
    </div>
    </TaskProvider>
  );
}
