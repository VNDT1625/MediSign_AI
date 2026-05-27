import { Reveal } from "@/components/Reveal";

export function CTABanner({ onCta }: { onCta?: () => void }) {
  return (
    <section id="cta" className="pb-16 lg:pb-20 2xl:pb-24">
      <div className="container-page">
        <Reveal className="relative overflow-hidden rounded-[20px] bg-gradient-to-r from-[#0B3A8C] via-brand to-[#0F4FBF] px-5 py-7 shadow-card sm:rounded-[28px] sm:px-6 sm:py-8 lg:px-10">
          {/* Animated ambient glow */}
          <div
            aria-hidden="true"
            className="anim-blob-drift pointer-events-none absolute -left-16 -top-16 h-72 w-72 rounded-full bg-white/10 blur-3xl"
          />
          <div
            aria-hidden="true"
            className="anim-blob-drift pointer-events-none absolute -right-12 -bottom-12 h-72 w-72 rounded-full bg-accent/20 blur-3xl"
            style={{ animationDelay: "-5s" }}
          />

          <div className="relative grid items-center gap-5 sm:gap-6 lg:grid-cols-[1fr_auto] lg:gap-10">
            <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-5">
              <div className="hidden h-20 w-20 flex-none rounded-card bg-white/10 ring-1 ring-inset ring-white/20 sm:grid sm:place-items-center lg:h-24 lg:w-24">
                <span className="grid h-12 w-12 place-items-center rounded-pill bg-white text-brand-700 shadow-soft">
                  <svg
                    width="22"
                    height="22"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M12 21s-7-4.5-7-11a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 6.5-7 11-7 11h-4z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
              </div>
              <div>
                <h2 className="text-[22px] font-bold leading-tight text-white sm:text-2xl lg:text-3xl">
                  Sức khoẻ của bạn,
                  <br className="hidden sm:block" />
                  <span className="sm:hidden"> </span>ưu tiên hàng đầu của chúng tôi.
                </h2>
                <p className="mt-2 text-[14px] text-white/85 sm:text-sm sm:text-white/80">
                  Bắt đầu chăm sóc sức khoẻ cùng bác sĩ AI của bạn — MediSign AI luôn đồng hành.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onCta}
              className="card-lift group inline-flex w-full items-center justify-center gap-2 rounded-pill bg-white px-7 py-3.5 text-base font-semibold text-brand-700 shadow-soft hover:bg-brand-50 sm:w-auto lg:self-center cursor-pointer"
            >
              Bắt đầu ngay
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
                className="transition-transform duration-300 group-hover:translate-x-1"
              >
                <path
                  d="M5 12h14M13 6l6 6-6 6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
