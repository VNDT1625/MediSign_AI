"use client";

import { Reveal } from "../Reveal";

type Value = {
  title: string;
  desc: string;
  tone: "brand" | "accent" | "success" | "warn";
  icon: React.ReactNode;
};

const VALUES: Value[] = [
  {
    title: "Tin cậy",
    tone: "brand",
    desc: "Mọi thông tin y khoa được kiểm chứng. AI luôn nói rõ giới hạn của mình.",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
        <path
          d="M9 12l2 2 4-4"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    title: "Bao quát",
    tone: "accent",
    desc: "Người cao tuổi, khiếm thị, khiếm thính, bệnh nhân ở vùng sâu — đều dùng được.",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
        <path
          d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
  {
    title: "Riêng tư",
    tone: "success",
    desc: "Bạn chọn lưu cục bộ hay đám mây. Dữ liệu y tế là của bạn, không phải của chúng tôi.",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
        <path d="M8 11V7a4 4 0 1 1 8 0v4" stroke="currentColor" strokeWidth="2" />
      </svg>
    ),
  },
  {
    title: "Khiêm tốn",
    tone: "warn",
    desc: "AI là gợi ý, không thay bác sĩ. Chúng tôi nhắc bạn đi khám khi cần thiết.",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
        <path
          d="M9 9.5a3 3 0 1 1 4.4 2.6c-.9.5-1.4 1.1-1.4 1.9M12 17h.01"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
];

const TONE: Record<Value["tone"], { chip: string; ring: string; glow: string }> = {
  brand: {
    chip: "bg-brand-50 text-brand-700",
    ring: "group-hover:ring-brand/30",
    glow: "group-hover:shadow-[0_18px_40px_-20px_rgba(2,132,199,0.5)]",
  },
  accent: {
    chip: "bg-accent-soft text-accent",
    ring: "group-hover:ring-accent/30",
    glow: "group-hover:shadow-[0_18px_40px_-20px_rgba(249,115,22,0.5)]",
  },
  success: {
    chip: "bg-success-soft text-success",
    ring: "group-hover:ring-success/30",
    glow: "group-hover:shadow-[0_18px_40px_-20px_rgba(34,197,94,0.5)]",
  },
  warn: {
    chip: "bg-warn-soft text-warn",
    ring: "group-hover:ring-warn/30",
    glow: "group-hover:shadow-[0_18px_40px_-20px_rgba(245,158,11,0.5)]",
  },
};

export function AboutValues() {
  return (
    <section id="values" className="py-16 lg:py-20">
      <div className="container-page">
        <Reveal direction="up" className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Giá trị cốt lõi
          </p>
          <h2 className="text-h1 text-ink-900">Bốn điều chúng tôi luôn giữ</h2>
          <p className="mt-4 text-body text-ink-600">
            Không phải tính năng nào cũng nên có. Bốn nguyên tắc dưới đây quyết
            định cái gì được vào và cái gì bị loại khỏi MediSign.
          </p>
        </Reveal>

        <ul className="mx-auto mt-12 grid max-w-6xl gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {VALUES.map((v, idx) => {
            const tone = TONE[v.tone];
            const dir = idx % 2 === 0 ? "up" : "scale";
            return (
              <Reveal
                key={v.title}
                as="li"
                direction={dir}
                delay={idx * 100}
                className={`group relative rounded-card border border-ink-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1.5 hover:border-transparent ring-1 ring-inset ring-transparent ${tone.ring} ${tone.glow}`}
              >
                <span
                  aria-hidden="true"
                  className="absolute right-5 top-5 text-xs font-bold text-ink-200 transition-colors duration-200 group-hover:text-brand-700"
                >
                  0{idx + 1}
                </span>
                <div
                  aria-hidden="true"
                  className={`mb-4 grid h-12 w-12 place-items-center rounded-card transition-transform duration-500 ease-out group-hover:scale-110 group-hover:rotate-6 ${tone.chip}`}
                >
                  {v.icon}
                </div>
                <h3 className="text-base font-semibold text-ink-900">{v.title}</h3>
                <p className="mt-2 text-sm text-ink-600">{v.desc}</p>
              </Reveal>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
