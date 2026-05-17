export function SecuritySection() {
  const doors = [
    {
      title: "Bảo mật riêng tư",
      caption: "Tin nhắn an toàn 100%",
      desc: "Toàn bộ trò chuyện được mã hoá đầu cuối, lưu cục bộ trên thiết bị của bạn.",
      tone: "from-brand-50 to-white",
      icon: (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
          <path d="M8 11V7a4 4 0 1 1 8 0v4" stroke="currentColor" strokeWidth="2" />
        </svg>
      )
    },
    {
      title: "Đám mây tiện lợi",
      caption: "Đồng bộ đa thiết bị",
      desc: "Tự động sao lưu lịch sử khám và đơn thuốc, sẵn sàng truy cập từ mọi nơi.",
      tone: "from-accent/15 to-white",
      icon: (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M7 18a4 4 0 0 1-.4-7.97A6 6 0 0 1 18 10.5 4.5 4.5 0 0 1 17 18H7z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinejoin="round"
          />
        </svg>
      )
    }
  ];

  return (
    <section className="py-20 lg:py-28 bg-brand-50/60">
      <div className="container-page">
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Bảo mật
          </p>
          <h2 className="text-h1 text-ink-900">Hai cánh cửa, một sự an tâm</h2>
          <p className="mt-4 text-body text-ink-600">
            Bạn được toàn quyền chọn lưu dữ liệu cục bộ hay đồng bộ đám mây. Dù chọn cách nào,
            quyền riêng tư vẫn là ưu tiên số một.
          </p>
        </div>

        <div className="mx-auto mt-12 grid max-w-5xl gap-6 md:grid-cols-2">
          {doors.map((d) => (
            <article
              key={d.title}
              className={`relative overflow-hidden rounded-card border border-ink-200 bg-gradient-to-br ${d.tone} p-8 shadow-soft`}
            >
              <div className="mb-5 grid h-16 w-16 place-items-center rounded-pill bg-white text-brand-700 shadow-soft">
                {d.icon}
              </div>
              <h3 className="text-h2 text-ink-900">{d.title}</h3>
              <p className="mt-1 text-base font-semibold text-brand-700">{d.caption}</p>
              <p className="mt-3 text-body text-ink-600">{d.desc}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
