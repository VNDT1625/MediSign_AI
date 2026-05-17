"use client";

// Sidebar trái cho trang Soul Garden (desktop).
// Chứa: branding, nav 7 mục, card "Tưới mát tâm hồn", nút "Trồng cây mới".

import { useState } from "react";

type Section =
  | "overview"
  | "garden"
  | "journal"
  | "exercise"
  | "habits"
  | "music"
  | "insight";

const NAV: { id: Section; label: string; icon: React.ReactNode }[] = [
  { id: "overview", label: "Tổng quan", icon: <DashboardIcon /> },
  { id: "garden", label: "Vườn cảm xúc", icon: <FlowerIcon /> },
  { id: "journal", label: "Nhật ký", icon: <BookIcon /> },
  { id: "exercise", label: "Bài tập thư giãn", icon: <BreathIcon /> },
  { id: "habits", label: "Thói quen lành mạnh", icon: <SparkleIcon /> },
  { id: "music", label: "Âm nhạc & Thiền", icon: <MusicIcon /> },
  { id: "insight", label: "Insight của bạn", icon: <InsightIcon /> }
];

export function SoulSidebar() {
  const [active, setActive] = useState<Section>("overview");

  return (
    <div className="flex h-full flex-col rounded-card border border-ink-200 bg-white p-5 shadow-soft">
      {/* Branding */}
      <div className="mb-5 flex items-center gap-2.5 px-1">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
          <LeafIcon size={20} />
        </span>
        <span className="text-[17px] font-bold text-ink-900">Soul Garden</span>
      </div>

      {/* Nav */}
      <nav aria-label="Mục Soul Garden">
        <ul className="space-y-1">
          {NAV.map((item) => {
            const isActive = item.id === active;
            return (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => setActive(item.id)}
                  aria-current={isActive ? "page" : undefined}
                  className={`flex w-full items-center gap-3 rounded-card px-3 py-2.5 text-[14px] font-medium transition-colors cursor-pointer ${
                    isActive
                      ? "bg-emerald-50 text-emerald-800"
                      : "text-ink-600 hover:bg-ink-100 hover:text-ink-900"
                  }`}
                >
                  <span
                    aria-hidden="true"
                    className={isActive ? "text-emerald-700" : "text-ink-400"}
                  >
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Card tưới mát tâm hồn */}
      <div className="mt-6 rounded-card bg-emerald-50/60 p-4 text-center">
        <div className="mx-auto mb-3 grid h-20 w-20 place-items-center">
          <WaterCanIllustration />
        </div>
        <p className="text-[14px] font-semibold text-ink-900">
          Tưới mát tâm hồn
        </p>
        <p className="mt-1 text-[12px] leading-relaxed text-ink-500">
          Duy trì thói quen tốt mỗi ngày để khu vườn của bạn luôn tươi tốt.
        </p>
      </div>

      {/* CTA */}
      <button
        type="button"
        className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-pill bg-emerald-600 px-4 py-2.5 text-[14px] font-semibold text-white shadow-soft hover:bg-emerald-700 cursor-pointer"
      >
        <SeedlingIcon size={16} />
        Trồng cây mới
      </button>
    </div>
  );
}

/* ─────────── Icons ─────────── */

function DashboardIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <rect x="13" y="3" width="8" height="5" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <rect x="13" y="10" width="8" height="11" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <rect x="3" y="13" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function FlowerIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="2.5" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 4a3 3 0 0 1 0 6M12 14a3 3 0 0 1 0 6M4 12a3 3 0 0 1 6 0M14 12a3 3 0 0 1 6 0"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function BookIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M5 4h10a4 4 0 0 1 4 4v12H9a4 4 0 0 0-4 4V4z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function BreathIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 4v3M12 17v3M4 12h3M17 12h3M6 6l2 2M16 16l2 2M6 18l2-2M16 8l2-2"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function SparkleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 3l1.8 5.4 5.4 1.8-5.4 1.8L12 17.4l-1.8-5.4-5.4-1.8 5.4-1.8L12 3z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M19 17l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z" fill="currentColor" />
    </svg>
  );
}

function MusicIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M9 18V5l12-2v13"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <circle cx="6" cy="18" r="3" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="18" cy="16" r="3" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function InsightIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="6" stroke="currentColor" strokeWidth="1.8" />
      <path d="M11 8v3l2 1" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M16 16l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function LeafIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 4c-9 0-15 5-15 12 0 2 0 3 1 4 3-7 8-10 12-11-3 2-7 5-9 11 6 0 11-3 12-10 1-3 0-5-1-6z"
        fill="currentColor"
        fillOpacity="0.18"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SeedlingIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 21v-7M12 14c0-3 2-5 5-5-1 4-3 5-5 5zM12 14c0-3-2-5-5-5 1 4 3 5 5 5z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* ─────────── Watercan illustration ─────────── */

function WaterCanIllustration() {
  return (
    <svg viewBox="0 0 80 80" className="h-full w-full" aria-hidden="true">
      {/* spout */}
      <path
        d="M14 38 L4 32 L14 42 Z"
        fill="#9CA3AF"
      />
      {/* body */}
      <rect x="14" y="32" width="34" height="26" rx="4" fill="#9CA3AF" />
      {/* handle */}
      <path
        d="M48 38c6-1 12 0 12 6s-6 7-12 6"
        stroke="#6B7280"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      {/* sprouts on top */}
      <path
        d="M22 32c-2-6 4-9 6-5M30 32c0-7 6-7 6-2M38 32c0-5 5-6 6-1"
        stroke="#10B981"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <ellipse cx="22" cy="26" rx="3" ry="4" fill="#34D399" />
      <ellipse cx="32" cy="24" rx="3" ry="5" fill="#10B981" />
      <ellipse cx="42" cy="26" rx="3" ry="4" fill="#34D399" />
      {/* base shadow */}
      <ellipse cx="32" cy="62" rx="22" ry="3" fill="#000" fillOpacity="0.05" />
    </svg>
  );
}
