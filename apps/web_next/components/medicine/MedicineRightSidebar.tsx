"use client";

// Sidebar phải Tủ thuốc — 3 card:
// 1) Lịch uống hôm nay (4 entries + nút Xem lịch tuần)
// 2) Tóm tắt tồn kho (3 stat: 6 / 1 / 2)
// 3) Gợi ý & hỗ trợ (3 link nhỏ)

const SCHEDULE = [
  {
    time: "08:00",
    name: "Metformin 500mg",
    sub: "1 viên · Sau ăn sáng",
    status: "done"
  },
  {
    time: "10:00",
    name: "Vitamin D3 1000 IU",
    sub: "1 viên · Sau ăn sáng",
    status: "next"
  },
  {
    time: "13:00",
    name: "Amlodipine 5mg",
    sub: "1 viên · Sau ăn trưa",
    status: "pending"
  },
  {
    time: "20:00",
    name: "Omega 3",
    sub: "1 viên · Sau ăn tối",
    status: "pending"
  }
] as const;

const HELPS = [
  {
    icon: <BellIcon />,
    title: "Đặt nhắc uống thuốc",
    sub: "Không bỏ lỡ liều thuốc quan trọng"
  },
  {
    icon: <UsersIcon />,
    title: "Quản lý cho người thân",
    sub: "Chia sẻ để cùng chăm sóc"
  },
  {
    icon: <BoxIcon />,
    title: "Theo dõi tồn kho",
    sub: "Kiểm tra số lượng thuốc dễ dàng"
  }
];

export function MedicineRightSidebar() {
  return (
    <div className="flex flex-col gap-5">
      {/* 1. Schedule today */}
      <section
        aria-labelledby="schedule-today"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <h3
          id="schedule-today"
          className="inline-flex items-center gap-2 text-[14px] font-bold text-ink-900"
        >
          <span className="text-brand-700">
            <CalendarIcon />
          </span>
          Lịch uống hôm nay
        </h3>

        <ul className="mt-4 space-y-3">
          {SCHEDULE.map((s) => (
            <li
              key={s.time}
              className={`grid grid-cols-[64px_auto_1fr_auto] items-center gap-2.5 rounded-card border px-2.5 py-2 ${
                s.status === "next"
                  ? "border-brand-200 bg-brand-50/60"
                  : "border-transparent"
              }`}
            >
              <span
                className={`text-[13px] font-semibold ${
                  s.status === "next" ? "text-brand-700" : "text-ink-700"
                }`}
              >
                {s.time}
              </span>

              <StatusDot status={s.status} />

              <div className="min-w-0">
                <p className="truncate text-[13px] font-semibold text-ink-900">
                  {s.name}
                </p>
                <p className="truncate text-[11px] text-ink-500">{s.sub}</p>
              </div>

              {s.status === "next" && (
                <span className="rounded-pill bg-brand px-2 py-0.5 text-[10px] font-semibold text-white">
                  Tiếp theo
                </span>
              )}
            </li>
          ))}
        </ul>

        <button
          type="button"
          className="mt-4 inline-flex w-full items-center justify-center gap-1.5 rounded-card border border-ink-200 bg-white py-2 text-[13px] font-semibold text-ink-700 hover:border-brand hover:text-brand-700 cursor-pointer"
        >
          <CalendarIcon />
          Xem lịch tuần
        </button>
      </section>

      {/* 2. Inventory summary */}
      <section
        aria-labelledby="inventory"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <h3
          id="inventory"
          className="inline-flex items-center gap-2 text-[14px] font-bold text-ink-900"
        >
          <span className="text-brand-700">
            <BoxIcon />
          </span>
          Tóm tắt tồn kho
        </h3>

        <ul className="mt-4 grid grid-cols-3 gap-2 text-center">
          <Stat value="6" label={["loại đang", "dùng"]} tone="brand" />
          <Stat value="1" label={["sắp hết"]} tone="amber" />
          <Stat value="2" label={["đơn thuốc", "gần đây"]} tone="emerald" />
        </ul>
      </section>

      {/* 3. Help / suggestions */}
      <section
        aria-labelledby="help"
        className="rounded-card border border-ink-200 bg-white p-5 shadow-soft"
      >
        <h3
          id="help"
          className="inline-flex items-center gap-2 text-[14px] font-bold text-ink-900"
        >
          <span className="text-brand-700">
            <BulbIcon />
          </span>
          Gợi ý & hỗ trợ
        </h3>

        <ul className="mt-4 space-y-2">
          {HELPS.map((h) => (
            <li key={h.title}>
              <button
                type="button"
                className="flex w-full items-center gap-3 rounded-card px-2.5 py-2 text-left transition-colors hover:bg-ink-100/60 cursor-pointer"
              >
                <span
                  className="grid h-9 w-9 flex-none place-items-center rounded-card bg-brand-50 text-brand-700"
                  aria-hidden="true"
                >
                  {h.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13px] font-semibold text-ink-900">
                    {h.title}
                  </p>
                  <p className="truncate text-[11px] text-ink-500">{h.sub}</p>
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
    </div>
  );
}

/* ─────────── Sub-components ─────────── */

function StatusDot({ status }: { status: "done" | "next" | "pending" }) {
  if (status === "done") {
    return (
      <span
        className="grid h-5 w-5 place-items-center rounded-pill bg-emerald-100 text-emerald-700"
        aria-label="Đã uống"
      >
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M5 12l4 4L19 6"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
    );
  }
  if (status === "next") {
    return (
      <span
        className="grid h-5 w-5 place-items-center rounded-pill bg-brand text-white"
        aria-label="Tiếp theo"
      >
        <span className="block h-2 w-2 rounded-full bg-white" />
      </span>
    );
  }
  return (
    <span
      className="grid h-5 w-5 place-items-center rounded-pill ring-1 ring-inset ring-ink-300"
      aria-label="Chưa đến giờ"
    >
      <span className="block h-1.5 w-1.5 rounded-full bg-ink-300" />
    </span>
  );
}

function Stat({
  value,
  label,
  tone
}: {
  value: string;
  label: string[];
  tone: "brand" | "amber" | "emerald";
}) {
  const toneCls =
    tone === "brand"
      ? "text-brand-700 bg-brand-50"
      : tone === "amber"
      ? "text-amber-700 bg-amber-50"
      : "text-emerald-700 bg-emerald-50";
  return (
    <li className={`rounded-card ${toneCls} p-2.5`}>
      <span className="block text-[24px] font-extrabold leading-none">
        {value}
      </span>
      <p className="mt-1.5 text-[10px] font-medium leading-tight text-ink-700">
        {label.map((l, i) => (
          <span key={i} className="block">
            {l}
          </span>
        ))}
      </p>
    </li>
  );
}

/* ─────────── Icons ─────────── */

function CalendarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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

function BoxIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 7l9-4 9 4-9 4-9-4z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path
        d="M3 7v10l9 4 9-4V7"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path d="M12 11v10" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function BulbIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M9 18h6M10 21h4M7 13a5 5 0 1 1 10 0c0 2-1 3-2 4v1H9v-1c-1-1-2-2-2-4z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M6 9a6 6 0 1 1 12 0c0 4 1.5 6 2 6.5H4c.5-.5 2-2.5 2-6.5z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <path d="M10 19a2 2 0 0 0 4 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="9" cy="9" r="3.4" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="17" cy="10" r="2.6" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M3 19c1-3.5 3.5-5 6-5s5 1.5 6 5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="M14.5 14.5c1-0.7 2-1 3-1 2 0 3.5 1 4.5 4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
