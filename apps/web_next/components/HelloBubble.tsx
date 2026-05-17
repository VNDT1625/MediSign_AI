"use client";

import { useEffect, useState } from "react";

// Bong bóng chào hỏi nổi cạnh bác sĩ ở Hero.
// Cycle: hiện 10s với 1 kịch bản → tắt 5s → đổi sang kịch bản tiếp theo → lặp lại.
// 10 kịch bản xoay vòng để hero không bị tĩnh, vẫn cảm giác "bác sĩ đang chào".

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
  "Hãy kể cho tôi nghe nhé."
];

const VISIBLE_MS = 10_000; // hiện 10 giây
const HIDDEN_MS = 5_000; //  tắt 5 giây trước khi đổi kịch bản

export function HelloBubble() {
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;

    if (visible) {
      // Đang hiện → sau 10s thì ẩn đi
      timer = setTimeout(() => setVisible(false), VISIBLE_MS);
    } else {
      // Đang tắt → sau 5s thì đổi kịch bản và hiện lại
      timer = setTimeout(() => {
        setIndex((i) => (i + 1) % SCENARIOS.length);
        setVisible(true);
      }, HIDDEN_MS);
    }

    return () => clearTimeout(timer);
  }, [visible]);

  return (
    // Đặt ngay cạnh đầu bác sĩ (giữa trên, hơi lệch phải).
    // Đuôi bong bóng đặt ở dưới-trái, mũi chĩa xuống dưới-trái về phía bác sĩ.
    <div className="pointer-events-none absolute left-1/2 top-[8%] z-10 hidden -translate-x-[calc(50%-210px)] -translate-y-[25px] md:block lg:top-[10%] lg:-translate-x-[calc(50%-250px)] lg:-translate-y-[25px]">
      <div
        className={`relative flex items-center gap-2.5 rounded-pill bg-white px-5 py-2.5 text-base font-semibold text-ink-900 shadow-card transition-all duration-500 ease-out ${
          visible
            ? "scale-100 opacity-100"
            : "pointer-events-none scale-95 opacity-0"
        }`}
      >
        {/* Icon dấu + tròn xanh ở đầu pill */}
        <span
          aria-hidden
          className="grid h-7 w-7 flex-none place-items-center rounded-full bg-brand text-white"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 5v14M5 12h14"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
            />
          </svg>
        </span>

        {/*
          Live region để screen reader đọc câu mới mỗi lần đổi.
          min-w giữ kích thước pill ổn định khi text dài/ngắn khác nhau.
        */}
        <span
          aria-live="polite"
          aria-atomic="true"
          className="block min-w-[160px] whitespace-nowrap text-center"
        >
          {SCENARIOS[index]}
        </span>

        {/* Đuôi bong bóng — chĩa xuống dưới-trái về phía bác sĩ */}
        <svg
          aria-hidden="true"
          width="24"
          height="16"
          viewBox="0 0 24 16"
          className="pointer-events-none absolute left-6 top-full -mt-px"
        >
          <path d="M24 0 H4 L0 16 Z" fill="white" />
        </svg>
      </div>
    </div>
  );
}
