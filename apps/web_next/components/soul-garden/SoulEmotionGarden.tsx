"use client";

// Vườn cảm xúc — main visual của Soul Garden.
// Hiển thị "khu vườn 3D" giả lập + 4 chip cảm xúc (Bình yên, Tự tin, Biết ơn, Hy vọng)
// floating quanh ảnh.

const CHIPS = [
  {
    label: "Bình yên",
    level: 4,
    tone: "emerald",
    icon: <LeafIcon />,
    pos: "left-2 top-12 lg:left-6 lg:top-16"
  },
  {
    label: "Tự tin",
    level: 3,
    tone: "violet",
    icon: <StarIcon />,
    pos: "right-4 top-10 lg:right-12 lg:top-14"
  },
  {
    label: "Biết ơn",
    level: 3,
    tone: "rose",
    icon: <HeartIcon />,
    pos: "left-4 bottom-16 lg:left-12 lg:bottom-20"
  },
  {
    label: "Hy vọng",
    level: 2,
    tone: "amber",
    icon: <SunIcon />,
    pos: "right-6 bottom-14 lg:right-16 lg:bottom-16"
  }
] as const;

const TONE_CLASSES: Record<
  (typeof CHIPS)[number]["tone"],
  { bg: string; text: string; iconBg: string; iconText: string }
> = {
  emerald: {
    bg: "bg-emerald-50/95",
    text: "text-emerald-900",
    iconBg: "bg-emerald-100",
    iconText: "text-emerald-700"
  },
  violet: {
    bg: "bg-violet-50/95",
    text: "text-violet-900",
    iconBg: "bg-violet-100",
    iconText: "text-violet-700"
  },
  rose: {
    bg: "bg-rose-50/95",
    text: "text-rose-900",
    iconBg: "bg-rose-100",
    iconText: "text-rose-700"
  },
  amber: {
    bg: "bg-amber-50/95",
    text: "text-amber-900",
    iconBg: "bg-amber-100",
    iconText: "text-amber-700"
  }
};

export function SoulEmotionGarden() {
  return (
    <section
      aria-labelledby="emotion-garden"
      className="relative overflow-hidden rounded-[20px] border border-ink-200 bg-white p-6 shadow-soft lg:p-7"
    >
      {/* Heading */}
      <div className="mb-3 flex items-center justify-between">
        <h2
          id="emotion-garden"
          className="inline-flex items-center gap-1.5 text-[18px] font-bold text-ink-900"
        >
          Vườn cảm xúc của bạn
          <InfoIcon />
        </h2>
      </div>
      <p className="text-[13px] text-ink-500">
        Vườn của bạn đang phát triển tốt
        <span className="ml-1 inline-block align-middle text-emerald-600">
          <SeedlingIcon />
        </span>
      </p>

      {/* Garden visual + floating chips */}
      <div className="relative mt-5 h-[280px] w-full overflow-hidden rounded-[16px] bg-gradient-to-b from-emerald-50/70 to-white">
        {/* Background scene */}
        <GardenScene />

        {/* Floating chips */}
        {CHIPS.map((chip) => {
          const tone = TONE_CLASSES[chip.tone];
          return (
            <div
              key={chip.label}
              className={`absolute ${chip.pos} flex items-center gap-2 rounded-pill border border-white/80 ${tone.bg} px-3 py-1.5 shadow-card backdrop-blur`}
            >
              <span
                className={`grid h-7 w-7 place-items-center rounded-pill ${tone.iconBg} ${tone.iconText}`}
                aria-hidden="true"
              >
                {chip.icon}
              </span>
              <span>
                <span
                  className={`block text-[13px] font-semibold leading-tight ${tone.text}`}
                >
                  {chip.label}
                </span>
                <span className="block text-[11px] text-ink-500">
                  Lv. {chip.level}
                </span>
              </span>
            </div>
          );
        })}

        {/* CTA "Khám phá vườn" */}
        <button
          type="button"
          className="absolute bottom-3 left-1/2 inline-flex -translate-x-1/2 items-center gap-1.5 rounded-pill border border-emerald-200 bg-white/95 px-4 py-1.5 text-[12px] font-semibold text-emerald-800 shadow-card hover:bg-white cursor-pointer"
        >
          <SeedlingIcon />
          Khám phá vườn
        </button>
      </div>
    </section>
  );
}

/* ─────────── Garden background scene (SVG) ─────────── */

