"use client";

/**
 * `VslSignVideoPlayer` — phát chuỗi clip VSL khớp với câu trả lời của AI.
 *
 * Luồng:
 *   1. `tokenizeForVsl(text)` — tách câu thành segments (video + gap text).
 *   2. Lấy danh sách video entries → phát tuần tự bằng double-buffer
 *      (2 thẻ <video> A/B) để chuyển clip không bị "đen 1 frame".
 *   3. Khi tới clip cuối, DỪNG ở frame cuối cùng (không loop). User có
 *      thể bấm "Phát lại" để chạy lại từ đầu.
 *   4. Phụ đề tiếng Việt (text gốc) hiển thị bên dưới — accessibility cho
 *      cả người không thông thạo VSL và người chỉ muốn đọc.
 *
 * Khi mở rộng dictionary (thêm clip), file này KHÔNG cần đổi.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { tokenizeForVsl, videoSegmentsOnly } from "@/lib/sign/tokenize";
import { intentFromText, type SignIntent } from "./SignAvatar";

type Props = {
  /** Toàn bộ câu trả lời của AI (tiếng Việt). */
  text: string;
  /**
   * Intent suy ra từ `text`. KHÔNG dùng nội bộ ở Phase 1 (chỉ để tương
   * thích với caller cũ trong `ChatMain.tsx`); reserve cho Phase 2 khi
   * tokenizer biết ưu tiên token theo intent (vd "khẩn cấp" lên đầu).
   */
  intent?: SignIntent;
  elderly?: boolean;
};

