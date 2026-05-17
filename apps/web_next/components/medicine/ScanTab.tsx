"use client";

/**
 * `components/medicine/ScanTab.tsx` — Scan tab for `/app/medicine`.
 *
 * Form: "Tên thuốc đọc được" (medicine name) + OCR textarea (2–500 chars).
 * On submit → POST /medicine/scan → render MedicineScanResponse.
 *
 * @see Requirements 2.3.2
 */

import { useState, useId } from "react";
import type { MedicineScanResponse } from "@medisign/shared-contracts";
import { scan } from "@/lib/api/medicine";
import { ApiError } from "@/lib/api/errors";
import { useMedicineCabinet } from "@/lib/hooks/useMedicineCabinet";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const OCR_MIN = 2;
const OCR_MAX = 500;

// ---------------------------------------------------------------------------
// Risk badge helpers
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

function RiskIcon({ level }: { level: RiskLevel }) {
  if (level === "LOW") {
    return (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
        <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (level === "HIGH") {
    return (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
        <path d="M12 9v4M12 17h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    );
  }
  // MEDIUM or unknown
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Result card
// ---------------------------------------------------------------------------

function ScanResultCard({ result }: { result: MedicineScanResponse }) {
  return (
    <section
      aria-label="Kết quả phân tích thuốc"
      className="mt-6 rounded-[16px] border border-ink-200 bg-white p-5 shadow-soft"
    >
      {/* Header: normalized name + risk badge */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[12px] font-medium uppercase tracking-wide text-ink-500">
            Tên thuốc chuẩn hoá
          </p>
          <h2 className="mt-1 text-[20px] font-bold leading-tight text-ink-900">
            {result.normalized_name}
          </h2>
        </div>

        <span
          className={`inline-flex items-center gap-1.5 rounded-pill px-3 py-1.5 text-[13px] font-semibold ${getRiskBadgeClasses(result.risk_level)}`}
        >
          <RiskIcon level={result.risk_level} />
          {getRiskLabel(result.risk_level)}
        </span>
      </div>

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div className="mt-4">
          <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink-800">
            <WarningIcon />
            Cảnh báo
          </h3>
          <ul className="mt-2 space-y-2">
            {result.warnings.map((w, i) => (
              <li
                key={i}
                className="flex items-start gap-2 rounded-card border border-amber-100 bg-amber-50 px-3 py-2.5 text-[14px] text-amber-900"
              >
                <span aria-hidden className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500 mt-[7px]" />
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Guidance */}
      {result.guidance && (
        <div className="mt-4">
          <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink-800">
            <GuidanceIcon />
            Hướng dẫn sử dụng
          </h3>
          <p className="mt-2 rounded-card border border-sky-100 bg-sky-50 px-3 py-3 text-[14px] leading-6 text-sky-900">
            {result.guidance}
          </p>
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function ScanTab() {
  const nameId = useId();
  const ocrId = useId();

  const [medicineName, setMedicineName] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [result, setResult] = useState<MedicineScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [addedToCabinet, setAddedToCabinet] = useState(false);

  const { add: addToCabinet } = useMedicineCabinet();

  const ocrLength = ocrText.length;
  const ocrValid = ocrLength >= OCR_MIN && ocrLength <= OCR_MAX;
  const canSubmit = ocrValid && !isPending;

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!canSubmit) return;

    setIsPending(true);
    setError(null);
    setResult(null);
    setAddedToCabinet(false);

    try {
      // Combine medicine name (if provided) with OCR text for richer context.
      // The backend's extracted_text field accepts the full label content.
      const extractedText = medicineName.trim()
        ? `${medicineName.trim()}\n${ocrText}`
        : ocrText;

      const response = await scan({
        extracted_text: extractedText,
      });
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Đã xảy ra lỗi không xác định. Vui lòng thử lại.");
      }
    } finally {
      setIsPending(false);
    }
  }

  return (
    <div className="py-4">
      <form onSubmit={handleSubmit} noValidate>
        {/* Medicine name input */}
        <div className="mb-4">
          <label
            htmlFor={nameId}
            className="mb-1.5 block text-[14px] font-semibold text-ink-800"
          >
            Tên thuốc đọc được
            <span className="ml-1 text-[12px] font-normal text-ink-500">(tuỳ chọn)</span>
          </label>
          <input
            id={nameId}
            type="text"
            value={medicineName}
            onChange={(e) => setMedicineName(e.target.value)}
            placeholder="Ví dụ: Paracetamol 500mg"
            disabled={isPending}
            className="w-full rounded-card border border-ink-200 bg-white px-4 py-2.5 text-[15px] text-ink-800 placeholder:text-ink-400 transition-colors focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        {/* OCR textarea */}
        <div className="mb-4">
          <div className="mb-1.5 flex items-baseline justify-between">
            <label
              htmlFor={ocrId}
              className="text-[14px] font-semibold text-ink-800"
            >
              Văn bản OCR từ nhãn thuốc
              <span className="ml-1 text-rose-600" aria-hidden="true">*</span>
            </label>
            <span
              className={`text-[12px] font-medium tabular-nums ${
                ocrLength > OCR_MAX
                  ? "text-rose-600"
                  : ocrLength >= OCR_MIN
                  ? "text-emerald-600"
                  : "text-ink-400"
              }`}
              aria-live="polite"
              aria-label={`${ocrLength} / ${OCR_MAX} ký tự`}
            >
              {ocrLength} / {OCR_MAX}
            </span>
          </div>
          <textarea
            id={ocrId}
            value={ocrText}
            onChange={(e) => setOcrText(e.target.value)}
            placeholder="Dán hoặc nhập văn bản từ nhãn thuốc (tối thiểu 2 ký tự, tối đa 500 ký tự)…"
            rows={5}
            disabled={isPending}
            aria-required="true"
            aria-describedby={`${ocrId}-hint`}
            className="w-full resize-y rounded-card border border-ink-200 bg-white px-4 py-3 text-[15px] leading-6 text-ink-800 placeholder:text-ink-400 transition-colors focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 disabled:cursor-not-allowed disabled:opacity-60"
          />
          <p id={`${ocrId}-hint`} className="mt-1 text-[12px] text-ink-500">
            Nhập văn bản mô phỏng OCR từ nhãn thuốc. Tối thiểu {OCR_MIN} ký tự, tối đa {OCR_MAX} ký tự.
          </p>
          {ocrLength > OCR_MAX && (
            <p role="alert" className="mt-1 text-[12px] text-rose-600">
              Văn bản vượt quá {OCR_MAX} ký tự. Vui lòng rút ngắn.
            </p>
          )}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={!canSubmit}
          className="inline-flex w-full items-center justify-center gap-2 rounded-pill bg-brand px-6 py-3 text-[15px] font-semibold text-white shadow-soft transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
        >
          {isPending ? (
            <>
              <SpinnerIcon />
              Đang phân tích…
            </>
          ) : (
            <>
              <ScanIcon />
              Phân tích thuốc
            </>
          )}
        </button>
      </form>

      {/* Error state */}
      {error && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-3 rounded-card border border-rose-200 bg-rose-50 px-4 py-3 text-[14px] text-rose-800"
        >
          <ErrorIcon />
          <div className="flex-1">
            <p className="font-semibold">Không thể phân tích thuốc</p>
            <p className="mt-0.5 text-[13px]">{error}</p>
          </div>
          <button
            type="button"
            onClick={() => setError(null)}
            aria-label="Đóng thông báo lỗi"
            className="shrink-0 text-rose-500 hover:text-rose-700 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 rounded"
          >
            <CloseIcon />
          </button>
        </div>
      )}

      {/* Result */}
      {result && (
        <>
          <ScanResultCard result={result} />

          {/* Add to cabinet button */}
          <div className="mt-4">
            {addedToCabinet ? (
              <div
                role="status"
                aria-live="polite"
                className="flex items-center justify-center gap-2 rounded-pill border border-emerald-200 bg-emerald-50 px-6 py-3 text-[15px] font-semibold text-emerald-700"
              >
                <CheckIcon />
                Đã thêm vào tủ thuốc
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  addToCabinet(result);
                  setAddedToCabinet(true);
                }}
                className="inline-flex w-full items-center justify-center gap-2 rounded-pill border border-brand bg-white px-6 py-3 text-[15px] font-semibold text-brand shadow-soft transition-colors hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50 focus-visible:ring-offset-2 cursor-pointer"
              >
                <AddToCabinetIcon />
                Thêm vào tủ thuốc
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons (inline SVG — no emoji)
// ---------------------------------------------------------------------------

function ScanIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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

function SpinnerIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className="animate-spin"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" strokeOpacity="0.25" />
      <path
        d="M12 3a9 9 0 0 1 9 9"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path d="M12 9v4M12 17h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function GuidanceIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="mt-0.5 shrink-0 text-rose-500">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M15 9l-6 6M9 9l6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 6L9 17l-5-5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function AddToCabinetIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
