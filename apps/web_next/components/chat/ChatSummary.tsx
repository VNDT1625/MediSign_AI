"use client";

// Cột phải: tóm tắt nhanh — triệu chứng, đánh giá, khuyến nghị,
// gợi ý tiếp theo, tệp đính kèm. Theo spec mục 5.1.

import { useState } from "react";
import {
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  BellIcon,
  AppleNutritionIcon,
  RunIcon,
  HospitalIcon,
  FileImageIcon,
  FilePdfIcon,
  DownloadIcon
} from "./icons";
import { ATTACHMENTS, NEXT_SUGGESTIONS } from "./mock";

const SUGGESTION_ICONS = {
  bell: { Icon: BellIcon, tone: "bg-violet-50 text-violet-600" },
  apple: { Icon: AppleNutritionIcon, tone: "bg-amber-50 text-amber-600" },
  run: { Icon: RunIcon, tone: "bg-rose-50 text-rose-600" },
  hospital: { Icon: HospitalIcon, tone: "bg-brand-50 text-brand-700" }
} as const;

export function ChatSummary() {
  const [open, setOpen] = useState(true);

  return (
    <aside
      aria-label="Tóm tắt cuộc tư vấn"
      className="flex h-full w-full flex-col gap-4 overflow-y-auto p-4"
    >
      {/* Tóm tắt nhanh */}
      <section className="rounded-card border border-ink-200 bg-white p-4 shadow-soft">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className="flex w-full items-center justify-between cursor-pointer"
        >
          <h2 className="text-[15px] font-bold text-ink-900">Tóm tắt nhanh</h2>
          {open ? (
            <ChevronUpIcon size={18} className="text-ink-500" />
          ) : (
            <ChevronDownIcon size={18} className="text-ink-500" />
          )}
        </button>

        {open && (
          <div className="mt-3 space-y-3">
            <SummaryItem
              label="Triệu chứng"
              value="Đau họng, ho khan, sốt nhẹ 37.8°C, mệt nhẹ."
            />
            <SummaryItem
              label="Đánh giá sơ bộ"
              value="Khả năng cao là viêm họng do virus."
            />
            <SummaryItem
              label="Khuyến nghị"
              value="Nghỉ ngơi, uống nước ấm, súc họng. Theo dõi thêm 1–2 ngày."
            />

            <button
              type="button"
              className="mt-1 inline-flex w-full items-center justify-center rounded-pill bg-brand-50 px-4 py-2 text-[13px] font-semibold text-brand-700 transition-colors hover:bg-brand-100 cursor-pointer"
            >
              Xem chi tiết
            </button>
          </div>
        )}
      </section>

      {/* Gợi ý tiếp theo */}
      <section className="rounded-card border border-ink-200 bg-white p-4 shadow-soft">
        <h2 className="mb-3 text-[15px] font-bold text-ink-900">Gợi ý tiếp theo</h2>
        <ul className="space-y-1">
          {NEXT_SUGGESTIONS.map((s) => {
            const { Icon, tone } = SUGGESTION_ICONS[s.icon];
            return (
              <li key={s.id}>
                <button
                  type="button"
                  className="flex w-full items-center gap-3 rounded-card px-2 py-2 text-left text-[13.5px] font-medium text-ink-700 transition-colors hover:bg-ink-100 cursor-pointer"
                >
                  <span
                    aria-hidden
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-card ${tone}`}
                  >
                    <Icon size={16} />
                  </span>
                  <span className="flex-1">{s.label}</span>
                  <ChevronRightIcon size={16} className="text-ink-400" />
                </button>
              </li>
            );
          })}
        </ul>
      </section>

      {/* Tệp đính kèm */}
      <section className="rounded-card border border-ink-200 bg-white p-4 shadow-soft">
        <h2 className="mb-3 text-[15px] font-bold text-ink-900">Tệp đính kèm</h2>
        <ul className="space-y-2">
          {ATTACHMENTS.map((a) => {
            const isPdf = a.kind === "pdf";
            return (
              <li
                key={a.id}
                className="flex items-center gap-3 rounded-card border border-ink-200 bg-white px-3 py-2"
              >
                <span
                  aria-hidden
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-card ${
                    isPdf
                      ? "bg-rose-50 text-rose-600"
                      : "bg-brand-50 text-brand-700"
                  }`}
                >
                  {isPdf ? <FilePdfIcon size={20} /> : <FileImageIcon size={20} />}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13px] font-semibold text-ink-800">
                    {a.name}
                  </p>
                  <p className="text-[11px] text-ink-500">
                    {a.size} · {a.kind.toUpperCase()}
                  </p>
                </div>
                <button
                  type="button"
                  aria-label={`Tải xuống ${a.name}`}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-pill text-ink-500 hover:bg-ink-100 hover:text-brand cursor-pointer"
                >
                  <DownloadIcon size={18} />
                </button>
              </li>
            );
          })}
        </ul>
        <button
          type="button"
          className="mt-3 w-full rounded-pill px-4 py-2 text-[13px] font-semibold text-brand-700 hover:bg-brand-50 cursor-pointer"
        >
          Xem tất cả
        </button>
      </section>
    </aside>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[13px] font-semibold text-ink-800">{label}</p>
      <p className="mt-0.5 text-[13.5px] leading-6 text-ink-600">{value}</p>
    </div>
  );
}
