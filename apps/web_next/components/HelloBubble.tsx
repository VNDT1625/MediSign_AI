"use client";

import { useEffect, useState } from "react";
import { useVoice } from "@/lib/voice/VoiceContext";

/**
 * HelloBubble — bong bong chao + mic trigger cho voice control tren home.
 *
 * - Khi voice off: xoay vong 10 cau chao (10s hien / 5s tat).
 * - Khi voice enabled (wake/command/executing): hien text trang thai, bubble
 *   doi sang "active" (vien xanh + chấm nhấp nháy).
 * - Click vao bubble = toggle voice (giong pill o cac trang khac).
 */

const SCENARIOS = [
  "Xin chào!",
  "Hôm nay bạn khoẻ chứ?",
  "Có gì cần tư vấn không?",
  "Tôi sẵn sàng lắng nghe.",
  "Bạn ngủ đủ giấc chưa?",
  "Đã uống đủ nước chưa?",
  "Đo huyết áp gần đây không?",
  "Có triệu chứng gì lạ không?",
  "Cần giải thích đơn thuốc?",
  "Hãy kể cho tôi nghe nhé.",
];

const VISIBLE_MS = 10_000;
const HIDDEN_MS = 5_000;

export function HelloBubble() {
  const voice = useVoice();
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    if (visible) {
      timer = setTimeout(() => setVisible(false), VISIBLE_MS);
    } else {
      timer = setTimeout(() => {
        setIndex((i) => (i + 1) % SCENARIOS.length);
        setVisible(true);
      }, HIDDEN_MS);
    }
    return () => clearTimeout(timer);
  }, [visible]);

  // Khi voice on -> luon hien bubble (khong an theo cycle).
  const enabled = voice?.enabled ?? false;
  const supported = voice?.isSupported ?? false;
  const showVoiceState = enabled && voice?.mode !== "off";

  const voiceText = (() => {
    if (!voice) return "";
    switch (voice.mode) {
      case "wake": return 'Đang chờ "Bác sĩ ơi"...';
      case "command": return "Mình đang nghe...";
      case "executing": return voice.lastReply || "Đang xử lý...";
      default: return "Đang nghe...";
    }
  })();

  const text = showVoiceState ? voiceText : SCENARIOS[index];
  const bubbleVisible = showVoiceState ? true : visible;

  function onClick() {
    if (!voice || !supported) return;
    voice.toggle();
  }

  if (!voice || !voice.mounted) return null;

  return (
    <div className="pointer-events-auto absolute left-1/2 top-[8%] z-10 hidden -translate-x-[calc(50%-160px)] -translate-y-[20px] sm:block md:-translate-x-[calc(50%-210px)] md:-translate-y-[25px] lg:top-[10%] lg:-translate-x-[calc(50%-250px)]">
      <button
        type="button"
        onClick={onClick}
        disabled={!supported}
        aria-label={
          showVoiceState
            ? "Đang nghe — bấm để tắt điều khiển bằng giọng nói"
            : "Bấm để điều khiển web bằng giọng nói"
        }
        title={
          showVoiceState
            ? 'Đang nghe — bấm để tắt'
            : supported
              ? 'Điều khiển web qua giọng nói (bấm để bật)'
              : 'Trình duyệt không hỗ trợ nhận diện giọng nói'
        }
        className={`group relative flex items-center gap-2 rounded-pill px-4 py-2 text-sm font-semibold shadow-card transition-all duration-300 ease-out cursor-pointer sm:gap-2.5 sm:px-5 sm:py-2.5 sm:text-base
          ${bubbleVisible ? "scale-100 opacity-100" : "pointer-events-none scale-95 opacity-0"}
          ${showVoiceState
            ? "bg-rose-50 text-rose-700 ring-2 ring-rose-300 hover:bg-rose-100"
            : "bg-white text-ink-900 hover:bg-blue-50/80 hover:ring-2 hover:ring-blue-200"}
          ${!supported ? "opacity-60 cursor-not-allowed" : ""}
        `}
      >
        {/* Text — co min-width de pill khong nhay khi doi cau */}
        <span
          aria-live="polite"
          aria-atomic="true"
          className="block min-w-[120px] whitespace-nowrap text-center sm:min-w-[160px]"
        >
          {text}
        </span>

        {/* Mic icon o cuoi pill */}
        <span
          aria-hidden="true"
          className={`relative grid h-7 w-7 flex-none place-items-center rounded-full transition-colors
            ${showVoiceState ? "bg-rose-600 text-white" : "bg-brand text-white group-hover:bg-brand-700"}
          `}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" x2="12" y1="19" y2="22" />
          </svg>
          {showVoiceState && (
            <span className="absolute -right-0.5 -top-0.5 flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </span>
          )}
        </span>

        {/* Duoi bubble — chia xuong duoi-trai ve phia bac si */}
        <svg
          aria-hidden="true"
          width="24"
          height="16"
          viewBox="0 0 24 16"
          className="pointer-events-none absolute left-6 top-full -mt-px"
        >
          <path d="M24 0 H4 L0 16 Z" fill={showVoiceState ? "#FFF1F2" : "white"} />
        </svg>
      </button>
    </div>
  );
}
