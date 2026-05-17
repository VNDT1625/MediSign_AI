const ITEMS = [
  {
    label: "Email",
    value: "nguyenan@gmail.com",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M3 7l9 6 9-6" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  },
  {
    label: "Số điện thoại",
    value: "0912 345 678",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A14 14 0 0 1 4 7a2 2 0 0 1 1-3z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    )
  },
  {
    label: "Ngày sinh",
    value: "14/06/1992",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  },
  {
    label: "Mục tiêu chăm sóc",
    value: "Bình an · Tự tin · Yêu thương",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
        <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
        <circle cx="12" cy="12" r="1.5" fill="currentColor" />
      </svg>
    )
  }
];

export function ProfilePersonalInfo() {
  return (
    <section
      aria-label="Thông tin cá nhân"
      className="rounded-card border border-ink-200 bg-white p-6 shadow-soft"
    >
      <header className="mb-5 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-base font-semibold text-ink-900">
          <span className="grid h-7 w-7 place-items-center rounded-pill bg-brand-50 text-brand-700">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
              <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </span>
          Thông tin cá nhân
        </h3>
        <button
          type="button"
          aria-label="Mở chi tiết"
          className="grid h-8 w-8 place-items-center rounded-pill text-ink-400 hover:bg-ink-100 hover:text-ink-700 cursor-pointer"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </header>

      <ul className="grid gap-y-4 gap-x-8 sm:grid-cols-2">
        {ITEMS.map((it) => (
          <li key={it.label} className="flex items-start gap-3">
            <span className="grid h-9 w-9 flex-none place-items-center rounded-pill bg-ink-100 text-ink-600">
              {it.icon}
            </span>
            <div className="min-w-0">
              <p className="text-xs text-ink-500">{it.label}</p>
              <p className="truncate text-sm font-medium text-ink-900">{it.value}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
