"use client";

// Card "Uống tiếp theo" — Vitamin D3 1000 IU.
// Có thumbnail viên nang, tên + mô tả + 2 chip phụ, time + nút primary "Đánh dấu đã uống".

export function MedicineNextDose({
  name = "Vitamin D3 1000 IU",
  desc = "Hỗ trợ xương & miễn dịch",
  dose = "1 viên",
  schedule = "Sau ăn sáng",
  time = "10:00"
}: {
  name?: string;
  desc?: string;
  dose?: string;
  schedule?: string;
  time?: string;
}) {
  return (
    <section
      aria-labelledby="next-dose"
      className="rounded-card border border-ink-200 bg-white p-4 shadow-soft lg:p-5"
    >
      <h3
        id="next-dose"
        className="inline-flex items-center gap-2 text-[14px] font-bold text-ink-900"
      >
        <span className="text-brand-700">
          <AlarmIcon />
        </span>
        Uống tiếp theo
      </h3>

      <div className="mt-3 grid items-center gap-4 sm:grid-cols-[auto_1fr_auto]">
        {/* Thumbnail */}
        <div className="grid h-16 w-16 flex-none place-items-center rounded-card bg-brand-50/70">
          <CapsuleIllust />
        </div>

        {/* Info */}
        <div className="min-w-0">
          <p className="text-[15px] font-semibold text-ink-900">{name}</p>
          <p className="mt-0.5 text-[12px] text-ink-500">{desc}</p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Chip>{dose}</Chip>
            <Chip>{schedule}</Chip>
          </div>
        </div>

        {/* Time + CTA */}
        <div className="flex flex-col items-end gap-2 sm:items-end">
          <span className="text-[22px] font-extrabold leading-none text-ink-900">
            {time}
          </span>
          <button
            type="button"
            className="inline-flex items-center gap-1.5 rounded-pill bg-brand px-4 py-2 text-[13px] font-semibold text-white shadow-soft hover:bg-brand-700 cursor-pointer"
          >
            <CheckIcon />
            Đánh dấu đã uống
          </button>
        </div>
      </div>
    </section>
  );
}

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-pill bg-ink-100 px-2.5 py-0.5 text-[11px] font-medium text-ink-700">
      {children}
    </span>
  );
}

function AlarmIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="13" r="8" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 9v4l2.5 2M5 5l3-2M19 5l-3-2"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M5 12l4 4L19 6"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* Capsule illustration — original SVG */
function CapsuleIllust() {
  return (
    <svg viewBox="0 0 56 56" className="h-12 w-12" aria-hidden="true">
      <g transform="translate(28 28) rotate(-30) translate(-28 -28)">
        <rect x="10" y="22" width="36" height="14" rx="7" fill="#fff" stroke="#CBD5E1" strokeWidth="1.4" />
        <rect x="10" y="22" width="18" height="14" rx="7" fill="#0284C7" />
        <ellipse cx="22" cy="26" rx="3" ry="1.2" fill="#fff" fillOpacity="0.6" />
        <ellipse cx="38" cy="26" rx="3" ry="1.2" fill="#fff" fillOpacity="0.8" />
      </g>
    </svg>
  );
}
