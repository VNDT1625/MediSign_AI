"use client";

/**
 * `useTextToSpeech` — Custom hook wrapping the Web Speech Synthesis API.
 *
 * Features:
 * - Text-to-speech with Vietnamese voice support
 * - Play/pause/stop controls
 * - Rate and pitch configuration
 * - Auto-select best Vietnamese voice available
 */

import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface TextToSpeechOptions {
  /** BCP-47 language tag. Default: "vi-VN" */
  lang?: string;
  /** Speech rate (0.1 - 10). Default: 1 */
  rate?: number;
  /** Speech pitch (0 - 2). Default: 1 */
  pitch?: number;
}

export interface TextToSpeechState {
  /** Whether TTS is currently speaking */
  isSpeaking: boolean;
  /** Whether TTS is supported in this browser */
  isSupported: boolean;
  /** Speak the given text */
  speak: (text: string) => void;
  /** Stop speaking */
  stop: () => void;
  /** Pause speaking */
  pause: () => void;
  /** Resume speaking */
  resume: () => void;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useTextToSpeech(
  options: TextToSpeechOptions = {}
): TextToSpeechState {
  const { lang = "vi-VN", rate = 1, pitch = 1 } = options;

  const [isSpeaking, setIsSpeaking] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Initialize false to match server render; set to actual value after mount
  // to avoid SSR/client hydration mismatch.
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported("speechSynthesis" in window);
  }, []);

  // Find best Vietnamese voice
  const getVoice = useCallback((): SpeechSynthesisVoice | null => {
    if (!isSupported) return null;
    const voices = window.speechSynthesis.getVoices();
    // Prefer Vietnamese voice
    const viVoice = voices.find((v) => v.lang.startsWith("vi"));
    if (viVoice) return viVoice;
    // Fallback to default
    return voices.find((v) => v.default) ?? voices[0] ?? null;
  }, [isSupported]);

  const speak = useCallback(
    (text: string) => {
      if (!isSupported || !text.trim()) return;

      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.rate = rate;
      utterance.pitch = pitch;

      const voice = getVoice();
      if (voice) utterance.voice = voice;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    },
    [isSupported, lang, rate, pitch, getVoice]
  );

  const stop = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [isSupported]);

  const pause = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.pause();
  }, [isSupported]);

  const resume = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.resume();
  }, [isSupported]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isSupported) {
        window.speechSynthesis.cancel();
      }
    };
  }, [isSupported]);

  return { isSpeaking, isSupported, speak, stop, pause, resume };
}
