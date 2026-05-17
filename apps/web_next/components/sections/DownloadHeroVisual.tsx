"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Hero visual cho trang Download.
 * Hiệu ứng: parallax theo chuột (nhẹ), float chậm, glow ring nhấp nháy,
 * blob trôi nền, message bubbles xuất hiện luân phiên.
 * Tất cả đều bị tắt khi user bật `prefers-reduced-motion`.
 */
export function DownloadHeroVisual() {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [chatStep, setChatStep] = useState(0);

  useEffect(() => {
    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;

    // Cycle the chat bubbles to create life
    const id = window.setInterval(() => {
      setChatStep((s) => (s + 1) % 3);
    }, 1800);
    return () => window.clearInterval(id);
  }, []);

  function handleMove(e: React.MouseEvent<HTMLDivElement>) {
    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    const el = wrapRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const cx = (e.clientX - r.left) / r.width - 0.5;
    const cy = (e.clientY - r.top) / r.height - 0.5;
    // Limit max tilt to ~6deg/4deg for accessibility comfort
    setTilt({ x: cy * -4, y: cx * 6 });
  }
  function handleLeave() {
    setTilt({ x: 0, y: 0 });
  }

  return (
    <div
      ref={wrapRef}
      role="img"
      aria-label="Mockup MediSign AI trên điện thoại với bác sĩ AI đang trò chuyện"
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      className="relative mx-auto h-[480px] w-full max-w-[480px]"
      style={{ perspective: "1200px" }}
    >
      {/* Floating brand blobs in the back */}
      <div
        aria-hidden="true"
        className="anim-blob-drift absolute -left-6 top-2 h-40 w-40 rounded-full bg-brand/15 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="anim-blob-drift absolute right-0 bottom-2 h-44 w-44 rounded-full bg-accent/15 blur-3xl"
        style={{ animationDelay: "-4s" }}
      />

      {/* Soft gradient backdrop */}
      <div
        aria-hidden="true"
        className="absolute inset-6 rounded-[36px] bg-gradient-to-br from-brand-50 via-white to-accent/15 shadow-card"
      />
      <div
        aria-hidden="true"
        className="absolute inset-6 rounded-[36px] ring-1 ring-inset ring-white/60"
      />

      {/* Phone mockup — chính giữa, có parallax + float + glow ring */}
      <div
        className="anim-float-slow absolute left-1/2 top-12 w-[218px] -translate-x-1/2"
        style={{
          transform: `translateX(-50%) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
          transformStyle: "preserve-3d",
          transition: "transform 220ms cubic-bezier(0.22,1,0.36,1)",
        }}
      >
        <div className="anim-glow-ring rounded-[36px]">
          <div className="rounded-[32px] border-[8px] border-ink-900 bg-white shadow-card">
            {/* Notch */}
            <div className="mx-auto h-1.5 w-14 rounded-full bg-ink-700/60" />
            <div className="aspect-[9/19] overflow-hidden rounded-[20px] bg-gradient-to-b from-brand-50 to-white">
              <div className="space-y-2.5 p-3">
                <div className="flex items-center justify-between">
                  <span className="rounded-pill bg-white px-2.5 py-1 text-[10px] font-semibold text-brand-700 shadow-soft">
                    MediSign AI
                  </span>
                  <span className="grid h-6 w-6 place-items-center rounded-full bg-white text-brand-700 shadow-soft">
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <circle
                        cx="12"
                        cy="8"
                        r="3"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                      <path
                        d="M5 20c1-4 4-6 7-6s6 2 7 6"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  </span>
                </div>

                {/* Bubble 1 — user (luôn hiện) */}
                <div className="rounded-card bg-white p-2.5 shadow-soft">
                  <div className="h-1.5 w-3/4 rounded-pill bg-ink-200" />
                  <div className="mt-1.5 h-1.5 w-1/2 rounded-pill bg-ink-200" />
                </div>

                {/* Bubble 2 — bot (xuất hiện ở step >= 1) */}
                <div
                  className={`rounded-card bg-brand p-2.5 transition-all duration-500 ${
                    chatStep >= 1
                      ? "translate-y-0 opacity-100"
                      : "translate-y-2 opacity-0"
                  }`}
                >
                  <div className="h-1.5 w-3/4 rounded-pill bg-white/70" />
                  <div className="mt-1.5 h-1.5 w-2/3 rounded-pill bg-white/70" />
                </div>

                {/* Bubble 3 — user follow-up (xuất hiện ở step >= 2) */}
                <div
                  className={`rounded-card bg-white p-2.5 shadow-soft transition-all duration-500 ${
                    chatStep >= 2
                      ? "translate-y-0 opacity-100"
                      : "translate-y-2 opacity-0"
                  }`}
                >
                  <div className="h-1.5 w-1/2 rounded-pill bg-ink-200" />
                  <div className="mt-1.5 h-1.5 w-3/5 rounded-pill bg-ink-200" />
                </div>

                {/* Mic dock — typing dots khi đang chờ bot */}
                <div className="mt-3 flex items-center gap-2 rounded-pill bg-white px-2.5 py-2 shadow-soft">
                  <span className="grid h-7 w-7 flex-none place-items-center rounded-pill bg-accent text-white">
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <rect
                        x="9"
                        y="3"
                        width="6"
                        height="12"
                        rx="3"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                      <path
                        d="M5 11a7 7 0 0 0 14 0M12 18v3"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  </span>
                  <div className="flex flex-1 items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-ink-400 animate-pulse-soft" />
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-ink-400 animate-pulse-soft"
                      style={{ animationDelay: "0.2s" }}
                    />
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-ink-400 animate-pulse-soft"
                      style={{ animationDelay: "0.4s" }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating bubble — top-left */}
      <div
        className="anim-float-tilt absolute left-2 top-4 flex items-center gap-2 rounded-pill bg-white px-3 py-1.5 shadow-card"
        style={{ animationDelay: "-1.2s" }}
      >
        <span className="grid h-6 w-6 place-items-center rounded-full bg-success text-white">
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M5 12l4 4L19 6"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <span className="text-xs font-semibold text-ink-900">Đã đồng bộ</span>
      </div>

      {/* Floating bubble — bottom-right */}
      <div
        className="anim-float-tilt absolute right-2 bottom-12 flex items-center gap-2 rounded-pill bg-white px-3 py-1.5 shadow-card"
        style={{ animationDelay: "-3.6s" }}
      >
        <span className="grid h-6 w-6 place-items-center rounded-full bg-brand text-white">
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M3 12l18-8-8 18-2-8-8-2z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <span className="text-xs font-semibold text-ink-900">Voice tiếng Việt</span>
      </div>

      {/* Floating rating chip — bottom-left, nhấn mạnh trust signal */}
      <div className="absolute left-1 bottom-2 flex items-center gap-2 rounded-pill bg-white px-3 py-1.5 shadow-card anim-badge-pop">
        <span className="flex items-center gap-0.5 text-warn">
          {Array.from({ length: 5 }).map((_, i) => (
            <svg
              key={i}
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M12 2l2.9 6.9L22 10l-5 4.9 1.2 7L12 18.6 5.8 22 7 14.9 2 10l7.1-1.1L12 2z" />
            </svg>
          ))}
        </span>
        <span className="text-xs font-semibold text-ink-900">4.9 / 5</span>
      </div>
    </div>
  );
}
