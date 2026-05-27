"use client";

import { Reveal } from "../Reveal";

type TechItem = {
  title: string;
  desc: string;
  tag: string;
  icon: React.ReactNode;
};

const TECH: TechItem[] = [
  {
    title: "Self-hosted LLM",
    tag: "MedGemma 1.5 4B · QLoRA",
    desc: "google/medgemma-1.5-4b-it fine-tune QLoRA chạy trên GPU với 4-bit quantization. Toàn bộ inference trên hạ tầng của chúng tôi — không gửi dữ liệu ra ngoài.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="6" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 10h.01M8 14h.01M12 10h4M12 14h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "RAG y khoa Hybrid",
    tag: "BM25 + Dense + RRF",
    desc: "Hybrid retrieval BM25 + Dense embedding + Reciprocal Rank Fusion trên 128.380 records (60.472 thuốc DAV, 67.493 tương tác, 3.248 bệnh Vinmec/Hello Bacsi). AI luôn trích dẫn nguồn để giảm hallucination.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M4 5a2 2 0 0 1 2-2h9l5 5v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        <path d="M14 3v6h6M8 14h8M8 18h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Dual LoRA Adapter",
    tag: "Medical · Psychology",
    desc: "Hai bộ adapter QLoRA rank 32 chạy trên cùng MedGemma 1.5 4B: Medical cho tư vấn y khoa có nguồn và disclaimer, Psychology cho chăm sóc tinh thần theo phong cách OARS — tách phong cách mà không phải duy trì hai mô hình.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="8" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
        <circle cx="16" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
      </svg>
    ),
  },
  {
    title: "Cross-platform",
    tag: "Flutter · Next.js · FastAPI",
    desc: "Một backend FastAPI duy nhất phục vụ web (Next.js) và mobile (Flutter) — code share contracts qua OpenAPI để mọi nền tảng luôn đồng bộ.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="4" width="14" height="10" rx="1.5" stroke="currentColor" strokeWidth="2" />
        <rect x="14" y="10" width="7" height="11" rx="1.5" stroke="currentColor" strokeWidth="2" />
      </svg>
    ),
  },
  {
    title: "Triage 3 cấp",
    tag: "Xanh · Vàng · Đỏ",
    desc: "Logic phân loại triệu chứng thành 3 mức khẩn cấp với khuyến nghị hành động cụ thể — đặc biệt giúp người dùng biết khi nào phải đến bệnh viện ngay.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 2l10 18H2L12 2z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        <path d="M12 9v5M12 17h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Privacy-first",
    tag: "Local · Cloud · Bạn chọn",
    desc: "Dữ liệu sức khoẻ thuộc về bạn. Tuỳ chọn lưu cục bộ trên thiết bị, hoặc đồng bộ đám mây mã hoá — bạn quyết định, không phải chúng tôi.",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 11V7a4 4 0 1 1 8 0v4" stroke="currentColor" strokeWidth="2" />
      </svg>
    ),
  },
];

export function AboutTech() {
  return (
    <section id="tech" className="relative overflow-hidden py-16 lg:py-20">
      {/* drifting accent blob */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute right-1/4 top-10 -z-10 h-56 w-56 rounded-full bg-brand/10 blur-3xl animate-blob"
        style={{ animationDelay: "-3s" }}
      />

      <div className="container-page">
        <Reveal direction="up" className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Công nghệ
          </p>
          <h2 className="text-h1 text-ink-900">Đứng trên vai những người khổng lồ</h2>
          <p className="mt-4 text-body text-ink-600">
            Chúng tôi chọn open-source, tự host và minh bạch ở mọi lớp — vì y tế cần
            sự tin cậy, không phải hộp đen.
          </p>
        </Reveal>

        <ul className="mx-auto mt-12 grid max-w-6xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {TECH.map((t, i) => {
            const dir =
              i % 3 === 0 ? "left" : i % 3 === 2 ? "right" : "up";
            return (
              <Reveal
                key={t.title}
                as="li"
                direction={dir}
                delay={(i % 3) * 90}
                className="group relative flex gap-4 overflow-hidden rounded-card border border-ink-200 bg-white p-5 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:border-brand/40 hover:shadow-card"
              >
                {/* shimmer sweep on hover */}
                <span
                  aria-hidden="true"
                  className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-brand/10 to-transparent transition-transform duration-700 group-hover:translate-x-full"
                />
                <span
                  aria-hidden="true"
                  className="grid h-10 w-10 flex-none place-items-center rounded-card bg-brand-50 text-brand-700 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3"
                >
                  {t.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <h3 className="text-base font-semibold text-ink-900">
                      {t.title}
                    </h3>
                    <span className="rounded-pill bg-ink-100 px-2 py-0.5 text-[11px] font-medium text-ink-600 transition-colors duration-200 group-hover:bg-brand-50 group-hover:text-brand-700">
                      {t.tag}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-ink-600">{t.desc}</p>
                </div>
              </Reveal>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
