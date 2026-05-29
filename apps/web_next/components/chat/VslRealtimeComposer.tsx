"use client";

/**
 * `VslRealtimeComposer` — Realtime VSL recognition composer.
 *
 * Luồng:
 *   1. User bấm "Mở camera" → requestCamera + init VslRecognitionService.
 *   2. Service chạy MediaPipe HandLandmarker + Bi-LSTM inference liên tục.
 *   3. Khi nhận diện được ký hiệu (confidence đủ cao), hiển thị text realtime.
 *   4. User xác nhận → gửi text vào chat như input bình thường.
 *
 * Khác với SignComposer (record → Gemini):
 *   - Realtime, không cần bấm stop.
 *   - On-device (không gọi API), nhanh hơn, offline-capable.
 *   - Dùng model Bi-LSTM đã train (10 classes y tế VSL).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { VslRecognitionService, VSL_LABELS } from "@/lib/vsl/VslRecognitionService";

type Props = {
  elderly?: boolean;
  isSending: boolean;
  onSend: (message: string) => void;
};

type RecognizedSign = {
  label: string;
  confidence: number;
  timestamp: number;
};

export function VslRealtimeComposer({ elderly = false, isSending, onSend }: Props) {
  const [phase, setPhase] = useState<"closed" | "initializing" | "active" | "error">("closed");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [recognizedSigns, setRecognizedSigns] = useState<RecognizedSign[]>([]);
  const [currentSign, setCurrentSign] = useState<string | null>(null);
  const [composedText, setComposedText] = useState("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const serviceRef = useRef<VslRecognitionService | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  function cleanup() {
    if (serviceRef.current) {
      serviceRef.current.destroy();
      serviceRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }

  /**
   * Đợi `<video>` element được mount vào DOM. Cần thiết vì khi chuyển từ
   * phase "closed" → "initializing", React chưa kịp render <video> nên
   * `videoRef.current` còn `null`. Ta poll ref tối đa ~2s.
   */
  async function waitForVideoElement(timeoutMs = 2000): Promise<HTMLVideoElement> {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (videoRef.current) return videoRef.current;
      // Yield một frame để React commit
      await new Promise((r) => requestAnimationFrame(() => r(null)));
    }
    throw new Error("Không thể khởi tạo khung hình camera. Vui lòng thử lại.");
  }

  async function openCamera() {
    setErrorMessage(null);
    setPhase("initializing");

    try {
      // Request camera — 1280×720 cho FOV rộng hơn (tránh cảm giác "zoom-in"
      // chật chội) + chất lượng landmark tốt hơn cho khuôn mặt nhỏ.
      // Browser sẽ chọn resolution gần nhất camera hỗ trợ.
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      streamRef.current = stream;

      // Bind to video element — đợi DOM mount xong (xem `waitForVideoElement`)
      const videoEl = await waitForVideoElement();
      videoEl.srcObject = stream;
      await videoEl.play();

      // Init recognition service
      const service = new VslRecognitionService();
      await service.init(videoEl, canvasRef.current ?? undefined);
      serviceRef.current = service;

      // Listen for results
      service.onResult((label: string, confidence: number) => {
        const sign: RecognizedSign = { label, confidence, timestamp: Date.now() };
        setCurrentSign(label);
        setRecognizedSigns((prev) => [...prev, sign]);
        // Auto-append to composed text
        setComposedText((prev) => {
          if (prev.length === 0) return label;
          return prev + " " + label;
        });
      });

      // Start recognition
      service.start();
      setPhase("active");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Không thể khởi tạo camera.";
      setErrorMessage(msg);
      setPhase("error");
      cleanup();
    }
  }

  function closeCamera() {
    cleanup();
    setPhase("closed");
    setCurrentSign(null);
  }

  function handleSend() {
    if (!composedText.trim() || isSending) return;
    onSend(composedText.trim());
    setComposedText("");
    setRecognizedSigns([]);
    setCurrentSign(null);
  }

  function handleClear() {
    setComposedText("");
    setRecognizedSigns([]);
    setCurrentSign(null);
  }

  function handleEditText(e: React.ChangeEvent<HTMLInputElement>) {
    setComposedText(e.target.value);
  }

  const fontSize = elderly ? "text-[16px]" : "text-[13px]";
  const btnSize = elderly ? "px-5 py-3 text-[15px]" : "px-3 py-2 text-[13px]";

  // ─── Closed state ───
  if (phase === "closed") {
    return (
      <div className="flex flex-col items-center gap-3 p-4">
        <button
          type="button"
          onClick={openCamera}
          className={`rounded-xl bg-teal-600 font-bold text-white shadow-md hover:bg-teal-700 transition-colors ${btnSize}`}
          aria-label="Mở camera nhận diện ngôn ngữ ký hiệu"
        >
          📷 Mở camera ký hiệu (Realtime)
        </button>
        {errorMessage && (
          <p className="text-red-400 text-[12px] text-center" role="alert">{errorMessage}</p>
        )}
      </div>
    );
  }

  // ─── Error state ───
  if (phase === "error") {
    return (
      <div className="flex flex-col items-center gap-3 p-4">
        <p className="text-red-400 text-[13px] text-center" role="alert">
          {errorMessage || "Lỗi không xác định."}
        </p>
        <button
          type="button"
          onClick={() => { setPhase("closed"); setErrorMessage(null); }}
          className={`rounded-xl bg-slate-600 font-bold text-white ${btnSize}`}
        >
          Thử lại
        </button>
      </div>
    );
  }

  // ─── Initializing & Active states ───
  // <video> phải được mount ngay khi bước vào "initializing" để
  // `videoRef.current` available trước khi `openCamera()` truy cập.
  const isInitializing = phase === "initializing";
  return (
    <div className="flex flex-col gap-3 p-3">
      {/* Camera + Landmark overlay */}
      <div className="relative aspect-video max-h-[360px] overflow-hidden rounded-xl bg-black">
        <video
          ref={videoRef}
          muted
          playsInline
          className="absolute inset-0 h-full w-full object-cover mirror"
          style={{ transform: "scaleX(-1)" }}
          aria-label="Camera preview cho nhận diện ký hiệu"
        />
        {/*
          Canvas DÙNG `object-cover` GIỐNG video — cả hai layer crop đồng
          bộ theo cùng aspect ratio. Canvas internal resolution được service
          set = video native (1280×720) nên landmark normalized [0..1]
          mapping chính xác sang pixel video → khi CSS crop, chấm vẫn dính
          đúng vị trí pixel video bên dưới.
        */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 h-full w-full object-cover pointer-events-none"
          style={{ transform: "scaleX(-1)" }}
          aria-hidden="true"
        />

        {isInitializing && (
          <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/60">
            <span className="animate-spin h-4 w-4 border-2 border-teal-300 border-t-transparent rounded-full" />
            <span className={`text-white ${fontSize}`}>Đang khởi tạo camera & model...</span>
          </div>
        )}

        {/* Current recognition badge */}
        {!isInitializing && currentSign && (
          <div className="absolute top-3 left-3 rounded-xl bg-teal-500/90 px-3 py-1.5 shadow-lg">
            <span className="font-bold text-white text-[14px]">
              ✋ {currentSign}
            </span>
          </div>
        )}

        {/* Status indicator */}
        {!isInitializing && (
          <div className="absolute bottom-3 right-3 flex items-center gap-1.5 rounded-pill bg-black/70 px-2.5 py-1">
            <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-[11px] font-bold text-green-200">Đang nhận diện</span>
          </div>
        )}
      </div>

      {/* Recognized signs history */}
      {!isInitializing && recognizedSigns.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {recognizedSigns.slice(-10).map((sign, idx) => (
            <span
              key={`${sign.timestamp}-${idx}`}
              className="rounded-pill bg-teal-100 px-2 py-0.5 text-[11px] font-semibold text-teal-800"
            >
              {sign.label} ({sign.confidence}%)
            </span>
          ))}
        </div>
      )}

      {/* Composed text input (editable) */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={composedText}
          onChange={handleEditText}
          placeholder="Ký hiệu sẽ xuất hiện ở đây..."
          disabled={isInitializing}
          className={`flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 ${fontSize} text-ink-900 placeholder:text-ink-400 focus:border-teal-500 focus:outline-none disabled:opacity-50`}
          aria-label="Văn bản nhận diện từ ký hiệu"
        />
        {composedText && !isInitializing && (
          <button
            type="button"
            onClick={handleClear}
            className="rounded-lg bg-slate-200 px-2 py-1.5 text-[12px] font-bold text-slate-600 hover:bg-slate-300"
            aria-label="Xóa văn bản"
          >
            ✕
          </button>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleSend}
          disabled={isInitializing || !composedText.trim() || isSending}
          className={`flex-1 rounded-xl bg-teal-600 font-bold text-white shadow-md hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${btnSize}`}
          aria-label="Gửi tin nhắn"
        >
          {isSending ? "Đang gửi..." : "Gửi"}
        </button>
        <button
          type="button"
          onClick={closeCamera}
          className={`rounded-xl bg-red-500/80 font-bold text-white hover:bg-red-600 transition-colors ${btnSize}`}
          aria-label="Đóng camera"
        >
          Đóng
        </button>
      </div>
    </div>
  );
}
