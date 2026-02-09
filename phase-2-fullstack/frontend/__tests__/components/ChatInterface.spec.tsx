/**
 * ChatInterface Component Tests
 *
 * Tests for the ChatInterface component using Vitest and React Testing Library.
 */
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { useSession } from "@/lib/auth/client";

// Mock next/script to prevent loading external scripts in tests
vi.mock("next/script", () => ({
  default: ({ onLoad }: { onLoad?: () => void }) => {
    // Simulate script loaded immediately
    if (onLoad) {
      setTimeout(onLoad, 0);
    }
    return null;
  },
}));

// Mock VoiceInput component to simplify ChatInterface tests
vi.mock("@/components/chat/VoiceInput", () => ({
  default: () => <div data-testid="voice-input">Voice Input Mock</div>,
}));

// Dynamically import after mocks are set up
let ChatInterface: typeof import("@/components/chat/ChatInterface").default;

describe("ChatInterface", () => {
  beforeEach(async () => {
    vi.resetModules();

    // Re-mock useSession with authenticated user for these tests
    vi.mocked(useSession).mockReturnValue({
      data: { user: { id: "test-user", email: "test@example.com", name: "Test User" } } as any,
      isPending: false,
      error: null,
    });

    // Import component after mocks
    const module = await import("@/components/chat/ChatInterface");
    ChatInterface = module.default;
  });

  it("renders the header correctly", async () => {
    render(<ChatInterface />);

    // Wait for component to render
    await waitFor(() => {
      expect(screen.getByText("Todo Assistant")).toBeInTheDocument();
    });
  });

  it("shows loading state while session is pending", async () => {
    vi.mocked(useSession).mockReturnValue({
      data: null,
      isPending: true,
      error: null,
    });

    render(<ChatInterface />);
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("displays ChatKit badge", async () => {
    render(<ChatInterface />);

    await waitFor(() => {
      expect(screen.getByText("ChatKit")).toBeInTheDocument();
    });
  });

  it("displays description text", async () => {
    render(<ChatInterface />);

    await waitFor(() => {
      expect(
        screen.getByText("Manage your tasks through natural language. Powered by OpenAI ChatKit.")
      ).toBeInTheDocument();
    });
  });

  it("displays voice input component when loaded", async () => {
    render(<ChatInterface />);

    await waitFor(() => {
      expect(screen.getByTestId("voice-input")).toBeInTheDocument();
    });
  });
});
