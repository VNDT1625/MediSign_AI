"use client";

import { useState } from "react";
import { Reveal } from "@/components/Reveal";

type FAQItem = {
  q: string;
  a: string;
};

const FAQS: FAQItem[] = [
  {
    q: "Tôi có thể dùng thử trước khi trả tiền không?",
    a: "Có. Tất cả gói trả phí (Pro và Gia đình) đều có 7 ngày dùng thử miễn phí. Bạn không cần nhập thông tin thẻ tín dụng để bắt đầu dùng thử."
  },
  {
    q: "Tôi có thể huỷ gói bất cứ lúc nào không?",
    a: "Hoàn toàn có thể. Bạn có thể huỷ gói bất cứ lúc nào từ trang cài đặt tài khoản. Sau khi huỷ, bạn vẫn được dùng đến hết chu kỳ thanh toán hiện tại — không mất phí thêm."
  },
  {
    q: "Dữ liệu sức khoẻ của tôi có được bảo mật không?",
    a: "Có. Toàn bộ dữ liệu sức khoẻ được mã hoá end-to-end và lưu trữ trên máy chủ bảo mật. Chúng tôi không bán hay chia sẻ dữ liệu cá nhân của bạn với bất kỳ bên thứ ba nào."
  },
  {
    q: "Gói Gia đình hoạt động như thế nào?",
    a: "Với Gói Gia đình, bạn có thể thêm tối đa 6 thành viên vào tài khoản. Mỗi thành viên có hồ sơ sức khoẻ riêng, lịch sử tư vấn riêng và được hưởng đầy đủ tính năng Pro. Người quản lý tài khoản có thể xem báo cáo tổng hợp sức khoẻ cả nhà."
  },
  {
    q: "Tôi có thể đổi gói không?",
    a: "Có. Bạn có thể nâng cấp hoặc hạ cấp gói bất cứ lúc nào. Khi nâng cấp, bạn chỉ trả phần chênh lệch cho thời gian còn lại trong chu kỳ. Khi hạ cấp, thay đổi sẽ có hiệu lực từ chu kỳ tiếp theo."
  },
  {
    q: "MediSign AI có thay thế bác sĩ thật không?",
    a: "Không. MediSign AI là công cụ hỗ trợ tư vấn sức khoẻ ban đầu, giúp bạn hiểu triệu chứng và đưa ra quyết định sáng suốt hơn. Với các vấn đề nghiêm trọng, chúng tôi luôn khuyến nghị bạn đến gặp bác sĩ trực tiếp."
  },
  {
    q: "Phương thức thanh toán nào được chấp nhận?",
    a: "Chúng tôi chấp nhận thẻ tín dụng/ghi nợ (Visa, Mastercard), chuyển khoản ngân hàng, ví điện tử (MoMo, ZaloPay, VNPay) và thanh toán qua App Store / Google Play."
  }
];

export function PricingFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section aria-labelledby="faq-heading" className="bg-[#F8FAFC] py-16 lg:py-24">
      <div className="container-page">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="badge-pill">Câu hỏi thường gặp</span>
          <h2 id="faq-heading" className="mt-3 text-h1 text-ink-900">
            Bạn còn thắc mắc?
          </h2>
          <p className="mt-3 text-body text-ink-600">
            Những câu hỏi phổ biến nhất về gói dịch vụ và thanh toán.
          </p>
        </Reveal>

        <Reveal
          delay={150}
          className="mx-auto mt-12 max-w-3xl divide-y divide-ink-200 rounded-card border border-ink-200 bg-white shadow-soft"
        >
          {FAQS.map((faq, i) => {
            const isOpen = openIndex === i;
            return (
              <div key={faq.q}>
                <button
                  type="button"
                  aria-expanded={isOpen}
                  aria-controls={`faq-answer-${i}`}
                  id={`faq-btn-${i}`}
                  onClick={() => setOpenIndex(isOpen ? null : i)}
                  className="flex w-full cursor-pointer items-start justify-between gap-4 px-6 py-5 text-left transition-colors duration-150 hover:bg-ink-100/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand"
                >
                  <span className="text-base font-semibold text-ink-900">{faq.q}</span>
                  <span
                    aria-hidden
                    className={`mt-0.5 grid h-6 w-6 flex-none place-items-center rounded-full border border-ink-200 text-ink-500 transition-all duration-200 ${
                      isOpen ? "rotate-45 border-brand bg-brand-50 text-brand" : ""
                    }`}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
                    </svg>
                  </span>
                </button>

                {isOpen && (
                  <div
                    id={`faq-answer-${i}`}
                    role="region"
                    aria-labelledby={`faq-btn-${i}`}
                    className="px-6 pb-5"
                  >
                    <p className="text-base leading-relaxed text-ink-600">{faq.a}</p>
                  </div>
                )}
              </div>
            );
          })}
        </Reveal>

        <Reveal delay={250} className="mt-8 text-center text-sm text-ink-500">
          Vẫn còn câu hỏi?{" "}
          <a
            href="/support#contact"
            className="font-semibold text-brand-700 underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
          >
            Liên hệ đội hỗ trợ của chúng tôi
          </a>
        </Reveal>
      </div>
    </section>
  );
}
