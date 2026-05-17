"use client";

/**
 * `/app/medicine` — Tủ thuốc page.
 *
 * Tab layout:
 *   - Tab 1: Quét thuốc (ScanTab)   ← task 11.1 (this task)
 *   - Tab 2: Tra cứu (LookupTab)    ← task 11.2 (placeholder)
 *   - Tab 3: Tủ thuốc (CabinetTab)  ← task 11.3 (placeholder)
 *
 * @see Requirements 2.3.2
 */

import { useState } from "react";
import { DesktopAppHeader } from "@/components/desktop/DesktopAppHeader";
import { ScanTab } from "@/components/medicine/ScanTab";
import { CabinetTab } from "@/components/medicine/CabinetTab";
import { LookupTab } from "@/components/medicine/LookupTab";

// ---------------------------------------------------------------------------
// Tab definitions
// ---------------------------------------------------------------------------

type TabId = "scan" | "lookup" | "cabinet";

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  {
    id: "scan",
    label: "Quét thuốc",
    icon: <ScanTabIcon />,
  },
  {
    id: "lookup",
    label: "Tra cứu",
    icon: <LookupTabIcon />,
  },
  {
    id: "cabinet",
    label: "Tủ thuốc",
    icon: <CabinetTabIcon />,
  },
];

// ---------------------------------------------------------------------------
// Placeholder tabs (task 11.3)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function MedicinePage() {
  const [activeTab, setActiveTab] = useState<TabId>("scan");

  return (
    <div className="min-h-screen bg-[#F1F5F9]">
      <DesktopAppHeader
        pathname="/app/medicine"
        user={{ name: "Người dùng" }}
        notificationCount={0}
      />

      <main id="main" className="container-page pb-10 pt-4 lg:pt-5">
        {/* Page header */}
        <div className="mb-5 flex items-center gap-4">
          <span className="grid h-12 w-12 flex-none place-items-center rounded-[16px] bg-gradient-to-br from-brand to-brand-700 text-white shadow-soft">
            <MedicinePageIcon />
          </span>
          <div>
            <h1 className="text-[clamp(20px,2.2vw,26px)] font-bold leading-tight text-ink-900">
              Tủ thuốc
            </h1>
            <p className="mt-0.5 text-[13px] text-ink-600">
              Quét, tra cứu và quản lý thuốc thông minh
            </p>
          </div>
        </div>

        {/* Tab card */}
        <div className="rounded-[20px] border border-ink-200 bg-white shadow-soft">
          {/* Tab nav */}
          <nav
            aria-label="Chức năng tủ thuốc"
            role="tablist"
            className="border-b border-ink-200 px-4 pt-1"
          >
            <ul className="flex items-center gap-1">
              {TABS.map((tab) => {
                const isActive = tab.id === activeTab;
                return (
                  <li key={tab.id}>
                    <button
                      type="button"
                      role="tab"
                      id={`tab-${tab.id}`}
                      aria-selected={isActive}
                      aria-controls={`tabpanel-${tab.id}`}
                      onClick={() => setActiveTab(tab.id)}
                      className={`relative inline-flex items-center gap-2 px-4 py-3 text-[14px] font-semibold transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40 focus-visible:ring-offset-1 rounded-t-lg ${
                        isActive
                          ? "text-brand-700"
                          : "text-ink-500 hover:text-ink-800"
                      }`}
                    >
                      <span
                        className={isActive ? "text-brand-600" : "text-ink-400"}
                        aria-hidden="true"
                      >
                        {tab.icon}
                      </span>
                      {tab.label}
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

          {/* Tab panels */}
          <div className="px-5 pb-5 lg:px-6 lg:pb-6">
            <div
              role="tabpanel"
              id="tabpanel-scan"
              aria-labelledby="tab-scan"
              hidden={activeTab !== "scan"}
            >
              {activeTab === "scan" && <ScanTab />}
            </div>

            <div
              role="tabpanel"
              id="tabpanel-lookup"
              aria-labelledby="tab-lookup"
              hidden={activeTab !== "lookup"}
            >
              {activeTab === "lookup" && <LookupTab />}
            </div>

            <div
              role="tabpanel"
              id="tabpanel-cabinet"
              aria-labelledby="tab-cabinet"
              hidden={activeTab !== "cabinet"}
            >
              {activeTab === "cabinet" && <CabinetTab />}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------

function MedicinePageIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3.5" y="6" width="17" height="13.5" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="M3.5 11h17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path
        d="M9 3.5h6M12 14v3.5M10.25 15.75h3.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function ScanTabIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <rect x="7" y="7" width="10" height="10" rx="1" stroke="currentColor" strokeWidth="1.8" />
      <path d="M10 12h4M12 10v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function LookupTabIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16.5 16.5l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function CabinetTabIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M9 3h6v3H9z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <rect x="6" y="6" width="12" height="15" rx="3" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 11v6M9 14h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
