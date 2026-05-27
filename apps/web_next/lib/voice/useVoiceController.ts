"use client";

/**
 * useVoiceController — bao boc useSpeechRecognition + useTextToSpeech
 * voi state machine: idle -> wake -> command -> executing -> wake.
 *
 * Barge-in: trong mode `executing` mà TTS đang nói, nếu STT phát hiện
 * speech (onspeechstart) thì stop TTS, abort STT cũ, chuyển sang `command`
 * và start STT mới — cho phép user ngắt giữa chừng.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useTextToSpeech } from "../hooks/useTextToSpeech";
import {
  containsWakeWord,
  matchIntent,
  stripWakeWord,
  type IntentMatch,
} from "./intents";
import { correct } from "./transcriptCorrector";

export type ControllerMode = "off" | "wake" | "command" | "executing";

export interface VoiceControllerHandlers {
  onIntent: (intent: IntentMatch) => string;
  onClose?: () => void;
}

export interface VoiceControllerState {
  mode: ControllerMode;
  transcript: string;
  lastReply: string;
  lastCommand: string;
  isSupported: boolean;
  error: string | null;
  start: () => void;
  stop: () => void;
  beginCommand: () => void;
  /** Cho phep executor goi TTS (vd: doc trang / nhac lai). */
  speak: (text: string) => void;
}

