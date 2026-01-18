import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ChatInterface from '@/components/chat/ChatInterface';
import { useSession } from '@/lib/auth/client';
import { useRouter } from 'next/navigation';

// Mock the useSession hook
vi.mock('@/lib/auth/client', () => ({
  useSession: vi.fn(),
}));

// Mock the useRouter hook
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

// Mock the next/script component
vi.mock('next/script', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('ChatInterface', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Default mock for useRouter
    (useRouter as unknown as vi.Mock).mockReturnValue({
      push: vi.fn(),
    });

    // Default mock for useSession (authenticated user)
    (useSession as unknown as vi.Mock).mockReturnValue({
      data: { user: { id: 'test-user-id', email: 'test@example.com' } },
      isPending: false,
    });
  });

  it('renders loading state when session is pending', () => {
    (useSession as unknown as vi.Mock).mockReturnValue({
      data: null,
      isPending: true,
    });

    render(<ChatInterface />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument(); // Assuming a progressbar for spinner
  });

  it('redirects to login if not authenticated and not pending', () => {
    const mockRouterPush = vi.fn();
    (useRouter as unknown as vi.Mock).mockReturnValue({
      push: mockRouterPush,
    });
    (useSession as unknown as vi.Mock).mockReturnValue({
      data: null,
      isPending: false,
    });

    render(<ChatInterface />);
    expect(mockRouterPush).toHaveBeenCalledWith('/login');
  });

  it('renders the chat interface when authenticated', () => {
    render(<ChatInterface />);
    expect(screen.getByText('Todo Assistant')).toBeInTheDocument();
    expect(screen.getByText('Start a conversation')).toBeInTheDocument();
  });
});
