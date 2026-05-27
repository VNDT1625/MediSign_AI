export function AboutHeroVisual() {
  return (
    <div
      role="img"
      aria-label="Sơ đồ kiến trúc MediSign AI: Knowledge Base, MedGemma, FastAPI và Dataset Q&A y khoa"
      className="relative mx-auto aspect-square w-full max-w-[320px] sm:max-w-[400px] lg:max-w-[440px]"
    >
      {/* Soft gradient panel */}
      <div className="absolute inset-0 rounded-[24px] bg-gradient-to-br from-brand-50 via-white to-accent/15 shadow-card sm:rounded-[32px]" />
      <div className="absolute inset-0 rounded-[24px] ring-1 ring-inset ring-white/60 sm:rounded-[32px]" />

      {/* Slow rotating background ring */}
      <div
        aria-hidden="true"
        className="absolute inset-6 rounded-full border border-dashed border-brand/20 animate-spin-slow"
      />
      <div
        aria-hidden="true"
        className="absolute inset-14 rounded-full border border-dashed border-accent/20 animate-spin-slow"
        style={{ animationDirection: "reverse", animationDuration: "30s" }}
      />

      {/* Center logo with pulsing halo */}
      <div className="absolute inset-0 grid place-items-center">
        <div className="relative">
          <span
            aria-hidden="true"
            className="absolute -inset-3 rounded-pill bg-brand/20 blur-md animate-pulse-soft"
          />
          <span
            aria-hidden="true"
            className="absolute -inset-6 rounded-pill bg-brand/10 blur-lg animate-pulse-soft"
            style={{ animationDelay: "-1.2s" }}
          />
          <div className="relative grid h-16 w-16 place-items-center rounded-pill bg-brand text-white shadow-card sm:h-20 sm:w-20 lg:h-24 lg:w-24">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="sm:h-9 sm:w-9 lg:h-10 lg:w-10">
              <path
                d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"
                fill="white"
                fillOpacity="0.18"
                stroke="white"
                strokeWidth="1.5"
              />
              <path d="M12 8v6M9 11h6" stroke="white" strokeWidth="2.4" strokeLinecap="round" />
            </svg>
          </div>
        </div>
      </div>

      {/* Orbiting bubbles */}
      <Bubble label="Knowledge Base" sub="128K+ records" pos="top-3 left-3 sm:top-6 sm:left-6" anim="animate-float-slow" />
      <Bubble
        label="FastAPI"
        sub="77 endpoints"
        pos="top-3 right-3 sm:top-6 sm:right-6"
        tone="accent"
        anim="animate-float-mid"
        delay="-1s"
      />
      <Bubble
        label="MedGemma 4B"
        sub="QLoRA · self-hosted"
        pos="bottom-3 left-3 sm:bottom-6 sm:left-6"
        tone="success"
        anim="animate-float-mid"
        delay="-2.2s"
      />
      <Bubble
        label="Dataset Q&A"
        sub="17K+ cặp y khoa VN"
        pos="bottom-3 right-3 sm:bottom-6 sm:right-6"
        anim="animate-float-fast"
        delay="-0.5s"
      />

      {/* Connecting dashed lines with flowing dash animation */}
      <svg
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 h-full w-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        <g
          stroke="#0284C7"
          strokeOpacity="0.35"
          strokeWidth="0.4"
          strokeDasharray="1.2 1.2"
          fill="none"
        >
          <line x1="20" y1="20" x2="50" y2="50">
            <animate
              attributeName="stroke-dashoffset"
              values="0;-12"
              dur="2.4s"
              repeatCount="indefinite"
            />
          </line>
          <line x1="80" y1="20" x2="50" y2="50">
            <animate
              attributeName="stroke-dashoffset"
              values="0;-12"
              dur="3.2s"
              repeatCount="indefinite"
            />
          </line>
          <line x1="20" y1="80" x2="50" y2="50">
            <animate
              attributeName="stroke-dashoffset"
              values="0;-12"
              dur="2.8s"
              repeatCount="indefinite"
            />
          </line>
          <line x1="80" y1="80" x2="50" y2="50">
            <animate
              attributeName="stroke-dashoffset"
              values="0;-12"
              dur="3.6s"
              repeatCount="indefinite"
            />
          </line>
        </g>
      </svg>
    </div>
  );
}

function Bubble({
  label,
  sub,
  pos,
  tone = "brand",
  anim = "animate-float-mid",
  delay,
}: {
  label: string;
  sub: string;
  pos: string;
  tone?: "brand" | "accent" | "success";
  anim?: string;
  delay?: string;
}) {
  const dot =
    tone === "accent" ? "bg-accent" : tone === "success" ? "bg-success" : "bg-brand";
  return (
    <div
      className={`absolute ${pos} ${anim} flex items-center gap-1.5 rounded-pill bg-white/95 px-2 py-1 shadow-card backdrop-blur transition-transform duration-200 hover:scale-105 sm:gap-2 sm:px-3 sm:py-1.5`}
      style={delay ? { animationDelay: delay } : undefined}
    >
      <span className={`h-2 w-2 flex-none rounded-full ${dot} animate-pulse-soft sm:h-2.5 sm:w-2.5`} />
      <span>
        <span className="block text-[10px] font-semibold leading-tight text-ink-900 sm:text-xs">
          {label}
        </span>
        <span className="block text-[9px] leading-tight text-ink-500 sm:text-[11px]">{sub}</span>
      </span>
    </div>
  );
}
