// Unit test for TaskItem checkbox toggle (optimistic update, revert on error)
// T073 [P] [US5]

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TaskItem } from '@/components/tasks/TaskItem';
import { Task } from '@/types/task';

// Mock apiClient
vi.mock('@/lib/api/client', () => ({
  apiClient: {
    patchTask: vi.fn(),
  },
  getUserId: () => 'test-user-id-123',
}));
import { apiClient } from '@/lib/api/client';

const mockTask: Task = {
  id: '1',
  user_id: 'user1',
  title: 'Test Task',
  description: 'A description for the test task.',
  complete: false,
  created_at: '2025-01-01T12:00:00Z',
  updated_at: '2025-01-01T12:00:00Z',
};

describe('TaskItem', () => {
  it('renders the task item correctly', () => {
    render(<TaskItem task={mockTask} />);
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('A description for the test task.')).toBeInTheDocument();
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).not.toBeChecked();
  });

  it('optimistically updates the checkbox and calls patchTask', async () => {
    render(<TaskItem task={mockTask} />);
    const checkbox = screen.getByRole('checkbox');

    // Mock successful API call
    (apiClient.patchTask as any).mockResolvedValueOnce({ task: { ...mockTask, complete: true } });

    fireEvent.click(checkbox);

    // Check for optimistic update
    expect(checkbox).toBeChecked();

    // Wait for the API call
    await waitFor(() => {
      expect(apiClient.patchTask).toHaveBeenCalledWith(
        'test-user-id-123',
        mockTask.id,
        { complete: true }
      );
    });

    // Final state should remain checked
    expect(checkbox).toBeChecked();
  });

  it('reverts the checkbox state on API error', async () => {
    render(<TaskItem task={mockTask} />);
    const checkbox = screen.getByRole('checkbox');

    // Mock failed API call
    (apiClient.patchTask as any).mockRejectedValueOnce(new Error('API Error'));

    fireEvent.click(checkbox);

    // Check for optimistic update
    expect(checkbox).toBeChecked();

    // Wait for the API call to fail and the UI to revert
    await waitFor(() => {
      expect(apiClient.patchTask).toHaveBeenCalledWith(
        'test-user-id-123',
        mockTask.id,
        { complete: true }
      );
    });

    // Check that the checkbox is reverted to its original state
    expect(checkbox).not.toBeChecked();
    
    // Check that an error message is displayed
    expect(screen.getByText(/failed to update task/i)).toBeInTheDocument();
  });
});
