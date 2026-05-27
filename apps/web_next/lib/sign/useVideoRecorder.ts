"use client";

/**
 * `lib/sign/useVideoRecorder.ts` — React hook gói gọn `MediaRecorder`
 * để dùng trong sign-mode composer.
 *
 * Lifecycle:
 *   1. `requestCamera()` — xin quyền camera, tạo `MediaStream` (preview).
 *   2. `start()` — bắt đầu ghi vào buffer, trả `null` nếu chưa có stream.
 *   3. `stop()` — dừng ghi và RESOLVE 1 `Blob` (webm/vp9 hoặc mp4 tùy
 *      browser). Có timeout cứng `maxDurationMs` để tránh blob quá lớn.
 *   4. `releaseCamera()` — tắt tracks, giải phóng đèn camera.
 *
 * Trả về `MediaStream` để component có thể bind vào `<video srcObject>`
 * cho preview self-view trong khi record.
 *
 * Ghi chú browser:
 *   - Chrome/Edge: `video/webm;codecs=vp9,opus` — nhỏ + chất lượng tốt.
 *   - Safari: chưa hỗ trợ webm → fallback `video/mp4`.
 *   - Firefox: `video/webm;codecs=vp8,opus`.
 */

import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// MIME selection — pick what the browser actually supports.
// ---------------------------------------------------------------------------

const PREFERRED_MIME_TYPES = [
  "video/webm;codecs=vp9,opus",
  "video/webm;codecs=vp8,opus",
  "video/webm",
  "video/mp4",
];

function pickMimeType(): string | undefined {
  if (typeof MediaRecorder === "undefined") return undefined;
  for (const type of PREFERRED_MIME_TYPES) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return undefined;
}

// ---------------------------------------------------------------------------
// Hook types
// ---------------------------------------------------------------------------

export type RecorderStatus =
  | "idle"
  | "requesting"
  | "ready"
  | "recording"
  | "stopping"
  | "error";

export interface UseVideoRecorderOptions {
  /** Tự dừng sau X ms để chống user quên bấm stop. Mặc định 15s. */
  maxDurationMs?: number;
  /** Bitrate video. Mặc định 1.5 Mbps — đủ cho VSL recognition. */
  videoBitsPerSecond?: number;
}

export interface UseVideoRecorder {
  status: RecorderStatus;
  error: string | null;
  /** Stream để bind vào <video> preview. */
  stream: MediaStream | null;
  /** True khi đang record. */
  isRecording: boolean;
  /** Số ms đã record (cập nhật mỗi 250ms khi đang record). */
  elapsedMs: number;
  /** Mở camera; phải gọi trước start(). */
  requestCamera(): Promise<void>;
  /** Bắt đầu record. */
  start(): void;
  /** Dừng record và trả Blob. Resolve null nếu chưa từng record. */
  stop(): Promise<Blob | null>;
  /** Tắt camera, dọn tracks. Tự gọi trên unmount. */
  releaseCamera(): void;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useVideoRecorder(
  opts: UseVideoRecorderOptions = {},
): UseVideoRecorder {
  const { maxDurationMs = 15_000, videoBitsPerSecond = 1_500_000 } = opts;

  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [elapsedMs, setElapsedMs] = useState(0);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const stopResolverRef = useRef<((blob: Blob) => void) | null>(null);
  const startedAtRef = useRef<number>(0);
  const tickIntervalRef = useRef<number | null>(null);
  const autoStopTimerRef = useRef<number | null>(null);

  // ─── Camera management ────────────────────────────────────────────────

  const requestCamera = useCallback(async () => {
    setError(null);
    setStatus("requesting");
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("Trình duyệt không hỗ trợ camera.");
      }
      const ms = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      setStream(ms);
      setStatus("ready");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Không mở được camera.";
      setError(msg);
      setStatus("error");
    }
  }, []);

  const releaseCamera = useCallback(() => {
    // Dừng auto-stop + tick.
    if (tickIntervalRef.current !== null) {
      window.clearInterval(tickIntervalRef.current);
      tickIntervalRef.current = null;
    }
    if (autoStopTimerRef.current !== null) {
      window.clearTimeout(autoStopTimerRef.current);
      autoStopTimerRef.current = null;
    }

    // Dừng recorder nếu còn chạy.
    const rec = recorderRef.current;
    if (rec && rec.state !== "inactive") {
      try {
        rec.stop();
      } catch {
        // ignore — đã ở state cuối.
      }
    }
    recorderRef.current = null;

    // Tắt tracks.
    setStream((current) => {
      current?.getTracks().forEach((t) => t.stop());
      return null;
    });

    chunksRef.current = [];
    stopResolverRef.current = null;
    setElapsedMs(0);
    setStatus("idle");
  }, []);

  // ─── Recording ────────────────────────────────────────────────────────

  const start = useCallback(() => {
    if (!stream) {
      setError("Camera chưa sẵn sàng.");
      return;
    }
    if (status === "recording") return;

    const mimeType = pickMimeType();
    if (!mimeType) {
      setError("Trình duyệt không hỗ trợ ghi video.");
      setStatus("error");
      return;
    }

    chunksRef.current = [];
    let recorder: MediaRecorder;
    try {
      recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Không tạo được recorder.";
      setError(msg);
      setStatus("error");
      return;
    }

    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: mimeType });
      chunksRef.current = [];
      const resolver = stopResolverRef.current;
      stopResolverRef.current = null;
      if (resolver) resolver(blob);
      setStatus(stream ? "ready" : "idle");
    };

    recorder.onerror = (event) => {
      // MediaRecorder errors có shape { error: DOMException } trong spec.
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const e = (event as any).error;
      const msg = e instanceof Error ? e.message : "Lỗi khi ghi video.";
      setError(msg);
      setStatus("error");
    };

    recorderRef.current = recorder;
    startedAtRef.current = performance.now();
    recorder.start(250); // emit chunks mỗi 250ms để có data nếu auto-stop sớm
    setStatus("recording");
    setElapsedMs(0);

    // Tick để UI hiển thị thời lượng.
    tickIntervalRef.current = window.setInterval(() => {
      setElapsedMs(performance.now() - startedAtRef.current);
    }, 100);

    // Auto-stop khi đạt max duration.
    autoStopTimerRef.current = window.setTimeout(() => {
      if (recorderRef.current?.state === "recording") {
        try {
          recorderRef.current.stop();
        } catch {
          // ignore.
        }
      }
    }, maxDurationMs);
  }, [stream, status, maxDurationMs, videoBitsPerSecond]);

  const stop = useCallback((): Promise<Blob | null> => {
    const rec = recorderRef.current;
    if (!rec || rec.state === "inactive") {
      return Promise.resolve(null);
    }
    setStatus("stopping");
    if (tickIntervalRef.current !== null) {
      window.clearInterval(tickIntervalRef.current);
      tickIntervalRef.current = null;
    }
    if (autoStopTimerRef.current !== null) {
      window.clearTimeout(autoStopTimerRef.current);
      autoStopTimerRef.current = null;
    }

    return new Promise<Blob | null>((resolve) => {
      stopResolverRef.current = resolve;
      try {
        rec.stop();
      } catch {
        resolve(null);
      }
    });
  }, []);

  // ─── Cleanup on unmount ───────────────────────────────────────────────

  useEffect(() => {
    return () => {
      releaseCamera();
    };
    // releaseCamera có deps ổn định (useCallback []), nhưng để rõ ràng:
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    status,
    error,
    stream,
    isRecording: status === "recording",
    elapsedMs,
    requestCamera,
    start,
    stop,
    releaseCamera,
  };
}
