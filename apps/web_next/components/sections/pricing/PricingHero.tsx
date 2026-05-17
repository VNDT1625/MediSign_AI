import { Reveal } from "@/components/Reveal";

export function PricingHero({ onCta }: { onCta?: () => void }) {
  return (
    <section
      aria-labelledby="pricing-hero-heading"
      className="relative overflow-hidden bg-gradient-to-b from-[#F0F9FF] via-white to-white pt-28 pb-0 lg:pt-36"
    >
      {/* Ambient blobs — subtle, không distract */}
      <span
        aria-hidden
        className="pointer-events-none absolute -top-40 -left-40 h-[480px] w-[480px] rounded-full bg-brand/6 blur-3xl"
      />
      <span
        aria-hidden
        className="pointer-events-none absolute top-0 right-0 h-80 w-80 rounded-full bg-[#0EA5E9]/6 blur-3xl"
      />

      <div className="container-page relative">
        {/* ── Hero copy ── */}
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="badge-pill">Bảng giá minh bạch</span>

          <h1
            id="pricing-hero-heading"
            className="mt-4 text-h1 text-ink-900 [text-wrap:balance]"
          >
            Chăm sóc sức khoẻ không giới hạn,{" "}
            <span className="gradient-text-brand">giá phù hợp túi tiền</span>
          </h1>

          <p className="mt-4 text-body text-ink-600 [text-wrap:balance]">
            Bắt đầu miễn phí, nâng cấp khi bạn cần. Đổi gói hoặc huỷ bất cứ lúc nào —
            không ràng buộc, không phí ẩn.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <button
              type="button"
              onClick={onCta}
              className="btn-primary cursor-pointer shadow-[0_4px_14px_rgba(2,132,199,0.35)] hover:shadow-[0_6px_20px_rgba(2,132,199,0.45)]"
            >
              Bắt đầu miễn phí
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <a href="#plans" className="btn-outline cursor-pointer">
              Xem các gói
            </a>
          </div>
        </Reveal>

        {/* ── Metrics bar — social proof ngay dưới headline ── */}
        <Reveal delay={180} className="mx-auto mt-12 max-w-4xl">
          <div className="grid grid-cols-2 gap-4 rounded-card border border-ink-200 bg-white p-6 shadow-soft sm:grid-cols-4">
            {METRICS.map((m) => (
              <div key={m.label} className="text-center">
                <div className="text-2xl font-bold text-ink-900 lg:text-3xl">{m.value}</div>
                <div className="mt-1 text-sm text-ink-500">{m.label}</div>
              </div>
            ))}
          </div>
        </Reveal>

        {/* ── Trust badges ── */}
        <Reveal delay={260} className="mx-auto mt-6 flex max-w-3xl flex-wrap items-center justify-center gap-3 pb-16 lg:pb-20">
          {TRUST_ITEMS.map((item) => (
            <div
              key={item.label}
              className="flex items-center gap-2 rounded-pill border border-ink-200 bg-white px-4 py-2 text-sm font-medium text-ink-700 shadow-soft"
            >
              <span
                aria-hidden
                className="grid h-5 w-5 flex-none place-items-center rounded-full bg-success-soft text-success"
              >
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
                  <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              {item.label}
            </div>
          ))}
        </Reveal>
      </div>
    </section>
  );
}

const METRICS = [
  { value: "50.000+", label: "Người dùng tin tưởng" },
  { value: "4.9★", label: "Đánh giá trung bình" },
  { value: "24/7", label: "Hỗ trợ không nghỉ" },
  { value: "99.9%", label: "Uptime đảm bảo" }
];

const TRUST_ITEMS = [
  { label: "Dùng thử 7 ngày miễn phí" },
  { label: "Huỷ bất cứ lúc nào" },
  { label: "Không phí ẩn" },
  { label: "Dữ liệu mã hoá end-to-end" },
  { label: "Không cần thẻ tín dụng" }
];
