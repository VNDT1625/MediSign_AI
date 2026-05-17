"use client";

/**
 * PricingSection — Healthcare SaaS pricing.
 *
 * Design system (từ ui-ux-pro-max):
 * - Style: Conversion-Optimized + Dimensional Layering
 * - Colors: Cyan #0891B2 (primary), Green #059669 (CTA), bg #ECFEFF
 * - Typography: clean, 16px+ body, high contrast
 * - Effects: 4-level elevation shadows, card Pro nổi lên, hover lift
 * - A11y: WCAG AA, focus rings 3px, cursor-pointer, 44px touch targets
 */

import { useState } from "react";
import { Reveal } from "@/components/Reveal";

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

type Feature = { text: string; highlight?: boolean };

type Plan = {
  id: string;
  name: string;
  tagline: string;
  badge?: string;
  monthlyPrice: number | null;
  yearlyPrice: number | null;
  desc: string;
  features: Feature[];
  cta: string;
  ctaNote?: string;
  variant: "plain" | "featured" | "premium";
};

const PLANS: Plan[] = [
  {
    id: "free",
    name: "Cơ bản",
    tagline: "Miễn phí mãi mãi",
    monthlyPrice: null,
    yearlyPrice: null,
    desc: "Bắt đầu hành trình sức khoẻ không mất phí.",
    features: [
      { text: "Chat AI cơ bản (20 lượt/ngày)" },
      { text: "Lịch sử 7 ngày gần nhất" },
      { text: "Tra cứu thuốc cơ bản" },
      { text: "Hỗ trợ qua email" },
      { text: "1 thiết bị duy nhất" },
    ],
    cta: "Bắt đầu miễn phí",
    variant: "plain",
  },
  {
    id: "pro",
    name: "Pro",
    tagline: "Dành cho cá nhân",
    badge: "Phổ biến nhất",
    monthlyPrice: 199000,
    yearlyPrice: 159000,
    desc: "Trải nghiệm đầy đủ, không giới hạn.",
    features: [
      { text: "Chat AI không giới hạn", highlight: true },
      { text: "Tư vấn 24/7 ưu tiên", highlight: true },
      { text: "Hồ sơ sức khoẻ chi tiết" },
      { text: "Lịch sử & nhắc lịch không giới hạn" },
      { text: "Đồng bộ đa thiết bị" },
      { text: "Ưu tiên hỗ trợ 24/7" },
    ],
    cta: "Dùng thử 7 ngày miễn phí",
    ctaNote: "Không cần thẻ tín dụng",
    variant: "featured",
  },
  {
    id: "family",
    name: "Gia đình",
    tagline: "Cho cả nhà",
    monthlyPrice: 399000,
    yearlyPrice: 319000,
    desc: "Chăm sóc cả nhà cùng một tài khoản.",
    features: [
      { text: "Tất cả tính năng Pro" },
      { text: "Tối đa 6 thành viên", highlight: true },
      { text: "Theo dõi sức khoẻ từng người" },
      { text: "Tư vấn chuyên sâu" },
      { text: "Báo cáo tổng hợp hàng tháng" },
    ],
    cta: "Dùng thử Gia đình",
    ctaNote: "7 ngày miễn phí",
    variant: "premium",
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(n: number) {
  return n.toLocaleString("vi-VN") + "đ";
}

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------

function ICheck({ variant }: { variant: Plan["variant"] }) {
  const cls =
    variant === "featured"
      ? "bg-white/25 text-white"
      : variant === "premium"
        ? "bg-teal-100 text-teal-600"
        : "bg-cyan-50 text-cyan-600";
  return (
    <span
      aria-hidden
      className={`mt-0.5 grid h-5 w-5 flex-none place-items-center rounded-full ${cls}`}
    >
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
        <path d="M5 12l4 4L19 6" stroke="currentColor" strokeWidth="3"
          strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}

function IStar() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Toggle
// ---------------------------------------------------------------------------

function BillingToggle({ yearly, onChange }: { yearly: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-center gap-3">
      <span className={`text-[14px] font-medium transition-colors ${!yearly ? "text-slate-900" : "text-slate-400"}`}>
        Hàng tháng
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={yearly}
        onClick={() => onChange(!yearly)}
        className={`relative inline-flex h-7 w-12 cursor-pointer items-center rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2 ${
          yearly ? "bg-cyan-600" : "bg-slate-200"
        }`}
      >
        <span className="sr-only">{yearly ? "Đang chọn hàng năm" : "Đang chọn hàng tháng"}</span>
        <span
          className={`inline-block h-5 w-5 rounded-full bg-white shadow-md transition-transform duration-200 ${
            yearly ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
      <span className={`text-[14px] font-medium transition-colors ${yearly ? "text-slate-900" : "text-slate-400"}`}>
        Hàng năm
      </span>
      <span
        className={`overflow-hidden rounded-full bg-emerald-100 px-2.5 py-0.5 text-[12px] font-bold text-emerald-700 transition-all duration-300 ${
          yearly ? "max-w-[100px] opacity-100" : "max-w-0 opacity-0 px-0"
        }`}
        aria-live="polite"
      >
        Tiết kiệm 20%
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Plain card (Cơ bản)
// ---------------------------------------------------------------------------

function PlainCard({ plan, yearly }: { plan: Plan; yearly: boolean }) {
  const price = yearly ? plan.yearlyPrice : plan.monthlyPrice;

  return (
    <div className="flex h-full w-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-cyan-200 hover:shadow-md">
      {/* Header */}
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.15em] text-slate-400">
          {plan.name}
        </p>
        <p className="mt-0.5 text-[13px] text-slate-500">{plan.tagline}</p>
      </div>

      {/* Price */}
      <div className="mt-4">
        <div className="flex items-end gap-1">
          <span className="text-[36px] font-extrabold leading-none text-slate-900">
            Miễn phí
          </span>
        </div>
        <p className="mt-1 text-[12px] text-slate-400">Không cần thẻ tín dụng</p>
      </div>

      <div className="my-5 h-px bg-slate-100" />

      {/* Features */}
      <ul className="flex-1 space-y-3" aria-label={`Tính năng gói ${plan.name}`}>
        {plan.features.map((f) => (
          <li key={f.text} className="flex items-start gap-2.5">
            <ICheck variant="plain" />
            <span className="text-[13.5px] text-slate-600">{f.text}</span>
          </li>
        ))}
      </ul>

      {/* CTA */}
      <button
        type="button"
        className="mt-7 inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-xl border-2 border-slate-200 bg-white text-[14px] font-semibold text-slate-700 transition-all duration-200 hover:border-cyan-500 hover:text-cyan-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2"
      >
        {plan.cta}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Featured card (Pro) — nổi lên, conversion-optimized
// ---------------------------------------------------------------------------

function FeaturedCard({ plan, yearly }: { plan: Plan; yearly: boolean }) {
  const price = yearly ? plan.yearlyPrice : plan.monthlyPrice;
  const monthlyPrice = plan.monthlyPrice!;

  return (
    <div className="relative flex h-full w-full flex-col lg:-mt-5">
      {/* Badge nổi lên trên đỉnh card, không bị che */}
      {plan.badge && (
        <div className="flex justify-center">
          <span className="relative z-10 -mb-3 inline-flex items-center gap-1.5 rounded-full bg-amber-400 px-3.5 py-1 text-[12px] font-bold text-white shadow-md">
            <IStar />
            {plan.badge}
          </span>
        </div>
      )}

      <div className="relative flex flex-1 flex-col rounded-2xl bg-gradient-to-b from-cyan-600 via-cyan-700 to-blue-700 p-6 text-white shadow-[0_20px_60px_-10px_rgba(8,145,178,0.5)] transition-transform duration-300 hover:-translate-y-1 lg:pb-8 lg:pt-8">

      {/* Glow blobs */}
      <span aria-hidden className="pointer-events-none absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
      <span aria-hidden className="pointer-events-none absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-cyan-300/20 blur-2xl" />

      {/* Header */}
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.15em] text-white/50">
          {plan.name}
        </p>
        <p className="mt-0.5 text-[13px] text-white/70">{plan.tagline}</p>
      </div>

      {/* Price */}
      <div className="mt-4">
        <div className="flex items-end gap-1">
          <span className="text-[36px] font-extrabold leading-none">
            {price !== null ? fmt(price) : "Miễn phí"}
          </span>
          {price !== null && (
            <span className="mb-1 text-[14px] text-white/60">/ tháng</span>
          )}
        </div>
        {yearly && price !== null && (
          <p className="mt-1 text-[12px] text-cyan-200">
            Tiết kiệm {fmt((monthlyPrice - price) * 12)} / năm
          </p>
        )}
        {!yearly && (
          <p className="mt-1 text-[12px] text-white/50">
            hoặc {fmt(plan.yearlyPrice!)} / tháng khi trả năm
          </p>
        )}
      </div>

      <div className="my-5 h-px bg-white/15" />

      {/* Features */}
      <ul className="flex-1 space-y-3" aria-label={`Tính năng gói ${plan.name}`}>
        {plan.features.map((f) => (
          <li key={f.text} className="flex items-start gap-2.5">
            <ICheck variant="featured" />
            <span className={`text-[13.5px] ${f.highlight ? "font-semibold text-white" : "text-white/85"}`}>
              {f.text}
            </span>
          </li>
        ))}
      </ul>

      {/* CTA — green để tạo contrast rõ (healthcare green #059669) */}
      <div className="mt-7">
        <button
          type="button"
          className="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-xl bg-emerald-500 text-[14px] font-bold text-white shadow-lg shadow-emerald-500/30 transition-all duration-200 hover:bg-emerald-400 hover:shadow-xl active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-cyan-700"
        >
          {plan.cta}
        </button>
        {plan.ctaNote && (
          <p className="mt-2 text-center text-[12px] text-white/50">{plan.ctaNote}</p>
        )}
      </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Premium card (Gia đình)
// ---------------------------------------------------------------------------

function PremiumCard({ plan, yearly }: { plan: Plan; yearly: boolean }) {
  const price = yearly ? plan.yearlyPrice : plan.monthlyPrice;
  const monthlyPrice = plan.monthlyPrice!;

  return (
    <div className="flex h-full w-full flex-col rounded-2xl border border-teal-100 bg-gradient-to-b from-slate-50 to-teal-50/40 p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-teal-300 hover:shadow-md">
      {/* Header */}
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.15em] text-teal-500">
          {plan.name}
        </p>
        <p className="mt-0.5 text-[13px] text-slate-500">{plan.tagline}</p>
      </div>

      {/* Price */}
      <div className="mt-4">
        <div className="flex items-end gap-1">
          <span className="text-[36px] font-extrabold leading-none text-slate-900">
            {price !== null ? fmt(price) : "Miễn phí"}
          </span>
          {price !== null && (
            <span className="mb-1 text-[14px] text-slate-400">/ tháng</span>
          )}
        </div>
        {yearly && price !== null && (
          <p className="mt-1 text-[12px] text-emerald-600 font-medium">
            Tiết kiệm {fmt((monthlyPrice - price) * 12)} / năm
          </p>
        )}
        {!yearly && (
          <p className="mt-1 text-[12px] text-slate-400">
            hoặc {fmt(plan.yearlyPrice!)} / tháng khi trả năm
          </p>
        )}
      </div>

      <div className="my-5 h-px bg-teal-100" />

      {/* Features */}
      <ul className="flex-1 space-y-3" aria-label={`Tính năng gói ${plan.name}`}>
        {plan.features.map((f) => (
          <li key={f.text} className="flex items-start gap-2.5">
            <ICheck variant="premium" />
            <span className={`text-[13.5px] ${f.highlight ? "font-semibold text-slate-900" : "text-slate-600"}`}>
              {f.text}
            </span>
          </li>
        ))}
      </ul>

      {/* CTA */}
      <div className="mt-7">
        <button
          type="button"
          className="inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-xl border-2 border-teal-200 bg-white text-[14px] font-semibold text-teal-700 transition-all duration-200 hover:border-teal-500 hover:bg-teal-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
        >
          {plan.cta}
        </button>
        {plan.ctaNote && (
          <p className="mt-2 text-center text-[12px] text-slate-400">{plan.ctaNote}</p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function PricingSection() {
  const [yearly, setYearly] = useState(false);

  return (
    <section id="pricing" className="bg-gradient-to-b from-slate-50 to-white py-20 lg:py-28">
      <div className="container-page">

        {/* Header */}
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="badge-pill">Bảng giá</span>
          <h2 className="mt-3 text-h1 text-ink-900">
            Phù hợp cho mọi nhu cầu
          </h2>
          <p className="mt-3 text-body text-ink-600">
            Đổi gói hoặc huỷ bất cứ lúc nào — không ràng buộc.
          </p>
        </Reveal>

        {/* Billing toggle */}
        <Reveal className="mt-8">
          <BillingToggle yearly={yearly} onChange={setYearly} />
        </Reveal>

        {/* Cards */}
        <Reveal
          as="ul"
          stagger
          className="mx-auto mt-10 grid max-w-5xl items-end gap-5 lg:grid-cols-3"
        >
          {PLANS.map((plan, i) => (
            <li
              key={plan.id}
              className="reveal flex"
              style={{ ["--reveal-i" as any]: i }}
            >
              {plan.variant === "featured" ? (
                <FeaturedCard plan={plan} yearly={yearly} />
              ) : plan.variant === "premium" ? (
                <PremiumCard plan={plan} yearly={yearly} />
              ) : (
                <PlainCard plan={plan} yearly={yearly} />
              )}
            </li>
          ))}
        </Reveal>

        {/* Trust signals */}
        <Reveal className="mt-10 flex flex-wrap items-center justify-center gap-6 text-[13px] text-slate-400">
          {[
            { icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z", label: "Bảo mật dữ liệu y tế" },
            { icon: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z", label: "Không cần thẻ tín dụng" },
            { icon: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15", label: "Huỷ bất cứ lúc nào" },
          ].map((t) => (
            <span key={t.label} className="flex items-center gap-1.5">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="text-emerald-500">
                <path d={t.icon} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              {t.label}
            </span>
          ))}
        </Reveal>

      </div>
    </section>
  );
}
