// Unit test for CreateTaskForm component (validation, submission, character counter)
// T062 [P] [US4]

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CreateTaskForm } from '@/components/tasks/CreateTaskForm'; // Assuming component path

describe('CreateTaskForm', () => {
  it('renders create task form with all required fields', () => {
    render(<CreateTaskForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument();
  });

  it('validates title is required', async () => {
    render(<CreateTaskForm onSubmit={vi.fn()} />);
    const submitButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });
  });

  it('validates title max length (200 characters)', async () => {
    render(<CreateTaskForm onSubmit={vi.fn()} />);
    const titleInput = screen.getByLabelText(/title/i);
    const longTitle = 'a'.repeat(201);
    fireEvent.change(titleInput, { target: { value: longTitle } });

    const submitButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title must be 200 characters or less/i)).toBeInTheDocument();
    });
  });

  it('validates description max length (1000 characters)', async () => {
    render(<CreateTaskForm onSubmit={vi.fn()} />);
    const descriptionInput = screen.getByLabelText(/description/i);
    const longDescription = 'a'.repeat(1001);
    fireEvent.change(descriptionInput, { target: { value: longDescription } });

    const submitButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/description must be 1000 characters or less/i)).toBeInTheDocument();
    });
  });

  it('displays character counter for title and description', () => {
    render(<CreateTaskForm onSubmit={vi.fn()} />);
    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Title' } });
    expect(screen.getByText(/10 \/ 200/)).toBeInTheDocument();

    const descriptionInput = screen.getByLabelText(/description/i);
    fireEvent.change(descriptionInput, { target: { value: 'Test Description' } });
    expect(screen.getByText(/16 \/ 1000/)).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const mockOnSubmit = vi.fn();
    render(<CreateTaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    fireEvent.change(titleInput, { target: { value: 'New Task' } });
    fireEvent.change(descriptionInput, { target: { value: 'A description for the new task.' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'New Task',
        description: 'A description for the new task.',
      });
    });
  });

  it('shows loading state during submission', async () => {
    const mockOnSubmit = vi.fn(() => new Promise(resolve => setTimeout(resolve, 1000)));
    render(<CreateTaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    fireEvent.change(titleInput, { target: { value: 'New Task' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/adding task/i)).toBeInTheDocument();
    });
  });

  it('displays error message from API', async () => {
    const mockOnSubmit = vi.fn().mockRejectedValue(new Error('Failed to create task'));
    render(<CreateTaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    fireEvent.change(titleInput, { target: { value: 'New Task' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to create task/i)).toBeInTheDocument();
    });
  });
});
