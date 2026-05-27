// "Chỉ có trên app" — 2 tính năng độc quyền app (SoulGarden + Tủ thuốc)
// Layout 2-column grid, glassmorphism cards, hover effects

import { Reveal } from "@/components/Reveal";

const APP_FEATURES = [
  {
    name: "Vườn tâm hồn",
    desc: "Không gian chăm sóc tinh thần — theo dõi cảm xúc, nuôi dưỡng thói quen tích cực.",
    cardTone: "from-emerald-50 via-green-50/50 to-white",
    iconTone: "bg-emerald-100 text-emerald-700 ring-emerald-200",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 22c-1-1-3-2-3-5 0-2 1-3 3-3s3 1 3 3c0 3-2 4-3 5z"
          fill="currentColor"
          fillOpacity="0.15"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <path
          d="M9 14c-2-1-4-3-4-6 0-2 1.5-3.5 3-3.5 1 0 2 .5 3 1.5 1-1 2-1.5 3-1.5 1.5 0 3 1.5 3 3.5 0 3-2 5-4 6"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="12" cy="8" r="1.5" fill="currentColor" fillOpacity="0.3" />
      </svg>
    ),
    decorations: (
      <>
        {/* Leaf decorations */}
        <span
          aria-hidden
          className="pointer-events-none absolute -top-2 -right-2 h-16 w-16 rounded-full bg-emerald-200/30 blur-2xl"
        />
        <span
          aria-hidden
          className="pointer-events-none absolute -bottom-3 -left-3 h-20 w-20 rounded-full bg-green-300/20 blur-2xl"
        />
        {/* Leaf icons */}
        <svg
          className="pointer-events-none absolute top-4 right-4 h-8 w-8 text-emerald-200/40"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M12 3c4 0 9 2 9 9 0 4-3 7-6 9-1-2-3-4-3-7 0-2 1-4 3-5-2-1-4-2-6-2-3 0-6 2-6 6 0 3 2 6 4 8-3-2-5-5-5-9C2 5 7 3 12 3z"
            fill="currentColor"
          />
        </svg>
        <svg
          className="pointer-events-none absolute bottom-6 left-6 h-6 w-6 text-green-200/50 rotate-45"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M12 3c4 0 9 2 9 9 0 4-3 7-6 9-1-2-3-4-3-7 0-2 1-4 3-5-2-1-4-2-6-2-3 0-6 2-6 6 0 3 2 6 4 8-3-2-5-5-5-9C2 5 7 3 12 3z"
            fill="currentColor"
          />
        </svg>
      </>
    )
  },
  {
    name: "Tủ thuốc",
    desc: "Quản lý thuốc, nhắc lịch uống và lưu đơn thuốc cho cả gia đình.",
    cardTone: "from-accent/15 to-white",
    iconTone: "bg-accent-soft text-accent ring-accent/20",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="4" y="6" width="16" height="14" rx="3" stroke="currentColor" strokeWidth="1.8" />
        <path d="M4 12h16M9 9v6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
    decorations: (
      <>
        {/* Pill decorations */}
        <span
          aria-hidden
          className="pointer-events-none absolute -top-3 -right-3 h-20 w-20 rounded-full bg-accent/20 blur-2xl"
        />
        <span
          aria-hidden
          className="pointer-events-none absolute -bottom-2 -left-2 h-16 w-16 rounded-full bg-blue-200/30 blur-2xl"
        />
        {/* Pill icons */}
        <svg
          className="pointer-events-none absolute top-5 right-5 h-7 w-7 text-accent/20 rotate-12"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <rect x="4" y="4" width="16" height="16" rx="8" fill="currentColor" />
          <rect x="4" y="4" width="16" height="8" fill="currentColor" fillOpacity="0.5" />
        </svg>
        <svg
          className="pointer-events-none absolute bottom-7 left-7 h-5 w-5 text-blue-300/30 -rotate-45"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="8" fill="currentColor" />
          <path d="M12 4v16" stroke="white" strokeWidth="2" strokeOpacity="0.5" />
        </svg>
      </>
    )
  }
];

export function AppOnlyFeaturesSection() {
  return (
    <section id="app-features" className="relative overflow-hidden py-16 lg:py-24">
      {/* Ambient gradient blobs */}
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/4 top-0 h-[360px] w-[360px] rounded-full bg-brand/8 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute right-1/4 bottom-0 h-[340px] w-[340px] rounded-full bg-accent/8 blur-3xl"
      />

      <div className="container-page relative">
        <Reveal className="text-center">
          <span className="badge-pill">Độc quyền trên app</span>
          <h2 className="mt-3 text-h1 text-ink-900">
            Chỉ có trên app
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-body text-ink-600">
            Hai tính năng đặc biệt được thiết kế riêng cho trải nghiệm di động — 
            chăm sóc tinh thần và quản lý sức khỏe toàn diện.
          </p>
        </Reveal>

        <ul className="mt-10 grid gap-6 sm:grid-cols-2 lg:mt-12 lg:gap-8 2xl:gap-10">
          {APP_FEATURES.map((feature, idx) => (
            <li key={feature.name}>
              <Reveal delay={idx * 100}>
                <button
                  type="button"
                  className={`group relative flex h-full w-full flex-col items-start gap-4 overflow-hidden rounded-card border border-ink-200 bg-gradient-to-br ${feature.cardTone} p-6 text-left shadow-soft transition-all duration-300 hover:-translate-y-1 hover:border-brand/30 hover:shadow-card cursor-pointer lg:p-8`}
                >
                  {/* Decorations (if any) */}
                  {feature.decorations}

                  {/* Icon + Badge */}
                  <div className="relative z-10 flex w-full items-start justify-between">
                    <span
                      aria-hidden
                      className={`grid h-12 w-12 flex-none place-items-center rounded-pill ring-1 transition-transform duration-300 group-hover:scale-105 ${feature.iconTone}`}
                    >
                      {feature.icon}
                    </span>
                    <span className="badge-app text-[10px]">Chỉ trên app</span>
                  </div>

                  {/* Content */}
                  <div className="relative z-10 flex-1">
                    <h3 className="text-[18px] font-semibold text-ink-900 lg:text-[20px]">
                      {feature.name}
                    </h3>
                    <p className="mt-2 text-[14px] leading-relaxed text-ink-600 lg:text-[15px]">
                      {feature.desc}
                    </p>
                  </div>

                  {/* Arrow indicator */}
                  <span
                    aria-hidden
                    className="relative z-10 self-end text-ink-400 transition-all duration-300 group-hover:translate-x-1 group-hover:text-brand-700"
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path
                        d="m9 6 6 6-6 6"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                </button>
              </Reveal>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
