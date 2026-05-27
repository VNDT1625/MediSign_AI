import { Reveal } from "@/components/Reveal";
import type { ReactNode } from "react";

type Feature = {
  title: string;
  desc: string;
  badge: "Chỉ trên app" | "Web & app" | "Tất cả";
  tone: "brand" | "accent" | "success" | "ink";
  icon: ReactNode;
  /** Tailwind grid spans for lg breakpoint */
  span?: string;
  /** Optional decorative visual for featured tiles */
  visual?: ReactNode;
};

const FEATURES: Feature[] = [
  {
    title: "Tủ thuốc thông minh",
    desc: "Quét vỉ thuốc → tự nhận tên, liều, tương tác. Đồng bộ cho cả nhà và nhắc giờ uống tự động.",
    badge: "Chỉ trên app",
    tone: "accent",
    span: "lg:col-span-2 lg:row-span-2",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" strokeWidth="1.8" />
        <path d="M3 12h18M12 3v18" stroke="currentColor" strokeWidth="1.8" />
        <circle cx="7.5" cy="7.5" r="1.4" fill="currentColor" />
        <circle cx="16.5" cy="16.5" r="1.4" fill="currentColor" />
      </svg>
    ),
    visual: (
      <div className="absolute inset-x-6 bottom-6 grid grid-cols-3 gap-2">
        <PillVisual label="Paracetamol" sub="500mg · 3×/ngày" />
        <PillVisual label="Vitamin C" sub="1000mg · sáng" />
        <PillVisual label="Omega-3" sub="2 viên · tối" />
      </div>
    ),
  },
  {
    title: "Voice tiếng Việt",
    desc: "Hỏi tự nhiên, AI hiểu giọng vùng miền và trả lời như đang trò chuyện.",
    badge: "Web & app",
    tone: "brand",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="9" y="3" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="1.8" />
        <path
          d="M5 11a7 7 0 0 0 14 0M12 18v3"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
  {
    title: "SoulGarden",
    desc: "Nhật ký cảm xúc, bài tập thở. AI đồng hành chăm sóc tinh thần.",
    badge: "Chỉ trên app",
    tone: "success",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 21s-7-4.5-7-11a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 6.5-7 11-7 11h-4z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    title: "Đồng bộ đa thiết bị",
    desc: "Bắt đầu trên điện thoại, tiếp tục trên laptop. Không gián đoạn.",
    badge: "Tất cả",
    tone: "brand",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M21 12a9 9 0 0 1-15 6.7L3 16M3 12a9 9 0 0 1 15-6.7L21 8M3 4v4h4M21 20v-4h-4"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    title: "Chế độ người cao tuổi",
    desc: "Font lớn, contrast cao, nút ≥56px, đọc to nội dung khi cần.",
    badge: "Tất cả",
    tone: "ink",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
        <path
          d="M8 11v2a4 4 0 0 0 8 0v-2"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <circle cx="9" cy="9" r="1" fill="currentColor" />
        <circle cx="15" cy="9" r="1" fill="currentColor" />
      </svg>
    ),
  },
  {
    title: "Bảo mật riêng tư",
    desc: "Mã hoá đầu cuối, lưu cục bộ hoặc đám mây — bạn quyết định.",
    badge: "Tất cả",
    tone: "success",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
        <path
          d="M9 12l2 2 4-4"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
];

const TONE: Record<Feature["tone"], { tile: string; bg: string }> = {
  brand: {
    tile: "from-brand-50 to-white text-brand-700 ring-brand-100",
    bg: "from-brand-50/40 to-white",
  },
  accent: {
    tile: "from-accent-soft to-white text-accent ring-accent/30",
    bg: "from-accent-soft/40 to-white",
  },
  success: {
    tile: "from-success/10 to-white text-success ring-success/20",
    bg: "from-success/5 to-white",
  },
  ink: {
    tile: "from-ink-100 to-white text-ink-800 ring-ink-200",
    bg: "from-ink-100/60 to-white",
  },
};

const BADGE: Record<Feature["badge"], string> = {
  "Chỉ trên app": "bg-accent-soft text-accent-800",
  "Web & app": "bg-brand-50 text-brand-700",
  "Tất cả": "bg-success/15 text-success-900",
};

export function DownloadFeatures() {
  return (
    <section className="relative py-16 lg:py-20">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Có gì khi tải app
          </p>
          <h2 className="text-h1 text-ink-900">
            App có nhiều thứ <span className="gradient-text-brand">web không có</span>
          </h2>
          <p className="mt-4 text-body text-ink-600">
            Trải nghiệm trọn vẹn với camera, voice, thông báo và đồng bộ — tất cả trong cùng một app.
          </p>
        </Reveal>

        {/* Bento grid: featured 2x2 + 5 small in 3 cols */}
        <Reveal
          as="ul"
          stagger
          className="mx-auto mt-12 grid max-w-6xl auto-rows-[minmax(200px,auto)] gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {FEATURES.map((f, i) => (
            <li
              key={f.title}
              className={`reveal card-lift group relative overflow-hidden rounded-[20px] border border-ink-200 bg-gradient-to-br ${TONE[f.tone].bg} p-6 shadow-soft cursor-default ${
                f.span ?? ""
              }`}
            >
              {/* Icon tile */}
              <div
                className={`mb-4 grid h-12 w-12 place-items-center rounded-card bg-gradient-to-br ${TONE[f.tone].tile} ring-1 ring-inset transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:scale-105`}
              >
                {f.icon}
              </div>

              <span
                className={`inline-flex items-center gap-1 rounded-pill px-2.5 py-0.5 text-[11px] font-semibold ${BADGE[f.badge]}`}
              >
                {f.badge}
              </span>

              <h3 className={`mt-3 font-semibold text-ink-900 ${i === 0 ? "text-lg sm:text-xl" : "text-base"}`}>
                {f.title}
              </h3>
              <p className={`mt-2 text-ink-600 ${i === 0 ? "max-w-md text-sm sm:text-[15px]" : "text-sm"}`}>
                {f.desc}
              </p>

              {/* Featured visual */}
              {f.visual}

              {/* Bottom gradient line on hover */}
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-x-6 bottom-3 h-px origin-left scale-x-0 bg-gradient-to-r from-brand to-transparent transition-transform duration-500 group-hover:scale-x-100"
              />
            </li>
          ))}
        </Reveal>
      </div>
    </section>
  );
}

function PillVisual({ label, sub }: { label: string; sub: string }) {
  return (
    <div className="rounded-card border border-white bg-white/80 p-2.5 shadow-soft backdrop-blur">
      <div className="flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full bg-accent" />
        <span className="text-[11px] font-semibold text-ink-900">{label}</span>
      </div>
      <p className="mt-0.5 text-[10px] text-ink-500">{sub}</p>
    </div>
  );
}
