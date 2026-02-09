/**
 * VoiceInput Component Tests
 *
 * Tests for the VoiceInput component using Vitest and React Testing Library.
 * Tests cover Web Speech API integration, language selection, and error handling.
 */
import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import VoiceInput from "@/components/chat/VoiceInput";

// Mock SpeechRecognition API
class MockSpeechRecognition {
  continuous = false;
  interimResults = true;
  lang = "en-US";
  onresult: ((event: any) => void) | null = null;
  onerror: ((event: any) => void) | null = null;
  onend: (() => void) | null = null;
  onstart: (() => void) | null = null;

  start = vi.fn(() => {
    if (this.onstart) {
      this.onstart();
    }
  });

  stop = vi.fn(() => {
    if (this.onend) {
      this.onend();
    }
  });

  abort = vi.fn();
}

// Setup mock before tests
beforeEach(() => {
  // @ts-ignore
  global.window.SpeechRecognition = MockSpeechRecognition;
  // @ts-ignore
  global.window.webkitSpeechRecognition = MockSpeechRecognition;
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("VoiceInput", () => {
  it("renders correctly when speech recognition is supported", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    // Should show language selector
    expect(screen.getByRole("combobox")).toBeInTheDocument();
    // Should show microphone button
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("displays 'not supported' message when speech recognition is unavailable", () => {
    // Remove SpeechRecognition from window
    // @ts-ignore
    delete global.window.SpeechRecognition;
    // @ts-ignore
    delete global.window.webkitSpeechRecognition;

    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    expect(
      screen.getByText("Voice input not supported in this browser")
    ).toBeInTheDocument();

    // Restore for other tests
    // @ts-ignore
    global.window.SpeechRecognition = MockSpeechRecognition;
    // @ts-ignore
    global.window.webkitSpeechRecognition = MockSpeechRecognition;
  });

  it("starts recording when microphone button is clicked", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    const micButton = screen.getByRole("button");
    fireEvent.click(micButton);

    // Button should have recording state (red background)
    expect(micButton).toHaveClass("bg-red-500");
  });

  it("shows language options for English and Urdu", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    const languageSelect = screen.getByRole("combobox");
    expect(languageSelect).toBeInTheDocument();

    // Should have English and Urdu options
    const options = screen.getAllByRole("option");
    expect(options).toHaveLength(2);
    expect(options[0]).toHaveValue("en-US");
    expect(options[1]).toHaveValue("ur-PK");
  });

  it("changes language when selector is changed", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    const languageSelect = screen.getByRole("combobox");
    fireEvent.change(languageSelect, { target: { value: "ur-PK" } });

    expect(languageSelect).toHaveValue("ur-PK");
  });

  it("disables controls when disabled prop is true", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} disabled={true} />);

    const micButton = screen.getByRole("button");
    const languageSelect = screen.getByRole("combobox");

    expect(micButton).toBeDisabled();
    expect(languageSelect).toBeDisabled();
  });

  it("uses default language from props", () => {
    const mockOnTranscript = vi.fn();
    render(
      <VoiceInput onTranscript={mockOnTranscript} defaultLanguage="ur-PK" />
    );

    const languageSelect = screen.getByRole("combobox");
    expect(languageSelect).toHaveValue("ur-PK");
  });

  it("calls onTranscript with final transcript", () => {
    const mockOnTranscript = vi.fn();
    let capturedRecognition: MockSpeechRecognition | null = null;

    // Capture the recognition instance
    vi.spyOn(global.window, "SpeechRecognition" as any).mockImplementation(
      () => {
        capturedRecognition = new MockSpeechRecognition();
        return capturedRecognition;
      }
    );

    render(<VoiceInput onTranscript={mockOnTranscript} />);

    // Start recording
    const micButton = screen.getByRole("button");
    fireEvent.click(micButton);

    // Simulate speech recognition result
    if (capturedRecognition && capturedRecognition.onresult) {
      act(() => {
        capturedRecognition!.onresult({
          resultIndex: 0,
          results: [
            {
              0: { transcript: "add a task to buy groceries", confidence: 0.9 },
              length: 1,
              isFinal: true,
            },
          ],
        });
      });
    }

    expect(mockOnTranscript).toHaveBeenCalledWith("add a task to buy groceries");
  });

  it("shows 'Listening...' when recording starts", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    const micButton = screen.getByRole("button");
    fireEvent.click(micButton);

    expect(screen.getByText("Listening...")).toBeInTheDocument();
  });

  it("has proper aria labels for accessibility", () => {
    const mockOnTranscript = vi.fn();
    render(<VoiceInput onTranscript={mockOnTranscript} />);

    expect(
      screen.getByLabelText("Select voice input language")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Start voice input")).toBeInTheDocument();
  });
});

describe("VoiceInput Error Handling", () => {
  it("handles no-speech error gracefully", () => {
    const mockOnTranscript = vi.fn();
    let capturedRecognition: MockSpeechRecognition | null = null;

    vi.spyOn(global.window, "SpeechRecognition" as any).mockImplementation(
      () => {
        capturedRecognition = new MockSpeechRecognition();
        return capturedRecognition;
      }
    );

    render(<VoiceInput onTranscript={mockOnTranscript} />);

    const micButton = screen.getByRole("button");
    fireEvent.click(micButton);

    // Simulate no-speech error
    if (capturedRecognition && capturedRecognition.onerror) {
      act(() => {
        capturedRecognition!.onerror({ error: "no-speech" });
      });
    }

    expect(screen.getByText(/No speech detected/)).toBeInTheDocument();
  });

  it("handles not-allowed error for microphone access", () => {
    const mockOnTranscript = vi.fn();
    let capturedRecognition: MockSpeechRecognition | null = null;

    vi.spyOn(global.window, "SpeechRecognition" as any).mockImplementation(
      () => {
        capturedRecognition = new MockSpeechRecognition();
        return capturedRecognition;
      }
    );

    render(<VoiceInput onTranscript={mockOnTranscript} />);

    const micButton = screen.getByRole("button");
    fireEvent.click(micButton);

    // Simulate permission denied error
    if (capturedRecognition && capturedRecognition.onerror) {
      act(() => {
        capturedRecognition!.onerror({ error: "not-allowed" });
      });
    }

    expect(screen.getByText(/Microphone access denied/)).toBeInTheDocument();
  });
});
