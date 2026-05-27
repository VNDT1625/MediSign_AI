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
  const [mounted, setMounted] = useState(false);
  const [message, setMessage] = useState("");
  const [listening, setListening] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const recRef = useRef<any>(null);

  useEffect(() => {
    setMounted(true);
    if (typeof window === "undefined") return;
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setVoiceSupported(Boolean(SR));
  }, []);

  // Clean up SpeechRecognition khi unmount để tránh "stuck listening" giữa các
  // route hoặc khi modal close.
  useEffect(() => {
    return () => {
      try {
        recRef.current?.stop?.();
      } catch {
        // ignore — instance có thể đã stop.
      }
      recRef.current = null;
    };
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
      // Hero responsive:
      // - Mobile (<640px): min-h-[620px] + h-[92svh] để không cắt search bar và để
      //   thiết bị có thanh URL tự co/giãn không bị "bay" content.
      // - Tablet trở lên: 100svh full-bleed cinematic.
      className="relative isolate flex min-h-[600px] h-[92svh] w-full flex-col overflow-hidden sm:h-[100svh] sm:min-h-[640px]"
      // Suppress hydration warning: một số extension trình duyệt
      // (Bitdefender Anti-tracker, Grammarly...) tiêm attribute như
      // `bis_skin_checked` vào DOM sau SSR, gây mismatch giả.
      suppressHydrationWarning
    >
      {/* Background media — khung cố định full hero, video object-cover crop phần thừa.
          - Mobile: objectPosition kéo lên trên (28%) để khuôn mặt bác sĩ ở giữa,
            không bị header che.
          - Desktop: 42% như cũ (đã tối ưu sẵn). */}
      <div className="absolute inset-0 -z-10 overflow-hidden bg-ink-900">
        {mounted ? (
          <video
            src={HOME_VIDEO}
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            aria-hidden="true"
            className="h-full w-full object-cover [object-position:center_28%] sm:[object-position:center_42%]"
          />
        ) : (
          <div className="h-full w-full bg-ink-900" />
        )}
        {/* Gradient overlay — mobile cần đậm hơn ở đáy để search bar đọc rõ trên
            background video động; desktop giữ nhẹ vì đã có glass card đỡ. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-gradient-to-b from-white/0 via-transparent to-white/40 sm:to-white/15"
        />
      </div>

      <div className="container-page flex flex-1 flex-col py-3 pt-24 sm:py-4 sm:pt-28 lg:py-6 lg:pt-32 2xl:pt-36">

        {/* Khu overlay top: card glass trái + bong bóng phải */}
        <div className="relative flex flex-1 flex-col items-start sm:flex-row">
          {/* Card glass trái:
              - Mobile (<640px): full width, scale nhỏ hơn (max-w-[300px], padding gọn).
              - Tablet (sm-lg): 360-380px, không transform.
              - Desktop (lg+): 420px + 3D rotate-Y hover effect cinematic. */}
          <div
            className="w-full max-w-[300px] sm:max-w-[360px] md:max-w-[380px] lg:max-w-[420px] lg:origin-top-left lg:scale-[1.05] lg:translate-y-[calc(5%+30px)] lg:-translate-x-[calc(20%+25px)]"
            style={{ perspective: "900px" }}
          >
            <div
              className="transform-gpu transition-transform duration-300 will-change-transform lg:[transform:rotateY(22.4deg)] lg:[transform-style:preserve-3d] lg:hover:[transform:rotateY(0deg)]"
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

              <h1 className="text-[clamp(28px,8vw,54px)] font-extrabold leading-[0.96] tracking-tight text-ink-900 sm:text-[clamp(34px,4.3vw,54px)]">
                <span className="block">MediSign</span>
                <span className="block bg-gradient-to-br from-brand to-[#0EA5E9] bg-clip-text text-transparent">
                  AI
                </span>
              </h1>
              <span
                aria-hidden="true"
                className="mt-2 block h-[3px] w-[72px] rounded-pill bg-gradient-to-r from-brand via-[#3B82F6] to-accent sm:mt-3 sm:h-[3.5px] sm:w-[92px]"
              />

              <p className="mt-3 max-w-[28ch] text-[13.5px] font-medium leading-[1.55] text-ink-800 [text-wrap:balance] sm:mt-4 sm:text-[14.5px]">
                Bác sĩ AI đồng hành đáng tin cậy, kết nối yêu thương.
              </p>

              {/* 3 bullet — compact trên mobile, full trên desktop */}
              <ul className="mt-4 space-y-1.5 sm:mt-5 sm:space-y-2">
                {BULLETS.map((b) => (
                  <li
                    key={b}
                    className="flex items-center gap-2 rounded-pill border border-white/70 bg-white/40 px-2.5 py-1 text-[12.5px] font-medium text-ink-800 backdrop-blur-md sm:gap-2.5 sm:px-3 sm:py-1.5 sm:text-[13.5px]"
                  >
                    <span
                      aria-hidden="true"
                      className="grid h-4 w-4 flex-none place-items-center rounded-full bg-brand/15 text-brand sm:h-5 sm:w-5"
                    >
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" className="h-2.5 w-2.5 sm:h-3 sm:w-3">
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

        {/* Khu bottom: search bar — dịch xuống ít hơn để gần web mockup hơn */}
        <div className="mt-4 space-y-3 translate-y-[2px] sm:mt-2">
          <form
            onSubmit={handleSubmit}
            className="mx-auto w-full max-w-[calc(100%-1rem)] sm:max-w-[600px]"
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
                placeholder="Mô tả triệu chứng hoặc hỏi về sức khoẻ…"
                className="relative min-w-0 flex-1 bg-transparent px-2 py-1.5 text-[13px] text-ink-900 placeholder:text-ink-500 focus:outline-none sm:text-[14.5px]"
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
                className={`relative grid h-10 w-10 flex-none place-items-center rounded-pill transition-all duration-200 cursor-pointer sm:h-9 sm:w-9 ${
                  listening
                    ? "bg-accent text-white animate-pulse-soft"
                    : "text-ink-500 hover:bg-ink-100 hover:text-brand-700"
                } disabled:cursor-not-allowed disabled:opacity-50`}
              >
                <MicIcon size={18} />
              </button>

              <button
                type="submit"
                className="relative grid h-10 w-10 flex-none place-items-center rounded-pill bg-brand text-white shadow-soft transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 cursor-pointer sm:h-9 sm:w-9"
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
    <div className="relative overflow-hidden rounded-[22px] border border-white/80 bg-white/25 p-4 shadow-card ring-1 ring-white/70 backdrop-blur-2xl backdrop-saturate-150 sm:rounded-[28px] sm:p-5 md:p-6">
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
        className="pointer-events-none absolute inset-0 rounded-[22px] ring-1 ring-inset ring-white/40 sm:rounded-[28px]"
      />
      <div className="relative">{children}</div>
    </div>
  );
}