function GardenScene() {
  return (
    <svg
      viewBox="0 0 600 300"
      preserveAspectRatio="xMidYMid slice"
      className="absolute inset-0 h-full w-full"
      aria-hidden="true"
    >
      {/* Sky gradient */}
      <defs>
        <radialGradient id="bgGlow" cx="50%" cy="80%" r="60%">
          <stop offset="0%" stopColor="#FEF3C7" stopOpacity="0.7" />
          <stop offset="100%" stopColor="#ECFDF5" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="islandShade" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#86EFAC" />
          <stop offset="100%" stopColor="#22C55E" />
        </radialGradient>
      </defs>

      <rect width="600" height="300" fill="url(#bgGlow)" />

      {/* Floating island */}
      <ellipse cx="300" cy="240" rx="170" ry="22" fill="#000" fillOpacity="0.06" />
      <ellipse cx="300" cy="230" rx="160" ry="32" fill="url(#islandShade)" />
      <ellipse cx="300" cy="225" rx="155" ry="20" fill="#BBF7D0" />

      {/* Grass tufts */}
      {[160, 200, 250, 350, 410, 440].map((x) => (
        <g key={x}>
          <path
            d={`M${x} 215 q3 -8 6 0 q3 -10 6 0 q3 -8 6 0`}
            stroke="#16A34A"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
          />
        </g>
      ))}

      {/* Central tree */}
      <g transform="translate(290, 130)">
        {/* trunk */}
        <path
          d="M8 85 L10 50 Q12 40 16 35 L20 30 L24 35 Q28 40 30 50 L32 85 z"
          fill="#92400E"
        />
        {/* canopy layers */}
        <ellipse cx="20" cy="40" rx="38" ry="30" fill="#16A34A" />
        <ellipse cx="20" cy="32" rx="32" ry="26" fill="#22C55E" />
        <ellipse cx="20" cy="26" rx="24" ry="20" fill="#4ADE80" />
        {/* highlights */}
        <ellipse cx="14" cy="22" rx="6" ry="4" fill="#86EFAC" fillOpacity="0.7" />
      </g>

      {/* Small flowers */}
      <g transform="translate(220, 215)">
        <circle cx="0" cy="0" r="4" fill="#F472B6" />
        <circle cx="-4" cy="0" r="3" fill="#F9A8D4" />
        <circle cx="4" cy="0" r="3" fill="#F9A8D4" />
        <circle cx="0" cy="-3" r="3" fill="#F9A8D4" />
        <circle cx="0" cy="0" r="2" fill="#FBBF24" />
      </g>
      <g transform="translate(380, 218)">
        <circle cx="0" cy="0" r="4" fill="#A78BFA" />
        <circle cx="-4" cy="0" r="3" fill="#C4B5FD" />
        <circle cx="4" cy="0" r="3" fill="#C4B5FD" />
        <circle cx="0" cy="-3" r="3" fill="#C4B5FD" />
        <circle cx="0" cy="0" r="2" fill="#FBBF24" />
      </g>

      {/* Bushes */}
      <ellipse cx="180" cy="220" rx="20" ry="12" fill="#16A34A" />
      <ellipse cx="195" cy="215" rx="14" ry="8" fill="#22C55E" />
      <ellipse cx="420" cy="222" rx="22" ry="13" fill="#16A34A" />
      <ellipse cx="405" cy="218" rx="13" ry="7" fill="#22C55E" />

      {/* Fallen leaves */}
      <ellipse cx="240" cy="240" rx="3" ry="2" fill="#F59E0B" transform="rotate(20 240 240)" />
      <ellipse cx="360" cy="245" rx="3" ry="2" fill="#FBBF24" transform="rotate(-15 360 245)" />
    </svg>
  );
}

/* ─────────── Tiny icons ─────────── */

function InfoIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className="text-ink-400"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 11v5M12 8.5h.01"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function SeedlingIcon() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 21v-7M12 14c0-3 2-5 5-5-1 4-3 5-5 5zM12 14c0-3-2-5-5-5 1 4 3 5 5 5z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function LeafIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 4c-9 0-15 5-15 12 0 2 0 3 1 4 3-7 8-10 12-11-3 2-7 5-9 11 6 0 11-3 12-10 1-3 0-5-1-6z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function StarIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2l3 6.5 7 .9-5 4.8 1.2 7-6.2-3.4-6.2 3.4 1.2-7-5-4.8 7-.9z" />
    </svg>
  );
}

function HeartIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 21s-7-4.5-9.5-9C1 9 2.5 5 6 5c2 0 3.5 1 6 3 2.5-2 4-3 6-3 3.5 0 5 4 3.5 7-2.5 4.5-9.5 9-9.5 9z" />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
