const ITEMS = [
  {
    title: "Vườn cây của tôi",
    desc: "Xem và chăm sóc khu vườn cảm xúc của bạn",
    tone: "success",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 21c-3-3-7-6-7-11a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5-4 8-7 11z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    )
  },
  {
    title: "Nhật ký của tôi",
    desc: "Xem lại hành trình cảm xúc",
    tone: "brand",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M5 4h11a3 3 0 0 1 3 3v13l-3-2-3 2-3-2-3 2-2-2V6a2 2 0 0 1 2-2zM9 9h7M9 13h5"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    )
  },
  {
    title: "Huy hiệu & Thành tựu",
    desc: "Thành tích trong hành trình chữa lành",
    tone: "warn",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77 5.82 21l1.18-6.88-5-4.87 6.91-1.01L12 2z" />
      </svg>
    )
  },
  {
    title: "Âm nhạc yêu thích",
    desc: "Những giai điệu giúp bạn thư giãn",
    tone: "purple",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M9 18V5l12-2v13" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        <circle cx="6" cy="18" r="3" stroke="currentColor" strokeWidth="2" />
        <circle cx="18" cy="16" r="3" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  }
];

const TONE: Record<string, string> = {
  success: "bg-success/12 text-success",
  brand: "bg-brand-50 text-brand-700",
  warn: "bg-warn/15 text-warn",
  purple: "bg-purple-100 text-purple-600"
};

export function ProfileJourney() {
  return (
    <section aria-label="Hành trình của tôi">
      <h3 className="mb-3 flex items-center gap-2 text-base font-semibold text-ink-900">
        <span className="grid h-7 w-7 place-items-center rounded-pill bg-success/12 text-success">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M12 21c-3-3-7-6-7-11a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5-4 8-7 11z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        Hành trình của tôi
      </h3>

      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {ITEMS.map((it) => (
          <li key={it.title}>
            <button
              type="button"
              className="group flex w-full items-center gap-3 rounded-card border border-ink-200 bg-white p-4 text-left shadow-soft transition-shadow hover:border-brand/30 hover:shadow-card cursor-pointer"
            >
              <span className={`grid h-10 w-10 flex-none place-items-center rounded-pill ${TONE[it.tone]}`}>
                {it.icon}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-ink-900">{it.title}</span>
                <span className="block text-xs text-ink-500">{it.desc}</span>
              </span>
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
                className="flex-none text-ink-400 transition-transform group-hover:translate-x-0.5 group-hover:text-brand"
              >
                <path
                  d="M9 6l6 6-6 6"
                  stroke="currentColor"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
