export function AboutHeroVisual() {
  return (
    <div
      role="img"
      aria-label="Sơ đồ hệ sinh thái MediSign AI: bác sĩ, người dùng và công nghệ"
      className="relative mx-auto aspect-square w-full max-w-[440px]"
    >
      {/* Soft gradient panel */}
      <div className="absolute inset-0 rounded-[32px] bg-gradient-to-br from-brand-50 via-white to-accent/15 shadow-card" />
      <div className="absolute inset-0 rounded-[32px] ring-1 ring-inset ring-white/60" />

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
          <div className="relative grid h-24 w-24 place-items-center rounded-pill bg-brand text-white shadow-card">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
      <Bubble label="Người dùng" sub="50K+ gia đình" pos="top-6 left-6" anim="animate-float-slow" />
      <Bubble
        label="Bác sĩ tư vấn"
        sub="Đang hợp tác"
        pos="top-6 right-6"
        tone="accent"
        anim="animate-float-mid"
        delay="-1s"
      />
      <Bubble
        label="Mô hình AI"
        sub="MedGemma 4"
        pos="bottom-6 left-6"
        tone="success"
        anim="animate-float-mid"
        delay="-2.2s"
      />
      <Bubble
        label="Dữ liệu y khoa"
        sub="18K+ cặp Q&A"
        pos="bottom-6 right-6"
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
      className={`absolute ${pos} ${anim} flex items-center gap-2 rounded-pill bg-white/95 px-3 py-1.5 shadow-card backdrop-blur transition-transform duration-200 hover:scale-105`}
      style={delay ? { animationDelay: delay } : undefined}
    >
      <span className={`h-2.5 w-2.5 flex-none rounded-full ${dot} animate-pulse-soft`} />
      <span>
        <span className="block text-xs font-semibold leading-tight text-ink-900">
          {label}
        </span>
        <span className="block text-[11px] leading-tight text-ink-500">{sub}</span>
      </span>
    </div>
  );
}
