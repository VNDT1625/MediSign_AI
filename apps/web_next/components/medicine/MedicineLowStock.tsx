"use client";

// Banner cảnh báo "Sắp hết thuốc" — Metformin 500mg + nút "Mua thêm".
// Tone amber/warning.

export function MedicineLowStock({
  name = "Metformin 500mg",
  remain = "Còn 5 viên"
}: {
  name?: string;
  remain?: string;
}) {
  return (
    <section
      aria-labelledby="low-stock"
      className="flex flex-wrap items-center gap-3 rounded-card border border-amber-200 bg-amber-50/70 p-3 lg:p-4"
    >
      <span className="grid h-9 w-9 flex-none place-items-center rounded-pill bg-amber-100 text-amber-700">
        <WarnIcon />
      </span>

      <div className="min-w-0 flex-1">
        <p
          id="low-stock"
          className="text-[13px] font-semibold text-amber-900"
        >
          Sắp hết thuốc
        </p>
      </div>

      {/* med chip */}
      <div className="flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-card bg-white">
          <PillDot />
        </span>
        <span>
          <span className="block text-[12px] font-semibold text-ink-900">
            {name}
          </span>
          <span className="block text-[11px] text-ink-500">{remain}</span>
        </span>
      </div>

      <button
        type="button"
        className="ml-auto inline-flex items-center gap-1.5 rounded-pill border border-amber-200 bg-white px-3.5 py-1.5 text-[13px] font-semibold text-amber-700 shadow-soft hover:bg-amber-100 cursor-pointer"
      >
        <CartIcon />
        Mua thêm
      </button>
    </section>
  );
}

function WarnIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 4l9 16H3l9-16z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path
        d="M12 10v4M12 17v.5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function CartIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 4h2l2 12h12l2-8H6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="9" cy="20" r="1.5" fill="currentColor" />
      <circle cx="17" cy="20" r="1.5" fill="currentColor" />
    </svg>
  );
}

function PillDot() {
  return (
    <svg viewBox="0 0 32 32" className="h-7 w-7" aria-hidden="true">
      <g transform="translate(16 16) rotate(-30) translate(-16 -16)">
        <rect x="6" y="13" width="20" height="6" rx="3" fill="#fff" stroke="#CBD5E1" strokeWidth="1" />
        <rect x="6" y="13" width="10" height="6" rx="3" fill="#0284C7" />
      </g>
    </svg>
  );
}
