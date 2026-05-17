export function PlatformsSection() {
  const platforms = [
    {
      name: "Điện thoại",
      detail: "iOS & Android",
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="6" y="2" width="12" height="20" rx="3" stroke="currentColor" strokeWidth="2" />
          <path d="M11 18h2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      )
    },
    {
      name: "Laptop",
      detail: "Windows • macOS • Linux",
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="3" y="5" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="2" />
          <path d="M2 20h20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      )
    },
    {
      name: "Tablet",
      detail: "iPad & Android tablet",
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" strokeWidth="2" />
          <path d="M11 18h2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      )
    },
    {
      name: "Web",
      detail: "Trình duyệt bất kỳ",
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
          <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" stroke="currentColor" strokeWidth="2" />
        </svg>
      )
    }
  ];

  return (
    <section className="py-20 lg:py-28 bg-white">
      <div className="container-page">
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Đa nền tảng
          </p>
          <h2 className="text-h1 text-ink-900">
            Bác sĩ AI sẵn sàng trên mọi thiết bị của bạn
          </h2>
          <p className="mt-4 text-body text-ink-600">
            Đồng bộ liền mạch — bắt đầu cuộc trò chuyện trên điện thoại, tiếp tục trên laptop, kết
            thúc trên tablet.
          </p>
        </div>

        <ul className="mx-auto mt-12 grid max-w-5xl grid-cols-2 gap-4 lg:grid-cols-4 lg:gap-6">
          {platforms.map((p) => (
            <li
              key={p.name}
              className="card-soft text-center hover:border-brand hover:shadow-card cursor-default"
            >
              <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-pill bg-brand-50 text-brand-700">
                {p.icon}
              </div>
              <h3 className="text-h3 text-ink-900">{p.name}</h3>
              <p className="mt-1 text-sm text-ink-500">{p.detail}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
