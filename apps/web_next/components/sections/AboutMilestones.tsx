"use client";

import { Reveal } from "../Reveal";

type Milestone = {
  year: string;
  title: string;
  desc: string;
  status: "done" | "doing" | "next";
};

const MILESTONES: Milestone[] = [
  {
    year: "2025 Q3",
    title: "Khởi đầu",
    desc: "Ý tưởng MediSign — bác sĩ AI tiếng Việt cho mọi gia đình. Khảo sát người khuyết tật và người cao tuổi để xác định nhu cầu thực tế.",
    status: "done",
  },
  {
    year: "2025 Q4",
    title: "Dữ liệu y khoa",
    desc: "Thu thập, dịch và làm sạch hơn 18,764 cặp Q&A y khoa Việt từ MedQuAD, ChatDoctor và nguồn tự tạo.",
    status: "done",
  },
  {
    year: "2026 Q1",
    title: "Huấn luyện AI",
    desc: "Fine-tune MedGemma 4 với 4-bit quantization và Dual LoRA Adapter — chạy được trên 1 GPU 40GB.",
    status: "done",
  },
  {
    year: "2026 Q2",
    title: "Beta nội bộ",
    desc: "Mời người dùng đầu tiên thử nghiệm — bao gồm người cao tuổi và khiếm thính. Đo lường độ chính xác Triage qua phản hồi của bác sĩ.",
    status: "doing",
  },
  {
    year: "2026 Q3",
    title: "Mở rộng cộng đồng",
    desc: "Phát hành ứng dụng Flutter trên Android & iOS, kết nối với chuyên gia y tế tại các bệnh viện đối tác.",
    status: "next",
  },
];

const STATUS_DOT: Record<Milestone["status"], string> = {
  done: "bg-success ring-success/30",
  doing: "bg-accent ring-accent/30 animate-pulse-soft",
  next: "bg-white ring-ink-200",
};

const STATUS_CHIP: Record<Milestone["status"], { label: string; className: string }> = {
  done: {
    label: "Hoàn thành",
    className: "bg-success-soft text-success",
  },
  doing: {
    label: "Đang làm",
    className: "bg-accent-soft text-accent",
  },
  next: {
    label: "Sắp tới",
    className: "bg-ink-100 text-ink-600",
  },
};

export function AboutMilestones() {
  return (
    <section id="story" className="py-16 lg:py-20">
      <div className="container-page">
        <Reveal direction="up" className="mx-auto max-w-2xl text-center">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
            Câu chuyện
          </p>
          <h2 className="text-h1 text-ink-900">Hành trình của MediSign</h2>
          <p className="mt-4 text-body text-ink-600">
            Từ một câu hỏi cá nhân đến một sản phẩm phục vụ cộng đồng.
          </p>
        </Reveal>

        <ol className="relative mx-auto mt-12 max-w-3xl">
          {/* Vertical line */}
          <span
            aria-hidden="true"
            className="absolute left-[15px] top-2 bottom-2 w-px bg-gradient-to-b from-success via-accent to-ink-200"
          />

          {MILESTONES.map((m, i) => {
            const chip = STATUS_CHIP[m.status];
            return (
              <Reveal
                key={m.year}
                as="li"
                direction="left"
                delay={i * 120}
                distance={28}
                className="relative mb-8 pl-12 last:mb-0"
              >
                <span
                  aria-hidden="true"
                  className={`absolute left-0 top-1 grid h-8 w-8 place-items-center rounded-full border-4 border-white shadow-soft ring-2 transition-transform duration-300 hover:scale-110 ${STATUS_DOT[m.status]}`}
                >
                  {m.status === "done" && (
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d="M5 12l4 4L19 6"
                        stroke="white"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                </span>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">
                    {m.year}
                  </p>
                  <span
                    className={`rounded-pill px-2 py-0.5 text-[11px] font-semibold ${chip.className}`}
                  >
                    {chip.label}
                  </span>
                </div>
                <h3 className="mt-1 text-h3 text-ink-900">{m.title}</h3>
                <p className="mt-1 text-body text-ink-600">{m.desc}</p>
              </Reveal>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
