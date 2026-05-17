"use client";

/**
 * `components/medicine/LookupTab.tsx` — Lookup tab for `/app/medicine`.
 *
 * Features:
 *  1. Search input with 300ms debounce → GET /api/drug/suggestions/{keyword}
 *  2. Keyboard-navigable autocomplete dropdown (↑↓ Enter Escape)
 *  3. On select → POST /api/drug/search → render DrugSearchResponse details
 *     (description, contraindications, side effects, interactions)
 *  4. Loading state during search
 *  5. Error state
 *
 * @see Requirements 2.3.2
 */

import { useState, useEffect, useRef, useCallback, useId } from "react";
import type { DrugSearchResponse } from "@medisign/shared-contracts";
import type { DrugSuggestionsResponse } from "@/lib/api/medicine";
import { drugSuggestions, drugSearch } from "@/lib/api/medicine";
import { ApiError } from "@/lib/api/errors";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEBOUNCE_MS = 300;
const MIN_KEYWORD_LENGTH = 2;

// ---------------------------------------------------------------------------
// Helpers — extract typed fields from opaque drug record
// ---------------------------------------------------------------------------

function getString(obj: Record<string, unknown>, key: string): string {
  const v = obj[key];
  return typeof v === "string" ? v : "";
}

function getStringArray(obj: Record<string, unknown>, key: string): string[] {
  const v = obj[key];
  if (Array.isArray(v)) {
    return v.filter((x): x is string => typeof x === "string");
  }
  return [];
}

/** Extract a display name from a suggestion row. */
function getSuggestionLabel(row: Record<string, unknown>): string {
  // Try common field names the backend may use
  return (
    getString(row, "ten_thuoc") ||
    getString(row, "name") ||
    getString(row, "drug_name") ||
    getString(row, "ten") ||
    getString(row, "id") ||
    "Không rõ tên"
  );
}

/** Extract a display name from the found drug record. */
function getDrugName(drug: Record<string, unknown>): string {
  return (
    getString(drug, "ten_thuoc") ||
    getString(drug, "name") ||
    getString(drug, "drug_name") ||
    getString(drug, "ten") ||
    "Không rõ tên"
  );
}

// ---------------------------------------------------------------------------
// DrugDetailCard — renders a found DrugSearchResponse
// ---------------------------------------------------------------------------

