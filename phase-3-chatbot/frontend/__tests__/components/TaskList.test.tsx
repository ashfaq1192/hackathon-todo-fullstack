// Unit test for TaskList component (empty state, task display, loading)
// T050 [P] [US3]

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { TaskList } from '@/components/tasks/TaskList'; // Assuming TaskList component path
import { Task } from '@/types/task'; // Assuming Task type path

// Mocking the TaskItem component since it's a sub-component and will be tested separately
vi.mock('@/components/tasks/TaskItem', () => ({
  TaskItem: vi.fn(({ task }) => (
    <div data-testid={`task-item-${task.id}`}>{task.title}</div>
  )),
}));

describe('TaskList', () => {
  const mockTasks: Task[] = [
    {
      id: '1',
      user_id: 'user1',
      title: 'Task 1',
      description: 'Description 1',
      complete: false,
      created_at: '2025-01-01T12:00:00Z',
      updated_at: '2025-01-01T12:00:00Z',
    },
    {
      id: '2',
      user_id: 'user1',
      title: 'Task 2',
      description: 'Description 2',
      complete: true,
      created_at: '2025-01-02T12:00:00Z',
      updated_at: '2025-01-02T12:00:00Z',
    },
  ];

  it('renders loading state when isLoading is true', () => {
    render(<TaskList tasks={[]} isLoading={true} error={null} />);
    expect(screen.getByTestId('task-list-loading')).toBeInTheDocument(); // Assuming a data-testid for loading state
  });

  it('renders error message when an error is present', () => {
    const errorMessage = 'Failed to fetch tasks.';
    render(<TaskList tasks={[]} isLoading={false} error={new Error(errorMessage)} />);
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('renders empty state when no tasks and not loading/error', () => {
    render(<TaskList tasks={[]} isLoading={false} error={null} />);
    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument(); // Assuming "No tasks yet" for empty state
  });

  it('renders a list of tasks', () => {
    render(<TaskList tasks={mockTasks} isLoading={false} error={null} />);
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
    expect(screen.getAllByTestId(/task-item-/)).toHaveLength(mockTasks.length);
  });

  it('does not render loading or error when tasks are present', () => {
    render(<TaskList tasks={mockTasks} isLoading={false} error={null} />);
    expect(screen.queryByTestId('task-list-loading')).not.toBeInTheDocument();
    expect(screen.queryByText(/failed to fetch tasks/i)).not.toBeInTheDocument();
  });
});