export function useVoiceController(handlers: VoiceControllerHandlers): VoiceControllerState {
  const [mode, setMode] = useState<ControllerMode>("off");
  const [lastReply, setLastReply] = useState("");
  const [lastCommand, setLastCommand] = useState("");
  const modeRef = useRef<ControllerMode>("off");
  const handledRef = useRef(false);

  // Tham chiếu được gắn sau khi tạo hooks bên dưới (forward ref pattern)
  // để callback `onSpeechStart` luôn dùng instance mới nhất của tts/speech.
  const ttsRef = useRef<ReturnType<typeof useTextToSpeech> | null>(null);
  const speechRef = useRef<ReturnType<typeof useSpeechRecognition> | null>(null);

  /**
   * Barge-in handler: được gọi từ STT khi phát hiện user bắt đầu nói thật
   * (onspeechstart). Yêu cầu: chỉ kích hoạt nếu đang `executing` + TTS speaking.
   */
  const handleSpeechStart = useCallback(() => {
    if (modeRef.current !== "executing") return;
    const tts = ttsRef.current;
    const speech = speechRef.current;
    if (!tts || !speech) return;
    if (!tts.isSpeaking) return;

    // 1) Dừng TTS ngay (< 100ms)
    tts.stop();
    // 2) Abort phiên STT hiện tại để clear transcript đã ghi nhận
    speech.stop();
    // 3) Sang mode command, start phiên mới (< 200ms)
    setTimeout(() => {
      handledRef.current = false;
      speech.resetTranscript();
      modeRef.current = "command";
      setMode("command");
      speech.start();
    }, 30);
  }, []);

  const speech = useSpeechRecognition({
    lang: "vi-VN",
    interimResults: true,
    continuous: true,
    silenceTimeoutMs: 1200,
    onSpeechStart: handleSpeechStart,
  });
  const tts = useTextToSpeech({ lang: "vi-VN", rate: 0.95 });

  // Gắn ref mỗi render để barge-in handler luôn thấy state mới
  ttsRef.current = tts;
  speechRef.current = speech;

  const setModeBoth = useCallback((m: ControllerMode) => {
    modeRef.current = m;
    setMode(m);
  }, []);

  const goWake = useCallback(() => {
    handledRef.current = false;
    speech.resetTranscript();
    setModeBoth("wake");
    if (!speech.isListening) speech.start();
  }, [setModeBoth, speech]);

  const goCommand = useCallback(() => {
    handledRef.current = false;
    speech.resetTranscript();
    setModeBoth("command");
    if (!speech.isListening) speech.start();
  }, [setModeBoth, speech]);

  const start = useCallback(() => {
    if (modeRef.current !== "off") return;
    goWake();
  }, [goWake]);

  const stop = useCallback(() => {
    setModeBoth("off");
    speech.stop();
    tts.stop();
  }, [setModeBoth, speech, tts]);

  const beginCommand = useCallback(() => {
    speech.stop();
    setTimeout(() => goCommand(), 30);
  }, [goCommand, speech]);

  /** API public: TTS doc 1 cau (vd: read_page / repeat). */
  const speak = useCallback((text: string) => {
    if (!text) return;
    tts.speak(text);
  }, [tts]);

  // Wake mode: im lặng (isListening = false) và có transcript -> xử lý lệnh trực tiếp không cần wake word!
  useEffect(() => {
    if (modeRef.current !== "wake") return;
    if (handledRef.current) return;
    if (speech.isListening) return; // chờ im lặng
    if (!speech.transcript.trim()) return;

    handledRef.current = true;
    let text = speech.transcript.trim();
    // Tự động loại bỏ wake word nếu người dùng có nói để tăng độ chính xác so khớp
    if (containsWakeWord(text)) {
      text = stripWakeWord(text);
    }
    // Sửa lỗi nhận dạng phổ biến (vd: "cũng xuống" → "cuộn xuống").
    text = correct(text);
    
    if (!text) {
      // Nếu chỉ nói "bác sĩ ơi" rồi im lặng
      const greeting = "Mình đang nghe.";
      setLastReply(greeting);
      tts.speak(greeting);
      speech.stop();
      setTimeout(() => goCommand(), 200);
      return;
    }

    setLastCommand(text);
    setModeBoth("executing");
    const intent = matchIntent(text);
    const reply = handlers.onIntent(intent);
    setLastReply(reply);
    if (reply) {
      tts.speak(reply);
      // Barge-in: trong khi TTS đang đọc, vẫn cần STT lắng nghe để
      // bắt sự kiện onspeechstart (user ngắt). Restart STT sau 250ms
      // (đủ để tts.speak() set isSpeaking=true và tránh STT bắt lại
      // chính giọng TTS).
      handledRef.current = true; // không cho effect handle lại
      speech.resetTranscript();
      setTimeout(() => {
        if (modeRef.current === "executing" && !speech.isListening) {
          speech.start();
        }
      }, 250);
    }
  }, [speech.isListening, speech.transcript, handlers, tts, setModeBoth, goCommand]);

  // Command mode: STT dung -> xu ly final
  useEffect(() => {
    if (modeRef.current !== "command") return;
    if (handledRef.current) return;
    if (speech.isListening) return;
    if (!speech.transcript.trim()) {
      goWake();
      return;
    }
    handledRef.current = true;
    const text = correct(speech.transcript.trim());
    setLastCommand(text);
    setModeBoth("executing");
    const intent = matchIntent(text);
    const reply = handlers.onIntent(intent);
    setLastReply(reply);
    if (reply) tts.speak(reply);
  }, [speech.isListening, speech.transcript, handlers, tts, setModeBoth, goWake]);

  // Sau khi TTS xong & dang executing -> wake
  useEffect(() => {
    if (modeRef.current !== "executing") return;
    if (tts.isSpeaking) return;
    const t = setTimeout(() => {
      if (modeRef.current === "executing") goWake();
    }, 200);
    return () => clearTimeout(t);
  }, [tts.isSpeaking, goWake]);

  // Auto-restart STT khi mode wake
  useEffect(() => {
    if (modeRef.current !== "wake") return;
    if (speech.isListening) return;
    const t = setTimeout(() => {
      if (modeRef.current === "wake" && !speech.isListening) {
        speech.start();
      }
    }, 300);
    return () => clearTimeout(t);
  }, [speech.isListening, speech]);

  useEffect(() => {
    return () => {
      speech.stop();
      tts.stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    mode,
    transcript: speech.transcript,
    lastReply,
    lastCommand,
    isSupported: speech.isSupported,
    error: speech.error,
    start,
    stop,
    beginCommand,
    speak,
  };
}
