"use client";

// Hàng cuối main: 2 card "Đơn thuốc gần đây" + "Tủ thuốc gia đình".

export function MedicineFooterRow() {
  return (
    <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
      <li>
        <FooterCard
          icon={<RxIcon />}
          tone="brand"
          title="Đơn thuốc gần đây"
          line1="Đơn ngày 12/05/2025"
          line2="3 loại thuốc"
        />
      </li>
      <li>
        <FooterCard
          icon={<UsersIcon />}
          tone="emerald"
          title="Tủ thuốc gia đình"
          line1="4 thành viên"
          line2="Chia sẻ & quản lý"
        />
      </li>
    </ul>
  );
}

function FooterCard({
  icon,
  tone,
  title,
  line1,
  line2
}: {
  icon: React.ReactNode;
  tone: "brand" | "emerald";
  title: string;
  line1: string;
  line2: string;
}) {
  const toneCls =
    tone === "brand"
      ? "bg-brand-50 text-brand-700"
      : "bg-emerald-50 text-emerald-700";
  return (
    <button
      type="button"
      className="flex w-full items-center gap-3 rounded-card border border-ink-200 bg-white p-4 text-left shadow-soft transition-colors hover:border-brand hover:shadow-card cursor-pointer"
    >
      <span
        className={`grid h-12 w-12 flex-none place-items-center rounded-card ${toneCls}`}
        aria-hidden="true"
      >
        {icon}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-[13px] font-semibold text-ink-900">{title}</p>
        <p className="mt-0.5 text-[11px] text-ink-700">{line1}</p>
        <p className="text-[11px] text-ink-500">{line2}</p>
      </div>
      <span aria-hidden="true" className="text-ink-400">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
  );
}

function RxIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="5" y="3" width="14" height="18" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M9 8h6M9 12h6M9 16h4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
