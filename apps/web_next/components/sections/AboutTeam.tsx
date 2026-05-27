"use client";

import { Reveal } from "../Reveal";

type Member = {
  name: string;
  role: string;
  bio?: string;
  initials: string;
  badge?: string;
  accent?: "brand" | "accent" | "success" | "warn";
};

const LEADS: Member[] = [
  {
    name: "Nguyễn Duy Thuận",
    role: "Trưởng nhóm · Kiến trúc & AI",
    bio: "Sinh viên 23DKTPM1A · MSSV 2311555799. Phụ trách kiến trúc hệ thống, fine-tune mô hình và phát triển sản phẩm tổng thể.",
    initials: "NT",
    badge: "Lead",
    accent: "brand",
  },
  {
    name: "ThS. Đỗ Gia Bảo",
    role: "Giảng viên hướng dẫn",
    bio: "Định hướng nghiên cứu, đánh giá học thuật và phản biện nội dung y khoa cho dự án.",
    initials: "GB",
    badge: "GVHD",
    accent: "accent",
  },
];

const TEAMS: Member[] = [
  {
    name: "AI Research",
    role: "ML & Vision-Language",
    bio: "Huấn luyện MedGemma 1.5 4B trên 17.263 cặp Q&A y khoa Việt (dedup từ 35.513) — kết hợp RAG hybrid và Dual LoRA Medical/Psychology.",
    initials: "AR",
    accent: "brand",
  },
  {
    name: "Backend & Data",
    role: "FastAPI · PostgreSQL",
    bio: "Xây dựng API y tế, schema hồ sơ sức khoẻ và pipeline làm sạch dữ liệu thuốc.",
    initials: "BE",
    accent: "success",
  },
  {
    name: "Mobile & Web",
    role: "Flutter · Next.js",
    bio: "Phát triển ứng dụng đa nền tảng — chia sẻ contracts qua OpenAPI để mọi client luôn đồng bộ.",
    initials: "FE",
    accent: "accent",
  },
  {
    name: "UX & Accessibility",
    role: "Thiết kế cho mọi người",
    bio: "Tập trung vào người cao tuổi, khiếm thị, khiếm thính — kiểm thử WCAG và Elderly Mode.",
    initials: "UX",
    accent: "warn",
  },
];

const ACCENT: Record<NonNullable<Member["accent"]>, { ring: string; text: string; chip: string; glow: string }> = {
  brand: {
    ring: "ring-brand-500/20",
    text: "text-brand-700",
    chip: "bg-brand-50 text-brand-700",
    glow: "hover:shadow-[0_18px_40px_-20px_rgba(2,132,199,0.5)]",
  },
  accent: {
    ring: "ring-accent/30",
    text: "text-accent-700",
    chip: "bg-accent-soft text-accent-800",
    glow: "hover:shadow-[0_18px_40px_-20px_rgba(249,115,22,0.5)]",
  },
  success: {
    ring: "ring-success/30",
    text: "text-success-700",
    chip: "bg-success-soft text-success-900",
    glow: "hover:shadow-[0_18px_40px_-20px_rgba(34,197,94,0.5)]",
  },
  warn: {
    ring: "ring-warn/30",
    text: "text-warn-800",
    chip: "bg-warn-soft text-warn-800",
    glow: "hover:shadow-[0_18px_40px_-20px_rgba(245,158,11,0.5)]",
  },
};

