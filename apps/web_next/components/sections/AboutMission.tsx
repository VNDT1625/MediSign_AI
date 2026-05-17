"use client";

import { Reveal } from "../Reveal";
import { CountUp } from "../CountUp";

type Stat = {
  end: number;
  format?: boolean;
  suffix?: string;
  display?: string; // overrides the rendered number for non-numeric values
  label: string;
  sub: string;
  tone: "brand" | "accent" | "success";
};

const STATS: Stat[] = [
  {
    end: 18764,
    label: "Cặp hỏi-đáp y khoa tiếng Việt",
    sub: "Đã làm sạch và huấn luyện",
    tone: "brand",
  },
  {
    end: 242,
    label: "Thuốc trong cơ sở dữ liệu",
    sub: "Có cảnh báo tương tác",
    tone: "accent",
  },
  {
    end: 4,
    label: "Mô-đun chính trong hệ thống",
    sub: "AI – Quét thuốc – Soul Garden – Hỗ trợ NKT",
    tone: "success",
  },
  {
    end: 0,
    display: "0₫",
    label: "Cho người yếu thế",
    sub: "Người cao tuổi, khiếm thị/thính, vùng sâu",
    tone: "brand",
  },
];

const TONE_RING: Record<Stat["tone"], string> = {
  brand: "ring-brand-500/20 text-brand-700",
  accent: "ring-accent/30 text-accent",
  success: "ring-success/30 text-success",
};

const BULLETS = [
  "Tư vấn y khoa 24/7 bằng tiếng Việt",
  "Phân loại khẩn cấp 3 mức (Xanh – Vàng – Đỏ)",
  "Quét ảnh nhận diện thuốc + cảnh báo tương tác",
  "Hỗ trợ ngôn ngữ ký hiệu cho người khiếm thính",
];

export function AboutMission() {
  return (
    <section id="mission" className="relative overflow-hidden py-16 lg:py-20">
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 -z-10 h-px bg-gradient-to-r from-transparent via-ink-200 to-transparent"
      />
      {/* Soft animated blobs */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-24 top-10 -z-10 h-72 w-72 rounded-full bg-brand/10 blur-3xl animate-blob"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-20 bottom-0 -z-10 h-64 w-64 rounded-full bg-accent/10 blur-3xl animate-blob"
        style={{ animationDelay: "-7s" }}
      />

      <div className="container-page">
        <div className="grid gap-10 lg:grid-cols-12 lg:items-start lg:gap-12">
          {/* Mission statement */}
          <div className="lg:col-span-7">
            <Reveal direction="up">
              <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
                Sứ mệnh
              </p>
              <h2 className="text-h1 text-ink-900">
                Để mỗi gia đình Việt đều có một bác sĩ
                <span className="text-brand"> ngay trong điện thoại</span>.
              </h2>
            </Reveal>

            <Reveal direction="up" delay={120}>
              <div className="mt-6 space-y-4 text-body text-ink-700">
                <p>
                  Ở Việt Nam, không phải ai cũng có thể đến bệnh viện ngay khi cần.
                  Người cao tuổi ở quê, người khuyết tật, gia đình thu nhập thấp —
                  họ vẫn cần lời tư vấn y tế đáng tin cậy bằng tiếng mẹ đẻ.
                </p>
                <p>
                  MediSign AI dùng mô hình y khoa tự host (MedGemma 4 fine-tune
                  LoRA) cùng kỹ thuật RAG để đưa ra gợi ý y khoa chính xác, dễ
                  hiểu, và{" "}
                  <span className="font-semibold text-ink-900">
                    luôn nhắc bạn đi khám khi cần thiết
                  </span>
                  . Không thay thế bác sĩ — chỉ giúp bạn không bị bỏ lại phía sau.
                </p>
              </div>
            </Reveal>

            <ul className="mt-7 grid gap-3 sm:grid-cols-2">
              {BULLETS.map((item, i) => (
                <Reveal
                  key={item}
                  as="li"
                  direction="left"
                  delay={200 + i * 80}
                  className="flex items-start gap-2.5 text-sm text-ink-700"
                >
                  <span className="mt-0.5 grid h-5 w-5 flex-none place-items-center rounded-full bg-success/15 text-success">
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d="M5 12l4 4L19 6"
                        stroke="currentColor"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                  {item}
                </Reveal>
              ))}
            </ul>
          </div>

          {/* Stats grid */}
          <div className="lg:col-span-5">
            <ul className="grid grid-cols-2 gap-4">
              {STATS.map((s, i) => (
                <Reveal
                  key={s.label}
                  as="li"
                  direction="scale"
                  delay={i * 90}
                  className={`group rounded-card border border-ink-200 bg-white p-5 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-card hover:border-brand/30 ring-1 ring-inset ${TONE_RING[s.tone]}`}
                >
                  <p className="text-[clamp(28px,3.5vw,36px)] font-extrabold leading-none tracking-tight text-ink-900">
                    {s.display ? (
                      s.display
                    ) : (
                      <CountUp
                        end={s.end}
                        format={s.format ?? true}
                        suffix={s.suffix}
                      />
                    )}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-ink-800">
                    {s.label}
                  </p>
                  <p className="mt-1 text-xs text-ink-500">{s.sub}</p>
                </Reveal>
              ))}
            </ul>

            <Reveal direction="up" delay={400}>
              <p className="mt-4 text-xs italic text-ink-500">
                Dữ liệu cập nhật quý 2/2026. Một số chỉ số đang trong giai đoạn
                beta nội bộ.
              </p>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}
