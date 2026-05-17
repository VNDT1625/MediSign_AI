"use client";

// 3 tab dưới hero: Hôm nay / Đang dùng / Đơn thuốc.
// Tab active có gạch dưới brand.

import { useState } from "react";

type TabId = "today" | "current" | "prescription";

const TABS: { id: TabId; label: string }[] = [
  { id: "today", label: "Hôm nay" },
  { id: "current", label: "Đang dùng" },
  { id: "prescription", label: "Đơn thuốc" }
];

export function MedicineTabs() {
  const [active, setActive] = useState<TabId>("today");

  return (
    <nav aria-label="Lọc thuốc" role="tablist" className="border-b border-ink-200">
      <ul className="flex items-center gap-1">
        {TABS.map((t) => {
          const isActive = t.id === active;
          return (
            <li key={t.id}>
              <button
                type="button"
                role="tab"
                aria-selected={isActive}
                onClick={() => setActive(t.id)}
                className={`relative px-4 py-2.5 text-[14px] font-semibold transition-colors cursor-pointer ${
                  isActive
                    ? "text-brand-700"
                    : "text-ink-500 hover:text-ink-800"
                }`}
              >
                {t.label}
                {isActive && (
                  <span
                    aria-hidden="true"
                    className="absolute inset-x-3 -bottom-px h-[3px] rounded-full bg-brand"
                  />
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
