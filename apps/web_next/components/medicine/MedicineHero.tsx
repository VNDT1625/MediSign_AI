"use client";

// Banner top — gradient xanh nhạt với 2 stats và illustration thuốc bên phải.
// Có nút "Thêm thuốc" góc trên phải.

export function MedicineHero({
  todayCount = 3,
  nextDoseAt = "10:00",
  remainMinutes = 45
}: {
  todayCount?: number;
  nextDoseAt?: string;
  remainMinutes?: number;
}) {
  return (
    <section
      aria-labelledby="medicine-hero"
      className="relative overflow-hidden rounded-[20px] border border-brand-100/70 bg-gradient-to-br from-brand-50/70 via-sky-50/50 to-white p-6 lg:p-7"
    >
      {/* Top row: title + Thêm thuốc */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <span className="grid h-14 w-14 flex-none place-items-center rounded-[16px] bg-gradient-to-br from-brand to-brand-700 text-white shadow-soft">
            <BottleIcon size={26} />
          </span>
          <div>
            <h1
              id="medicine-hero"
              className="text-[clamp(22px,2.4vw,28px)] font-bold leading-tight text-ink-900"
            >
              Tủ thuốc
            </h1>
            <p className="mt-0.5 text-[13px] text-ink-600">
              Quản lý thuốc thông minh
            </p>
          </div>
        </div>

        <button
          type="button"
          className="inline-flex items-center gap-1.5 rounded-pill border border-ink-200 bg-white px-4 py-2 text-[13px] font-semibold text-ink-800 shadow-soft hover:border-brand hover:text-brand-700 cursor-pointer"
        >
          <PlusIcon />
          Thêm thuốc
        </button>
      </div>

      {/* Stats row + illustration */}
      <div className="mt-5 grid items-end gap-4 md:grid-cols-[1fr_auto]">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {/* Today */}
          <div className="rounded-card bg-white/60 p-4 backdrop-blur">
            <div className="flex items-center gap-2 text-[12px] font-medium text-ink-500">
              <CalendarIcon /> Hôm nay
            </div>
            <p className="mt-2 leading-tight">
              <span className="text-[28px] font-extrabold text-ink-900">
                {todayCount}
              </span>
              <span className="ml-1.5 text-[14px] font-medium text-ink-700">
                loại thuốc
              </span>
            </p>
            <p className="text-[12px] text-ink-500">cần uống</p>
          </div>

          {/* Next dose */}
          <div className="rounded-card bg-white/60 p-4 backdrop-blur">
            <div className="flex items-center gap-2 text-[12px] font-medium text-ink-500">
              <ClockIcon /> Uống tiếp theo
            </div>
            <p className="mt-2 text-[28px] font-extrabold leading-tight text-ink-900">
              {nextDoseAt}
            </p>
            <p className="text-[12px] text-ink-500">Còn {remainMinutes} phút</p>
          </div>
        </div>

        {/* Illustration */}
        <div className="hidden md:block">
          <PillsIllust />
        </div>
      </div>
    </section>
  );
}

/* ─────────── Icons ─────────── */

function BottleIcon({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
      <path d="M12 11v6M9 14h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
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

function CalendarIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3.5" y="5" width="17" height="15" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M8 3v3M16 3v3M3.5 10h17"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 7v5l3 2"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

/* ─────────── Pills illustration ─────────── */

function PillsIllust() {
  return (
    <svg
      viewBox="0 0 220 160"
      className="h-[140px] w-[200px] lg:h-[160px] lg:w-[230px]"
      aria-hidden="true"
    >
      {/* shadow */}
      <ellipse cx="110" cy="148" rx="90" ry="6" fill="#000" fillOpacity="0.06" />

      {/* Bottle body */}
      <rect x="60" y="50" width="64" height="92" rx="10" fill="#fff" stroke="#CBD5E1" strokeWidth="1.5" />
      <rect x="68" y="58" width="48" height="76" rx="6" fill="#EFF6FF" />
      {/* bottle cap */}
      <rect x="64" y="34" width="56" height="20" rx="4" fill="#0284C7" />
      <rect x="68" y="38" width="48" height="12" rx="3" fill="#0EA5E9" />
      {/* label cross */}
      <rect x="80" y="78" width="24" height="24" rx="4" fill="#fff" stroke="#0284C7" strokeWidth="1.5" />
      <path
        d="M92 84v12M86 90h12"
        stroke="#0284C7"
        strokeWidth="2.6"
        strokeLinecap="round"
      />
      {/* horizontal line on label */}
      <line x1="74" y1="112" x2="110" y2="112" stroke="#CBD5E1" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="74" y1="118" x2="100" y2="118" stroke="#CBD5E1" strokeWidth="1.5" strokeLinecap="round" />

      {/* Capsule 1 — orange/white */}
      <g transform="translate(140, 72) rotate(20)">
        <rect x="0" y="0" width="50" height="18" rx="9" fill="#FED7AA" />
        <rect x="0" y="0" width="25" height="18" rx="9" fill="#FB923C" />
        <ellipse cx="38" cy="6" rx="4" ry="2" fill="#fff" fillOpacity="0.6" />
      </g>

      {/* Capsule 2 — blue/white */}
      <g transform="translate(150, 110) rotate(-10)">
        <rect x="0" y="0" width="46" height="16" rx="8" fill="#fff" stroke="#CBD5E1" strokeWidth="1" />
        <rect x="0" y="0" width="23" height="16" rx="8" fill="#0284C7" />
        <ellipse cx="34" cy="5" rx="4" ry="1.5" fill="#fff" fillOpacity="0.7" />
      </g>

      {/* Round pill */}
      <g transform="translate(40, 110)">
        <circle cx="10" cy="10" r="10" fill="#fff" stroke="#CBD5E1" strokeWidth="1" />
        <line x1="0" y1="10" x2="20" y2="10" stroke="#CBD5E1" strokeWidth="1.5" />
      </g>
    </svg>
  );
}
