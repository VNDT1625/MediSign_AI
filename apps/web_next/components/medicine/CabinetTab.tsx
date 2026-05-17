"use client";

/**
 * `components/medicine/CabinetTab.tsx`
 *
 * Local medicine cabinet tab for `/app/medicine`.
 *
 * Features:
 * - Reads/writes `localStorage["medisign:cabinet"]` via `useMedicineCabinet`.
 * - Interaction warning: if any item's `warnings` array contains a substring
 *   that matches another item's `normalized_name`, the conflicting items are
 *   highlighted in red with a warning message.
 * - Banner: "Danh sách này lưu trên thiết bị, sẽ đồng bộ trong Phase 2".
 * - Empty state when cabinet is empty.
 *
 * UI follows Pre-Delivery Checklist: cursor-pointer, focus-visible:ring-2,
 * no emoji icons (inline SVG only).
 *
 * @see Requirements 2.3.2
 */

import { useMemo } from "react";
import type { MedicineScanResponse } from "@medisign/shared-contracts";
import { useMedicineCabinet } from "@/lib/hooks/useMedicineCabinet";

// ---------------------------------------------------------------------------
// Interaction detection
// ---------------------------------------------------------------------------

/**
 * Returns a Set of `normalized_name` values (lowercased) that have a
 * detected interaction conflict with at least one other cabinet item.
 *
 * Detection rule: item A conflicts with item B if any string in
 * `A.warnings` contains `B.normalized_name` as a case-insensitive
 * substring (or vice-versa).
 */
function detectConflicts(items: MedicineScanResponse[]): Set<string> {
  const conflicting = new Set<string>();

  for (let i = 0; i < items.length; i++) {
    for (let j = 0; j < items.length; j++) {
      if (i === j) continue;

      const a = items[i];
      const b = items[j];
      const bNameLower = b.normalized_name.toLowerCase();

      const hasConflict = a.warnings.some((w) =>
        w.toLowerCase().includes(bNameLower)
      );

      if (hasConflict) {
        conflicting.add(a.normalized_name.toLowerCase());
        conflicting.add(b.normalized_name.toLowerCase());
      }
    }
  }

  return conflicting;
}

// ---------------------------------------------------------------------------
// Risk badge helpers (mirrors ScanTab)
// ---------------------------------------------------------------------------

type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | string;

function getRiskBadgeClasses(level: RiskLevel): string {
  switch (level) {
    case "LOW":
      return "bg-emerald-100 text-emerald-800 border border-emerald-200";
    case "MEDIUM":
      return "bg-amber-100 text-amber-800 border border-amber-200";
    case "HIGH":
      return "bg-rose-100 text-rose-800 border border-rose-200";
    default:
      return "bg-slate-100 text-slate-700 border border-slate-200";
  }
}

