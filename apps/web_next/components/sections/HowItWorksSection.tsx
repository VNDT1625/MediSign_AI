// "Cách hoạt động" — 3 bước.
// Pinned scroll: section sticky, mỗi đoạn scroll user thấy 1 card thêm xuất hiện.
// - Card 1 reveal khi vào pin
// - Card 2 reveal sau ~33% pin
// - Card 3 reveal sau ~66% pin
// Khi qua hết section, page scroll bình thường tiếp.

"use client";

import { useEffect, useRef, useState } from "react";
import { Reveal } from "@/components/Reveal";

type Step = {
  n: number;
  title: string;
  desc: string;
  icon: React.ReactNode;
  /** URL ảnh minh hoạ. Nếu rỗng, fallback icon SVG. */
  image?: string;
  /** URL video minh hoạ (mp4). Ưu tiên hơn `image` nếu có. */
  video?: string;
  imageAlt?: string;
};

const STEPS: Step[] = [
  {
    n: 1,
    title: "Mô tả triệu chứng",
    desc: "Gõ, nói, hoặc gửi ảnh. AI hiểu cả tiếng Việt và ngôn ngữ ký hiệu.",
    video: "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/ho.mp4",
    imageAlt: "Người dùng nhập triệu chứng",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M21 11a8 8 0 0 1-12 7L4 20l1.6-4.5A8 8 0 1 1 21 11Z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
        <path
          d="M9 11h.01M12 11h.01M15 11h.01"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    )
  },
  {
    n: 2,
    title: "AI phân tích",
    desc: "Đối chiếu triệu chứng với hàng triệu ca y khoa, đưa ra chẩn đoán sơ bộ.",
    video: "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/analyze.mp4",
    imageAlt: "AI xử lý dữ liệu",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3v3M12 18v3M21 12h-3M6 12H3M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1M18.4 18.4l-2.1-2.1M7.7 7.7 5.6 5.6"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
        <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.8" />
        <path d="M10 12h4M12 10v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    )
  },
  {
    n: 3,
    title: "Tư vấn & chăm sóc",
    desc: "Nhận lời khuyên, đơn thuốc gợi ý, lịch theo dõi và chăm sóc tại nhà.",
    video: "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/chamsoc.mp4",
    imageAlt: "Bác sĩ tư vấn",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M3 12a9 9 0 1 0 4.5-7.8"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path d="M3 4v5h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
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

// Mỗi card "ăn" ~30vh chiều dài scroll — khoảng 1-2 lần lăn chuột là sang card
// tiếp. Tăng số nếu muốn user cuộn lâu hơn để xem từng card.
const SCROLL_PER_CARD_VH = 30;

export function HowItWorksSection() {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  // Số card đã reveal (0..STEPS.length).
  const [revealed, setRevealed] = useState(0);
  const [reduced, setReduced] = useState(false);

  // Detect prefers-reduced-motion → bỏ pin, hiện cả 3 ngay.
  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener?.("change", onChange);
    return () => mq.removeEventListener?.("change", onChange);
  }, []);

  // Scroll listener: tính xem user đã cuộn qua bao nhiêu trong block pin
  // → ra số card cần reveal.
  useEffect(() => {
    if (reduced) {
      setRevealed(STEPS.length);
      return;
    }

    function update() {
      const el = wrapRef.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const vh = window.innerHeight;
      const pinHeight = el.offsetHeight - vh; // tổng chiều cuộn trong pin
      // distance đã cuộn vào pin (0 ở đầu, pinHeight ở cuối)
      const scrolled = Math.min(Math.max(-rect.top, 0), pinHeight);
      const progress = pinHeight > 0 ? scrolled / pinHeight : 0;

      // Chia progress thành N chặng đều. Ngay khi user bắt đầu cuộn vào pin
      // (progress > 0), card 1 đã hiện. Cuộn tiếp 1/3 → card 2, tiếp 1/3 → card 3.
      const next = Math.min(
        STEPS.length,
        Math.ceil(progress * STEPS.length)
      );
      setRevealed((prev) => (prev === next ? prev : next));
    }

    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [reduced]);

  const wrapHeightVh = reduced
    ? "auto"
    : `${SCROLL_PER_CARD_VH * STEPS.length + 50}vh`;

  return (
    <section className="bg-gradient-to-b from-brand-50/60 to-transparent">
      {/* Outer wrapper — định độ dài cuộn để pin con sticky chạy */}
      <div
        ref={wrapRef}
        className="relative"
        style={{ minHeight: wrapHeightVh }}
      >
        {/* Inner sticky — pin lại ở giữa viewport khi user cuộn */}
        <div className="sticky top-0 flex min-h-screen items-center py-16 lg:py-20">
          <div className="container-page w-full">
            <Reveal className="mx-auto max-w-2xl text-center">
              <span className="badge-pill">Cách hoạt động</span>
              <h2 className="mt-3 text-h1 text-ink-900">3 bước, đồng hành sức khoẻ</h2>
              <p className="mt-3 text-body text-ink-600">
                Đơn giản như một cuộc trò chuyện — AI lắng nghe, phân tích, tư vấn cho bạn.
              </p>
            </Reveal>

            <ol className="mx-auto mt-14 grid max-w-6xl items-stretch gap-6 lg:grid-cols-3 lg:gap-10">
              {STEPS.map((s, i) => (
                <li key={s.n} className="relative">
                  <SequentialCard
                    step={s}
                    isLast={i === STEPS.length - 1}
                    visible={i < revealed}
                  />
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </section>
  );
}

function SequentialCard({
  step,
  isLast,
  visible
}: {
  step: Step;
  isLast: boolean;
  visible: boolean;
}) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const wasVisible = useRef(false);

  // Khi card vừa được reveal → tự động play video 1 lần.
  useEffect(() => {
    if (visible && !wasVisible.current && videoRef.current) {
      const v = videoRef.current;
      v.currentTime = 0;
      v.play().catch(() => {});
    }
    wasVisible.current = visible;
  }, [visible]);

  function playFromStart() {
    const v = videoRef.current;
    if (!v) return;
    v.currentTime = 0;
    v.play().catch(() => {});
  }

  function pauseAtStart() {
    const v = videoRef.current;
    if (!v) return;
    v.pause();
    if (step.n === 3) {
      // Card 3: dừng ở frame cuối
      if (v.duration && Number.isFinite(v.duration)) {
        v.currentTime = Math.max(0, v.duration - 0.05);
      }
    } else {
      // Card 1, 2: dừng ở frame đầu
      v.currentTime = 0;
    }
  }

  return (
    <>
      <article
        onMouseEnter={playFromStart}
        onMouseLeave={pauseAtStart}
        onFocus={playFromStart}
        onBlur={pauseAtStart}
        tabIndex={step.video ? 0 : -1}
        style={{
          opacity: visible ? 1 : 0,
          transform: visible ? "translate3d(0, 0, 0) scale(1)" : "translate3d(0, 32px, 0) scale(0.95)",
          transition: "opacity 600ms cubic-bezier(0.4,0,0.2,1), transform 600ms cubic-bezier(0.4,0,0.2,1)"
        }}
        className="group relative flex h-full flex-col items-center rounded-card border border-ink-200 bg-white p-7 text-center shadow-soft hover:-translate-y-1 hover:border-brand/40 hover:shadow-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
      >
        {/* Số bước nổi góc trên */}
        <span
          aria-hidden
          className="absolute -top-4 left-1/2 inline-flex h-9 w-9 -translate-x-1/2 items-center justify-center rounded-pill bg-brand text-base font-bold text-white shadow-soft ring-4 ring-white"
        >
          {step.n}
        </span>

        {/* Slot media — ưu tiên video, fallback ảnh, cuối cùng là icon */}
        <div
          aria-hidden
          className={`mt-4 mb-5 flex items-center justify-center overflow-hidden rounded-card bg-white text-brand-700 transition-transform duration-300 group-hover:scale-105 ${
            step.n === 3 
              ? "aspect-video w-48" 
              : "aspect-square w-32"
          }`}
        >
          {step.video ? (
            <video
              ref={videoRef}
              src={step.video}
              muted
              playsInline
              preload="metadata"
              aria-label={step.imageAlt || ""}
              onEnded={(e) => {
                // Card 1, 2: tua về đầu sau khi chạy xong.
                // Card 3: để nguyên ở frame cuối.
                if (step.n !== 3) {
                  const v = e.currentTarget;
                  v.pause();
                  v.currentTime = 0;
                }
              }}
              className="h-full w-full object-cover"
            />
          ) : step.image ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={step.image}
              alt={step.imageAlt || ""}
              loading="lazy"
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="scale-125 opacity-80">{step.icon}</span>
          )}
        </div>

        <h3 className="text-h3 text-ink-900">{step.title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-ink-600">{step.desc}</p>
      </article>

      {/* Mũi tên kết nối — chỉ hiện ở giữa các bước, desktop */}
      {!isLast && (
        <span
          aria-hidden
          style={{
            opacity: visible ? 1 : 0,
            transition: "opacity 500ms ease-out 200ms"
          }}
          className="hidden lg:absolute lg:top-1/2 lg:-right-7 lg:block lg:-translate-y-1/2 lg:text-brand/50"
        >
          <svg width="56" height="14" viewBox="0 0 56 14" fill="none">
            <path
              d="M2 7h44m0 0-5-5m5 5-5 5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="4 5"
            />
          </svg>
        </span>
      )}
    </>
  );
}