export function VslSignVideoPlayer({ text, elderly = false }: Props) {
  // ─── Tokenize 1 lần per text ───────────────────────────────────────
  const segments = useMemo(() => tokenizeForVsl(text), [text]);
  const videoEntries = useMemo(() => videoSegmentsOnly(segments), [segments]);

  // ─── State playback ────────────────────────────────────────────────
  const [currentIndex, setCurrentIndex] = useState(0);
  const [activeLayer, setActiveLayer] = useState<0 | 1>(0);
  const [isFinished, setIsFinished] = useState(false);
  const videoARef = useRef<HTMLVideoElement>(null);
  const videoBRef = useRef<HTMLVideoElement>(null);

  // Reset khi text thay đổi (câu AI mới).
  useEffect(() => {
    setCurrentIndex(0);
    setActiveLayer(0);
    setIsFinished(false);
  }, [text]);

  // Load + play active layer mỗi khi đổi index hoặc layer.
  useEffect(() => {
    if (videoEntries.length === 0 || isFinished) return;

    const activeRef = activeLayer === 0 ? videoARef : videoBRef;
    const inactiveRef = activeLayer === 0 ? videoBRef : videoARef;
    const activeEl = activeRef.current;
    const inactiveEl = inactiveRef.current;
    if (!activeEl) return;

    const currentSrc = videoEntries[currentIndex].src;
    if (activeEl.src !== absUrl(currentSrc)) {
      activeEl.src = currentSrc;
    }
    activeEl.currentTime = 0;
    activeEl.play().catch(() => {
      // Autoplay policy — user có thể cần interact trước. Hiển thị fallback
      // bằng nút phát lại; không cần throw.
    });

    // Pre-load clip kế tiếp vào layer kia để chuyển không giật.
    const nextIndex = currentIndex + 1;
    if (inactiveEl && nextIndex < videoEntries.length) {
      const nextSrc = videoEntries[nextIndex].src;
      if (inactiveEl.src !== absUrl(nextSrc)) {
        inactiveEl.src = nextSrc;
        inactiveEl.load();
      }
    }
  }, [activeLayer, currentIndex, videoEntries, isFinished]);

  // Convert "/signs/x.webm" → URL absolute để so sánh với video.src của
  // browser (browser trả absolute). Chỉ chạy ở client.
  function absUrl(path: string): string {
    if (typeof window === "undefined") return path;
    return new URL(path, window.location.origin).toString();
  }

  function handleEnded() {
    if (currentIndex + 1 >= videoEntries.length) {
      setIsFinished(true);
      return;
    }
    setCurrentIndex((i) => i + 1);
    setActiveLayer((l) => (l === 0 ? 1 : 0));
  }

  function handleReplay() {
    setIsFinished(false);
    setCurrentIndex(0);
    setActiveLayer(0);
  }

  if (videoEntries.length === 0) {
    // Không có từ nào trong dictionary → fallback: chỉ hiển thị bubble chữ.
    // Trả null để parent (`MessageRow`) lo render `AiBubble` thay thế.
    return null;
  }

  const currentLabel = videoEntries[currentIndex]?.label ?? "";
  const totalCount = videoEntries.length;

  return (
    <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-slate-950 px-4 py-3 shadow-soft sm:max-w-[640px]">
      {/* ── Stage video ── */}
      <div className="relative aspect-video overflow-hidden rounded-xl bg-black">
        <video
          ref={videoARef}
          muted
          playsInline
          preload="auto"
          onEnded={activeLayer === 0 && !isFinished ? handleEnded : undefined}
          aria-label={`Clip ký hiệu: ${currentLabel}`}
          className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-150 ${
            activeLayer === 0 ? "opacity-100" : "opacity-0"
          }`}
        />
        <video
          ref={videoBRef}
          muted
          playsInline
          preload="auto"
          onEnded={activeLayer === 1 && !isFinished ? handleEnded : undefined}
          aria-hidden="true"
          className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-150 ${
            activeLayer === 1 ? "opacity-100" : "opacity-0"
          }`}
        />

        {/* Caption overlay — từ đang phát */}
        <div className="absolute bottom-3 left-3 right-3 rounded-xl bg-black/70 px-3 py-2 text-center">
          <p className={`font-extrabold text-teal-100 ${elderly ? "text-[18px]" : "text-[15px]"}`}>
            {isFinished ? "✓ Hoàn tất" : currentLabel}
          </p>
        </div>

        {/* Progress bar — số clip còn lại */}
        <div className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-pill bg-black/70 px-2.5 py-1 text-[11px] font-bold text-teal-100">
          <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-teal-300" />
          {Math.min(currentIndex + 1, totalCount)} / {totalCount}
        </div>

        {/* Replay overlay khi xong */}
        {isFinished && (
          <button
            type="button"
            onClick={handleReplay}
            aria-label="Phát lại từ đầu"
            className="absolute inset-0 flex items-center justify-center bg-black/40 text-white transition-opacity hover:bg-black/55 cursor-pointer"
          >
            <span className="flex items-center gap-2 rounded-pill bg-white/90 px-4 py-2 text-[14px] font-bold text-slate-900 shadow-lg">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden>
                <path d="M3 12a9 9 0 1 0 3-6.7" strokeLinecap="round" />
                <path d="M3 4v6h6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Phát lại
            </span>
          </button>
        )}
      </div>

      {/* ── Token pills — highlight clip đang phát ── */}
      <div className="mt-3 flex flex-wrap gap-2">
        {videoEntries.map((entry, idx) => {
          const isActive = !isFinished && idx === currentIndex;
          const isPlayed = isFinished || idx < currentIndex;
          return (
            <span
              key={`${entry.src}-${idx}`}
              className={`rounded-pill px-2.5 py-1 text-[12px] font-bold transition-colors ${
                isActive
                  ? "bg-teal-300 text-slate-950"
                  : isPlayed
                    ? "bg-white/25 text-teal-50"
                    : "bg-white/10 text-teal-100"
              }`}
            >
              {entry.label}
            </span>
          );
        })}
      </div>

      {/* ── Phụ đề toàn câu (subtitle) ── */}
      <p className={`mt-3 leading-relaxed text-teal-50 ${elderly ? "text-[16px]" : "text-[13px]"}`}>
        {text}
      </p>
    </div>
  );
}

// Re-export helper cho callers cũ.
export { intentFromText };
export type { SignIntent };
