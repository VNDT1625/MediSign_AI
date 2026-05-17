import { Reveal } from "@/components/Reveal";

export function PricingCTA({ onCta }: { onCta?: () => void }) {
  return (
    <section aria-labelledby="pricing-cta-heading" className="pb-16 lg:pb-24">
      <div className="container-page">
        <Reveal className="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-[#0B3A8C] via-brand to-[#0369A1] px-6 py-14 shadow-card lg:px-14 lg:py-16">
          {/* Ambient blobs */}
          <span
            aria-hidden
            className="anim-blob-drift pointer-events-none absolute -left-20 -top-20 h-80 w-80 rounded-full bg-white/8 blur-3xl"
          />
          <span
            aria-hidden
            className="anim-blob-drift pointer-events-none absolute -right-16 -bottom-16 h-80 w-80 rounded-full bg-accent/15 blur-3xl"
            style={{ animationDelay: "-5s" }}
          />
          {/* Subtle grid pattern overlay */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage:
                "linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)",
              backgroundSize: "40px 40px"
            }}
          />

          <div className="relative mx-auto max-w-2xl text-center">
            {/* Shield icon */}
            <div
              aria-hidden
              className="mx-auto mb-6 grid h-16 w-16 place-items-center rounded-card bg-white/15 ring-1 ring-inset ring-white/25"
            >
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" className="text-white">
                <path
                  d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinejoin="round"
                />
                <path d="M12 8v6M9 11h6" stroke="white" strokeWidth="2.2" strokeLinecap="round" />
              </svg>
            </div>

            <h2
              id="pricing-cta-heading"
              className="text-h1 text-white [text-wrap:balance]"
            >
              Bắt đầu hành trình sức khoẻ của bạn hôm nay
            </h2>
            <p className="mt-4 text-base text-white/80 [text-wrap:balance]">
              Hơn 50.000 người Việt đã tin tưởng MediSign AI. Dùng thử miễn phí 7 ngày,
              không cần thẻ tín dụng.
            </p>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                onClick={onCta}
                className="card-lift group inline-flex cursor-pointer items-center gap-2 rounded-pill bg-white px-7 py-3.5 text-base font-semibold text-brand-700 shadow-soft transition-colors duration-200 hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-700"
              >
                Bắt đầu miễn phí
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                  className="transition-transform duration-300 group-hover:translate-x-1"
                >
                  <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <a
                href="/about"
                className="inline-flex cursor-pointer items-center gap-2 rounded-pill border border-white/35 px-7 py-3.5 text-base font-semibold text-white transition-colors duration-200 hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-700"
              >
                Tìm hiểu thêm
              </a>
            </div>

            {/* Social proof row */}
            <div className="mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm text-white/70">
              <span className="flex items-center gap-2">
                <StarRow />
                <span>4.9/5 từ 2.000+ đánh giá</span>
              </span>
              <span aria-hidden className="hidden h-4 w-px bg-white/25 sm:block" />
              <span>50.000+ người dùng</span>
              <span aria-hidden className="hidden h-4 w-px bg-white/25 sm:block" />
              <span>Dùng thử 7 ngày miễn phí</span>
            </div>

            {/* Trust badges row */}
            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              {TRUST_BADGES.map((b) => (
                <div
                  key={b.label}
                  className="flex items-center gap-1.5 rounded-pill border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/80 backdrop-blur-sm"
                >
                  <span aria-hidden className="text-white/60">{b.icon}</span>
                  {b.label}
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function StarRow() {
  return (
    <span className="flex items-center gap-0.5" aria-label="5 sao">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
          className="text-yellow-300"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      ))}
    </span>
  );
}

const TRUST_BADGES = [
  {
    label: "Mã hoá SSL",
    icon: (
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  },
  {
    label: "Không phí ẩn",
    icon: (
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  },
  {
    label: "Huỷ dễ dàng",
    icon: (
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  },
  {
    label: "Hỗ trợ 24/7",
    icon: (
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
        <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  }
];
