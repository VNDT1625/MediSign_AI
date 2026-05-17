"use client";

// "Thuốc đang dùng" — 3 card thuốc + nút "Xem tất cả" và "+" thêm.
// Mỗi card: thumbnail, tên + dosage, info (điều trị / lần/ngày / còn X viên), arrow.

const MEDS = [
  {
    name: "Metformin 500mg",
    treat: "Điều trị tiểu đường type 2",
    schedule: "1 viên × 2 lần/ngày",
    remain: "Còn 18 viên",
    color: "blue"
  },
  {
    name: "Amlodipine 5mg",
    treat: "Điều trị cao huyết áp",
    schedule: "1 viên × 1 lần/ngày",
    remain: "Còn 12 viên",
    color: "green"
  },
  {
    name: "Omega 3",
    treat: "Tốt cho tim mạch",
    schedule: "1 viên × 1 lần/ngày",
    remain: "Còn 25 viên",
    color: "amber"
  }
] as const;

export function MedicineCurrent() {
  return (
    <section
      aria-labelledby="current-meds"
      className="rounded-card border border-ink-200 bg-white p-4 shadow-soft lg:p-5"
    >
      <div className="mb-3 flex items-center justify-between">
        <h3
          id="current-meds"
          className="inline-flex items-center gap-2 text-[14px] font-bold text-ink-900"
        >
          <span className="text-brand-700">
            <CapsuleIcon />
          </span>
          Thuốc đang dùng
        </h3>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="text-[12px] font-semibold text-brand-700 hover:underline cursor-pointer"
          >
            Xem tất cả
          </button>
          <span className="text-ink-400">›</span>
          <button
            type="button"
            aria-label="Thêm thuốc đang dùng"
            className="grid h-7 w-7 place-items-center rounded-pill border border-ink-200 text-ink-500 hover:border-brand hover:text-brand-700 cursor-pointer"
          >
            <PlusIcon />
          </button>
        </div>
      </div>

      <ul className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {MEDS.map((m) => (
          <li key={m.name}>
            <button
              type="button"
              className="flex w-full items-center gap-3 rounded-card border border-ink-200 bg-white p-3 text-left shadow-soft transition-colors hover:border-brand hover:shadow-card cursor-pointer"
            >
              <span className="grid h-12 w-12 flex-none place-items-center rounded-card bg-ink-100/40">
                <PillThumb color={m.color} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-[13px] font-semibold text-ink-900">
                  {m.name}
                </p>
                <p className="truncate text-[11px] text-ink-500">{m.treat}</p>
                <p className="truncate text-[11px] text-ink-700">{m.schedule}</p>
                <p className="truncate text-[11px] font-medium text-ink-900">
                  {m.remain}
                </p>
              </div>
              <span aria-hidden="true" className="text-ink-400">
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M9 6l6 6-6 6"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

/* ─────────── Thumbnails ─────────── */

function PillThumb({ color }: { color: "blue" | "green" | "amber" }) {
  if (color === "blue") {
    return (
      <svg viewBox="0 0 40 40" className="h-9 w-9" aria-hidden="true">
        <g transform="translate(20 20) rotate(-30) translate(-20 -20)">
          <rect x="6" y="16" width="28" height="10" rx="5" fill="#fff" stroke="#CBD5E1" strokeWidth="1" />
          <rect x="6" y="16" width="14" height="10" rx="5" fill="#0284C7" />
          <ellipse cx="14" cy="19" rx="2" ry="0.8" fill="#fff" fillOpacity="0.6" />
          <ellipse cx="28" cy="19" rx="2" ry="0.8" fill="#fff" fillOpacity="0.7" />
        </g>
      </svg>
    );
  }
  if (color === "green") {
    return (
      <svg viewBox="0 0 40 40" className="h-9 w-9" aria-hidden="true">
        <circle cx="20" cy="20" r="11" fill="#86EFAC" />
        <circle cx="20" cy="20" r="11" stroke="#16A34A" strokeWidth="1" fill="none" />
        <line x1="9" y1="20" x2="31" y2="20" stroke="#16A34A" strokeWidth="1" />
        <ellipse cx="17" cy="16" rx="3" ry="1.5" fill="#fff" fillOpacity="0.7" />
      </svg>
    );
  }
  // amber
  return (
    <svg viewBox="0 0 40 40" className="h-9 w-9" aria-hidden="true">
      <g transform="translate(20 20) rotate(20) translate(-20 -20)">
        <ellipse cx="20" cy="20" rx="13" ry="8" fill="#FB923C" />
        <ellipse cx="16" cy="16" rx="3" ry="1.5" fill="#fff" fillOpacity="0.6" />
      </g>
    </svg>
  );
}

function CapsuleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect
        x="3"
        y="9"
        width="18"
        height="6"
        rx="3"
        stroke="currentColor"
        strokeWidth="1.8"
        transform="rotate(-30 12 12)"
      />
      <path
        d="M8.5 7.5l7 7"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 5v14M5 12h14"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
    </svg>
  );
}
