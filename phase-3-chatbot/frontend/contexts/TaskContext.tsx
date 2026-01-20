'use client';

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  ReactNode,
} from 'react';
import { apiClient, getUserId } from '../lib/api/client';
import type { Task, TaskCreate, TaskPatch } from '../types/task';

/** Context value for TaskContext */
export interface TaskContextValue {
  // State
  tasks: Task[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchTasks: () => Promise<void>;
  addTask: (task: TaskCreate) => Promise<Task>;
  updateTask: (taskId: number, updates: TaskPatch) => Promise<Task>;
  deleteTask: (taskId: number) => Promise<void>;

  // Sync
  triggerRefresh: () => void;
}

const TaskContext = createContext<TaskContextValue | null>(null);

interface TaskProviderProps {
  children: ReactNode;
}

export function TaskProvider({ children }: TaskProviderProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    const userId = getUserId();
    if (!userId) {
      setError('User not authenticated');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getTasks(userId);
      setTasks(response.tasks);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch tasks';
      setError(message);
      console.error('Failed to fetch tasks:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addTask = useCallback(async (taskData: TaskCreate): Promise<Task> => {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const newTask = await apiClient.createTask(userId, taskData);
    setTasks(prev => [newTask, ...prev]);
    return newTask;
  }, []);

  const updateTask = useCallback(async (taskId: number, updates: TaskPatch): Promise<Task> => {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const updatedTask = await apiClient.patchTask(userId, taskId, updates);
    setTasks(prev =>
      prev.map(task => (task.id === taskId ? updatedTask : task))
    );
    return updatedTask;
  }, []);

  const deleteTask = useCallback(async (taskId: number): Promise<void> => {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    await apiClient.deleteTask(userId, taskId);
    setTasks(prev => prev.filter(task => task.id !== taskId));
  }, []);

  const triggerRefresh = useCallback(() => {
    fetchTasks();
  }, [fetchTasks]);

  const value = useMemo<TaskContextValue>(
    () => ({
      tasks,
      isLoading,
      error,
      fetchTasks,
      addTask,
      updateTask,
      deleteTask,
      triggerRefresh,
    }),
    [tasks, isLoading, error, fetchTasks, addTask, updateTask, deleteTask, triggerRefresh]
  );

  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}

export function useTaskContext(): TaskContextValue {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTaskContext must be used within a TaskProvider');
  }
  return context;
}

export default TaskContext;
