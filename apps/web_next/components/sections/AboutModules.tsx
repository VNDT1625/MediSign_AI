"use client";

import { Reveal } from "../Reveal";

type Module = {
  title: string;
  desc: string;
  bullets: string[];
  tone: "brand" | "accent" | "success" | "warn";
  icon: React.ReactNode;
};

const MODULES: Module[] = [
  {
    title: "AI Medical Assistant",
    desc: "Trợ lý y khoa hiểu tiếng Việt, kết hợp RAG với cơ sở tri thức y tế đã được kiểm chứng.",
    tone: "brand",
    bullets: [
      "Self-hosted LLM (MedGemma 1.5 4B) — không phụ thuộc API ngoài",
      "Phân loại khẩn cấp 3 mức Xanh / Vàng / Đỏ",
      "Trích nguồn rõ ràng, giảm hallucination",
    ],
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
        <path d="M12 8v4M12 15h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Camera Quét Thuốc",
    desc: "Đưa máy ảnh lên hộp thuốc — AI đọc tên, tra cứu công dụng và cảnh báo tương tác.",
    tone: "accent",
    bullets: [
      "Vision-Language model đọc nhãn thuốc",
      "Tra cứu trong CSDL 60.472 thuốc DAV Việt Nam",
      "67.493 cảnh báo tương tác thuốc nguy hiểm",
    ],
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="7" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 7l1.5-3h5L16 7" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        <circle cx="12" cy="13.5" r="3.5" stroke="currentColor" strokeWidth="2" />
      </svg>
    ),
  },
  {
    title: "Soul Garden",
    desc: "Nhật ký sức khoẻ tinh thần — chăm cây mỗi ngày, AI giúp phát hiện sớm trầm cảm.",
    tone: "success",
    bullets: [
      "3 cách nhập: text, voice, biểu tượng cảm xúc",
      "Phân tích xu hướng tâm trạng dài hạn",
      "Gamification: Cây Tâm Hồn lớn dần theo bạn",
    ],
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 21V11M12 11c0-3 2-6 6-6 0 3-2 6-6 6zM12 13c0-2.5-1.7-5-5-5 0 2.5 1.7 5 5 5z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    title: "Hỗ trợ Người Khuyết Tật",
    desc: "Avatar bác sĩ 3D giao tiếp đa phương thức cho 5 nhóm khuyết tật và người cao tuổi.",
    tone: "warn",
    bullets: [
      "Văn bản — Hình ảnh — Giọng nói — Ngôn ngữ ký hiệu",
      "Thiết kế WCAG AA, font lớn, vùng chạm 44px+",
      "Hoạt động cả khi mạng yếu",
    ],
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="6" r="2.5" stroke="currentColor" strokeWidth="2" />
        <path
          d="M12 9v6M9 12h6M8 21l2-6M16 21l-2-6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
];

const TONE_BG: Record<Module["tone"], string> = {
  brand: "bg-brand-50 text-brand-700",
  accent: "bg-accent-soft text-accent",
  success: "bg-success-soft text-success",
  warn: "bg-warn-soft text-warn",
};

const TONE_HOVER: Record<Module["tone"], string> = {
  brand: "hover:border-brand/40 hover:shadow-[0_18px_40px_-20px_rgba(2,132,199,0.45)]",
  accent: "hover:border-accent/40 hover:shadow-[0_18px_40px_-20px_rgba(249,115,22,0.45)]",
  success: "hover:border-success/40 hover:shadow-[0_18px_40px_-20px_rgba(34,197,94,0.45)]",
  warn: "hover:border-warn/40 hover:shadow-[0_18px_40px_-20px_rgba(245,158,11,0.45)]",
};

export function AboutModules() {
  return (
    <section id="modules" className="relative overflow-hidden bg-ink-100/50 py-16 lg:py-20">
      {/* subtle dotted background */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 opacity-40"
        style={{
          backgroundImage:
            "radial-gradient(rgba(2,132,199,0.10) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          maskImage:
            "radial-gradient(ellipse at center, black 30%, transparent 75%)",
          WebkitMaskImage:
            "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        }}
      />

      <div className="container-page">
        <Reveal direction="up" className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Sản phẩm
          </p>
          <h2 className="text-h1 text-ink-900">Bốn mô-đun, một mục tiêu</h2>
          <p className="mt-4 text-body text-ink-600">
            MediSign không phải một chatbot đơn lẻ. Đó là hệ thống bốn mô-đun, mỗi
            mô-đun giải một bài toán khác nhau cho cùng một người dùng.
          </p>
        </Reveal>

        <ul className="mx-auto mt-12 grid max-w-6xl gap-5 md:grid-cols-2">
          {MODULES.map((m, i) => (
            <Reveal
              key={m.title}
              as="li"
              direction="up"
              delay={i * 110}
              className={`group rounded-card border border-ink-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1.5 ${TONE_HOVER[m.tone]}`}
            >
              <div className="flex items-start gap-4">
                <span
                  className={`grid h-12 w-12 flex-none place-items-center rounded-card transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3 ${TONE_BG[m.tone]}`}
                  aria-hidden="true"
                >
                  {m.icon}
                </span>
                <div className="flex-1">
                  <h3 className="text-h3 text-ink-900 transition-colors duration-200 group-hover:text-brand-700">
                    {m.title}
                  </h3>
                  <p className="mt-1.5 text-sm text-ink-600">{m.desc}</p>
                </div>
              </div>

              <ul className="mt-5 space-y-2 border-t border-ink-200 pt-4">
                {m.bullets.map((b) => (
                  <li
                    key={b}
                    className="flex items-start gap-2 text-sm text-ink-700"
                  >
                    <span
                      className="mt-1.5 h-1.5 w-1.5 flex-none rounded-full bg-ink-400 transition-colors duration-200 group-hover:bg-brand"
                      aria-hidden="true"
                    />
                    {b}
                  </li>
                ))}
              </ul>
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  );
}
