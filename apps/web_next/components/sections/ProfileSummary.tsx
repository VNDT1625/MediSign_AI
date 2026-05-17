export function ProfileSummary() {
  return (
    <section className="relative overflow-hidden pt-28 pb-10 lg:pt-32 lg:pb-12">
      {/* Background mềm */}
      <div
        aria-hidden="true"
        className="absolute inset-0 -z-10 bg-gradient-to-b from-brand-50 via-white to-white"
      />
      <div
        aria-hidden="true"
        className="absolute -top-32 left-1/2 -z-10 h-[420px] w-[1100px] -translate-x-1/2 rounded-full bg-brand/10 blur-3xl"
      />

      <div className="container-page">
        <div className="mx-auto flex max-w-5xl flex-col items-start gap-6 rounded-card border border-ink-200 bg-white p-6 shadow-soft sm:flex-row sm:items-center sm:p-8">
          {/* Avatar */}
          <div className="relative">
            <div
              aria-hidden="true"
              className="grid h-24 w-24 place-items-center rounded-pill bg-gradient-to-br from-brand-100 to-accent/20 text-3xl font-bold text-brand-700"
            >
              N
            </div>
            <button
              type="button"
              aria-label="Đổi ảnh đại diện"
              className="absolute -bottom-1 -right-1 grid h-9 w-9 place-items-center rounded-pill border-2 border-white bg-brand text-white shadow-soft hover:bg-brand-700 cursor-pointer"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M4 7h3l2-3h6l2 3h3v12H4V7z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinejoin="round"
                />
                <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="2" />
              </svg>
            </button>
          </div>

          {/* Tên + email + plan */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-h2 text-ink-900">Nguyễn Văn A</h1>
              <span className="badge-app">MediSign Pro</span>
            </div>
            <p className="mt-1 text-base text-ink-600">nguyenvana@example.com · 0901 234 567</p>
            <ul className="mt-4 grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
              <Stat label="Cuộc hội thoại" value="48" />
              <Stat label="Triệu chứng đã ghi" value="12" />
              <Stat label="Thuốc đang theo dõi" value="3" />
              <Stat label="Ngày đồng hành" value="76" />
            </ul>
          </div>

          {/* Action */}
          <div className="flex w-full flex-col gap-2 sm:w-auto">
            <button type="button" className="btn-primary">
              Lưu thay đổi
            </button>
            <button type="button" className="btn-outline">
              Xem hoạt động
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <li className="rounded-card bg-ink-100/60 px-3 py-2">
      <span className="block text-xs text-ink-500">{label}</span>
      <span className="block text-lg font-bold text-ink-900">{value}</span>
    </li>
  );
}