function DrugDetailCard({ response }: { response: DrugSearchResponse }) {
  if (response.status === "not_found") {
    return (
      <div
        role="status"
        className="mt-6 flex flex-col items-center gap-3 rounded-[16px] border border-ink-200 bg-white px-6 py-10 text-center shadow-soft"
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-[16px] bg-slate-100 text-slate-400">
          <NotFoundIcon />
        </span>
        <p className="text-[15px] font-semibold text-ink-800">Không tìm thấy thuốc</p>
        <p className="max-w-xs text-[13px] text-ink-500">
          {response.message ?? "Thuốc này chưa có trong cơ sở dữ liệu. Vui lòng thử tên khác."}
        </p>
      </div>
    );
  }

  if (response.status === "ambiguous" && response.suggestions?.length) {
    return (
      <div className="mt-6 rounded-[16px] border border-amber-200 bg-amber-50 px-5 py-4 shadow-soft">
        <p className="flex items-center gap-2 text-[14px] font-semibold text-amber-800">
          <AmbiguousIcon />
          Nhiều kết quả phù hợp
        </p>
        <p className="mt-1 text-[13px] text-amber-700">
          Vui lòng chọn chính xác hơn từ danh sách gợi ý bên trên.
        </p>
        <ul className="mt-3 space-y-1">
          {response.suggestions.map((s, i) => (
            <li key={i} className="text-[13px] text-amber-900">
              • {getSuggestionLabel(s)}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (response.status === "found" && response.drug) {
    const drug = response.drug;
    const name = getDrugName(drug);

    // Extract detail fields — backend may use various key names
    const description =
      getString(drug, "mo_ta") ||
      getString(drug, "description") ||
      getString(drug, "cong_dung") ||
      getString(drug, "indication");

    const contraindications =
      getStringArray(drug, "chong_chi_dinh") ||
      getStringArray(drug, "contraindications");

    const sideEffects =
      getStringArray(drug, "tac_dung_phu") ||
      getStringArray(drug, "side_effects");

    const interactions =
      getStringArray(drug, "tuong_tac") ||
      getStringArray(drug, "interactions");

    // Fallback: if arrays are empty, try string fields and split by newline/semicolon
    function splitFallback(key1: string, key2: string): string[] {
      const raw = getString(drug, key1) || getString(drug, key2);
      if (!raw) return [];
      return raw
        .split(/[;\n]+/)
        .map((s) => s.trim())
        .filter(Boolean);
    }

    const contraindicationList =
      contraindications.length > 0
        ? contraindications
        : splitFallback("chong_chi_dinh", "contraindications");

    const sideEffectList =
      sideEffects.length > 0
        ? sideEffects
        : splitFallback("tac_dung_phu", "side_effects");

    const interactionList =
      interactions.length > 0
        ? interactions
        : splitFallback("tuong_tac", "interactions");

    return (
      <section
        aria-label={`Chi tiết thuốc ${name}`}
        className="mt-6 rounded-[16px] border border-ink-200 bg-white shadow-soft"
      >
        {/* Drug name heading */}
        <div className="border-b border-ink-100 px-5 py-4">
          <p className="text-[12px] font-medium uppercase tracking-wide text-ink-500">
            Thông tin thuốc
          </p>
          <h2 className="mt-1 text-[20px] font-bold leading-tight text-ink-900">{name}</h2>
        </div>

        <div className="divide-y divide-ink-100 px-5">
          {/* Description */}
          {description && (
            <div className="py-4">
              <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink-800">
                <DescriptionIcon />
                Mô tả / Công dụng
              </h3>
              <p className="mt-2 text-[14px] leading-6 text-ink-700">{description}</p>
            </div>
          )}

          {/* Contraindications */}
          {contraindicationList.length > 0 && (
            <div className="py-4">
              <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink-800">
                <ContraIcon />
                Chống chỉ định
              </h3>
              <ul className="mt-2 space-y-1.5">
                {contraindicationList.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 rounded-card border border-rose-100 bg-rose-50 px-3 py-2 text-[13px] text-rose-800"
                  >
                    <span
                      aria-hidden
                      className="mt-[6px] h-1.5 w-1.5 shrink-0 rounded-full bg-rose-500"
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Side effects */}
          {sideEffectList.length > 0 && (
            <div className="py-4">
              <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink-800">
                <SideEffectIcon />
                Tác dụng phụ
              </h3>
              <ul className="mt-2 space-y-1.5">
                {sideEffectList.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 rounded-card border border-amber-100 bg-amber-50 px-3 py-2 text-[13px] text-amber-800"
                  >
                    <span
                      aria-hidden
                      className="mt-[6px] h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500"
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Interactions */}
          {interactionList.length > 0 && (
            <div className="py-4">
              <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink-800">
                <InteractionIcon />
                Tương tác thuốc
              </h3>
              <ul className="mt-2 space-y-1.5">
                {interactionList.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 rounded-card border border-sky-100 bg-sky-50 px-3 py-2 text-[13px] text-sky-800"
                  >
                    <span
                      aria-hidden
                      className="mt-[6px] h-1.5 w-1.5 shrink-0 rounded-full bg-sky-500"
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Fallback: no detail fields found */}
          {!description &&
            contraindicationList.length === 0 &&
            sideEffectList.length === 0 &&
            interactionList.length === 0 && (
              <div className="py-4">
                <p className="text-[14px] text-ink-500">
                  Không có thông tin chi tiết cho thuốc này trong cơ sở dữ liệu.
                </p>
              </div>
            )}
        </div>
      </section>
    );
  }

  return null;
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function LookupTab() {
  const inputId = useId();
  const listboxId = useId();

  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<Record<string, unknown>[]>([]);
  const [isSuggestionsLoading, setIsSuggestionsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<DrugSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // ---------------------------------------------------------------------------
  // Debounced suggestions fetch
  // ---------------------------------------------------------------------------

  const fetchSuggestions = useCallback(async (keyword: string) => {
    if (keyword.length < MIN_KEYWORD_LENGTH) {
      setSuggestions([]);
      setIsDropdownOpen(false);
      return;
    }

    // Cancel any in-flight suggestion request
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setIsSuggestionsLoading(true);
    try {
      const res: DrugSuggestionsResponse = await drugSuggestions(keyword);
      setSuggestions(res.suggestions ?? []);
      setIsDropdownOpen((res.suggestions?.length ?? 0) > 0);
      setActiveIndex(-1);
    } catch {
      // Silently ignore suggestion errors (don't block the user)
      setSuggestions([]);
      setIsDropdownOpen(false);
    } finally {
      setIsSuggestionsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchSuggestions(query.trim());
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, fetchSuggestions]);

  // ---------------------------------------------------------------------------
  // Drug search on selection
  // ---------------------------------------------------------------------------

  const handleSelect = useCallback(
    async (row: Record<string, unknown>) => {
      const label = getSuggestionLabel(row);
      setQuery(label);
      setIsDropdownOpen(false);
      setSuggestions([]);
      setActiveIndex(-1);
      setError(null);
      setSearchResult(null);
      setIsSearching(true);

      try {
        const result = await drugSearch({ drug_name: label });
        setSearchResult(result);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Đã xảy ra lỗi không xác định. Vui lòng thử lại.");
        }
      } finally {
        setIsSearching(false);
      }
    },
    [],
  );

  // ---------------------------------------------------------------------------
  // Keyboard navigation
  // ---------------------------------------------------------------------------

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!isDropdownOpen || suggestions.length === 0) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) => {
          const next = prev < suggestions.length - 1 ? prev + 1 : 0;
          scrollItemIntoView(next);
          return next;
        });
        break;

      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) => {
          const next = prev > 0 ? prev - 1 : suggestions.length - 1;
          scrollItemIntoView(next);
          return next;
        });
        break;

      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < suggestions.length) {
          handleSelect(suggestions[activeIndex]);
        }
        break;

      case "Escape":
        e.preventDefault();
        setIsDropdownOpen(false);
        setActiveIndex(-1);
        break;
    }
  }

  function scrollItemIntoView(index: number) {
    const list = listRef.current;
    if (!list) return;
    const item = list.children[index] as HTMLElement | undefined;
    item?.scrollIntoView({ block: "nearest" });
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    function handlePointerDown(e: PointerEvent) {
      const target = e.target as Node;
      if (
        inputRef.current &&
        !inputRef.current.contains(target) &&
        listRef.current &&
        !listRef.current.contains(target)
      ) {
        setIsDropdownOpen(false);
        setActiveIndex(-1);
      }
    }
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, []);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const activeDescendant =
    activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined;

  return (
    <div className="py-4">
      {/* Search input with autocomplete */}
      <div className="relative">
        <label
          htmlFor={inputId}
          className="mb-1.5 block text-[14px] font-semibold text-ink-800"
        >
          Tên thuốc cần tra cứu
        </label>

        <div className="relative">
          <span
            aria-hidden="true"
            className="pointer-events-none absolute inset-y-0 left-3.5 flex items-center text-ink-400"
          >
            <SearchIcon />
          </span>

          <input
            ref={inputRef}
            id={inputId}
            type="search"
            autoComplete="off"
            role="combobox"
            aria-expanded={isDropdownOpen}
            aria-autocomplete="list"
            aria-controls={listboxId}
            aria-activedescendant={activeDescendant}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSearchResult(null);
              setError(null);
            }}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              if (suggestions.length > 0) setIsDropdownOpen(true);
            }}
            placeholder="Nhập tên thuốc (tối thiểu 2 ký tự)…"
            disabled={isSearching}
            className="w-full rounded-card border border-ink-200 bg-white py-2.5 pl-10 pr-10 text-[15px] text-ink-800 placeholder:text-ink-400 transition-colors focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 disabled:cursor-not-allowed disabled:opacity-60"
          />

          {/* Spinner inside input */}
          {isSuggestionsLoading && (
            <span
              aria-hidden="true"
              className="pointer-events-none absolute inset-y-0 right-3.5 flex items-center text-ink-400"
            >
              <SpinnerIcon size={16} />
            </span>
          )}

          {/* Clear button */}
          {query && !isSuggestionsLoading && !isSearching && (
            <button
              type="button"
              aria-label="Xoá tìm kiếm"
              onClick={() => {
                setQuery("");
                setSuggestions([]);
                setIsDropdownOpen(false);
                setSearchResult(null);
                setError(null);
                inputRef.current?.focus();
              }}
              className="absolute inset-y-0 right-3 flex items-center text-ink-400 hover:text-ink-700 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40 rounded"
            >
              <CloseIcon />
            </button>
          )}
        </div>

        {/* Autocomplete dropdown */}
        {isDropdownOpen && suggestions.length > 0 && (
          <ul
            ref={listRef}
            id={listboxId}
            role="listbox"
            aria-label="Gợi ý thuốc"
            className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded-card border border-ink-200 bg-white py-1 shadow-lg"
          >
            {suggestions.map((row, i) => {
              const label = getSuggestionLabel(row);
              const isActive = i === activeIndex;
              return (
                <li
                  key={i}
                  id={`${listboxId}-option-${i}`}
                  role="option"
                  aria-selected={isActive}
                  onPointerDown={(e) => {
                    // Prevent input blur before click fires
                    e.preventDefault();
                  }}
                  onClick={() => handleSelect(row)}
                  className={`flex cursor-pointer items-center gap-2 px-4 py-2.5 text-[14px] transition-colors ${
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-ink-800 hover:bg-slate-50"
                  }`}
                >
                  <PillIcon />
                  <span className="flex-1 truncate">{label}</span>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Hint text */}
      <p className="mt-1.5 text-[12px] text-ink-500">
        Nhập ít nhất {MIN_KEYWORD_LENGTH} ký tự để xem gợi ý. Chọn một thuốc để xem chi tiết.
      </p>

      {/* Loading state */}
      {isSearching && (
        <div
          role="status"
          aria-live="polite"
          className="mt-6 flex flex-col items-center gap-3 py-10 text-center"
        >
          <SpinnerIcon size={32} className="text-brand" />
          <p className="text-[14px] text-ink-600">Đang tra cứu thông tin thuốc…</p>
        </div>
      )}

      {/* Error state */}
      {error && !isSearching && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-3 rounded-card border border-rose-200 bg-rose-50 px-4 py-3 text-[14px] text-rose-800"
        >
          <ErrorIcon />
          <div className="flex-1">
            <p className="font-semibold">Không thể tra cứu thuốc</p>
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

      {/* Drug detail result */}
      {searchResult && !isSearching && (
        <DrugDetailCard response={searchResult} />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons (inline SVG — no emoji)
// ---------------------------------------------------------------------------

function SearchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16.5 16.5l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function PillIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="shrink-0 text-ink-400">
      <rect x="3" y="9" width="18" height="6" rx="3" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 9v6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function SpinnerIcon({ size = 18, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={`animate-spin ${className}`}
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

function CloseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className="mt-0.5 shrink-0 text-rose-500"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M15 9l-6 6M9 9l6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function NotFoundIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16.5 16.5l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M9 9l4 4M13 9l-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function AmbiguousIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function DescriptionIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ContraIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path d="M6.34 6.34l11.32 11.32" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function SideEffectIcon() {
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

function InteractionIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path d="M12 8v8M8 12h8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
