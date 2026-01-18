// app/(dashboard)/page.tsx
'use client'; // This page now uses hooks, so it must be a client component

import { TaskList } from '@/components/tasks/TaskList';
import { CreateTaskForm } from '@/components/tasks/CreateTaskForm';
import React, { useState } from 'react';

export default function DashboardPage() {
  // Use a key to force re-mounting and re-fetching of the TaskList
  const [taskListKey, setTaskListKey] = useState(Date.now());

  const handleTaskCreated = () => {
    // Update the key to trigger a refresh of the TaskList
    setTaskListKey(Date.now());
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Your Tasks</h1>
      <div className="mb-8">
        <CreateTaskForm onTaskCreated={handleTaskCreated} />
      </div>
      <TaskList key={taskListKey} />
    </div>
  );
}
