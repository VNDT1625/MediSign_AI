"use client";

import { useState } from "react";
import { Reveal } from "@/components/Reveal";

const FAQS = [
  {
    q: "MediSign AI có miễn phí không?",
    a: "Có gói Cơ bản miễn phí với chat AI cơ bản và voice input. Gói Pro 99k/tháng mở khoá lịch sử không giới hạn, ưu tiên phản hồi và Tủ thuốc + SoulGarden.",
  },
  {
    q: "Tôi cần đăng ký tài khoản mới dùng được không?",
    a: "Không bắt buộc. Bạn có thể trải nghiệm trên web mà không cần tài khoản. Tài khoản giúp đồng bộ giữa các thiết bị và lưu lịch sử.",
  },
  {
    q: "Cài đặt trên Windows / macOS / Linux có gì khác?",
    a: "Bản desktop là PWA — cài 1 lần, chạy độc lập, có thể dùng offline cơ bản. Tất cả tính năng giống nhau giữa các nền tảng.",
  },
  {
    q: "Dữ liệu y tế của tôi có an toàn không?",
    a: "Có. Mã hoá đầu cuối khi truyền, mặc định lưu trên thiết bị. Bạn có thể bật đồng bộ đám mây khi cần — và tắt bất cứ lúc nào.",
  },
  {
    q: "AI có thay thế bác sĩ không?",
    a: "Không. MediSign cung cấp gợi ý tham khảo và hướng dẫn sơ cấp cứu. Khi triệu chứng nghiêm trọng, AI luôn nhắc bạn đến gặp bác sĩ thật.",
  },
];

export function DownloadFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="bg-brand-50/40 py-16 lg:py-20">
      <div className="container-page">
        <div className="mx-auto grid max-w-6xl items-start gap-10 lg:grid-cols-12 lg:gap-12">
          {/* LEFT: heading + support card */}
          <div className="lg:col-span-4">
            <Reveal>
              <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
                Câu hỏi thường gặp
              </p>
              <h2 className="text-h2 text-ink-900">Bạn có thắc mắc gì không?</h2>
              <p className="mt-3 text-body text-ink-600">
                Không tìm thấy câu trả lời? Đội ngũ hỗ trợ phản hồi trong 24 giờ.
              </p>
            </Reveal>

            <Reveal className="card-lift mt-6 rounded-[20px] border border-ink-200 bg-white p-5 shadow-soft">
              <div className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-pill bg-brand text-white">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                <div>
                  <p className="text-sm font-semibold text-ink-900">Liên hệ hỗ trợ</p>
                  <p className="text-xs text-ink-600">Phản hồi trong 24 giờ</p>
                </div>
              </div>

              <ul className="mt-4 space-y-2 text-sm text-ink-700">
                <li className="flex items-center gap-2">
                  <span className="text-ink-400">·</span>
                  <a
                    href="mailto:support@medisign.ai"
                    className="font-medium text-brand-700 hover:underline cursor-pointer"
                  >
                    support@medisign.ai
                  </a>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-ink-400">·</span>
                  <span>Hotline: 1900 0000 (8h–22h)</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-ink-400">·</span>
                  <a
                    href="#"
                    className="font-medium text-brand-700 hover:underline cursor-pointer"
                  >
                    Trung tâm trợ giúp →
                  </a>
                </li>
              </ul>
            </Reveal>
          </div>

          {/* RIGHT: accordion list */}
          <Reveal as="ul" stagger className="space-y-3 lg:col-span-8">
            {FAQS.map((f, i) => {
              const open = openIndex === i;
              return (
                <li key={f.q} className="reveal">
                  <details
                    open={open}
                    onToggle={(e) => {
                      if ((e.target as HTMLDetailsElement).open) setOpenIndex(i);
                      else if (openIndex === i) setOpenIndex(null);
                    }}
                    className="group card-lift rounded-card border border-ink-200 bg-white shadow-soft transition-colors open:border-brand/40"
                  >
                    <summary className="flex cursor-pointer items-center justify-between gap-4 p-5 text-base font-semibold text-ink-900 marker:hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 [&::-webkit-details-marker]:hidden">
                      <span>{f.q}</span>
                      <span
                        aria-hidden="true"
                        className="grid h-9 w-9 flex-none place-items-center rounded-pill bg-brand-50 text-brand-700 transition-all duration-300 group-open:rotate-180 group-open:bg-brand group-open:text-white"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path
                            d="M6 9l6 6 6-6"
                            stroke="currentColor"
                            strokeWidth="2.4"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </span>
                    </summary>
                    <div className="px-5 pb-5 pt-0 text-base text-ink-600">
                      <p className="border-t border-ink-100 pt-4">{f.a}</p>
                    </div>
                  </details>
                </li>
              );
            })}
          </Reveal>
        </div>
      </div>
    </section>
  );
}
