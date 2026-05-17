"use client";

import { useEffect, useRef, useState } from "react";
import { HelloBubble } from "./HelloBubble";
import { SearchIcon, MicIcon, SendIcon } from "./chat/icons";

const HOME_VIDEO =
  "https://pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev/kling_20260516_%E4%BD%9C%E5%93%81_The_doctor_3654_0.mp4";

const BULLETS = [
  "Phân tích triệu chứng chính xác",
  "Tư vấn sức khoẻ 24/7 bằng giọng nói",
  "Bảo mật & bảo vệ dữ liệu"
];

export function HeroVideo({ onAsk }: { onAsk: (message: string) => void }) {
  const [message, setMessage] = useState("");
  const [listening, setListening] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const recRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setVoiceSupported(Boolean(SR));
  }, []);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onAsk(message.trim());
  }

  function toggleVoice() {
    if (!voiceSupported) return;
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) return;
    if (listening) {
      recRef.current?.stop?.();
      setListening(false);
      return;
    }
    const rec = new SR();
    rec.lang = "vi-VN";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (ev: any) => {
      const text = ev.results?.[0]?.[0]?.transcript ?? "";
      setMessage((prev) => (prev ? `${prev} ${text}` : text));
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recRef.current = rec;
    setListening(true);
    rec.start();
  }

  return (
    <section
      aria-label="Giới thiệu MediSign AI"
      // Hero vừa khít 1 viewport, không scroll.
      className="relative isolate flex h-[100svh] min-h-[640px] w-full flex-col overflow-hidden"
    >
      {/* Background media — khung cố định full hero, video object-cover crop phần thừa.
          Có thể phóng to/thu nhỏ (scale) và kéo lên/xuống (objectPosition) để chỉnh
          framing. */}
      <div className="absolute inset-0 -z-10 overflow-hidden bg-ink-900">
        <video
          src={HOME_VIDEO}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          aria-hidden="true"
          className="h-full w-full object-cover"
          style={{
            // Chỉnh framing tại đây:
            // - scale: phóng to/thu nhỏ video trong khung (1 = nguyên, >1 = zoom in)
            // - objectPosition: kéo khung nhìn (0% = top, 50% = center, 100% = bottom)
            //   Y nhỏ hơn 50 → khung neo phía trên video → đầu doctor xuất hiện thấp
            //   hơn trong viewport, tóc cách header.
            transform: "scale(1)",
            objectPosition: "center 42%"
          }}
        />
        {/* Gradient mờ ở đáy — nhẹ thôi để không lấp toàn bộ video, giữ vibe glass
            cho search bar phía dưới có "thứ" để mờ phía sau. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-gradient-to-b from-white/0 via-transparent to-white/15"
        />
      </div>

      <div className="container-page flex flex-1 flex-col py-4 pt-24 lg:py-6 lg:pt-28">
        {/* Khu overlay top: card glass trái + bong bóng phải */}
        <div className="relative flex flex-1 items-start">
          {/* Card glass trái — nghiêng nhẹ tạo chiều sâu 3D, scale 1.15 cho rõ ràng */}
          <div
            className="w-full max-w-[420px] origin-top-left scale-[1.05] lg:translate-y-[calc(5%+30px)] lg:-translate-x-[calc(20%+25px)]"
            style={{ perspective: "900px" }}
          >
            <div
              className="transform-gpu transition-transform duration-300 will-change-transform hover:[transform:rotateY(0deg)]"
              style={{
                transform: "rotateY(22.4deg)",
                transformStyle: "preserve-3d"
              }}
            >
              <GlassCard>
              {/* Logo + eyebrow nhỏ — thêm context, không phá hierarchy */}
              <div className="mb-4 flex items-center gap-2.5">
                <div className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-brand text-white shadow-soft">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M12 3l8 3v5c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-3z"
                      fill="currentColor"
                      fillOpacity="0.18"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    />
                    <path d="M12 8v6M9 11h6" stroke="white" strokeWidth="2.4" strokeLinecap="round" />
                  </svg>
                </div>
                <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-brand-700">
                  Trợ lý y tế AI
                </span>
              </div>

              <h1 className="text-[clamp(34px,4.3vw,54px)] font-extrabold leading-[0.96] tracking-tight text-ink-900">
                <span className="block">MediSign</span>
                <span className="block bg-gradient-to-br from-brand to-[#0EA5E9] bg-clip-text text-transparent">
                  AI
                </span>
              </h1>
              <span
                aria-hidden="true"
                className="mt-3 block h-[3.5px] w-[92px] rounded-pill bg-gradient-to-r from-brand via-[#3B82F6] to-accent"
              />

              <p className="mt-4 max-w-[28ch] text-[14.5px] font-medium leading-[1.55] text-ink-800 [text-wrap:balance]">
                Bác sĩ AI đồng hành đáng tin cậy, kết nối yêu thương.
              </p>

              {/* 3 bullet — mỗi cái là 1 pill kính nhỏ với check tròn */}
              <ul className="mt-5 space-y-2">
                {BULLETS.map((b) => (
                  <li
                    key={b}
                    className="flex items-center gap-2.5 rounded-pill border border-white/70 bg-white/40 px-3 py-1.5 text-[13.5px] font-medium text-ink-800 backdrop-blur-md"
                  >
                    <span
                      aria-hidden="true"
                      className="grid h-5 w-5 flex-none place-items-center rounded-full bg-brand/15 text-brand"
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                        <path
                          d="M5 12l4 4L19 6"
                          stroke="currentColor"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </GlassCard>
            </div>
          </div>

          {/* Bong bóng chào — tự xoay 10 kịch bản, đổi mỗi 20s */}
          <HelloBubble />
        </div>

        {/* Khu bottom: search bar — dịch xuống thêm 20px so với mặc định. */}
        <div className="mt-4 space-y-3 translate-y-[5px]">
          <form
            onSubmit={handleSubmit}
            className="mx-auto w-full max-w-[600px]"
            aria-label="Hỏi MediSign AI"
          >
            {/* Composer pill — glassmorphism rõ:
                - bg trong hơn để thấy mờ video phía sau,
                - border xám đậm để tách khỏi nền sáng,
                - inset ring + gradient highlight cho cảm giác mép kính,
                - shadow ngoài + shadow inset đáy → cảm giác pill nổi 3D. */}
            <div className="group relative flex items-center gap-2 rounded-pill border border-ink-400/60 bg-white/30 px-2 py-1.5 shadow-[0_12px_32px_-8px_rgba(2,132,199,0.18),0_4px_12px_-2px_rgba(15,23,42,0.08)] ring-1 ring-inset ring-white/50 backdrop-blur-2xl backdrop-saturate-150 supports-[backdrop-filter]:bg-white/25 transition-all duration-200 focus-within:border-brand/70 focus-within:shadow-focus focus-within:ring-brand/20 hover:shadow-[0_16px_40px_-8px_rgba(2,132,199,0.22),0_4px_14px_-2px_rgba(15,23,42,0.1)]">
              {/* Inset gradient highlight — mép kính: sáng đỉnh, lắng đáy */}
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-pill bg-gradient-to-b from-white/45 via-white/10 to-white/5"
              />
              {/* Inner shadow đáy — depth tinh tế, giả "lòng" pill */}
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-pill shadow-[inset_0_-1px_0_rgba(15,23,42,0.06),inset_0_1px_0_rgba(255,255,255,0.6)]"
              />

              <span className="relative flex-none pl-2 text-ink-400 transition-colors group-focus-within:text-brand">
                <SearchIcon size={18} />
              </span>

              <label htmlFor="hero-message" className="sr-only">
                Hỏi MediSign AI
              </label>
              <input
                id="hero-message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                type="text"
                placeholder="Mô tả triệu chứng, hỏi đơn thuốc, hoặc bất cứ điều gì về sức khoẻ…"
                className="relative min-w-0 flex-1 bg-transparent px-2 py-1.5 text-[14.5px] text-ink-900 placeholder:text-ink-500 focus:outline-none"
              />

              {/* Phân cách dọc tinh tế giữa input và action buttons */}
              <span
                aria-hidden="true"
                className="relative h-5 w-px flex-none bg-ink-300/50"
              />

              <button
                type="button"
                onClick={toggleVoice}
                aria-pressed={listening}
                aria-label={listening ? "Đang nghe — nhấn để dừng" : "Nhấn để nói"}
                disabled={!voiceSupported}
                className={`relative grid h-9 w-9 flex-none place-items-center rounded-pill transition-all duration-200 cursor-pointer ${
                  listening
                    ? "bg-accent text-white animate-pulse-soft"
                    : "text-ink-500 hover:bg-ink-100 hover:text-brand-700"
                } disabled:cursor-not-allowed disabled:opacity-50`}
              >
                <MicIcon size={18} />
              </button>

              <button
                type="submit"
                className="relative grid h-9 w-9 flex-none place-items-center rounded-pill bg-brand text-white shadow-soft transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 cursor-pointer"
                aria-label="Gửi câu hỏi"
              >
                <SendIcon size={18} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}

function GlassCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative overflow-hidden rounded-[28px] border border-white/80 bg-white/25 p-5 shadow-card ring-1 ring-white/70 backdrop-blur-2xl backdrop-saturate-150 sm:p-6">
      {/* Highlight ánh sáng góc trên-trái — như phản chiếu trên kính */}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute -top-20 -left-14 h-48 w-48 rounded-full bg-white/50 blur-3xl"
      />
      <span
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-24 -right-14 h-52 w-52 rounded-full bg-brand/20 blur-3xl"
      />
      {/* Đường viền sáng nội bộ giả mép kính */}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 rounded-[28px] ring-1 ring-inset ring-white/40"
      />
      <div className="relative">{children}</div>
    </div>
  );
}