function getRiskLabel(level: RiskLevel): string {
  switch (level) {
    case "LOW":
      return "An toàn";
    case "MEDIUM":
      return "Thận trọng";
    case "HIGH":
      return "Nguy hiểm";
    default:
      return level;
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function DeviceBanner() {
  return (
    <div
      role="note"
      aria-label="Thông tin lưu trữ"
      className="mb-5 flex items-start gap-3 rounded-[12px] border border-sky-200 bg-sky-50 px-4 py-3"
    >
      <span className="mt-0.5 shrink-0 text-sky-600" aria-hidden="true">
        <InfoIcon />
      </span>
      <p className="text-[13px] leading-5 text-sky-800">
        Danh sách này lưu trên thiết bị, sẽ đồng bộ trong Phase 2.
      </p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <span
        className="mb-4 flex h-16 w-16 items-center justify-center rounded-[20px] bg-brand-50 text-brand-600"
        aria-hidden="true"
      >
        <CabinetEmptyIcon />
      </span>
      <h3 className="text-[16px] font-semibold text-ink-800">
        Tủ thuốc trống
      </h3>
      <p className="mt-2 max-w-xs text-[14px] text-ink-500">
        Quét thuốc ở tab "Quét thuốc" rồi nhấn "Thêm vào tủ thuốc" để lưu vào
        đây.
      </p>
    </div>
  );
}

interface CabinetItemCardProps {
  item: MedicineScanResponse;
  hasConflict: boolean;
  conflictingNames: string[];
  onRemove: (name: string) => void;
}

function CabinetItemCard({
  item,
  hasConflict,
  conflictingNames,
  onRemove,
}: CabinetItemCardProps) {
  const borderClass = hasConflict
    ? "border-rose-300 bg-rose-50"
    : "border-ink-200 bg-white";

  return (
    <li
      className={`rounded-[14px] border p-4 transition-colors ${borderClass}`}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="truncate text-[15px] font-semibold text-ink-900">
            {item.normalized_name}
          </p>
          <span
            className={`mt-1 inline-flex items-center gap-1 rounded-pill px-2.5 py-0.5 text-[12px] font-semibold ${getRiskBadgeClasses(item.risk_level)}`}
          >
            {getRiskLabel(item.risk_level)}
          </span>
        </div>

        <button
          type="button"
          onClick={() => onRemove(item.normalized_name)}
          aria-label={`Xoá ${item.normalized_name} khỏi tủ thuốc`}
          className="shrink-0 rounded-lg p-1.5 text-ink-400 transition-colors hover:bg-rose-100 hover:text-rose-600 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400"
        >
          <TrashIcon />
        </button>
      </div>

      {/* Conflict warning */}
      {hasConflict && conflictingNames.length > 0 && (
        <div
          role="alert"
          className="mt-3 flex items-start gap-2 rounded-[10px] border border-rose-200 bg-rose-100 px-3 py-2.5"
        >
          <span className="mt-0.5 shrink-0 text-rose-600" aria-hidden="true">
            <ConflictWarningIcon />
          </span>
          <div>
            <p className="text-[13px] font-semibold text-rose-800">
              Cảnh báo tương tác thuốc
            </p>
            <p className="mt-0.5 text-[12px] text-rose-700">
              Có thể tương tác với:{" "}
              <span className="font-semibold">
                {conflictingNames.join(", ")}
              </span>
            </p>
          </div>
        </div>
      )}

      {/* Warnings list (non-conflict) */}
      {!hasConflict && item.warnings.length > 0 && (
        <ul className="mt-3 space-y-1">
          {item.warnings.map((w, i) => (
            <li
              key={i}
              className="flex items-start gap-2 text-[13px] text-ink-600"
            >
              <span
                aria-hidden
                className="mt-[6px] h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400"
              />
              <span>{w}</span>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function CabinetTab() {
  const { items, remove } = useMedicineCabinet();

  const conflicts = useMemo(() => detectConflicts(items), [items]);

  /**
   * For each item, compute which other items it conflicts with (by name).
   */
  const conflictMap = useMemo(() => {
    const map = new Map<string, string[]>();

    for (const item of items) {
      const keyA = item.normalized_name.toLowerCase();
      if (!conflicts.has(keyA)) continue;

      const others: string[] = [];
      for (const other of items) {
        if (other === item) continue;
        const keyB = other.normalized_name.toLowerCase();
        // A conflicts with B if A's warnings mention B's name.
        const aWarnsAboutB = item.warnings.some((w) =>
          w.toLowerCase().includes(keyB)
        );
        // B conflicts with A if B's warnings mention A's name.
        const bWarnsAboutA = other.warnings.some((w) =>
          w.toLowerCase().includes(keyA)
        );
        if (aWarnsAboutB || bWarnsAboutA) {
          others.push(other.normalized_name);
        }
      }
      map.set(keyA, others);
    }

    return map;
  }, [items, conflicts]);

  return (
    <div className="py-4">
      <DeviceBanner />

      {items.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {/* Conflict summary banner */}
          {conflicts.size > 0 && (
            <div
              role="alert"
              className="mb-4 flex items-start gap-3 rounded-[12px] border border-rose-300 bg-rose-50 px-4 py-3"
            >
              <span className="mt-0.5 shrink-0 text-rose-600" aria-hidden="true">
                <ConflictWarningIcon />
              </span>
              <div>
                <p className="text-[14px] font-semibold text-rose-800">
                  Phát hiện tương tác thuốc
                </p>
                <p className="mt-0.5 text-[13px] text-rose-700">
                  Một số thuốc trong tủ có thể tương tác với nhau. Xem chi tiết
                  bên dưới.
                </p>
              </div>
            </div>
          )}

          {/* Item count */}
          <p className="mb-3 text-[13px] text-ink-500">
            {items.length} thuốc trong tủ
          </p>

          <ul className="space-y-3" aria-label="Danh sách thuốc trong tủ">
            {items.map((item) => {
              const key = item.normalized_name.toLowerCase();
              const hasConflict = conflicts.has(key);
              const conflictingNames = conflictMap.get(key) ?? [];
              return (
                <CabinetItemCard
                  key={item.normalized_name}
                  item={item}
                  hasConflict={hasConflict}
                  conflictingNames={conflictingNames}
                  onRemove={remove}
                />
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons (inline SVG — no emoji)
// ---------------------------------------------------------------------------

function InfoIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 8v4M12 16h.01"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function CabinetEmptyIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M9 3h6v3H9z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <rect
        x="6"
        y="6"
        width="12"
        height="15"
        rx="3"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M12 11v6M9 14h6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 6h18M8 6V4h8v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M10 11v6M14 11v6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function ConflictWarningIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path
        d="M12 9v4M12 17h.01"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}
