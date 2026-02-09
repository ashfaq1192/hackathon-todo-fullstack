"use client";

/**
 * VoiceInput Component
 *
 * Provides voice input capabilities for the chatbot using Web Speech API.
 * Supports English and Urdu voice recognition for hands-free task management.
 *
 * Features:
 * - Real-time speech-to-text transcription
 * - Language selection (English/Urdu)
 * - Visual feedback for recording state
 * - Error handling for browser compatibility
 *
 * @component
 * Phase III - User Story 8 (+200 bonus points)
 */

import { useState, useEffect, useCallback } from "react";

// Type definitions for Web Speech API
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

export interface VoiceInputProps {
  /** Callback when transcription is complete */
  onTranscript: (text: string) => void;
  /** Whether the chat is currently processing a message */
  disabled?: boolean;
  /** Default language for voice recognition */
  defaultLanguage?: "en-US" | "ur-PK";
}

type RecordingState = "idle" | "recording" | "processing";
type SupportedLanguage = "en-US" | "ur-PK";

const LANGUAGE_OPTIONS: { value: SupportedLanguage; label: string; flag: string }[] = [
  { value: "en-US", label: "English", flag: "🇺🇸" },
  { value: "ur-PK", label: "اردو (Urdu)", flag: "🇵🇰" },
];

export default function VoiceInput({
  onTranscript,
  disabled = false,
  defaultLanguage = "en-US",
}: VoiceInputProps) {
  const [isSupported, setIsSupported] = useState(false);
  const [recordingState, setRecordingState] = useState<RecordingState>("idle");
  const [language, setLanguage] = useState<SupportedLanguage>(defaultLanguage);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);

  // Check browser support on mount
  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognitionAPI) {
      setIsSupported(true);

      // Initialize recognition instance
      const recognitionInstance = new SpeechRecognitionAPI();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = language;

      recognitionInstance.onstart = () => {
        setRecordingState("recording");
        setError(null);
        setTranscript("");
      };

      recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
        let finalTranscript = "";
        let interimTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interimTranscript += result[0].transcript;
          }
        }

        // Update transcript display
        setTranscript(finalTranscript || interimTranscript);

        // If final, send to callback
        if (finalTranscript) {
          setRecordingState("processing");
          onTranscript(finalTranscript);
        }
      };

      recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error("Speech recognition error:", event.error);

        // T056: Error handling for speech recognition failures
        let errorMessage = "Voice recognition failed. ";
        switch (event.error) {
          case "no-speech":
            errorMessage += "No speech detected. Please try again.";
            break;
          case "audio-capture":
            errorMessage += "No microphone found. Please connect a microphone.";
            break;
          case "not-allowed":
            errorMessage += "Microphone access denied. Please allow microphone access.";
            break;
          case "network":
            errorMessage += "Network error. Please check your connection.";
            break;
          case "aborted":
            errorMessage = ""; // User cancelled, no error message needed
            break;
          default:
            errorMessage += event.message || "Please try again.";
        }

        setError(errorMessage);
        setRecordingState("idle");
      };

      recognitionInstance.onend = () => {
        // Only reset to idle if not in processing state
        setRecordingState((prev) => (prev === "processing" ? "idle" : prev));
      };

      setRecognition(recognitionInstance);

      // Cleanup on unmount
      return () => {
        recognitionInstance.abort();
      };
    }
  }, [language, onTranscript]);

  // Update language when it changes
  useEffect(() => {
    if (recognition) {
      recognition.lang = language;
    }
  }, [language, recognition]);

  const startRecording = useCallback(() => {
    if (recognition && recordingState === "idle" && !disabled) {
      setError(null);
      try {
        recognition.start();
      } catch (err) {
        console.error("Failed to start recording:", err);
        setError("Failed to start voice recognition. Please try again.");
      }
    }
  }, [recognition, recordingState, disabled]);

  const stopRecording = useCallback(() => {
    if (recognition && recordingState === "recording") {
      recognition.stop();
      setRecordingState("idle");
    }
  }, [recognition, recordingState]);

  const toggleRecording = useCallback(() => {
    if (recordingState === "recording") {
      stopRecording();
    } else {
      startRecording();
    }
  }, [recordingState, startRecording, stopRecording]);

  // Not supported message
  if (!isSupported) {
    return (
      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
        <span className="mr-2">🎤</span>
        <span>Voice input not supported in this browser</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      {/* Language Selector (T055) */}
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
        disabled={disabled || recordingState === "recording"}
        className="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        aria-label="Select voice input language"
      >
        {LANGUAGE_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.flag} {option.label}
          </option>
        ))}
      </select>

      {/* Voice Input Button */}
      <button
        type="button"
        onClick={toggleRecording}
        disabled={disabled}
        className={`p-3 rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          recordingState === "recording"
            ? "bg-red-500 text-white animate-pulse hover:bg-red-600"
            : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        aria-label={recordingState === "recording" ? "Stop recording" : "Start voice input"}
        title={recordingState === "recording" ? "Click to stop" : "Click to speak"}
      >
        {recordingState === "recording" ? (
          // Recording indicator - animated mic
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        ) : (
          // Idle microphone icon
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        )}
      </button>

      {/* Live Transcript Display */}
      {(recordingState === "recording" || transcript) && (
        <div className="flex-1 min-w-0">
          <div className="text-sm text-gray-600 dark:text-gray-400 truncate">
            {recordingState === "recording" && !transcript && (
              <span className="animate-pulse">Listening...</span>
            )}
            {transcript && (
              <span className="italic">&quot;{transcript}&quot;</span>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="text-sm text-red-500 dark:text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}
