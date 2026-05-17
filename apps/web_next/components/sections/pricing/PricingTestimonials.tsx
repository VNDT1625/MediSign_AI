import { Reveal } from "@/components/Reveal";

type Testimonial = {
  quote: string;
  name: string;
  role: string;
  plan: string;
  rating: number;
  avatar: string;
};

const TESTIMONIALS: Testimonial[] = [
  {
    quote:
      "MediSign AI giúp tôi theo dõi sức khoẻ cả nhà dễ dàng hơn rất nhiều. Mỗi khi con sốt hay ho, tôi hỏi ngay và được tư vấn rõ ràng, không cần chờ đến sáng mới gọi bác sĩ.",
    name: "Nguyễn Thị Lan",
    role: "Mẹ 2 con, Hà Nội",
    plan: "Gói Gia đình",
    rating: 5,
    avatar: "NL"
  },
  {
    quote:
      "Tôi bị tiểu đường type 2, cần theo dõi chỉ số thường xuyên. Gói Pro giúp tôi có hồ sơ sức khoẻ chi tiết và nhắc lịch uống thuốc đúng giờ. Rất tiện lợi!",
    name: "Trần Văn Minh",
    role: "Kỹ sư, TP.HCM",
    plan: "Gói Pro",
    rating: 5,
    avatar: "TM"
  },
  {
    quote:
      "Ban đầu tôi dùng gói miễn phí để thử, sau 3 ngày đã nâng lên Pro ngay. Chat AI phân tích triệu chứng rất chính xác, giúp tôi quyết định có cần đi khám không.",
    name: "Phạm Thị Hoa",
    role: "Giáo viên, Đà Nẵng",
    plan: "Gói Pro",
    rating: 5,
    avatar: "PH"
  }
];

export function PricingTestimonials() {
  return (
    <section aria-labelledby="testimonials-heading" className="py-16 lg:py-24">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="badge-pill">Người dùng nói gì</span>
          <h2 id="testimonials-heading" className="mt-3 text-h1 text-ink-900">
            Hơn 50.000 người tin tưởng MediSign AI
          </h2>
          <p className="mt-3 text-body text-ink-600">
            Đánh giá thực từ người dùng thực — không phải quảng cáo.
          </p>
        </Reveal>

        {/* Aggregate rating */}
        <Reveal delay={120} className="mx-auto mt-8 flex max-w-xs flex-col items-center gap-2">
          <div className="flex items-center gap-1">
            {Array.from({ length: 5 }).map((_, i) => (
              <svg
                key={i}
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
                className="text-yellow-400"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            ))}
          </div>
          <p className="text-2xl font-bold text-ink-900">4.9 / 5</p>
          <p className="text-sm text-ink-500">Dựa trên 2.000+ đánh giá</p>
        </Reveal>

        {/* Testimonial cards */}
        <Reveal
          as="ul"
          stagger
          className="mx-auto mt-12 grid max-w-6xl gap-6 lg:grid-cols-3"
        >
          {TESTIMONIALS.map((t, i) => (
            <li
              key={t.name}
              className="reveal"
              style={{ ["--reveal-i" as any]: i }}
            >
              <article className="card-lift flex h-full flex-col rounded-card border border-ink-200 bg-white p-6 shadow-soft hover:border-brand/30">
                {/* Stars */}
                <div className="flex items-center gap-0.5" aria-label={`${t.rating} sao`}>
                  {Array.from({ length: t.rating }).map((_, si) => (
                    <svg
                      key={si}
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      aria-hidden="true"
                      className="text-yellow-400"
                    >
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  ))}
                </div>

                {/* Quote */}
                <blockquote className="mt-4 flex-1 text-base leading-relaxed text-ink-700">
                  <p>"{t.quote}"</p>
                </blockquote>

                {/* Author */}
                <footer className="mt-5 flex items-center gap-3 border-t border-ink-100 pt-4">
                  <div
                    aria-hidden
                    className="grid h-10 w-10 flex-none place-items-center rounded-full bg-brand-50 text-sm font-bold text-brand-700"
                  >
                    {t.avatar}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-ink-900">{t.name}</div>
                    <div className="text-xs text-ink-500">{t.role}</div>
                  </div>
                  <span className="ml-auto rounded-pill bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700">
                    {t.plan}
                  </span>
                </footer>
              </article>
            </li>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
