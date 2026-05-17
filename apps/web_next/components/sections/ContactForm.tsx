"use client";

import { useState } from "react";

export function ContactForm() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
  }

  return (
    <section id="contact" className="bg-brand-50/40 py-16 lg:py-20">
      <div className="container-page">
        <div className="mx-auto grid max-w-5xl gap-10 lg:grid-cols-[1fr_1.2fr] lg:items-start">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">
              Liên hệ
            </p>
            <h2 className="text-h1 text-ink-900">Mọi góp ý đều quý với chúng tôi</h2>
            <p className="mt-4 text-body text-ink-600">
              Bạn là bác sĩ muốn cộng tác? Người dùng có ý kiến? Hay đang tìm đối tác y tế? Gửi
              cho chúng tôi vài dòng — đội ngũ MediSign sẽ phản hồi trong 1-2 ngày.
            </p>

            <ul className="mt-6 space-y-3 text-base text-ink-700">
              <li className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-pill bg-brand-50 text-brand-700">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" strokeWidth="2" />
                    <path d="M3 7l9 6 9-6" stroke="currentColor" strokeWidth="2" />
                  </svg>
                </span>
                hello@medisign.ai
              </li>
              <li className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-pill bg-brand-50 text-brand-700">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                      d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A14 14 0 0 1 4 7a2 2 0 0 1 1-3z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                Hỗ trợ 24/7 qua chat
              </li>
              <li className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-pill bg-brand-50 text-brand-700">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <circle cx="12" cy="11" r="3" stroke="currentColor" strokeWidth="2" />
                    <path d="M12 21s7-7 7-12a7 7 0 1 0-14 0c0 5 7 12 7 12z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                  </svg>
                </span>
                Hà Nội, Việt Nam
              </li>
            </ul>
          </div>

          <div className="rounded-card border border-ink-200 bg-white p-6 shadow-soft sm:p-8">
            {submitted ? (
              <div role="status" aria-live="polite" className="text-center">
                <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-pill bg-success/15 text-success">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <h3 className="text-h3 text-ink-900">Đã nhận được tin của bạn</h3>
                <p className="mt-2 text-body text-ink-600">
                  Cảm ơn bạn — chúng tôi sẽ phản hồi qua email trong vòng 1-2 ngày làm việc.
                </p>
                <button
                  type="button"
                  onClick={() => setSubmitted(false)}
                  className="btn-outline mt-5"
                >
                  Gửi tin khác
                </button>
              </div>
            ) : (
              <form className="space-y-4" onSubmit={handleSubmit}>
                <Field id="ct-name" label="Họ và tên" required />
                <Field id="ct-email" label="Email" type="email" required />
                <Field id="ct-topic" label="Chủ đề" placeholder="VD: Hợp tác y tế" />
                <div>
                  <label htmlFor="ct-message" className="mb-1 block text-sm font-medium text-ink-800">
                    Nội dung <span className="text-danger">*</span>
                  </label>
                  <textarea
                    id="ct-message"
                    required
                    rows={4}
                    placeholder="Bạn muốn chia sẻ điều gì?"
                    className="w-full rounded-card border-2 border-ink-200 px-4 py-3 text-base text-ink-900 placeholder:text-ink-400 focus:border-brand focus:outline-none focus:shadow-focus"
                  />
                </div>
                <button type="submit" className="btn-primary w-full">
                  Gửi lời nhắn
                </button>
                <p className="text-center text-xs text-ink-500">
                  Bằng cách gửi, bạn đồng ý với{" "}
                  <a href="#" className="font-medium text-brand-700 hover:underline">
                    chính sách bảo mật
                  </a>{" "}
                  của chúng tôi.
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function Field({
  id,
  label,
  type = "text",
  placeholder,
  required
}: {
  id: string;
  label: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-ink-800">
        {label}
        {required && <span className="ml-1 text-danger" aria-hidden="true">*</span>}
      </label>
      <input
        id={id}
        type={type}
        required={required}
        placeholder={placeholder}
        className="h-11 w-full rounded-card border-2 border-ink-200 px-4 text-base text-ink-900 placeholder:text-ink-400 focus:border-brand focus:outline-none focus:shadow-focus"
      />
    </div>
  );
}
