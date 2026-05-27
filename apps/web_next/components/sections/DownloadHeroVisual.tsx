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
      className="relative mx-auto h-[360px] w-full max-w-[580px] sm:h-[420px] lg:h-[480px]"
      style={{ perspective: "1200px" }}
    >
      {/* Ambient blobs */}
      <div aria-hidden="true" className="anim-blob-drift absolute -left-8 top-0 h-32 w-32 rounded-full bg-brand/10 blur-3xl sm:h-48 sm:w-48" />
      <div aria-hidden="true" className="anim-blob-drift absolute -right-4 bottom-0 h-32 w-32 rounded-full bg-accent/10 blur-3xl sm:h-48 sm:w-48" style={{ animationDelay: "-5s" }} />

      {/* ── Desktop card — gần hơn, chiếm gần hết chiều rộng ── */}
      <div
        aria-hidden="true"
        className="absolute left-0 top-2 w-[88%] overflow-hidden rounded-[16px] shadow-[0_8px_40px_-12px_rgba(15,23,42,0.22)] ring-1 ring-ink-200/60"
        style={{
          transform: `rotateX(${tilt.x * 0.35}deg) rotateY(${tilt.y * 0.35}deg)`,
          transition: "transform 240ms cubic-bezier(0.22,1,0.36,1)",
          zIndex: 1,
        }}
      >
        {/* Title bar */}
        <div className="flex items-center gap-1.5 border-b border-ink-100 bg-white px-3 py-2">
          <span className="h-2.5 w-2.5 rounded-full bg-[#FF5F57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#FEBC2E]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28C840]" />
          <div className="ml-2 flex flex-1 items-center gap-1.5 rounded-full border border-ink-200 bg-ink-50 px-3 py-1">
            {/* Lock icon */}
            <svg width="9" height="9" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="flex-none text-ink-400">
              <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="2"/>
              <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <span className="text-[10.5px] font-medium tracking-tight text-ink-600">medisign.ai</span>
          </div>
        </div>
        {/* Screenshot full width */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/Screenshot%202026-05-17%20184902.png"
          alt="Giao diện ứng dụng MediSign AI trên điện thoại"
          className="block w-full"
          draggable={false}
        />
      </div>

      {/* ── Phone — thon, cao, che góc phải desktop ── */}
      <div
        className="anim-float-slow absolute bottom-0 right-0 w-[100px] sm:w-[115px] lg:w-[130px]"
        style={{
          transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
          transformStyle: "preserve-3d",
          transition: "transform 240ms cubic-bezier(0.22,1,0.36,1)",
          zIndex: 10,
        }}
      >
        <div className="anim-glow-ring rounded-[28px]">
          {/* Frame — border mỏng, bo nhiều = dáng thon */}
          <div className="overflow-hidden rounded-[24px] border-[5px] border-ink-900 bg-white shadow-[0_24px_64px_-16px_rgba(15,23,42,0.40)]">
            {/* Notch bar */}
            <div className="flex justify-center bg-ink-900 pb-1 pt-1">
              <div className="h-[3px] w-8 rounded-full bg-ink-700" />
            </div>
            {/* Screen — tỉ lệ 9:20 = thon hơn 9:19 */}
            <div className="bg-gradient-to-b from-brand-50 to-white px-2.5 pb-3 pt-2.5" style={{ aspectRatio: "9/20" }}>
              {/* App header */}
              <div className="mb-2.5 flex items-center justify-between">
                <span className="text-[9px] font-bold text-ink-900">MediSign AI</span>
                <span className="grid h-5 w-5 place-items-center rounded-full bg-ink-100 text-ink-500">
                  <svg width="9" height="9" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <circle cx="12" cy="8" r="3" stroke="currentColor" strokeWidth="2" />
                    <path d="M5 20c1-4 4-6 7-6s6 2 7 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </span>
              </div>

              {/* Bubble 1 — user */}
              <div className="mb-1.5 rounded-lg bg-white p-2 shadow-soft">
                <div className="h-1 w-3/4 rounded-full bg-ink-200" />
                <div className="mt-1 h-1 w-1/2 rounded-full bg-ink-200" />
              </div>

              {/* Bubble 2 — bot */}
              <div className={`mb-1.5 rounded-lg bg-brand p-2 transition-all duration-500 ${chatStep >= 1 ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"}`}>
                <div className="h-1 w-3/4 rounded-full bg-white/70" />
                <div className="mt-1 h-1 w-2/3 rounded-full bg-white/70" />
              </div>

              {/* Bubble 3 — user */}
              <div className={`mb-2.5 rounded-lg bg-white p-2 shadow-soft transition-all duration-500 ${chatStep >= 2 ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"}`}>
                <div className="h-1 w-1/2 rounded-full bg-ink-200" />
                <div className="mt-1 h-1 w-3/5 rounded-full bg-ink-200" />
              </div>

              {/* Mic bar */}
              <div className="flex items-center gap-1.5 rounded-full bg-white px-2 py-1.5 shadow-soft">
                <span className="grid h-5 w-5 flex-none place-items-center rounded-full bg-accent text-white">
                  <svg width="8" height="8" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <rect x="9" y="3" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="2" />
                    <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </span>
                <div className="flex gap-0.5">
                  <span className="h-1 w-1 rounded-full bg-ink-300 animate-pulse-soft" />
                  <span className="h-1 w-1 rounded-full bg-ink-300 animate-pulse-soft" style={{ animationDelay: "0.2s" }} />
                  <span className="h-1 w-1 rounded-full bg-ink-300 animate-pulse-soft" style={{ animationDelay: "0.4s" }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chip: Đã đồng bộ — overlap góc phải title bar của web card */}
      <div
        className="anim-float-tilt absolute right-[-12px] top-[30px] z-20 hidden items-center gap-2 rounded-full bg-white px-3 py-1.5 shadow-card sm:flex"
        style={{ animationDelay: "-1.2s" }}
      >
        <span className="grid h-5 w-5 place-items-center rounded-full bg-success text-white">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
        <span className="text-xs font-semibold text-ink-900">Đã đồng bộ</span>
      </div>

      {/* Chip: Voice tiếng Việt — sát cạnh trái phone */}
      <div
        className="anim-float-tilt absolute bottom-[100px] right-[100px] z-20 hidden items-center gap-2 rounded-full bg-white px-3 py-1.5 shadow-card sm:bottom-[150px] sm:right-[124px] sm:flex"
        style={{ animationDelay: "-3.6s" }}
      >
        <span className="grid h-5 w-5 place-items-center rounded-full bg-brand text-white">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M3 12l18-8-8 18-2-8-8-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
        <span className="text-xs font-semibold text-ink-900">Voice tiếng Việt</span>
      </div>


    </div>
  );
}