export function AboutTeam() {
  return (
    <section id="team" className="relative overflow-hidden bg-brand-50/30 py-16 lg:py-20">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-20 top-1/4 -z-10 h-72 w-72 rounded-full bg-brand/10 blur-3xl animate-blob"
      />

      <div className="container-page">
        <Reveal direction="up" className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Đội ngũ
          </p>
          <h2 className="text-h1 text-ink-900">Những người đứng sau MediSign</h2>
          <p className="mt-4 text-body text-ink-600">
            Một nhóm nhỏ tại TP.HCM, mỗi ngày làm 1 việc thôi: giúp người Việt chăm
            sóc sức khoẻ tại nhà dễ hơn.
          </p>
        </Reveal>

        {/* Lead row */}
        <ul className="mx-auto mt-12 grid max-w-3xl gap-5 sm:grid-cols-2">
          {LEADS.map((m, i) => {
            const tone = ACCENT[m.accent ?? "brand"];
            const dir = i === 0 ? "left" : "right";
            return (
              <Reveal
                key={m.name}
                as="li"
                direction={dir}
                delay={i * 140}
                className={`group relative rounded-card border border-ink-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-card ring-1 ring-inset ${tone.ring} ${tone.glow}`}
              >
                {m.badge && (
                  <span
                    className={`absolute right-4 top-4 rounded-pill px-2.5 py-0.5 text-[11px] font-semibold ${tone.chip}`}
                  >
                    {m.badge}
                  </span>
                )}
                <div className="flex items-center gap-4">
                  <span
                    aria-hidden="true"
                    className={`grid h-16 w-16 flex-none place-items-center rounded-pill bg-gradient-to-br from-brand-50 to-white text-xl font-bold transition-transform duration-500 ease-out group-hover:scale-110 group-hover:rotate-6 ${tone.text}`}
                  >
                    {m.initials}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-base font-semibold text-ink-900">
                      {m.name}
                    </p>
                    <p className={`mt-0.5 text-sm font-medium ${tone.text}`}>
                      {m.role}
                    </p>
                  </div>
                </div>
                {m.bio && (
                  <p className="mt-4 text-sm text-ink-600">{m.bio}</p>
                )}
              </Reveal>
            );
          })}
        </ul>

        {/* Subteams */}
        <div className="mx-auto mt-10 max-w-6xl">
          <Reveal direction="up">
            <p className="mb-5 text-center text-sm font-semibold uppercase tracking-wide text-ink-500">
              Các tổ chuyên môn
            </p>
          </Reveal>
          <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {TEAMS.map((m, i) => {
              const tone = ACCENT[m.accent ?? "brand"];
              return (
                <Reveal
                  key={m.name}
                  as="li"
                  direction="up"
                  delay={i * 100}
                  className={`group rounded-card border border-ink-200 bg-white p-5 text-center shadow-soft transition-all duration-300 hover:-translate-y-1.5 hover:border-brand/30 hover:shadow-card ${tone.glow}`}
                >
                  <span
                    aria-hidden="true"
                    className={`mx-auto mb-3 grid h-14 w-14 place-items-center rounded-pill text-base font-bold transition-transform duration-500 ease-out group-hover:scale-110 group-hover:-rotate-6 ${tone.chip}`}
                  >
                    {m.initials}
                  </span>
                  <p className="text-base font-semibold text-ink-900">{m.name}</p>
                  <p className={`mt-1 text-xs font-medium ${tone.text}`}>
                    {m.role}
                  </p>
                  {m.bio && (
                    <p className="mt-3 text-sm leading-relaxed text-ink-600">
                      {m.bio}
                    </p>
                  )}
                </Reveal>
              );
            })}
          </ul>
        </div>

        {/* University acknowledgement */}
        <Reveal direction="up" delay={200} className="mx-auto mt-12 max-w-4xl">
          <div className="rounded-card border border-ink-200 bg-white px-6 py-5 shadow-soft transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card sm:flex sm:items-center sm:justify-between sm:gap-6">
            <div className="flex items-center gap-4">
              <span
                aria-hidden="true"
                className="grid h-12 w-12 flex-none place-items-center rounded-card bg-brand-50 text-brand-700"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M3 10l9-5 9 5-9 5-9-5z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M7 12v5c0 1 2 2 5 2s5-1 5-2v-5M21 10v6"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </span>
              <div>
                <p className="text-sm font-semibold text-ink-900">
                  Đề tài Nghiên cứu Khoa học Sinh viên cấp Trường
                </p>
                <p className="mt-0.5 text-sm text-ink-600">
                  Trường Đại học Nguyễn Tất Thành · Phòng Khoa học Công nghệ ·
                  TP.HCM 2026
                </p>
              </div>
            </div>
            <span className="mt-4 inline-flex flex-none items-center gap-1.5 rounded-pill bg-success-soft px-3 py-1 text-xs font-semibold text-success-900 sm:mt-0">
              <span
                aria-hidden="true"
                className="h-1.5 w-1.5 rounded-full bg-success animate-pulse-soft"
              />
              Đang triển khai
            </span>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
