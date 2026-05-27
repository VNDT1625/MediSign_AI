"use client";

/**
 * `useSpeechRecognition` — Custom hook wrapping the Web Speech API.
 *
 * Features:
 * - Real speech-to-text using browser's SpeechRecognition
 * - Vietnamese language support (vi-VN)
 * - Interim (partial) results for live transcript display
 * - Auto-stop after configurable silence timeout
 * - Error handling with user-friendly messages
 * - Browser compatibility detection
 *
 * Usage:
 *   const { transcript, isListening, start, stop, isSupported, error } = useSpeechRecognition();
 */

import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SpeechRecognitionOptions {
  /** BCP-47 language tag. Default: "vi-VN" */
  lang?: string;
  /** Show interim (partial) results while speaking. Default: true */
  interimResults?: boolean;
  /** Auto-stop after this many ms of silence. Default: 3000 */
  silenceTimeoutMs?: number;
  /** Continuous recognition (keeps listening after pause). Default: true */
  continuous?: boolean;
  /**
   * Callback fired when STT begins receiving audio (browser `onstart` event).
   * Used by `useVoiceController` to detect barge-in: if TTS is currently
   * speaking when the user starts talking, the controller can stop TTS
   * and switch to command mode.
   *
   * The callback runs synchronously after `isListening` is set to `true`.
   */
  onSpeechStart?: () => void;
}

export interface SpeechRecognitionState {
  /** Current transcript text (interim + final combined) */
  transcript: string;
  /** Final confirmed transcript (only finalized segments) */
  finalTranscript: string;
  /** Whether the recognizer is actively listening */
  isListening: boolean;
  /** Whether the browser supports Web Speech API */
  isSupported: boolean;
  /** Human-readable error message, null if no error */
  error: string | null;
  /** Confidence score of last final result (0-1) */
  confidence: number;
  /** Start listening */
  start: () => void;
  /** Stop listening and return final transcript */
  stop: () => string;
  /** Reset transcript without stopping */
  resetTranscript: () => void;
}

// ---------------------------------------------------------------------------
// Browser API types (not all browsers ship these in TS lib)
// ---------------------------------------------------------------------------

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

// ---------------------------------------------------------------------------
// Helper: get SpeechRecognition constructor
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type SpeechRecognitionCtor = new () => any;

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = window as any;
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useSpeechRecognition(
  options: SpeechRecognitionOptions = {}
): SpeechRecognitionState {
  const {
    lang = "vi-VN",
    interimResults = true,
    silenceTimeoutMs = 3000,
    continuous = true,
    onSpeechStart,
  } = options;

  const [transcript, setTranscript] = useState("");
  const [finalTranscript, setFinalTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0);
  // Initialize false to match server render; set to actual value after mount
  // to avoid SSR/client hydration mismatch.
  const [isSupported, setIsSupported] = useState(false);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);
  const silenceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isStoppingRef = useRef(false);
  // Hold the latest `onSpeechStart` in a ref so the callback fires the most
  // recent function passed by the consumer without forcing `start` to be
  // recreated on every render.
  const onSpeechStartRef = useRef<(() => void) | undefined>(onSpeechStart);
  useEffect(() => {
    onSpeechStartRef.current = onSpeechStart;
  }, [onSpeechStart]);

  useEffect(() => {
    setIsSupported(getSpeechRecognition() !== null);
  }, []);

  // Clear silence timer
  const clearSilenceTimer = useCallback(() => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  }, []);

  // Start silence timer — auto-stop after silence
  const startSilenceTimer = useCallback(() => {
    clearSilenceTimer();
    silenceTimerRef.current = setTimeout(() => {
      if (recognitionRef.current && !isStoppingRef.current) {
        isStoppingRef.current = true;
        recognitionRef.current.stop();
      }
    }, silenceTimeoutMs);
  }, [clearSilenceTimer, silenceTimeoutMs]);

  // Start recognition
  const start = useCallback(() => {
    const SpeechRecognitionCtor = getSpeechRecognition();
    if (!SpeechRecognitionCtor) {
      setError("Trình duyệt không hỗ trợ nhận diện giọng nói. Hãy dùng Chrome hoặc Edge.");
      return;
    }

    // Clean up previous instance
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch { /* ignore */ }
    }

    setError(null);
    setTranscript("");
    setFinalTranscript("");
    setConfidence(0);
    isStoppingRef.current = false;

    const recognition = new SpeechRecognitionCtor();
    recognition.lang = lang;
    recognition.interimResults = interimResults;
    recognition.continuous = continuous;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      startSilenceTimer();
    };

    /**
     * `onspeechstart` fires when the speech recognizer detects that audio
     * is, in fact, speech (not background noise). This is the correct event
     * for barge-in: it means the user has actually started speaking, not just
     * that the microphone has been turned on.
     *
     * The earlier wiring used `onstart` (recognition session start), which
     * fires immediately on `start()` — not useful for detecting barge-in.
     */
    recognition.onspeechstart = () => {
      try {
        onSpeechStartRef.current?.();
      } catch (err) {
        // Don't let consumer errors break recognition flow.
        // eslint-disable-next-line no-console
        console.warn("[useSpeechRecognition] onSpeechStart callback threw:", err);
      }
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      clearSilenceTimer();
      startSilenceTimer();

      let interim = "";
      let final = "";

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;
        if (result.isFinal) {
          final += text;
          setConfidence(result[0].confidence);
        } else {
          interim += text;
        }
      }

      setFinalTranscript(final);
      setTranscript(final + interim);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      clearSilenceTimer();

      const errorMessages: Record<string, string> = {
        "not-allowed": "Bạn chưa cấp quyền microphone. Hãy cho phép truy cập micro trong cài đặt trình duyệt.",
        "no-speech": "", // Im lặng/ồn — không hiện lỗi, để onend tự xử lý + caller restart
        "audio-capture": "Không tìm thấy microphone. Hãy kiểm tra thiết bị.",
        "network": "Lỗi mạng. Kiểm tra kết nối internet.",
        "aborted": "", // User-initiated, not an error
        "service-not-available": "Dịch vụ nhận diện giọng nói không khả dụng. Thử lại sau.",
      };

      const msg = errorMessages[event.error] ?? `Lỗi nhận diện giọng nói: ${event.error}`;
      if (msg) setError(msg);

      // Set isListening=false cho mọi error để caller (useVoiceController)
      // có thể detect và auto-restart. Trước đây giữ true cho `no-speech`
      // gây kẹt session khi có ambient noise dài.
      setIsListening(false);
    };

    recognition.onend = () => {
      clearSilenceTimer();
      setIsListening(false);
      isStoppingRef.current = false;
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      setError("Không thể khởi động nhận diện giọng nói. Thử tải lại trang.");
      setIsListening(false);
    }
  }, [lang, interimResults, continuous, startSilenceTimer, clearSilenceTimer]);

  // Stop recognition and return final transcript
  const stop = useCallback((): string => {
    clearSilenceTimer();
    if (recognitionRef.current && !isStoppingRef.current) {
      isStoppingRef.current = true;
      recognitionRef.current.stop();
    }
    setIsListening(false);
    return transcript;
  }, [clearSilenceTimer, transcript]);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript("");
    setFinalTranscript("");
    setConfidence(0);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearSilenceTimer();
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch { /* ignore */ }
      }
    };
  }, [clearSilenceTimer]);

  return {
    transcript,
    finalTranscript,
    isListening,
    isSupported,
    error,
    confidence,
    start,
    stop,
    resetTranscript,
  };
}
