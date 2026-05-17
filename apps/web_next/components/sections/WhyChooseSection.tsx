// "Tại sao chọn MediSign AI?" — 4 lý do cốt lõi.
// Áp dụng "breakout / pop-out" effect: ảnh PNG nền trong suốt được đặt
// vượt mép trên của card → tạo cảm giác 3D nhân vật nhô ra khỏi khung.
// Khi hover, ảnh nhô cao hơn nữa cho cảm giác sống động.

import { Reveal } from "@/components/Reveal";

type Item = {
  title: string;
  desc: string;
  icon: React.ReactNode;
  tone: "brand" | "accent" | "success" | "violet";
  /** URL ảnh PNG nền trong suốt — sẽ pop ra khỏi card. */
  image?: string;
  imageAlt?: string;
};

const ITEMS: Item[] = [
  {
    title: "Đội ngũ bác sĩ chuyên môn",
    desc: "AI được huấn luyện bởi bác sĩ và chuyên gia y tế giàu kinh nghiệm, đảm bảo tư vấn chính xác và đáng tin cậy.",
    tone: "brand",
    image:
      "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/hello.png",
    imageAlt: "Bác sĩ vẫy tay chào",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 4v6a4 4 0 0 0 8 0V4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path d="M5 4h2M11 4h2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path d="M9 14v2a4 4 0 0 0 8 0v-1" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="17" cy="13" r="2" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    )
  },
  {
    title: "Hiểu bạn, chăm bạn",
    desc: "AI nhận biết cảm xúc, theo dõi sức khoẻ và chăm sóc bạn từ những điều nhỏ nhất.",
    tone: "violet",
    image:
      "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/care.png",
    imageAlt: "Bác sĩ nghiêng người quan tâm",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10Z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
      </svg>
    )
  },
  {
    title: "Dễ dùng, sẵn sàng 24/7",
    desc: "Giao diện đơn giản, gõ-nói-chạm đều được. AI phục vụ mọi lúc mọi nơi, không nghỉ.",
    tone: "accent",
    image:
      "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/online.png",
    imageAlt: "Bác sĩ cầm điện thoại tư vấn online",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="6" y="2.5" width="12" height="19" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
        <path d="M10 18.5h4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    )
  },
  {
    title: "Bảo mật & riêng tư",
    desc: "Dữ liệu được mã hoá, kiểm soát chặt chẽ. Bạn yên tâm chia sẻ và tin tưởng MediSign.",
    tone: "success",
    image:
      "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/protect.png",
    imageAlt: "Bác sĩ cầm khiên bảo vệ",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
        <path
          d="m9 12 2 2 4-4"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    )
  }
];

// Mỗi card có gradient riêng làm "stage" cho nhân vật pop ra.
const TONE_CLASSES: Record<
  Item["tone"],
  { stage: string; glow: string; iconBg: string }
> = {
  brand: {
    stage: "from-brand-50 via-brand-50 to-white",
    glow: "bg-brand/15",
    iconBg: "bg-brand-50 text-brand-700 ring-brand-100"
  },
  violet: {
    stage: "from-violet-50 via-violet-50 to-white",
    glow: "bg-violet-300/20",
    iconBg: "bg-violet-50 text-violet-700 ring-violet-100"
  },
  accent: {
    stage: "from-accent-soft via-orange-50 to-white",
    glow: "bg-accent/15",
    iconBg: "bg-accent-soft text-accent ring-accent/20"
  },
  success: {
    stage: "from-success-soft via-emerald-50 to-white",
    glow: "bg-success/15",
    iconBg: "bg-success-soft text-success ring-success/20"
  }
};

export function WhyChooseSection() {
  return (
    <section className="py-16 lg:py-24" id="benefits">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="badge-pill">Vì sao MediSign AI</span>
          <h2 className="mt-3 text-h1 text-ink-900">
            Sức khoẻ thông minh, đồng hành tận tâm
          </h2>
          <p className="mt-3 text-body text-ink-600">
            Kết hợp AI hiện đại với tri thức y khoa, mang đến trải nghiệm chăm sóc
            toàn diện cho mỗi người Việt.
          </p>
        </Reveal>

        {/* pt-20 để chừa khoảng cho phần ảnh tràn lên đỉnh card */}
        <ul className="mx-auto mt-12 grid max-w-6xl gap-6 pt-20 sm:grid-cols-2 lg:grid-cols-4 lg:gap-5">
          {ITEMS.map((it, i) => {
            const tone = TONE_CLASSES[it.tone];
            return (
              <Reveal
                as="li"
                key={it.title}
                delay={i * 120}
                className="relative"
              >
                <article
                  className={`group relative h-full overflow-visible rounded-card border border-ink-200 bg-gradient-to-b ${tone.stage} px-6 pb-6 pt-32 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:border-brand/40 hover:shadow-card`}
                >
                  {/* Vùng "stage" pop-out — nhân vật nhô lên khỏi card */}
                  <div className="pointer-events-none absolute inset-x-0 -top-20 flex h-44 items-end justify-center">
                    {/* Soft glow phía sau nhân vật */}
                    <span
                      aria-hidden
                      className={`absolute bottom-2 h-24 w-32 rounded-full blur-2xl ${tone.glow}`}
                    />

                    {it.image ? (
                      /* eslint-disable-next-line @next/next/no-img-element */
                      <img
                        src={it.image}
                        alt={it.imageAlt || ""}
                        loading="lazy"
                        className="relative h-44 w-auto select-none object-contain drop-shadow-[0_18px_18px_rgba(15,23,42,0.18)] transition-transform duration-500 ease-out group-hover:-translate-y-2 group-hover:scale-[1.04]"
                        draggable={false}
                      />
                    ) : (
                      // Fallback: icon + base disc khi chưa có ảnh
                      <span
                        aria-hidden
                        className={`relative grid h-24 w-24 place-items-center rounded-pill ring-1 transition-all duration-500 group-hover:-translate-y-2 group-hover:scale-105 ${tone.iconBg}`}
                      >
                        {it.icon}
                      </span>
                    )}
                  </div>

                  {/* Đường ground-shadow ellipse nhỏ (chỉ khi có ảnh) */}
                  {it.image && (
                    <span
                      aria-hidden
                      className="pointer-events-none absolute inset-x-0 -top-3 mx-auto h-2 w-24 rounded-[50%] bg-ink-900/15 blur-md"
                    />
                  )}

                  <h3 className="text-center text-base font-semibold text-ink-900">
                    {it.title}
                  </h3>
                  <p className="mt-2 text-center text-sm leading-relaxed text-ink-600">
                    {it.desc}
                  </p>
                </article>
              </Reveal>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
