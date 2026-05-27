// "Người dùng nói gì" — feedback section.
// Refactor: bỏ placeholder text avatar → avatar gradient tròn với chữ cái đầu.
// Thêm dấu nháy lớn trang trí, layout thoáng, reveal stagger.

import { Reveal } from "@/components/Reveal";

type Review = {
  name: string;
  initials: string;
  age: string;
  quote: string;
  tone: string;
  /** URL avatar. Nếu rỗng, fallback gradient + chữ initials. */
  avatar?: string;
};

const REVIEWS: Review[] = [
  {
    name: "Trần Minh Nguyệt",
    initials: "TN",
    age: "62 tuổi · Hà Nội",
    quote:
      "Tôi rất hài lòng vì AI giúp đỡ tôi mỗi khi cần. Bác sĩ ảo dễ hiểu, tận tình, hơn cả mong đợi.",
    tone: "from-brand-100 to-brand-50 text-brand-700",
    avatar: "" // TODO: avatar "Bác sĩ với cụ bà"
  },
  {
    name: "Lê Anh Dũng",
    initials: "AD",
    age: "35 tuổi · Đà Nẵng",
    quote:
      "Trải nghiệm tuyệt vời, AI phản hồi nhanh, hướng dẫn cụ thể. Cả gia đình tôi đều an tâm sử dụng.",
    tone: "from-accent-soft to-orange-50 text-accent",
    avatar: "" // TODO: avatar "Người dùng nam"
  },
  {
    name: "Nguyễn Thu Hương",
    initials: "TH",
    age: "29 tuổi · TP.HCM",
    quote:
      "Tôi thích app vì rất tiện lợi. Tư vấn nhanh chóng và lời khuyên rất hữu ích cho cả gia đình.",
    tone: "from-violet-100 to-violet-50 text-violet-700",
    avatar: "" // TODO: avatar "Người dùng nữ"
  }
];

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="py-16 lg:py-24">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="badge-pill">Phản hồi thật</span>
          <h2 className="mt-3 text-h1 text-ink-900">
            Người dùng nói gì về MediSign AI?
          </h2>
          <div className="mt-4 inline-flex items-center gap-2">
            <Stars />
            <span className="text-sm font-semibold text-ink-700">
              4.9/5 từ hơn 1.200 đánh giá
            </span>
          </div>
        </Reveal>

        <Reveal as="ul" stagger className="mx-auto mt-10 grid max-w-6xl gap-5 sm:mt-12 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3 2xl:max-w-7xl 2xl:gap-8">
          {REVIEWS.map((r, i) => (
            <li key={r.name} className="reveal" style={{ ["--reveal-i" as any]: i }}>
              <article className="relative h-full rounded-card border border-ink-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:border-brand/30 hover:shadow-card">
                {/* Dấu nháy trang trí */}
                <span
                  aria-hidden
                  className="absolute right-5 top-4 select-none font-serif text-[64px] leading-none text-brand-100"
                >
                  &ldquo;
                </span>

                <Stars />
                <p className="relative mt-4 text-[15px] leading-relaxed text-ink-800">
                  {r.quote}
                </p>

                <div className="mt-6 flex items-center gap-3 border-t border-ink-200 pt-4">
                  {/* Avatar — <img> nếu có URL, fallback gradient + chữ initials */}
                  {r.avatar ? (
                    /* eslint-disable-next-line @next/next/no-img-element */
                    <img
                      src={r.avatar}
                      alt={r.name}
                      loading="lazy"
                      className="h-11 w-11 flex-none rounded-pill object-cover"
                    />
                  ) : (
                    <span
                      aria-hidden
                      className={`grid h-11 w-11 flex-none place-items-center rounded-pill bg-gradient-to-br ${r.tone} text-sm font-bold`}
                    >
                      {r.initials}
                    </span>
                  )}
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-ink-900">
                      {r.name}
                    </p>
                    <p className="truncate text-xs text-ink-500">{r.age}</p>
                  </div>
                </div>
              </article>
            </li>
          ))}
        </Reveal>
      </div>
    </section>
  );
}

function Stars() {
  return (
    <span
      className="inline-flex items-center gap-0.5 text-accent"
      role="img"
      aria-label="5/5 sao"
    >
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77 5.82 21l1.18-6.88-5-4.87 6.91-1.01L12 2z" />
        </svg>
      ))}
    </span>
  );
}
